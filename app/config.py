from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float, minimum: float = 0.0) -> float:
    try:
        return max(minimum, float(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


def _env_path(name: str, default: Path) -> Path:
    path = Path(os.getenv(name, str(default))).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    embedding_url: str = os.getenv(
        "EMBEDDING_URL", "http://localhost:11434/api/embeddings"
    )
    model_name: str = os.getenv("MODEL_NAME", "qwen3:8b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    memory_path: Path = _env_path("MEMORY_PATH", PROJECT_ROOT / "memory")
    timeout: int = _env_int("OLLAMA_TIMEOUT", 120, minimum=1)
    embedding_timeout: int = _env_int("EMBEDDING_TIMEOUT", 60, minimum=1)
    retry: int = _env_int("OLLAMA_RETRY", 2)
    retry_backoff: float = _env_float("OLLAMA_RETRY_BACKOFF", 0.5)
    temperature: float = _env_float("LLM_TEMPERATURE", 0.3)
    num_predict: int = _env_int("LLM_NUM_PREDICT", 200, minimum=1)
    max_history_messages: int = _env_int("MAX_HISTORY_MESSAGES", 20, minimum=2)
    recent_history_messages: int = _env_int("RECENT_HISTORY_MESSAGES", 8, minimum=2)
    max_context_chars: int = _env_int("MAX_CONTEXT_CHARS", 6000, minimum=500)
    summary_after_messages: int = _env_int("SUMMARY_AFTER_MESSAGES", 16, minimum=2)
    embedding_cache_size: int = _env_int("EMBEDDING_CACHE_SIZE", 256, minimum=1)
    vector_search_limit: int = _env_int("VECTOR_SEARCH_LIMIT", 3, minimum=1)
    vector_duplicate_distance: float = _env_float(
        "VECTOR_DUPLICATE_DISTANCE", 0.1
    )


settings = Settings()

# Backwards-compatible constants. New code should prefer ``settings``.
OLLAMA_URL = settings.ollama_url
EMBEDDING_URL = settings.embedding_url
MODEL_NAME = settings.model_name
EMBEDDING_MODEL = settings.embedding_model
MEMORY_PATH = settings.memory_path
TIMEOUT = settings.timeout
EMBEDDING_TIMEOUT = settings.embedding_timeout
RETRY = settings.retry
