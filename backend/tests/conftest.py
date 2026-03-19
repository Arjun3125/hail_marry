import pytest
import os
import sys
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

if create_engine and sessionmaker:
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
    from database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
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
