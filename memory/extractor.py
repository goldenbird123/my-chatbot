from __future__ import annotations

import json
import logging
import re

from app.prompts import build_extraction_prompt
from core.llm import LLMConfig, LLMService, is_unavailable_response
from memory.schemas import MemoryData, MemoryExtractionResult


logger = logging.getLogger(__name__)


class MemoryExtractor:
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

    @staticmethod
    def _repair_json(text: str) -> str:
        cleaned = text.strip().replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        return match.group(0) if match else cleaned

    def _parse(self, content: str) -> MemoryExtractionResult:
        try:
            return MemoryExtractionResult.safe_parse(json.loads(self._repair_json(content)))
        except (TypeError, ValueError, json.JSONDecodeError):
            logger.warning("Could not parse memory extraction response")
            return MemoryExtractionResult()

    def extract(self, user_input: str) -> dict:
        content = self.service.chat(
            [
                {
                    "role": "system",
                    "content": "你负责提取用户长期记忆，只返回 JSON。",
                },
                {
                    "role": "user",
                    "content": build_extraction_prompt(user_input=user_input, user_profile=""),
                },
            ]
        )
        if is_unavailable_response(content):
            return MemoryExtractionResult().model_dump()
        result = self._parse(content)
        if not result.memory:
            return {"memory": False, "data": MemoryData().model_dump()}
        return result.model_dump()
