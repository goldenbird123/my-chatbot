from __future__ import annotations

from .ollama import LLMConfig, LLMService


def create_llm(provider: str = "ollama", config: LLMConfig | None = None):
    if provider != "ollama":
        raise ValueError(f"unsupported LLM provider: {provider}")
    return LLMService(config=config)


def create_llm_service(config: LLMConfig | None = None) -> LLMService:
    return create_llm(config=config)
