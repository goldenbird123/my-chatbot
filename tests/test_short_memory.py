from memory.short_memory import ShortMemory


class FakeHistory:
    def recent(self, limit):
        return [{"content": str(i)} for i in range(limit)]


class FakeManager:
    history = FakeHistory()


def test_short_memory_returns_requested_recent_messages():
    result = ShortMemory(FakeManager()).get_recent(3)
    assert [item["content"] for item in result] == ["0", "1", "2"]


def test_short_memory_rejects_non_positive_limit():
    assert ShortMemory(FakeManager()).get_recent(0) == []
