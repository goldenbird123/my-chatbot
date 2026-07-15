import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from memory.memory_retriever import MemoryRetriever
from memory.memory_manager import MemoryManager


retriever = MemoryRetriever(MemoryManager())


tests = [
    "我的学习方向是什么？",
    "我的项目是什么？",
    "你知道我的名字吗？",
    "你还记得我吗？"
]


for t in tests:

    print("\n问题:",t)

    result = retriever.retrieve(t)

    print(result)
