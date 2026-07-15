from core.llm import chat
import json



class MemoryJudge:


    def judge(self,text):


        prompt=f"""

你是一个AI记忆管理助手。

判断下面用户的话是否值得长期保存。


用户输入：

{text}


判断标准：

值得保存：
- 用户身份
- 用户长期目标
- 学习方向
- 工作方向
- 项目经历
- 长期兴趣


不值得保存：
- 普通聊天
- 一次性问题
- 今天吃什么
- 临时情绪


只返回JSON。


格式：

{{
"memory":true,
"type":"profile",
"reason":"原因"
}}


或者：

{{
"memory":false,
"type":"none",
"reason":"原因"
}}

"""


        result = chat([
            {
                "role":"user",
                "content":prompt
            }
        ])


        try:

            # 去除 markdown 代码块

            result = result.replace(
                "```json",
                ""
            )

            result = result.replace(
                "```",
                ""
            )


            result = result.strip()


            return json.loads(result)



        except Exception as e:


            print(
                "MemoryJudge解析失败:",
                e
            )


            print(
                "原始输出:",
                result
            )


            return {

                "memory":False,

                "type":"none",

                "reason":"解析失败"

            }
