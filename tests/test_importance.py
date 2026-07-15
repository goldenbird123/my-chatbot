import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from memory.memory_extractor import MemoryExtractor


extractor = MemoryExtractor()


tests=[

"我今天吃了一碗面",

"我的目标是成为AI Agent工程师",

"我叫golden bird",

"天气今天很好"

]


for t in tests:

    print("\n用户:",t)

    result=extractor.extract(t)

    print(result)