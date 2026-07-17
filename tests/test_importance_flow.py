from memory.pipeline import MemoryPipeline


class FakeProfile:
    def __init__(self):
        self.data = None

    def update(self, data):
        self.data = data


class FakeImportance:
    def check(self, text):
        return {"memory": True, "type": "project", "reason": "test"}


class FakeExtractor:
    def extract(self, text):
        return {"memory": True, "data": {"project": "AI Agent"}}


class FakeVector:
    def __init__(self):
        self.items = []

    def add_memory(self, text):
        self.items.append(text)
        return True


def test_memory_pipeline_judges_extracts_and_stores():
    profile, vector = FakeProfile(), FakeVector()
    pipeline = MemoryPipeline(
        profile,
        lambda: vector,
        importance=FakeImportance(),
        extractor=FakeExtractor(),
    )
    result = pipeline.process("我正在开发 AI Agent")
    assert profile.data == {"project": "AI Agent"}
    assert vector.items == ["我正在开发 AI Agent"]
    assert result["vector_saved"] is True
