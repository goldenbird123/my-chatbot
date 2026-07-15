import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from memory.memory_manager import MemoryManager
from memory.short_memory import ShortMemory


manager = MemoryManager()


short = ShortMemory(
    manager
)


result = short.get_recent(5)


print("最近聊天:")
print(result)