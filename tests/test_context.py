from app.context_builder import ContextBuilder
from memory.context_manager import ContextManager


def test_legacy_context_manager_keeps_recent_history():
    history = [{"role": "user", "content": str(i)} for i in range(10)]
    context = ContextManager(max_history=3).build_context(history, {"name": "Alice"})
    assert [item["content"] for item in context["history"]] == ["7", "8", "9"]


def test_context_builder_adds_memory_history_and_current_user():
    messages = ContextBuilder().build_messages(
        "current",
        {
            "profile": {"name": "Alice"},
            "summary": {},
            "retrieved": {},
            "history": [{"role": "assistant", "content": "previous"}],
        },
    )
    assert messages[0]["role"] == "system"
    assert "Alice" in messages[0]["content"]
    assert messages[-1] == {"role": "user", "content": "current"}
