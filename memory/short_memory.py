class ShortMemory:

    def __init__(self, manager):
        self.manager = manager


    def get_recent(self, limit=5):

        history = self.manager.load_history()

        if not history:
            return []

        return history[-limit:]