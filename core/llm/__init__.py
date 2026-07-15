from .factory import create_llm
from .ollama import OllamaLLM


def chat(messages):
    return create_llm().chat(messages)


__all__ = ["create_llm", "OllamaLLM", "chat"]
