import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from memory.memory_summary import MemorySummary
from memory.memory_manager import MemoryManager
print("==============================")
print("       测试 MemorySummary")
print("==============================")


# 创建管理器
memory = MemoryManager()


# 读取聊天记录
history = memory.load_history()


print("\n当前聊天记录数量:")
print(len(history))


print("\n开始生成总结...\n")


# 创建总结器
summary = MemorySummary()


# 注意这里！！！
# summarize只需要history
result = summary.summarize(history)


print("==============================")
print("生成结果:")
print(result)
print("==============================")


# 保存
memory.save_summary(
    {
        "summary": result
    }
)


print("\n保存成功")