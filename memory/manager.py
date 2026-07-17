from __future__ import annotations

import logging
import threading
from typing import Any

from app.config import settings
from core.llm import is_unavailable_response
from memory.extractor import MemoryExtractor
from memory.history import ChatHistoryMemory
from memory.pipeline import MemoryPipeline
from memory.profile import ProfileMemory
from memory.retriever import MemoryRetriever
from memory.summarizer import MemorySummarizer


logger = logging.getLogger(__name__)


class MemoryManager:
    """Stable facade for short, long and vector memory services."""

    def __init__(
        self,
        profile: ProfileMemory | None = None,
        history: ChatHistoryMemory | None = None,
        extractor: MemoryExtractor | None = None,
        summarizer: MemorySummarizer | None = None,
        importance=None,
        vector_memory=None,
        pipeline: MemoryPipeline | None = None,
    ):
        self.profile = profile or ProfileMemory()
        self.history = history or ChatHistoryMemory()
        self.summarizer = summarizer or MemorySummarizer()
        self._vector_memory = vector_memory
        self._vector_lock = threading.Lock()
        self._messages_since_summary = 0
        self.pipeline = pipeline or MemoryPipeline(
            profile=self.profile,
            vector_memory_supplier=lambda: self.vector_memory,
            importance=importance,
            extractor=extractor,
        )
        self.extractor = getattr(self.pipeline, "extractor", extractor)
        self.retriever = MemoryRetriever(self)

    @property
    def vector_memory(self):
        if self._vector_memory is None:
            with self._vector_lock:
                if self._vector_memory is None:
                    from memory.vector import get_vector_memory

                    self._vector_memory = get_vector_memory()
        return self._vector_memory

    def load_profile(self):
        return self.profile.load()

    def save_profile(self, profile):
        return self.profile.save(profile)

    def update_profile(self, new_data):
        return self.profile.update(new_data)

    def load_history(self):
        return self.history.load()

    def save_history(self, history):
        return self.history.save(history)

    def append_exchange(self, user_input: str, answer: str):
        return self.history.append_exchange(
            user_input, answer, max_messages=settings.max_history_messages
        )

    def trim_history(self, history, max_messages=None):
        return self.history.trim(
            history, max_messages=max_messages or settings.max_history_messages
        )

    def load_summary(self):
        return self.summarizer.load()

    def save_summary(self, summary):
        return self.summarizer.save(summary)

    def save_vector_memory(self, text):
        return self.vector_memory.add_memory(text)

    def retrieve(self, query):
        return self.retriever.retrieve(query)

    def load_all_memory(self):
        return {
            "profile": self.load_profile(),
            "summary": self.load_summary(),
            "history": self.load_history(),
        }

    def format_context(self, memory_context: Any, history: list[dict]) -> dict:
        context = {
            "profile": self.load_profile(),
            "summary": self.load_summary(),
            "retrieved": memory_context or {},
            "history": self.trim_history(
                history, max_messages=settings.recent_history_messages
            ),
        }
        return self._trim_context_chars(context, settings.max_context_chars)

    @staticmethod
    def _trim_context_chars(context: dict, max_chars: int) -> dict:
        if len(str(context)) <= max_chars:
            return context
        trimmed = dict(context)
        history = list(trimmed.get("history") or [])
        while history and len(str(trimmed)) > max_chars:
            history.pop(0)
            trimmed["history"] = history
        if len(str(trimmed)) > max_chars:
            summary = str(trimmed.get("summary", ""))
            trimmed["summary"] = summary[-max_chars // 3 :]
        return trimmed

    def apply_memory_lifecycle(self, user_input, history=None):
        result = self.pipeline.process(user_input)
        result["summary_updated"] = False
        self._messages_since_summary += 2
        if (
            history
            and len(history) >= settings.summary_after_messages
            and self._messages_since_summary >= settings.summary_after_messages
        ):
            result["summary_updated"] = self._summarize_history(history)
            if result["summary_updated"]:
                self._messages_since_summary = 0
        result["memory"] = self.retrieve(user_input)
        return result

    def _summarize_history(self, history) -> bool:
        try:
            new_summary = self.summarizer.summarize(
                history, old_summary=self.load_summary()
            )
            if new_summary and not is_unavailable_response(new_summary):
                self.save_summary({"content": new_summary})
                return True
        except Exception:
            logger.exception("Memory summary failed")
        return False

    def close(self):
        services = [
            getattr(getattr(self.pipeline, "extractor", None), "service", None),
            getattr(
                getattr(getattr(self.pipeline, "importance", None), "judge", None),
                "service",
                None,
            ),
            getattr(self.summarizer, "service", None),
        ]
        for service in services:
            close = getattr(service, "close", None)
            if callable(close):
                close()
