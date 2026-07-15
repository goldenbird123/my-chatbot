import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from langchain_ollama import OllamaLLM


llm = OllamaLLM(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0
)


result = llm.invoke(
    "你是谁？"
)


print(result)