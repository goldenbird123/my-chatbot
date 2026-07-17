"""Deprecated compatibility tombstone.

The canonical implementation is the ``core.llm`` package. The historical
implementation below is intentionally inert.

from langchain_core.language_models.llms import LLM
from langchain_core.messages import HumanMessage, SystemMessage

import requests
from typing import Optional, List


class LocalOllama(LLM):

    model: str = "qwen3:8b"
    url: str = "http://localhost:11434/api/chat"


    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs
    ):

        try:

            response = requests.post(
                self.url,
                json={
                    "model": self.model,

                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    # 非流式返回
                    "stream": False,

                    # 关闭 qwen3 思考模式
                    "think": False,

                    "options":{

                        # 降低随机发挥
                        "temperature":0.3,

                        # 限制输出长度
                        "num_predict":200

                    }
                },

                timeout=120
            )


            response.raise_for_status()


            data = response.json()


            return data["message"]["content"]


        except Exception as e:

            print("Ollama调用失败:", e)

            return "模型调用失败"


    @property
    def _llm_type(self):

        return "local-ollama"



# 创建模型实例

llm = LocalOllama()
class LLMService:


    def __init__(self):

        self.model = LocalOllama()



    def chat(self, messages):


        prompt = ""


        for m in messages:


            if m["role"] == "system":

                prompt += (
                    "系统设定："
                    + m["content"]
                    + "\n\n"
                )


            elif m["role"] == "user":

                prompt += (
                    "用户："
                    + m["content"]
                    + "\n\n"
                )


            elif m["role"] == "assistant":

                prompt += (
                    "助手："
                    + m["content"]
                    + "\n\n"
                )


        return self.model.invoke(prompt)
llm_service=LLMService()



def chat(messages):

    try:

        prompt = ""


        for m in messages:


            if m["role"] == "system":

                prompt += (
                    "系统设定："
                    + m["content"]
                    + "\n\n"
                )


            elif m["role"] == "user":

                prompt += (
                    "用户："
                    + m["content"]
                    + "\n\n"
                )
            elif m["role"] == "assistant":

                prompt += (
                    "鸟神："
                    + m["content"]
                    + "\n\n"
                )



        result = llm.invoke(prompt)


        return result



    except Exception as e:


        print("聊天错误:", e)


        return "模型调用失败，请检查 Ollama 服务"
"""
