import pytest
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from importlib.util import find_spec

# Ensure backend modules can be imported when tests are run from backend dir.
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uuid

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ModuleNotFoundError:
    create_engine = None
    sessionmaker = None

os.environ["DEBUG"] = "true"
os.environ["DEBUG"] = "true"
os.environ["DEMO_MODE"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

_TEST_TEMP_DIR = os.path.join(project_root, ".pytest_tmp")
os.makedirs(_TEST_TEMP_DIR, exist_ok=True)
os.environ["TMP"] = _TEST_TEMP_DIR
os.environ["TEMP"] = _TEST_TEMP_DIR
os.environ["TMPDIR"] = _TEST_TEMP_DIR
tempfile.tempdir = _TEST_TEMP_DIR


def _make_safe_temp_dir() -> str:
    path = os.path.join(_TEST_TEMP_DIR, f"tmp_{uuid.uuid4().hex}")
    os.makedirs(path, exist_ok=True)
    return path


class _SafeTemporaryDirectory:
    def __init__(self, suffix="", prefix="tmp", dir=None, ignore_cleanup_errors=False):
        base_dir = dir or _TEST_TEMP_DIR
        os.makedirs(base_dir, exist_ok=True)
        self.name = os.path.join(base_dir, f"{prefix}_{uuid.uuid4().hex}{suffix}")
        os.makedirs(self.name, exist_ok=True)
        self._ignore_cleanup_errors = ignore_cleanup_errors

    def __enter__(self):
        return self.name

    def cleanup(self):
        shutil.rmtree(self.name, ignore_errors=self._ignore_cleanup_errors or True)

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()


class _NamedTemporaryFileWrapper:
    def __init__(self, file_obj, path: str, delete: bool):
        self._file = file_obj
        self.name = path
        self._delete = delete

    def __getattr__(self, item):
        return getattr(self._file, item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        if not self._file.closed:
            self._file.close()
        if self._delete and os.path.exists(self.name):
            os.unlink(self.name)


def _safe_named_temporary_file(mode="w+b", suffix="", prefix="tmp", dir=None, delete=True, encoding=None, **_kwargs):
    base_dir = dir or _TEST_TEMP_DIR
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, f"{prefix}_{uuid.uuid4().hex}{suffix}")
    file_obj = open(path, mode, encoding=encoding)
    return _NamedTemporaryFileWrapper(file_obj, path, delete)

_LIGHTWEIGHT_TEST_ALLOWLIST = {
    os.path.join("backend", "tests", "test_whatsapp_gateway.py"),
    os.path.join("backend", "tests", "test_whatsapp.py"),
    os.path.join("backend", "tests", "test_ai_queue.py"),
    os.path.join("backend", "tests", "integration", "test_webhook_integration.py"),
}

_CORE_TEST_DEPENDENCIES = (
    "fastapi",
    "httpx",
    "numpy",
    "pydantic",
    "sqlalchemy",
    "starlette",
    "langchain_ollama",
)


def _missing_core_test_dependencies() -> list[str]:
    return [module_name for module_name in _CORE_TEST_DEPENDENCIES if find_spec(module_name) is None]


def _lightweight_test_mode() -> bool:
    mode = os.getenv("LIGHTWEIGHT_TEST_MODE", "auto").strip().lower()
    if mode in {"1", "true", "on"}:
        return True
    if mode in {"0", "false", "off"}:
        return False
    return bool(_missing_core_test_dependencies())


def pytest_ignore_collect(collection_path, config):
    missing_modules = _missing_core_test_dependencies()
    if not _lightweight_test_mode():
        return False

    rel_path = os.path.relpath(str(collection_path), project_root)
    if not rel_path.startswith(os.path.join("backend", "tests")):
        return False

    if not rel_path.endswith(".py"):
        return False

    return rel_path not in _LIGHTWEIGHT_TEST_ALLOWLIST


def pytest_report_header(config):
    missing_modules = _missing_core_test_dependencies()
    mode = os.getenv("LIGHTWEIGHT_TEST_MODE", "auto").strip().lower()
    if not _lightweight_test_mode():
        if not missing_modules:
            return "backend tests: full dependency set available"
        return (
            "backend tests: full collection forced "
            f"(LIGHTWEIGHT_TEST_MODE={mode}; missing dependencies: {', '.join(missing_modules)})"
        )
    return (
        "backend tests: lightweight mode active "
        f"(LIGHTWEIGHT_TEST_MODE={mode}; missing dependencies skipped during collection: {', '.join(missing_modules)})"
    )


@pytest.fixture(autouse=True)
def _patch_tempfile(monkeypatch):
    monkeypatch.setattr(tempfile, "TemporaryDirectory", _SafeTemporaryDirectory)
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", _safe_named_temporary_file)


@pytest.fixture(autouse=True)
def _stabilize_runtime_env(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("TESTING", "true")

    try:
        from auth import dependencies as auth_dependencies

        auth_dependencies._demo_user_cache.clear()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _clear_app_dependency_overrides():
    try:
        from main import app

        app.dependency_overrides.clear()
        yield
        app.dependency_overrides.clear()
    except Exception:
        yield


@pytest.fixture
def tmp_path():
    path = Path(_make_safe_temp_dir())
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

if create_engine and sessionmaker:
    import models  # noqa: F401  # Ensure SQLAlchemy model modules are imported before create_all
    from database import Base

    engine = create_engine(
        os.getenv("DATABASE_URL"),
        connect_args={"check_same_thread": False}
    )
    engine.dialect.insert_returning = False
    engine.dialect.update_returning = False

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    Base = None
    engine = None
    TestingSessionLocal = None

@pytest.fixture(scope="session")
def setup_database():
    if Base is None or engine is None:
        pytest.skip("SQLAlchemy is unavailable in this environment")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    fastapi = pytest.importorskip("fastapi.testclient")
    from main import app
    from database import get_db, get_async_session

    class AsyncSessionAdapter:
        def __init__(self, session):
            self._session = session

        async def execute(self, *args, **kwargs):
            return self._session.execute(*args, **kwargs)

        def add(self, instance):
            self._session.add(instance)

        async def commit(self):
            self._session.commit()

        async def refresh(self, instance):
            self._session.refresh(instance)

        async def rollback(self):
            self._session.rollback()

    def override_get_db():
        yield db_session

    async def override_get_async_session():
        yield AsyncSessionAdapter(db_session)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_session] = override_get_async_session
    with fastapi.TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def active_tenant(db_session):
    from src.domains.identity.models.tenant import Tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test School",
        domain="testschool.edu"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant
