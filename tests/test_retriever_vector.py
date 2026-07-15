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


print("开始测试")


retriever = MemoryRetriever(MemoryManager())



result = retriever.retrieve(
    "你记得我之前学习什么吗"
)


print("================")

print(result)


print("================")
