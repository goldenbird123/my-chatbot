class ContextManager:
    """Legacy context facade. New model-message construction lives in app.ContextBuilder."""

    def __init__(self, max_history=6):
        self.max_history = max_history

    def build_context(self, history, memory):
        return {
            "history": list(history)[-self.max_history :],
            "memory": memory,
        }
