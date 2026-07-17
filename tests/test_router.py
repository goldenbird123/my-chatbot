from memory.memory_router import MemoryRouter


class FakeRetriever:
    def retrieve(self, text):
        return {"query": text}


def test_memory_router_delegates_to_retriever():
    router = MemoryRouter(FakeRetriever())

    assert router.route("hello") == {"query": "hello"}
