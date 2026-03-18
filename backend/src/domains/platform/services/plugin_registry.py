"""Module plugin architecture — extensible feature modules.

Allows features to be registered as plugins that can be
enabled/disabled per tenant without modifying core code.
"""
from typing import Any, Callable, Optional


class PluginMeta:
    """Metadata for a registered plugin module."""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str = "VidyaOS",
        dependencies: list[str] = None,
        config_schema: dict = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.dependencies = dependencies or []
        self.config_schema = config_schema or {}
        self.enabled = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
        }


class PluginHook:
    """A named extension point that plugins can attach to."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.handlers: list[Callable] = []

    def register(self, handler: Callable):
        """Register a handler for this hook."""
        self.handlers.append(handler)

    def execute(self, *args, **kwargs) -> list[Any]:
        """Execute all registered handlers and collect results."""
        results = []
        for handler in self.handlers:
            try:
                results.append(handler(*args, **kwargs))
            except Exception as e:
                results.append({"error": str(e), "handler": handler.__name__})
        return results


# ── Plugin Registry ──

_plugins: dict[str, PluginMeta] = {}
_hooks: dict[str, PluginHook] = {}

# Pre-defined hooks
HOOK_NAMES = {
    "on_student_enrolled": "Triggered when a student is enrolled",
    "on_fee_paid": "Triggered when a fee payment is recorded",
    "on_document_ingested": "Triggered when a document is ingested",
    "on_ai_query": "Triggered after an AI query completes",
    "on_attendance_marked": "Triggered when attendance is recorded",
    "on_exam_graded": "Triggered when exam marks are entered",
}

# Initialize hooks
for hook_name, hook_desc in HOOK_NAMES.items():
    _hooks[hook_name] = PluginHook(hook_name, hook_desc)


def register_plugin(meta: PluginMeta, hooks: dict[str, Callable] = None):
    """Register a plugin with optional hook handlers."""
    _plugins[meta.name] = meta
    if hooks:
        for hook_name, handler in hooks.items():
            if hook_name in _hooks:
                _hooks[hook_name].register(handler)


def unregister_plugin(name: str):
    """Unregister a plugin."""
    _plugins.pop(name, None)


def get_plugin(name: str) -> Optional[PluginMeta]:
    """Get plugin metadata by name."""
    return _plugins.get(name)


def list_plugins() -> list[dict]:
    """List all registered plugins."""
    return [p.to_dict() for p in _plugins.values()]


def list_hooks() -> list[dict]:
    """List all available extension hooks."""
    return [
        {"name": h.name, "description": h.description, "handler_count": len(h.handlers)}
        for h in _hooks.values()
    ]


def execute_hook(hook_name: str, *args, **kwargs) -> list[Any]:
    """Execute all handlers for a hook."""
    hook = _hooks.get(hook_name)
    if not hook:
        return []
    return hook.execute(*args, **kwargs)


def enable_plugin(name: str) -> bool:
    plugin = _plugins.get(name)
    if plugin:
        plugin.enabled = True
        return True
    return False


def disable_plugin(name: str) -> bool:
    plugin = _plugins.get(name)
    if plugin:
        plugin.enabled = False
        return True
    return False
