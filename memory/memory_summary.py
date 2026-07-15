import requests


class MemorySummary:


    def summarize(self,history,old_summary=""):

        prompt=f"""

你是一个长期记忆管理助手。

以前保存的长期记忆：

{old_summary}



最近聊天：

{history}



请生成新的长期记忆。


要求:

1. 保留旧记忆中稳定信息

2. 加入新的重要信息

3. 删除无意义聊天

4. 不重复内容

5. 不丢失用户目标、学习方向、项目

输出简洁总结。

"""


        response = requests.post(

            "http://localhost:11434/api/chat",

            json={

                "model": "qwen3:8b",

                "messages": [

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                "stream": False

            },
            timeout=30

        )


        try:
            data = response.json()
            return data["message"]["content"]
        except Exception as e:
            return f"总结失败: {e}"
