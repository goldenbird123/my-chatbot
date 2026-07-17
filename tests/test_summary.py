from memory.summarizer import MemorySummarizer


class FakeService:
    def chat(self, messages):
        return "用户正在学习 LangChain"


def test_memory_summarizer_uses_model_and_persists_normalized_summary(tmp_path):
    summarizer = MemorySummarizer(tmp_path / "summary.json", service=FakeService())
    result = summarizer.summarize([{"role": "user", "content": "学习 LangChain"}])
    assert result == "用户正在学习 LangChain"
    summarizer.save({"summary": result})
    assert summarizer.load() == {"content": "用户正在学习 LangChain"}
