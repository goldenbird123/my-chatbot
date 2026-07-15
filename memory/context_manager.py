class ContextManager:


    def __init__(self):

        # 最大保留聊天数量
        self.max_history = 6



    def build_context(
            self,
            history,
            memory
    ):


        context = {

            "history": [],

            "memory": memory

        }


        # =====================
        # 处理聊天记录
        # =====================


        if len(history) > self.max_history:


            history = history[
                -self.max_history:
            ]


        context["history"] = history



        return context