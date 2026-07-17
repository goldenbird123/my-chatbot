from __future__ import annotations

from pathlib import Path

from app.config import settings
from memory.json_store import JsonFileStore
from memory.schemas import MemoryData


PROFILE_PATH = settings.memory_path / "user_profile.json"


def _normalize_profile(payload) -> dict[str, str]:
    return MemoryData.safe_parse(payload).model_dump()


class ProfileMemory:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or PROFILE_PATH)
        self.store = JsonFileStore(self.path)

    @staticmethod
    def default() -> dict[str, str]:
        return MemoryData().model_dump()

    def load(self) -> dict[str, str]:
        return self.store.load(self.default(), validator=_normalize_profile)

    def save(self, profile) -> dict[str, str]:
        return self.store.save(profile, validator=_normalize_profile)

    def update(self, new_data) -> dict[str, str]:
        incoming = _normalize_profile(new_data)

        def merge(profile):
            for key, value in incoming.items():
                if value:
                    profile[key] = value
            return profile

        return self.store.update(self.default(), merge, validator=_normalize_profile)
