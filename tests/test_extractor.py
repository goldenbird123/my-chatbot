from memory.extractor import MemoryExtractor


class FakeService:
    def chat(self, messages):
        return '```json\n{"memory": true, "data": {"name": "Alice", "learning": "LangChain"}}\n```'


def test_memory_extractor_parses_fenced_json():
    result = MemoryExtractor(service=FakeService()).extract("我叫 Alice")
    assert result["memory"] is True
    assert result["data"]["name"] == "Alice"


class InvalidService:
    def chat(self, messages):
        return "not-json"


def test_memory_extractor_fails_closed_on_invalid_json():
    result = MemoryExtractor(service=InvalidService()).extract("hello")
    assert result["memory"] is False
