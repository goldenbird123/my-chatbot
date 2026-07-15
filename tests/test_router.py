import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)



from memory.memory_router import MemoryRouter



router = MemoryRouter()



tests=[


"我叫golden bird",


"我的学习方向是什么",


"我正在开发AI聊天助手",


"今天吃饭了吗"

]



for t in tests:


    print("\n用户:")
    print(t)


    result=router.route(t)


    print("返回:")
    print(result)