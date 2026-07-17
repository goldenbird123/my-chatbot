from .base import ChatModel, EmbeddingModel
from .factory import create_llm, create_llm_service
from .ollama import (
    LLMConfig,
    LLMService,
    OllamaLLM,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaServiceError,
    OllamaTimeoutError,
    OllamaUnavailableError,
    UNAVAILABLE_PREFIX,
    is_unavailable_response,
)


_default_service = LLMService()


def chat(messages, **kwargs):
    return _default_service.chat(messages, **kwargs)


def embedding(text, **kwargs):
    return _default_service.embedding(text, **kwargs)


__all__ = [
    "ChatModel",
    "EmbeddingModel",
    "LLMConfig",
    "LLMService",
    "OllamaLLM",
    "OllamaModelNotFoundError",
    "OllamaResponseError",
    "OllamaServiceError",
    "OllamaTimeoutError",
    "OllamaUnavailableError",
    "UNAVAILABLE_PREFIX",
    "chat",
    "create_llm",
    "create_llm_service",
    "embedding",
    "is_unavailable_response",
]
