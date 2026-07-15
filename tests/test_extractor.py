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


result = extractor.extract(
    "我的名字叫golden bird，我正在学习LangChain"
)


print(result)