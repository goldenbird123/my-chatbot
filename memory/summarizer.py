from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.prompts import build_memory_prompt
from core.llm import LLMConfig, LLMService
from memory.json_store import JsonFileStore


SUMMARY_PATH = settings.memory_path / "memory_summary.json"


def _normalize_summary(payload) -> dict:
    if isinstance(payload, str):
        return {"content": payload.strip()}
    if not isinstance(payload, dict):
        return {}
    content = payload.get("content", payload.get("summary", ""))
    return {"content": str(content).strip()} if content else {}


class MemorySummarizer:
    def __init__(
        self,
        path: Path | None = None,
        service=None,
        *,
        model=None,
        url=None,
        timeout=None,
    ):
        self.path = Path(path or SUMMARY_PATH)
        self.store = JsonFileStore(self.path)
        if service is not None:
            self.service = service
        else:
            config = LLMConfig()
            if model is not None:
                config.model = model
            if url is not None:
                config.chat_url = url
            if timeout is not None:
                config.timeout = timeout
            self.service = LLMService(config)

    def load(self) -> dict:
        return self.store.load({}, validator=_normalize_summary)

    def save(self, summary) -> dict:
        return self.store.save(summary, validator=_normalize_summary)

    def summarize(self, history, old_summary="") -> str:
        prompt = build_memory_prompt(memory=str(old_summary), history=str(history))
        return self.service.chat([{"role": "user", "content": prompt}])
