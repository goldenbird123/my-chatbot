import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from memory.vector_memory import vector_memory



print("测试开始")


memory=vector_memory()



print("\n第一次添加")


memory.add_memory(
    "golden bird正在学习LangChain，目标成为AI Agent工程师"
)



print("\n第二次添加相似内容")


memory.add_memory(
    "golden bird最近继续学习LangChain"
)



print("\n当前记忆数量")


print(
    memory.count_memory()
)



print("\n搜索")


result=memory.search(
    "他的学习方向是什么"
)


print(result)