from __future__ import annotations

import logging

from app.config import settings


logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Retrieve structured facts first and semantic memories only when useful."""

    def __init__(self, memory):
        self.memory = memory

    def retrieve(self, query: str) -> dict:
        profile = self.memory.load_profile()
        summary = self.memory.load_summary()
        result = {}
        field_keywords = {
            "name": ("名字", "叫什么", "姓名", "我是谁", "我的信息"),
            "learning": ("学习", "方向", "技术", "研究", "目标"),
            "project": ("项目", "开发", "正在做", "作品", "应用"),
            "likes": ("喜欢", "偏好", "爱好"),
        }
        for field, keywords in field_keywords.items():
            if any(keyword in query for keyword in keywords) and profile.get(field):
                result[field] = profile[field]

        recall_keywords = ("记得", "之前", "过去", "上次", "总结", "长期")
        if any(keyword in query for keyword in recall_keywords) and summary:
            result["summary"] = summary

        semantic_keywords = recall_keywords + (
            "学习",
            "项目",
            "目标",
            "偏好",
            "开发",
        )
        if any(keyword in query for keyword in semantic_keywords):
            try:
                memories = self.memory.vector_memory.search(
                    query, limit=settings.vector_search_limit
                )
                if memories:
                    result["vector_memory"] = memories
            except Exception:
                logger.exception("Vector memory search failed")
        return result
