from memory.retriever import MemoryRetriever


class EmptyMemory:
    class Vector:
        def search(self, query, limit=3):
            return []

    vector_memory = Vector()

    def load_profile(self):
        return {}

    def load_summary(self):
        return {}


def test_retriever_omits_empty_values():
    assert MemoryRetriever(EmptyMemory()).retrieve("记得之前吗") == {}
