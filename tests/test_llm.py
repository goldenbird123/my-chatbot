from core.llm import LLMService, create_llm


def test_llm_factory_creates_ollama_service():
    assert isinstance(create_llm(), LLMService)


def test_llm_factory_rejects_unknown_provider():
    try:
        create_llm("unknown")
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unknown provider should fail")
