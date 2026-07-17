from app.llm_service import LLMConfig, LLMService


class FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {"message": {"content": "ok"}}

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, json, timeout):
        self.calls.append((method, url, json, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_llm_service_chat_uses_expected_payload():
    session = FakeSession([FakeResponse()])
    service = LLMService(
        LLMConfig(model="test-model", chat_url="http://test/chat", timeout=3, retry=0),
        session=session,
    )
    assert service.chat([{"role": "user", "content": "hello"}]) == "ok"
    method, url, payload, timeout = session.calls[0]
    assert (method, url, timeout) == ("POST", "http://test/chat", 3)
    assert payload["model"] == "test-model"
    assert payload["stream"] is False


def test_llm_service_retries_http_5xx():
    session = FakeSession([FakeResponse(503), FakeResponse()])
    service = LLMService(
        LLMConfig(retry=1, retry_backoff=0), session=session, sleep=lambda _: None
    )
    assert service.chat([]) == "ok"
    assert len(session.calls) == 2


def test_embedding_accepts_new_ollama_response_shape():
    session = FakeSession([FakeResponse(data={"embeddings": [[1, 2, 3]]})])
    service = LLMService(LLMConfig(retry=0), session=session)
    assert service.embedding("hello") == [1.0, 2.0, 3.0]
