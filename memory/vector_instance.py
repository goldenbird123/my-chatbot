import threading

from memory.chroma_store import VectorMemory


_vector_memory_instance = None
_instance_lock = threading.Lock()


def get_vector_memory():
    global _vector_memory_instance
    if _vector_memory_instance is None:
        with _instance_lock:
            if _vector_memory_instance is None:
                _vector_memory_instance = VectorMemory()
    return _vector_memory_instance
