from dataclasses import dataclass


@dataclass(slots=True)
class IntentResult:
    intent: str
    confidence: float = 0.0
    needs_tool: bool = False
    tool_name: str = ""


class IntentClassifier:
    def classify(self, user_input: str) -> IntentResult:
        text = user_input.casefold().strip()
        if any(word in text for word in ("搜索", "查找", "查询", "检索", "lookup", "search")):
            return IntentResult("search", 0.8, True, "search")
        if any(word in text for word in ("总结", "梳理", "归纳", "summarize")):
            return IntentResult("summarize", 0.7)
        if any(word in text for word in ("记得", "之前", "上次", "我叫", "我的", "学习", "项目")):
            return IntentResult("memory", 0.75)
        if any(word in text for word in ("计算", "calc", "代码", "实现", "怎么做", "如何")):
            return IntentResult("reasoning", 0.65)
        return IntentResult("chat", 0.5)
