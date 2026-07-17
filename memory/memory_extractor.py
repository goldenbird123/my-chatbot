import requests
import json
from memory.extractor import MemoryExtractor


class _LegacyMemoryExtractor:


    def extract(self, user_input):


        prompt = f"""
规则：
1. 用户名字:
例如:
我叫xxx
"name"

2. 学习方向:
例如:
我正在学习LangChain
"learning"

3. 项目目标/职业目标:
例如:
我要成为AI Agent工程师、我的目标是做AI助手
都归类到:
"project"

4. 兴趣:
例如:
我喜欢xxx
"likes"

如果没有信息，保持为空字符串。
判断下面用户消息是否值得长期记忆。
只允许记忆：

1. 用户身份
例如：我叫xxx

2. 用户长期目标
例如：我要成为AI工程师

3. 用户学习方向

4. 用户长期项目

5. 用户兴趣


不要记忆：
聊天寒暄
天气
临时事情
一次性问题

用户消息：
{user_input}


返回JSON:


如果值得记忆:

{{
"memory": true,
"data": {{
"name":"",
"learning":"",
"project":"",
"likes":""
}}
}}


如果不值得:

{{
"memory": false
}}

"""




        response = requests.post(

            "http://localhost:11434/api/chat",

            json={

                "model":"qwen3:8b",

                "messages":[

                    {
                        "role":"system",
                        "content":"你负责提取用户长期记忆"
                    },

                    {
                        "role":"user",
                        "content":prompt
                    }

                ],

                "stream":False

            },
            timeout=30

        )


        try:
            result=response.json()
            content=result["message"]["content"]
        except Exception:
            return {"memory": False}

        try:
            memory_data= json.loads(content)
        except Exception:
            memory_data = {}
        return memory_data
