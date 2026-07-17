from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatModel(Protocol):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str: ...


@runtime_checkable
class EmbeddingModel(Protocol):
    def embedding(self, text: str, **kwargs: Any) -> list[float]: ...
