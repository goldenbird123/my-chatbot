import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from memory.memory_importance import MemoryImportance



importance = MemoryImportance()



tests = [

    "我叫golden bird",

    "我正在学习LangChain",

    "以后我想成为AI工程师",

    "今天晚上吃火锅"

]



for text in tests:


    print("================")

    print("输入:")

    print(text)


    result = importance.check(
        text
    )


    print(
        result
    )