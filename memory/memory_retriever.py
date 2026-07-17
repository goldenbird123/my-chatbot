from memory.manager import MemoryManager
from memory.vector_instance import get_vector_memory
from memory.retriever import MemoryRetriever


class _LegacyMemoryRetriever:
    def __init__(self,memory):

        self.memory = memory

        self.vector_memory = memory.vector_memory



    def retrieve(self, query):


        memory = {}


        # =====================
        # 1. 读取固定资料
        # =====================

        profile = self.memory.load_profile()

        summary = self.memory.load_summary()



        # =====================
        # 2. 名字
        # =====================

        if any(word in query for word in [
            "名字",
            "叫什么",
            "姓名",
            "是谁",
            "我的信息"
        ]):


            memory["name"] = profile.get(
                "name",
                ""
            )



        # =====================
        # 3. 学习方向
        # =====================

        if any(word in query for word in [

            "学习",
            "方向",
            "LangChain",
            "LangGraph",
            "技术",
            "研究",
            "目标"

        ]):


            memory["learning"] = profile.get(
                "learning",
                ""
            )


        # =====================
        # 4. 项目
        # =====================

        if any(word in query for word in [
            "项目",
            "开发",
            "做什么",
            "正在做",
            "作品",
            "应用"
        ]):


            memory["project"] = profile.get(
                "project",
                ""
            )



        # =====================
        # 5. 长期总结
        # =====================

        if any(word in query for word in [
            "记得",
            "之前",
            "过去"
        ]):


            memory["summary"] = summary



        # =====================
        # 6. 向量搜索
        # =====================

        need_vector = any(
            word in query
            for word in [
                "记得",
                "之前",
                "学习",
                "项目",
                "目标",
                "开发",
                "做什么"
            ]
        )


        if need_vector:

            try:

                vector_result = self.vector_memory.search(query)


                if vector_result:

                    memory["vector_memory"] = vector_result


            except Exception as e:

                print(
                    "向量搜索失败:",
                    e
                )


        return memory
