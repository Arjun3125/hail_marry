import importlib


def test_vector_store_module_is_importable():
    module = importlib.import_module("src.infrastructure.vector_store.vector_store")
    assert hasattr(module, "get_vector_store")


def test_main_app_imports_with_demo_env(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_demo_boot.db")
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("JWT_SECRET", "demo-smoke-secret-demo-smoke-secret")

    main = importlib.import_module("main")
    assert hasattr(main, "app")
