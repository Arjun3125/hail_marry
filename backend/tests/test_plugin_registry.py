"""Tests for module plugin architecture."""
import pytest
from services.plugin_registry import (
    HOOK_NAMES, PluginHook, PluginMeta, disable_plugin, enable_plugin,
    execute_hook, list_hooks, list_plugins, register_plugin,
)


def test_hook_names_defined():
    assert "on_student_enrolled" in HOOK_NAMES
    assert "on_fee_paid" in HOOK_NAMES
    assert "on_document_ingested" in HOOK_NAMES
    assert "on_ai_query" in HOOK_NAMES


def test_plugin_meta():
    meta = PluginMeta("test_plugin", "1.0.0", "A test plugin")
    assert meta.name == "test_plugin"
    assert meta.enabled is True


def test_register_and_list_plugin():
    meta = PluginMeta("sms_alerts", "1.0.0", "SMS alert plugin")
    register_plugin(meta)
    plugins = list_plugins()
    names = [p["name"] for p in plugins]
    assert "sms_alerts" in names


def test_disable_enable_plugin():
    meta = PluginMeta("toggle_test", "1.0.0", "Toggle test")
    register_plugin(meta)
    disable_plugin("toggle_test")
    assert meta.enabled is False
    enable_plugin("toggle_test")
    assert meta.enabled is True


def test_hook_execution():
    hook = PluginHook("test_hook", "A test hook")
    hook.register(lambda: "result_a")
    hook.register(lambda: "result_b")
    results = hook.execute()
    assert results == ["result_a", "result_b"]


def test_hook_error_handling():
    hook = PluginHook("err_hook")
    hook.register(lambda: 1 / 0)
    results = hook.execute()
    assert "error" in results[0]


def test_list_hooks():
    hooks = list_hooks()
    assert len(hooks) >= 6
    names = [h["name"] for h in hooks]
    assert "on_student_enrolled" in names


def test_execute_unknown_hook():
    results = execute_hook("nonexistent_hook")
    assert results == []
