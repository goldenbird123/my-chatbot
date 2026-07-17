from memory.importance import MemoryImportance


class FailingJudge:
    def judge(self, text):
        raise AssertionError("durable rule should not call LLM judge")


def test_importance_matches_stable_profile_rule():
    result = MemoryImportance(judge=FailingJudge()).check("我叫 Alice")
    assert result["memory"] is True
    assert result["type"] == "profile"


def test_importance_matches_preference_rule():
    result = MemoryImportance(judge=FailingJudge()).check("我喜欢简洁的回答")
    assert result["type"] == "preference"
