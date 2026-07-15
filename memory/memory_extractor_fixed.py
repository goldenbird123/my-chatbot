import json
import requests


class MemoryExtractor:
    def extract(self, user_input):
        prompt = f"""
你负责提取用户长期记忆，并只返回JSON。

用户消息：
{user_input}

返回格式：
{{
  "memory": true,
  "data": {{
    "name": "",
    "learning": "",
    "project": "",
    "likes": ""
  }}
}}
"""
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen3:8b",
                    "messages": [
                        {"role": "system", "content": "你负责提取用户长期记忆。"},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
        except Exception:
            return {"memory": False}

        try:
            return json.loads(content)
        except Exception:
            return {"memory": False}
