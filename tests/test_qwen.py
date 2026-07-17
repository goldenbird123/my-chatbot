from concurrent.futures import ThreadPoolExecutor

from app.agent import Agent


class FakeLLM:
    def chat(self, messages):
        return "ok"


class FakeMemory:
    def __init__(self):
        self.history = []
        self.lifecycle_calls = []

    def retrieve(self, query):
        return {}

    def format_context(self, memory_context, history):
        return {"profile": {}, "summary": {}, "retrieved": {}, "history": history}

    def load_history(self):
        return list(self.history)

    def append_exchange(self, user_input, answer):
        self.history.extend(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer},
            ]
        )
        return list(self.history)

    def apply_memory_lifecycle(self, user_input, history=None):
        self.lifecycle_calls.append((user_input, list(history or [])))
        return {"memory": {}}


def test_agent_chat_returns_llm_answer_and_updates_memory():
    memory = FakeMemory()
    agent = Agent(llm=FakeLLM(), memory=memory, background_memory=False)
    assert agent.chat(" hello ") == "ok"
    assert [item["content"] for item in memory.history] == ["hello", "ok"]
    assert memory.lifecycle_calls[0][0] == "hello"


def test_agent_serializes_concurrent_history_updates():
    memory = FakeMemory()
    agent = Agent(llm=FakeLLM(), memory=memory, background_memory=False)
    with ThreadPoolExecutor(max_workers=4) as pool:
        answers = list(pool.map(agent.chat, ["a", "b", "c", "d"]))
    assert answers == ["ok"] * 4
    assert len(memory.history) == 8


def test_agent_rejects_empty_input():
    agent = Agent(llm=FakeLLM(), memory=FakeMemory(), background_memory=False)
    try:
        agent.chat(" ")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("empty input should fail")
