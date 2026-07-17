from __future__ import annotations

import json
import logging
import re

from app.prompts import build_judge_prompt
from core.llm import LLMConfig, LLMService, is_unavailable_response


logger = logging.getLogger(__name__)
VALID_TYPES = {"profile", "preference", "project", "goal", "knowledge", "vector"}


class MemoryJudge:
    def __init__(self, service=None, *, model=None, url=None, timeout=None):
        if service is not None:
            self.service = service
        else:
            config = LLMConfig()
            if model is not None:
                config.model = model
            if url is not None:
                config.chat_url = url
            if timeout is not None:
                config.timeout = timeout
            self.service = LLMService(config)

    def judge(self, text: str) -> dict:
        result = self.service.chat(
            [{"role": "user", "content": build_judge_prompt(user_input=text)}]
        )
        if is_unavailable_response(result):
            return {"memory": False, "type": "none", "reason": "模型不可用"}
        try:
            cleaned = result.replace("```json", "").replace("```", "").strip()
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            payload = json.loads(match.group(0) if match else cleaned)
        except (TypeError, ValueError, json.JSONDecodeError):
            return {"memory": False, "type": "none", "reason": "解析失败"}
        memory_type = str(payload.get("type", "none"))
        enabled = bool(payload.get("memory")) and memory_type in VALID_TYPES
        return {
            "memory": enabled,
            "type": memory_type if enabled else "none",
            "reason": str(payload.get("reason", "")),
        }


class MemoryImportance:
    """Fast deterministic rules first; LLM judge only for ambiguous messages."""

    def __init__(self, judge=None):
        self.judge = judge or MemoryJudge()

    def check(self, text: str) -> dict:
        normalized = text.strip()
        rules = (
            ("profile", ("我叫", "我的名字", "我的职业", "我是一个", "我来自")),
            ("preference", ("我喜欢", "我偏好", "我的爱好", "我不喜欢")),
            ("project", ("我的项目", "我正在开发", "我在做一个", "长期项目")),
            ("goal", ("我的目标", "我希望成为", "我想成为", "长期目标")),
            ("knowledge", ("我正在学习", "我在学习", "我的学习方向")),
        )
        for memory_type, keywords in rules:
            if any(keyword in normalized for keyword in keywords):
                return {
                    "memory": True,
                    "type": memory_type,
                    "reason": "matched durable-memory rule",
                }
        try:
            return self.judge.judge(normalized)
        except Exception:
            logger.exception("LLM memory judge failed")
            return {"memory": False, "type": "none", "reason": "judge failed"}


__all__ = ["MemoryImportance", "MemoryJudge"]
