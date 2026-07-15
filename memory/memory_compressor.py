from memory.memory_summary import MemorySummary
from memory.memory_manager import MemoryManager



class MemoryCompressor:


    def __init__(self):

        self.memory = MemoryManager()

        self.summary = MemorySummary()


        # 超过多少条开始压缩

        self.max_history = 30



    def check(self):


        history = self.memory.load_history()


        if len(history) < self.max_history:

            return False


        return True



    def compress(self):


        history = self.memory.load_history()


        print(
            "开始压缩记忆..."
        )


        new_summary = self.summary.summarize(
            history
        )


        self.memory.save_summary({

            "summary":
            new_summary

        })


        # 保留最近聊天

        new_history = history[-10:]


        self.memory.save_history(
            new_history
        )


        print(
            "记忆压缩完成"
        )


        return new_summary
