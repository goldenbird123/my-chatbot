import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0,
    stream=False
)


response = llm.invoke(
    [
        ("human", "你好，请介绍一下自己")
    ]
)


print(response.content)