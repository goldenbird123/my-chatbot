from __future__ import annotations

import json

from app.config import settings
from app.prompts import build_system_prompt


class ContextBuilder:
    """Build model messages independently from Agent orchestration."""

    def __init__(self, max_context_chars: int | None = None):
        self.max_context_chars = max_context_chars or settings.max_context_chars

    def build_messages(self, user_input: str, context: dict, tool_results=None):
        memory = {
            "profile": context.get("profile", {}),
            "summary": context.get("summary", {}),
            "retrieved": context.get("retrieved", {}),
        }
        history = context.get("history", [])
        system_prompt = build_system_prompt(
            memory=json.dumps(memory, ensure_ascii=False, default=str),
            history=json.dumps(history, ensure_ascii=False, default=str),
        )
        messages = [{"role": "system", "content": system_prompt}]
        for item in history:
            role, content = item.get("role"), item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str) and content:
                messages.append({"role": role, "content": content})
        if tool_results:
            messages.append(
                {
                    "role": "system",
                    "content": "工具结果："
                    + json.dumps(tool_results, ensure_ascii=False, default=str),
                }
            )
        messages.append({"role": "user", "content": user_input})
        return messages
