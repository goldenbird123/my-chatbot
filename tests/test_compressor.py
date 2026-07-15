import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from memory.memory_compressor import MemoryCompressor
from memory.memory_manager import MemoryManager



memory = MemoryManager()



history=[]



for i in range(35):

    history.append({

        "role":"user",

        "content":
        f"这是第{i}次聊天，我学习LangChain"

    })



memory.save_history(
    history
)



compressor = MemoryCompressor()



print(
    "是否需要压缩:"
)

print(
    compressor.check()
)



result = compressor.compress()



print(
    "新的总结:"
)

print(
    result
)



print(
    "剩余聊天:"
)

print(
    len(
        memory.load_history()
    )
)