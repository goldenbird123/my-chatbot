from __future__ import annotations

import logging

from memory.extractor import MemoryExtractor
from memory.importance import MemoryImportance


logger = logging.getLogger(__name__)


class MemoryPipeline:
    """Importance Judge -> Extractor -> long-term stores."""

    VECTOR_TYPES = {"preference", "project", "goal", "knowledge", "vector"}

    def __init__(
        self,
        profile,
        vector_memory_supplier,
        importance=None,
        extractor=None,
    ):
        self.profile = profile
        self.vector_memory_supplier = vector_memory_supplier
        self.importance = importance or MemoryImportance()
        self.extractor = extractor or MemoryExtractor()

    def process(self, user_input: str) -> dict:
        importance = self.importance.check(user_input)
        extracted = {"memory": False, "data": {}}
        vector_saved = False
        if not importance.get("memory"):
            return {
                "importance": importance,
                "extracted": extracted,
                "vector_saved": vector_saved,
            }

        extracted = self.extractor.extract(user_input)
        if extracted.get("memory") and extracted.get("data"):
            self.profile.update(extracted["data"])

        if importance.get("type") in self.VECTOR_TYPES:
            try:
                vector_saved = bool(self.vector_memory_supplier().add_memory(user_input))
            except Exception:
                logger.exception("Failed to save vector memory")

        return {
            "importance": importance,
            "extracted": extracted,
            "vector_saved": vector_saved,
        }
