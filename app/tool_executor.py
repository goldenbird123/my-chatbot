from __future__ import annotations

import logging

from app.tool_registry import ToolPermissionError


logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, plan_result) -> list[dict]:
        outputs = []
        for step in plan_result.steps:
            if not self.registry.has(step.action):
                logger.warning("Planner requested missing tool: %s", step.action)
                continue
            try:
                outputs.append(
                    {
                        "step": step.name,
                        "result": self.registry.call(step.action, **step.args),
                    }
                )
            except ToolPermissionError as exc:
                logger.warning("Tool blocked: %s", exc)
            except Exception:
                logger.exception("Tool execution failed: %s", step.action)
        return outputs
