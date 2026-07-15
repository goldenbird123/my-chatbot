import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from memory.context_manager import ContextManager



manager = ContextManager()



history=[]


for i in range(20):

    history.append({

        "role":"user",

        "content":
        f"第{i}句话"

    })



result = manager.build_context(

    history,

    "用户学习LangChain"

)



print(
    "聊天数量:"
)

print(
    len(result["history"])
)



print(
    result
)