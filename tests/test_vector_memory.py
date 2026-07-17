from memory.chroma_store import VectorMemory


class FakeCollection:
    def __init__(self):
        self.items = {}
        self.query_calls = 0

    def get(self, ids):
        return {"ids": [item for item in ids if item in self.items]}

    def count(self):
        return len(self.items)

    def add(self, ids, embeddings, documents, metadatas):
        self.items[ids[0]] = documents[0]

    def query(self, query_embeddings, n_results):
        self.query_calls += 1
        return {
            "documents": [list(self.items.values())[:n_results]],
            "distances": [[0.5]],
        }


def test_vector_memory_uses_hash_id_to_skip_exact_duplicates():
    collection = FakeCollection()
    embed_calls = []

    def embedder(text, **kwargs):
        embed_calls.append(text)
        return [0.1, 0.2]

    memory = VectorMemory(
        collection=collection, embedder=embedder, duplicate_distance=0
    )
    assert memory.add_memory("same text") is True
    assert memory.add_memory("same text") is False
    assert embed_calls == ["same text"]


def test_vector_memory_embedding_cache_is_bounded():
    memory = VectorMemory(
        collection=FakeCollection(),
        embedder=lambda text, **kwargs: [float(len(text))],
        cache_size=2,
        duplicate_distance=0,
    )
    memory.embedding("a")
    memory.embedding("b")
    memory.embedding("c")
    assert list(memory._embedding_cache) == ["b", "c"]


def test_vector_memory_search_limits_to_collection_size():
    collection = FakeCollection()
    collection.items["1"] = "memory"
    memory = VectorMemory(
        collection=collection,
        embedder=lambda text, **kwargs: [0.1],
        duplicate_distance=0,
    )
    assert memory.search("query", limit=3) == ["memory"]
