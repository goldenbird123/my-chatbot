from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from core.llm import create_llm

from memory.memory_manager import MemoryManager
from memory.memory_extractor_fixed import MemoryExtractor
from memory.memory_retriever_fixed import MemoryRetriever
from memory.memory_importance_fixed import MemoryImportance
from memory.memory_router import MemoryRouter
from memory.short_memory import ShortMemory


_background_executor = ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="memory-background",
)


class QwenBrain:
    def __init__(self):
        self.llm = create_llm()
        self.memory = MemoryManager()
        self.extractor = MemoryExtractor()
        self.retriever = MemoryRetriever(self.memory)
        self.importance = MemoryImportance()
        self.router = MemoryRouter(self.retriever)
        self.short_memory = ShortMemory(self.memory)

    def _run_background(self, task, *args):
        future = _background_executor.submit(task, *args)
        future.add_done_callback(self._log_background_error)

    def _log_background_error(self, future):
        try:
            future.result()
        except Exception as e:
            print("后台记忆任务失败:", e)

    def _update_memory_background(self, user_input, history):
        importance_result = self.importance.check(user_input)
        profile = self.memory.load_profile()

        if importance_result.get("memory"):
            result = self.extractor.extract(user_input)
            if result.get("memory"):
                for k, v in result.get("data", {}).items():
                    if v:
                        profile[k] = v

            if importance_result.get("type") == "vector":
                self.memory.save_vector_memory(user_input)

        if "我叫" in user_input:
            name = user_input.split("我叫", 1)[1]
            name = name.split("，")[0]
            name = name.split(",")[0]
            profile["name"] = name.strip()

        self.memory.save_profile(profile)

        if len(history) % 10 == 0:
            from memory.memory_summary import MemorySummary

            summary = MemorySummary()
            old = self.memory.load_summary()
            new_summary = summary.summarize(history, old)
            self.memory.save_summary({"summary": new_summary})

    def chat(self, user_input):
        history = self.short_memory.get_recent(limit=5)
        history = self.memory.trim_history(history)
        memory = self.router.route(user_input)
        memory_context = str(memory)

        messages = [
            {
                "role": "system",
                "content": f"""
你叫鸟神，是一个本地AI助手。
回答风格：
- 简洁
- 自然
- 像朋友交流，不夸张
规则：
1. 回复控制在6句话内。
2. 不要大量使用表情。
3. 不要说：
"我为你骄傲"
"你太厉害了"
4. 不编造自己的经历。
5. 用户问个人信息时直接回答。
6. 技术问题优先给解决方案。

用户信息：
{memory_context}
""",
            }
        ]

        for item in history:
            messages.append({"role": item["role"], "content": item["content"]})

        messages.append({"role": "user", "content": user_input})
        answer = self.llm.chat(messages)
        if answer.startswith("本地模型暂不可用"):
            answer = "本地模型现在不可用，Ollama 没有启动或连接失败了。你可以先启动服务，再继续聊。"

        history.append({"role": "user", "content": user_input, "time": str(datetime.now())})
        history.append({"role": "assistant", "content": answer, "time": str(datetime.now())})
        history = self.memory.trim_history(history)
        self.memory.save_history(history)
        self._run_background(self._update_memory_background, user_input, list(history))
        return answer
