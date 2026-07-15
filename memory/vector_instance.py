from memory.vector_memory import VectorMemory


_vector_memory_instance = None


def get_vector_memory():

    global _vector_memory_instance

    if _vector_memory_instance is None:

        _vector_memory_instance = VectorMemory()

    return _vector_memory_instance