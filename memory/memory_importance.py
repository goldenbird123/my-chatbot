from memory.importance import MemoryImportance, MemoryJudge


class _LegacyMemoryImportance:
    def __init__(self):
        self.judge = MemoryJudge()


    def check(self,text):


        profile_keywords = [
            "我叫",
            "我的名字",
            "我是",
            "来自",
            "职业",
            "学习",
            "正在学习",
            "想学",
            "LangChain",
            "LangGraph"
        ]


        project_keywords = [
            "项目",
            "正在开发",
            "开发一个",
            "做一个",
            "机器人",
            "AI助手"
        ]


        goal_keywords = [
            "目标",
            "希望成为",
            "想成为",
            "以后想"
        ]



        if any(
            k in text
            for k in profile_keywords
        ):

            return {
                "memory":True,
                "type":"profile"
            }



        if any(
            k in text
            for k in project_keywords
        ):

            return {
                "memory":True,
                "type":"vector"
            }



        if any(
            k in text
            for k in goal_keywords
        ):

            return {
                "memory":True,
                "type":"vector"
            }



        # AI 智能判断

        result = self.judge.judge(
            text
        )


        return result
