from __future__ import annotations

import copy
import json
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable


logger = logging.getLogger(__name__)
Validator = Callable[[Any], Any]


class JsonFileStore:
    """Thread-safe JSON storage with atomic writes and mtime-aware caching."""

    _registry_lock = threading.Lock()
    _path_locks: dict[Path, threading.RLock] = {}

    def __init__(self, path: Path):
        self.path = Path(path).resolve()
        with self._registry_lock:
            self._lock = self._path_locks.setdefault(self.path, threading.RLock())
        self._cache: Any = None
        self._cache_signature: tuple[int, int] | None = None

    def _signature(self) -> tuple[int, int] | None:
        try:
            stat = self.path.stat()
            return stat.st_mtime_ns, stat.st_size
        except FileNotFoundError:
            return None

    @staticmethod
    def _clone(value: Any) -> Any:
        return copy.deepcopy(value)

    def load(self, default: Any, validator: Validator | None = None) -> Any:
        with self._lock:
            signature = self._signature()
            if signature is None:
                return self._clone(default)
            if self._cache is not None and signature == self._cache_signature:
                return self._clone(self._cache)
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    value = json.load(handle)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                logger.exception("Failed to load JSON store: %s", self.path)
                return self._clone(default)
            if validator is not None:
                try:
                    value = validator(value)
                except Exception:
                    logger.exception("Invalid JSON store payload: %s", self.path)
                    return self._clone(default)
            self._cache = self._clone(value)
            self._cache_signature = signature
            return self._clone(value)

    def save(self, value: Any, validator: Validator | None = None) -> Any:
        with self._lock:
            normalized = validator(value) if validator is not None else value
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.path.parent,
                    prefix=f".{self.path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as handle:
                    temporary_path = handle.name
                    json.dump(normalized, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary_path, self.path)
            finally:
                if temporary_path and os.path.exists(temporary_path):
                    try:
                        os.unlink(temporary_path)
                    except OSError:
                        logger.warning("Could not remove temporary JSON file: %s", temporary_path)
            self._cache = self._clone(normalized)
            self._cache_signature = self._signature()
            return self._clone(normalized)

    def update(
        self,
        default: Any,
        updater: Callable[[Any], Any],
        validator: Validator | None = None,
    ) -> Any:
        with self._lock:
            current = self.load(default, validator=validator)
            return self.save(updater(current), validator=validator)
