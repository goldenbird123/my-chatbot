from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from app.config import settings


logger = logging.getLogger(__name__)
UNAVAILABLE_PREFIX = "本地模型暂时不可用"


@dataclass(slots=True)
class LLMConfig:
    model: str = settings.model_name
    embedding_model: str = settings.embedding_model
    chat_url: str = settings.ollama_url
    embedding_url: str = settings.embedding_url
    timeout: int = settings.timeout
    embedding_timeout: int = settings.embedding_timeout
    retry: int = settings.retry
    retry_backoff: float = settings.retry_backoff
    temperature: float = settings.temperature
    num_predict: int = settings.num_predict
    extra_options: dict[str, Any] = field(default_factory=dict)


class OllamaServiceError(RuntimeError):
    """Base error for an Ollama request."""


class OllamaUnavailableError(OllamaServiceError):
    pass


class OllamaModelNotFoundError(OllamaServiceError):
    pass


class OllamaTimeoutError(OllamaServiceError):
    pass


class OllamaResponseError(OllamaServiceError):
    pass


class LLMService:
    """Small Ollama adapter with connection reuse, timeouts and bounded retries."""

    def __init__(
        self,
        config: LLMConfig | None = None,
        session: requests.Session | None = None,
        sleep=time.sleep,
    ):
        self.config = config or LLMConfig()
        self._session = session or requests.Session()
        self._owns_session = session is None
        self._sleep = sleep

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    def _error_for_response(self, response: requests.Response) -> OllamaServiceError | None:
        status = response.status_code
        if status == 404:
            return OllamaModelNotFoundError("模型不存在或 Ollama 接口路径错误")
        if status == 429 or status >= 500:
            return OllamaUnavailableError(f"Ollama 服务暂不可用: HTTP {status}")
        if status >= 400:
            return OllamaServiceError(f"Ollama 请求失败: HTTP {status}")
        return None

    def _request_with_retry(self, method: str, url: str, *, timeout: int, payload: dict):
        last_error: OllamaServiceError | None = None
        for attempt in range(self.config.retry + 1):
            try:
                response = self._session.request(
                    method, url, json=payload, timeout=timeout
                )
                response_error = self._error_for_response(response)
                if response_error is None:
                    return response
                last_error = response_error
                if response.status_code < 500 and response.status_code != 429:
                    break
            except requests.exceptions.Timeout as exc:
                last_error = OllamaTimeoutError(f"Ollama 请求超时: {exc}")
            except requests.exceptions.ConnectionError as exc:
                last_error = OllamaUnavailableError(f"无法连接 Ollama: {exc}")
            except requests.exceptions.RequestException as exc:
                last_error = OllamaServiceError(f"Ollama 请求失败: {exc}")

            if attempt < self.config.retry:
                self._sleep(self.config.retry_backoff * (2**attempt))

        raise last_error or OllamaServiceError("Ollama 请求失败")

    @staticmethod
    def _response_json(response: requests.Response) -> dict:
        try:
            data = response.json()
        except (TypeError, ValueError) as exc:
            raise OllamaResponseError("Ollama 返回了无效 JSON") from exc
        if not isinstance(data, dict):
            raise OllamaResponseError("Ollama 返回结构无效")
        return data

    def chat(self, messages, stop=None, **kwargs) -> str:
        payload = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "stream": False,
            "think": kwargs.get("think", False),
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("num_predict", self.config.num_predict),
                **self.config.extra_options,
            },
        }
        if stop:
            payload["options"]["stop"] = stop

        try:
            response = self._request_with_retry(
                "POST",
                self.config.chat_url,
                timeout=kwargs.get("timeout", self.config.timeout),
                payload=payload,
            )
            data = self._response_json(response)
            content = data.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()
            return "本地模型暂时没有返回内容"
        except OllamaServiceError as exc:
            logger.warning("Ollama chat unavailable: %s", exc)
            return f"{UNAVAILABLE_PREFIX}：{exc}"
        except Exception as exc:  # Defensive adapter boundary.
            logger.exception("Unexpected Ollama chat failure")
            return f"{UNAVAILABLE_PREFIX}：{exc}"

    def embedding(self, text: str, **kwargs) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("embedding text must not be empty")
        payload = {
            "model": kwargs.get("model", self.config.embedding_model),
            "prompt": text,
        }
        response = self._request_with_retry(
            "POST",
            self.config.embedding_url,
            timeout=kwargs.get("timeout", self.config.embedding_timeout),
            payload=payload,
        )
        data = self._response_json(response)
        vector = data.get("embedding")
        if vector is None:
            vectors = data.get("embeddings")
            vector = vectors[0] if isinstance(vectors, list) and vectors else None
        if not isinstance(vector, list) or not vector:
            raise OllamaResponseError("Ollama embedding 返回结构无效")
        try:
            return [float(value) for value in vector]
        except (TypeError, ValueError) as exc:
            raise OllamaResponseError("Ollama embedding 包含非数值内容") from exc


class OllamaLLM(LLMService):
    """Backwards-compatible class name."""


def is_unavailable_response(value: object) -> bool:
    return isinstance(value, str) and value.startswith(UNAVAILABLE_PREFIX)
