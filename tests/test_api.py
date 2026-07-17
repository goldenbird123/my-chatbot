import app.api as api_module
from fastapi.testclient import TestClient


class FakeAgent:
    def __init__(self, answer="ok"):
        self.answer = answer

    def chat(self, message):
        return f"{self.answer}: {message}"

    def close(self):
        pass


def test_health_endpoint():
    response = TestClient(api_module.app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint_uses_agent(monkeypatch):
    monkeypatch.setattr(api_module, "get_agent", lambda: FakeAgent("echo"))
    response = TestClient(api_module.app).post("/chat", json={"message": " hello "})
    assert response.status_code == 200
    assert response.json() == {"answer": "echo: hello"}


def test_chat_rejects_blank_message():
    response = TestClient(api_module.app).post("/chat", json={"message": "   "})
    assert response.status_code == 422


def test_api_hides_internal_exception(monkeypatch):
    class BrokenAgent:
        def chat(self, message):
            raise RuntimeError("secret detail")

    monkeypatch.setattr(api_module, "get_agent", lambda: BrokenAgent())
    client = TestClient(api_module.app, raise_server_exceptions=False)
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "secret detail" not in response.text
