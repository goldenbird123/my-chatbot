from memory.importance import MemoryImportance


class FakeJudge:
    def judge(self, text):
        return {"memory": False, "type": "none", "reason": "temporary"}


def test_importance_delegates_ambiguous_message_to_judge():
    result = MemoryImportance(judge=FakeJudge()).check("今天天气不错")
    assert result == {"memory": False, "type": "none", "reason": "temporary"}
