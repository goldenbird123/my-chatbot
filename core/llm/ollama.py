import requests


class OllamaLLM:
    model: str = "qwen3:8b"
    url: str = "http://localhost:11434/api/chat"

    def chat(self, messages, stop=None, **kwargs):
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200,
                },
            }
            if stop:
                payload["options"]["stop"] = stop

            response = requests.post(self.url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
            if content:
                return content
            return "本地模型暂时没有返回内容"
        except Exception as e:
            return f"本地模型暂不可用：{e}"
