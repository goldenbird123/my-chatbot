import pytest

from app.tool_registry import ToolPermissionError, ToolRegistry


def test_tool_requires_explicit_permission():
    registry = ToolRegistry(allowed_tools={"another-tool"})
    registry.register("echo", lambda value: value)
    with pytest.raises(ToolPermissionError):
        registry.call("echo", value="hello")
    registry.allow("echo")
    assert registry.call("echo", value="hello") == "hello"
