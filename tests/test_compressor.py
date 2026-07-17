from memory.memory_compressor import MemoryCompressor


class FakeMemory:
    def __init__(self):
        self.history = [{"role": "user", "content": str(i)} for i in range(35)]
        self.summary = {}

    def load_history(self):
        return list(self.history)

    def save_history(self, history):
        self.history = list(history)

    def load_summary(self):
        return self.summary

    def save_summary(self, summary):
        self.summary = summary


class FakeSummary:
    def summarize(self, history, old_summary=""):
        return "summary"


def test_memory_compressor_compresses_long_history():
    memory = FakeMemory()
    compressor = MemoryCompressor(
        memory=memory, summarizer=FakeSummary(), max_history=30, keep_recent=10
    )
    assert compressor.check() is True
    assert compressor.compress() == "summary"
    assert memory.summary == {"content": "summary"}
    assert len(memory.history) == 10
