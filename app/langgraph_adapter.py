class LangGraphAdapter:
    def __init__(self, enabled=False):
        self.enabled = enabled

    def build(self, *args, **kwargs):
        return None

    def run(self, state):
        return state
