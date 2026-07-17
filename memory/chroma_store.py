from __future__ import annotations

import hashlib
import logging
import os
import threading
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from core.llm import OllamaServiceError, embedding as default_embedding


logger = logging.getLogger(__name__)
VECTOR_STORE_PATH = settings.memory_path / "vector_store"


class VectorMemory:
    """Thread-safe Chroma adapter with bounded embedding caching and idempotent writes."""

    def __init__(
        self,
        path: Path | None = None,
        collection=None,
        embedder=None,
        cache_size: int | None = None,
        duplicate_distance: float | None = None,
    ):
        self.path = Path(path or VECTOR_STORE_PATH)
        self._embedder = embedder or default_embedding
        self._cache_size = cache_size or settings.embedding_cache_size
        self._duplicate_distance = (
            settings.vector_duplicate_distance
            if duplicate_distance is None
            else duplicate_distance
        )
        self._embedding_cache: OrderedDict[str, list[float]] = OrderedDict()
        self._cache_lock = threading.Lock()
        self._collection_lock = threading.RLock()
        self.collection = collection or self._create_collection()

    def _create_collection(self):
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
        os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", "False")
        os.environ.setdefault("POSTHOG_DISABLED", "true")
        import chromadb

        self.path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(self.path),
            settings=chromadb.Settings(anonymized_telemetry=False, allow_reset=False),
        )
        return client.get_or_create_collection(
            name="chat_memory", embedding_function=None
        )

    def embedding(self, text: str) -> list[float]:
        normalized = " ".join(text.split())
        if not normalized:
            return []
        with self._cache_lock:
            cached = self._embedding_cache.get(normalized)
            if cached is not None:
                self._embedding_cache.move_to_end(normalized)
                return list(cached)
        try:
            vector = self._embedder(
                normalized,
                timeout=settings.embedding_timeout,
                model=settings.embedding_model,
            )
        except (OllamaServiceError, ValueError):
            logger.exception("Ollama embedding failed")
            return []
        if not vector:
            return []
        with self._cache_lock:
            self._embedding_cache[normalized] = list(vector)
            self._embedding_cache.move_to_end(normalized)
            while len(self._embedding_cache) > self._cache_size:
                self._embedding_cache.popitem(last=False)
        return list(vector)

    @staticmethod
    def _memory_id(text: str) -> str:
        value = f"{settings.embedding_model}\0{text}".encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    def _contains_id(self, memory_id: str) -> bool:
        try:
            existing = self.collection.get(ids=[memory_id])
            return bool(existing and existing.get("ids"))
        except Exception:
            logger.debug("Collection does not support exact id lookup", exc_info=True)
            return False

    def check_duplicate(self, vector, threshold=None) -> bool:
        if not vector or self.count_memory() == 0:
            return False
        maximum = self._duplicate_distance if threshold is None else threshold
        if maximum <= 0:
            return False
        try:
            result = self.collection.query(query_embeddings=[vector], n_results=1)
            distances = result.get("distances") or []
            return bool(distances and distances[0] and distances[0][0] <= maximum)
        except Exception:
            logger.exception("Vector duplicate check failed")
            return False

    def add_memory(self, text: str) -> bool:
        normalized = " ".join(text.split())
        if not normalized:
            return False
        memory_id = self._memory_id(normalized)
        with self._collection_lock:
            if self._contains_id(memory_id):
                return False
        vector = self.embedding(normalized)
        if not vector:
            return False
        with self._collection_lock:
            if self._contains_id(memory_id) or self.check_duplicate(vector):
                return False
            try:
                self.collection.add(
                    ids=[memory_id],
                    embeddings=[vector],
                    documents=[normalized],
                    metadatas=[
                        {
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "embedding_model": settings.embedding_model,
                        }
                    ],
                )
                return True
            except Exception:
                logger.exception("Failed to write vector memory")
                return False

    def search(self, query: str, limit=3) -> list[str]:
        if limit <= 0:
            return []
        count = self.count_memory()
        if count == 0:
            return []
        vector = self.embedding(query)
        if not vector:
            return []
        try:
            with self._collection_lock:
                result = self.collection.query(
                    query_embeddings=[vector], n_results=min(limit, count)
                )
            documents = result.get("documents") or []
            return [item for item in (documents[0] if documents else []) if item]
        except Exception:
            logger.exception("Vector memory query failed")
            return []

    def count_memory(self) -> int:
        try:
            with self._collection_lock:
                return int(self.collection.count())
        except Exception:
            logger.exception("Vector memory count failed")
            return 0
