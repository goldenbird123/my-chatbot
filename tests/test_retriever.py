from memory.retriever import MemoryRetriever


class FakeVectorMemory:
    def search(self, query, limit=3):
        return ["用户正在开发 AI Agent"]


class FakeMemory:
    vector_memory = FakeVectorMemory()

    def load_profile(self):
        return {
            "name": "Alice",
            "learning": "LangChain",
            "project": "AI Agent",
            "likes": "简洁回答",
        }

    def load_summary(self):
        return {"content": "长期学习本地 Agent"}


def test_retriever_combines_structured_and_vector_memory():
    result = MemoryRetriever(FakeMemory()).retrieve("你记得我的项目吗")
    assert result["project"] == "AI Agent"
    assert result["summary"]["content"] == "长期学习本地 Agent"
    assert result["vector_memory"] == ["用户正在开发 AI Agent"]


def test_retriever_avoids_vector_search_for_small_talk():
    class ExplodingVector:
        def search(self, query, limit=3):
            raise AssertionError("should not search vector memory")

    memory = FakeMemory()
    memory.vector_memory = ExplodingVector()
    assert MemoryRetriever(memory).retrieve("你好") == {}
