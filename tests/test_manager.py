from memory.history import ChatHistoryMemory
from memory.manager import MemoryManager
from memory.profile import ProfileMemory
from memory.summarizer import MemorySummarizer


class FakeService:
    def chat(self, messages):
        return "summary"

    def close(self):
        pass


class FakeImportance:
    judge = None

    def check(self, text):
        return {"memory": True, "type": "profile", "reason": "test"}


class FakeExtractor:
    service = None

    def extract(self, text):
        return {"memory": True, "data": {"name": "Alice"}}


class FakeVector:
    def add_memory(self, text):
        return True

    def search(self, query, limit=3):
        return []


def create_manager(tmp_path):
    return MemoryManager(
        profile=ProfileMemory(tmp_path / "profile.json"),
        history=ChatHistoryMemory(tmp_path / "history.json"),
        summarizer=MemorySummarizer(tmp_path / "summary.json", service=FakeService()),
        importance=FakeImportance(),
        extractor=FakeExtractor(),
        vector_memory=FakeVector(),
    )


def test_manager_appends_and_loads_history(tmp_path):
    manager = create_manager(tmp_path)
    history = manager.append_exchange("hello", "world")
    assert len(history) == 2
    assert manager.load_history()[1]["content"] == "world"


def test_manager_runs_memory_pipeline(tmp_path):
    manager = create_manager(tmp_path)
    result = manager.apply_memory_lifecycle("我叫 Alice", history=[])
    assert result["importance"]["memory"] is True
    assert manager.load_profile()["name"] == "Alice"
