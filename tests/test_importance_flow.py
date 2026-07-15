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


test = MemoryImportance()


cases=[

"今天吃了一碗面",

"我叫golden bird",

"我的目标是成为AI Agent工程师",

"天气不错"

]


for c in cases:

    print("\n用户:",c)

    print(
        test.check(c)
    )