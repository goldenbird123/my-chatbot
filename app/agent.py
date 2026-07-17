from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor

from app.config import settings
from app.context_builder import ContextBuilder
from app.intent import IntentClassifier
from app.langgraph_adapter import LangGraphAdapter
from app.planner import Planner
from app.tool_executor import ToolExecutor
from app.tool_registry import ToolRegistry
from core.llm import create_llm_service, is_unavailable_response
from memory.manager import MemoryManager
from memory.short_memory import ShortMemory


logger = logging.getLogger(__name__)


class Agent:
    """Agent Core: orchestrates collaborators without owning their implementations."""

    def __init__(
        self,
        llm=None,
        memory=None,
        intent_classifier=None,
        planner=None,
        tools=None,
        tool_executor=None,
        context_builder=None,
        langgraph=None,
        short_memory=None,
        background_memory: bool = True,
    ):
        self.llm = llm or create_llm_service()
        self.memory = memory or MemoryManager()
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.planner = planner or Planner()
        self.tools = tools or ToolRegistry(allowed_tools={"search"})
        self.tool_executor = tool_executor or ToolExecutor(self.tools)
        self.context_builder = context_builder or ContextBuilder()
        self.langgraph = langgraph or LangGraphAdapter()
        self.short_memory = short_memory or ShortMemory(self.memory)
        self._chat_lock = threading.RLock()
        self._executor = (
            ThreadPoolExecutor(max_workers=1, thread_name_prefix="memory-background")
            if background_memory
            else None
        )
        self._futures: set[Future] = set()
        self._future_lock = threading.Lock()
        self._closed = False
        self._register_default_tools()

    def _register_default_tools(self):
        if not self.tools.has("search"):
            self.tools.register("search", self._tool_search)
        self.tools.allow("search")

    def _tool_search(self, query, memory=None):
        return memory if memory is not None else self.memory.retrieve(query)

    def _submit_memory_task(self, user_input, history):
        if self._executor is None:
            return self.memory.apply_memory_lifecycle(user_input, history)
        future = self._executor.submit(
            self.memory.apply_memory_lifecycle, user_input, list(history)
        )
        with self._future_lock:
            self._futures.add(future)
        future.add_done_callback(self._memory_task_done)
        return future

    def _memory_task_done(self, future):
        with self._future_lock:
            self._futures.discard(future)
        try:
            future.result()
        except Exception:
            logger.exception("Background memory task failed")

    def _run_loop(self, user_input):
        intent_result = self.intent_classifier.classify(user_input)
        memory_context = self.memory.retrieve(user_input)
        plan_result = self.planner.plan(intent_result, memory_context, user_input)
        tool_results = self.tool_executor.execute(plan_result)
        history = self.short_memory.get_recent(
            limit=settings.recent_history_messages
        )
        context = self.memory.format_context(memory_context, history)
        messages = self.context_builder.build_messages(
            user_input, context, tool_results=tool_results
        )
        answer = self.llm.chat(messages)
        if is_unavailable_response(answer):
            answer = (
                "本地模型暂时不可用，Ollama 可能尚未启动或连接失败。"
                "请启动 Ollama 并确认模型已安装后重试。"
            )
        return answer, intent_result, tool_results

    def chat(self, user_input):
        if self._closed:
            raise RuntimeError("agent is closed")
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user input must not be empty")
        normalized = user_input.strip()
        with self._chat_lock:
            answer, intent_result, tool_results = self._run_loop(normalized)
            if hasattr(self.memory, "append_exchange"):
                history = self.memory.append_exchange(normalized, answer)
            else:
                history = self.memory.load_history()
                history.extend(
                    [
                        {"role": "user", "content": normalized},
                        {"role": "assistant", "content": answer},
                    ]
                )
                history = self.memory.trim_history(history)
                self.memory.save_history(history)
            self._submit_memory_task(normalized, history)
        logger.info(
            "Chat handled intent=%s confidence=%.2f tools=%d",
            intent_result.intent,
            intent_result.confidence,
            len(tool_results),
        )
        return answer

    def wait_for_memory_tasks(self):
        with self._future_lock:
            futures = list(self._futures)
        for future in futures:
            future.result()

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=False)
        for component in (self.memory, self.llm):
            close = getattr(component, "close", None)
            if callable(close):
                close()


class QwenBrain(Agent):
    pass


def create_agent():
    return QwenBrain()
