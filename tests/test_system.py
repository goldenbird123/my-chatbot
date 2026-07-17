from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_runtime_modules_exist():
    required = [
        "app/agent.py",
        "app/api.py",
        "core/llm/ollama.py",
        "memory/manager.py",
        "memory/pipeline.py",
        "memory/chroma_store.py",
    ]
    assert all((PROJECT_ROOT / path).is_file() for path in required)


def test_fixed_duplicate_modules_were_removed():
    assert not list((PROJECT_ROOT / "memory").glob("*_fixed.py"))
