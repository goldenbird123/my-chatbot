class ShortMemory:
    """The most recent N persisted conversation messages."""

    def __init__(self, manager):
        self.manager = manager

    def get_recent(self, limit=5):
        if limit <= 0:
            return []
        history_store = getattr(self.manager, "history", None)
        if history_store is not None and hasattr(history_store, "recent"):
            return history_store.recent(limit)
        return self.manager.load_history()[-limit:]
