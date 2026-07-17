from __future__ import annotations

from app.config import settings
from memory.manager import MemoryManager


class MemoryCompressor:
    """Compatibility utility for explicit history compression."""

    def __init__(self, memory=None, summarizer=None, max_history=None, keep_recent=None):
        self.memory = memory or MemoryManager()
        self.summary = summarizer or self.memory.summarizer
        self.max_history = max_history or settings.summary_after_messages
        self.keep_recent = keep_recent or settings.recent_history_messages

    def check(self):
        return len(self.memory.load_history()) >= self.max_history

    def compress(self):
        history = self.memory.load_history()
        new_summary = self.summary.summarize(
            history, old_summary=self.memory.load_summary()
        )
        self.memory.save_summary({"content": new_summary})
        self.memory.save_history(history[-self.keep_recent :])
        return new_summary
