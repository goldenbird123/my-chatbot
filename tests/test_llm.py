from core.llm import create_llm


def test_llm_factory_creates_object():
    llm = create_llm()
    assert hasattr(llm, "chat")
