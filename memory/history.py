from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from memory.json_store import JsonFileStore


HISTORY_PATH = settings.memory_path / "chat_history.json"


def _normalize_history(payload) -> list[dict]:
    if not isinstance(payload, list):
        return []
    result = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant", "system", "tool"} or not isinstance(content, str):
            continue
        normalized = {"role": role, "content": content}
        if item.get("time"):
            normalized["time"] = str(item["time"])
        result.append(normalized)
    return result


class ChatHistoryMemory:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or HISTORY_PATH)
        self.store = JsonFileStore(self.path)

    def load(self) -> list[dict]:
        return self.store.load([], validator=_normalize_history)

    def save(self, history) -> list[dict]:
        return self.store.save(history, validator=_normalize_history)

    @staticmethod
    def trim(history, max_messages=20) -> list[dict]:
        normalized = _normalize_history(history)
        return normalized[-max_messages:] if max_messages > 0 else []

    def recent(self, limit=5) -> list[dict]:
        return self.load()[-limit:] if limit > 0 else []

    def append_exchange(self, user_input: str, answer: str, max_messages: int) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()

        def append(history):
            history.extend(
                [
                    {"role": "user", "content": user_input, "time": now},
                    {"role": "assistant", "content": answer, "time": now},
                ]
            )
            return self.trim(history, max_messages=max_messages)

        return self.store.update([], append, validator=_normalize_history)
