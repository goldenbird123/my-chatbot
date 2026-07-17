from __future__ import annotations

import threading


class ToolPermissionError(PermissionError):
    pass


class ToolRegistry:
    def __init__(self, allowed_tools=None):
        self._tools = {}
        self._allowed_tools = set(allowed_tools or [])
        self._lock = threading.RLock()

    def register(self, name, handler, *, allow=None):
        if not name or not callable(handler):
            raise ValueError("tool name and callable handler are required")
        with self._lock:
            self._tools[name] = handler
            if allow is None:
                allow = not self._allowed_tools
            if allow:
                self._allowed_tools.add(name)

    def has(self, name):
        with self._lock:
            return name in self._tools

    def allow(self, name):
        with self._lock:
            self._allowed_tools.add(name)

    def deny(self, name):
        with self._lock:
            self._allowed_tools.discard(name)

    def is_allowed(self, name):
        with self._lock:
            return name in self._allowed_tools

    def call(self, name, **kwargs):
        with self._lock:
            if name not in self._tools:
                raise KeyError(f"tool not found: {name}")
            if name not in self._allowed_tools:
                raise ToolPermissionError(f"tool not allowed: {name}")
            handler = self._tools[name]
        return handler(**kwargs)
