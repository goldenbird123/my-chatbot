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


memory = MemoryManager()


print("===== 测试用户资料 =====")

profile = memory.load_profile()

print(profile)


print("\n===== 测试聊天历史 =====")

history = memory.load_history()

print("历史数量:", len(history))


print("\n===== 测试全部memory =====")

all_memory = memory.load_all_memory()

print(all_memory)