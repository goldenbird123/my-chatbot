import json

from core.llm import create_llm


class MemoryJudge:
    def judge(self, text):
        prompt = f"""
你是一个AI记忆管理助手。
判断下面用户的话是否值得长期保存。

用户输入：
{text}

只返回JSON：
{{
  "memory": true,
  "type": "profile",
  "reason": "原因"
}}

或者：
{{
  "memory": false,
  "type": "none",
  "reason": "原因"
}}
"""
        result = create_llm().chat([
            {"role": "user", "content": prompt}
        ])

        if result.startswith("本地模型暂不可用"):
            return {"memory": False, "type": "none", "reason": "模型不可用"}

        try:
            cleaned = result.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception:
            return {"memory": False, "type": "none", "reason": "解析失败"}
