from dataclasses import dataclass, field


@dataclass
class PlanStep:
    name: str
    action: str
    args: dict = field(default_factory=dict)


@dataclass
class PlanResult:
    intent: str
    steps: list[PlanStep] = field(default_factory=list)


class Planner:
    def plan(self, intent_result, memory_context, user_input):
        steps = []

        if intent_result.intent == "search" and intent_result.needs_tool:
            steps.append(
                PlanStep(
                    name="search_memory",
                    action="search",
                    args={"query": user_input, "memory": memory_context},
                )
            )

        return PlanResult(intent=intent_result.intent, steps=steps)
