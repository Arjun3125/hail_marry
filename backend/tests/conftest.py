import pytest
import os
import shutil
import sys
import uuid
from pathlib import Path
from unittest.mock import patch
from importlib.util import find_spec

# Prevent heavy ML modules from being imported during parallel worker test compilation
sys.modules["sentence_transformers"] = None
sys.modules["faiss"] = None

# Ensure backend modules can be imported when tests are run from backend dir.
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


try:
    from sqlalchemy import event
    from sqlalchemy.orm import sessionmaker
except ModuleNotFoundError:
    event = None
    sessionmaker = None

os.environ["DEBUG"] = "true"
os.environ["DEMO_MODE"] = "false"
os.environ["TESTING"] = "true"

_TEST_TEMP_DIR = os.path.join(project_root, ".pytest_tmp")
os.makedirs(_TEST_TEMP_DIR, exist_ok=True)
worker_id = os.environ.get("PYTEST_XDIST_WORKER", uuid.uuid4().hex[:8])
_TEST_DB_PATH = os.path.join(_TEST_TEMP_DIR, f"test_suite_{worker_id}.sqlite3")
_TEST_DB_URL = f"sqlite:///{Path(_TEST_DB_PATH).as_posix()}"
os.environ["TEST_DATABASE_URL"] = _TEST_DB_URL
os.environ["DATABASE_URL"] = _TEST_DB_URL


def _make_safe_temp_dir() -> str:
    path = os.path.join(_TEST_TEMP_DIR, f"tmp_{uuid.uuid4().hex}")
    os.makedirs(path, exist_ok=True)
    return path

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
    _missing_core_test_dependencies()
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
def _reset_rate_limit_state():
    try:
        from middleware import rate_limit

        rate_limit._memory_store.clear()
        rate_limit._redis = None
        rate_limit._redis_initialized = True
    except Exception:
        pass
    yield
    try:
        from middleware import rate_limit

        rate_limit._memory_store.clear()
        rate_limit._redis = None
        rate_limit._redis_initialized = True
    except Exception:
        pass


# --- Global AI Mocking Logic ---

class FakeLLMProvider:
    async def generate(self, prompt, **kwargs):
        return {"response": f"Fake response to: {prompt[:50]}...", "status": "success"}

    async def generate_structured(self, prompt, schema, **kwargs):
        # Handle MascotInterpretation schema detection generically
        schema_str = str(schema)
        if "MascotInterpretation" in schema_str:
             return {
                "intent": "chat",
                "confidence": 0.95,
                "translated_message": prompt,
                "normalized_message": str(prompt).lower().strip(),
                "language": "en",
                "parameters": {},
                "requires_confirmation": False
            }
        return {}

    def get_model_name(self):
        return "fake-llm-1.0"


class FakeEmbeddingProvider:
    def __init__(self, dimension=768):
        self.dimension = dimension

    async def embed(self, text):
        return [0.0] * self.dimension

    async def embed_batch(self, texts):
        return [[0.0] * self.dimension for _ in texts]

    def get_dimension(self):
        return self.dimension


class FakeVectorStoreProvider:
    def add_chunks(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        return []

    def similarity_search_with_score(self, *args, **kwargs):
        return []


def pytest_sessionstart(session):
    """
    Called before any tests are collected or run.
    We apply global patches here to ensure they are active even for modules
    that perform top-level imports of providers or gateway functions.
    """
    # 1. Define Fake Objects
    fake_llm = FakeLLMProvider()
    fake_embedding = FakeEmbeddingProvider()
    fake_vector_store = FakeVectorStoreProvider()

    # 2. Patch Providers
    # Pre-import to avoid AttributeError on submodules during patching
    print("\n[DEBUG] pytest_sessionstart: Starting global patches...")
    try:
        from src.infrastructure.llm import providers
        from src.domains.platform.services import ai_gateway
        from src.bootstrap import app_factory, startup
        
        patch.object(providers, "get_llm_provider", return_value=fake_llm).start()
        patch.object(providers, "get_embedding_provider", return_value=fake_embedding).start()
        patch.object(providers, "get_vector_store_provider", return_value=fake_vector_store).start()
        print("[DEBUG] AI Providers patched.")
    except Exception as e:
        print(f"[DEBUG] AI Providers patch failed: {e}")

    # 3. Patch Gateway/Service functions (to bypass deep logic)
    async def fake_run_text_query(*args, **kwargs):
        return {"answer": "Fake AI Answer", "citations": [], "mode": "general"}
        
    async def fake_run_study_tool(*args, **kwargs):
        return {"data": [], "citations": []}

    async def fake_ingest_youtube(*args, **kwargs):
        return {"id": "fake_yt_123", "title": "Fake Video"}

    # Patch in multiple locations where they are imported or used
    # AI Gateway - Patch all entry points
    gateway_mocks = [
        "run_text_query", "run_audio_overview", "run_video_overview",
        "run_study_tool", "run_teacher_assessment", "run_url_ingestion",
        "run_teacher_document_ingestion", "run_teacher_youtube_ingestion",
        "run_whatsapp_media_ingestion"
    ]
    for mock_name in gateway_mocks:
        try:
            patch.object(ai_gateway, mock_name, side_effect=fake_run_text_query).start()
        except AttributeError:
            pass
    print("[DEBUG] AI Gateway patched.")
        
    # Ingestion
    patch("src.infrastructure.vector_store.ingestion.ingest_youtube", side_effect=fake_ingest_youtube).start()

    # 4. Disable Heavy Startup/Observability Logic during tests
    # This prevents redundant seeding, telemetry, and logging setup for every app instance.
    try:
        from src.bootstrap import app_factory, startup
        patch.object(app_factory, "initialize_demo_mode").start()
        patch.object(app_factory, "configure_application_logging").start()
        patch.object(app_factory, "configure_telemetry").start()
        patch.object(app_factory, "configure_sentry").start()
        patch.object(app_factory, "instrument_sqlalchemy_engine").start()
        
        # Also patch deep in startup just in case
        patch.object(startup, "initialize_demo_mode").start()
        patch.object(startup, "init_feature_flags").start()
    except (ImportError, AttributeError):
        pass

    # 5. Patch LangGraph/LangChain to speed up collection and execution
    # This prevents real model discovery or heavy graph compilation
    try:
        patch("langchain_ollama.ChatOllama").start()

        # Build a fake compiled graph that returns the input state with plan_node-like defaults
        class _FakeCompiledGraph:
            def invoke(self, state, *args, **kwargs):
                # Simulate the plan_node: set a pending_mode/prompt or complete
                result = dict(state)
                current_step = int(result.get("current_step") or 0)
                if current_step >= 3:
                    result["status"] = "completed"
                    result["pending_mode"] = None
                    result["pending_prompt"] = None
                else:
                    result.get("workflow_type", "deep_study")
                    topic = result.get("topic", "General")
                    fallback_modes = ["qa", "quiz", "study_guide"]
                    mode = fallback_modes[current_step % len(fallback_modes)]
                    result["pending_mode"] = mode
                    result["pending_prompt"] = f"Provide a {mode} regarding {topic}"
                return result

            async def ainvoke(self, state, *args, **kwargs):
                return self.invoke(state)

        _fake_compiled = _FakeCompiledGraph()
        patch("langgraph.graph.StateGraph.compile", return_value=_fake_compiled).start()
    except (ImportError, AttributeError):
        pass


@pytest.fixture(autouse=True)
def global_ai_mocks():
    """No-op legacy fixture (logic moved to sessionstart)"""
    yield


@pytest.fixture(autouse=True)
def _clear_app_dependency_overrides():
    yield


@pytest.fixture
def stub_ai_query_runtime(monkeypatch):
    import importlib

    ai_routes = importlib.import_module("src.interfaces.rest_api.ai.routes.ai")

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        return {
            "answer": f"Stubbed answer for {request.query}",
            "citations": [],
            "token_usage": 1,
            "mode": request.mode,
            "has_context": False,
            "citation_valid": False,
            "citation_count": 0,
            "runtime_mode": "test-stub",
        }

    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)
    return ai_routes


@pytest.fixture
def tmp_path():
    path = Path(_make_safe_temp_dir())
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

_TestingSessionLocal = None


def get_test_engine():
    """Lazily create and return the test engine."""
    if sessionmaker is None:
        return None
    import models  # noqa: F401  # Ensure all models are loaded
    from database import Base, get_engine  # noqa: F401

    return get_engine()


def get_testing_session_local():
    """Lazily create and return the testing session local factory."""
    global _TestingSessionLocal
    if _TestingSessionLocal is None:
        if sessionmaker is None:
            return None
        _TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_test_engine()
        )
    return _TestingSessionLocal


class _ConftestLazyProxy:
    """A minimal proxy to defer engine/session initialization."""

    def __init__(self, factory):
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_instance", None)

    def _get_instance(self):
        if object.__getattribute__(self, "_instance") is None:
            object.__setattr__(
                self, "_instance", object.__getattribute__(self, "_factory")()
            )
        return object.__getattribute__(self, "_instance")

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

    def __call__(self, *args, **kwargs):
        return self._get_instance()(*args, **kwargs)


engine = _ConftestLazyProxy(get_test_engine)
TestingSessionLocal = _ConftestLazyProxy(get_testing_session_local)

try:
    from database import Base
except ImportError:
    Base = None


@pytest.fixture(scope="session")
def setup_database():
    if Base is None:
        pytest.skip("SQLAlchemy is unavailable in this environment")
    from database import reset_database_state

    reset_database_state()
    test_engine = get_test_engine()
    if test_engine is None:
        pytest.skip("SQLAlchemy is unavailable in this environment")
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    reset_database_state()
    if os.path.exists(_TEST_DB_PATH):
        try:
            os.remove(_TEST_DB_PATH)
        except PermissionError:
            pass

@pytest.fixture
def db_session(setup_database):
    connection = get_test_engine().connect()
    transaction = connection.begin()
    session = get_testing_session_local()(bind=connection)
    nested = connection.begin_nested()

    if event is not None:
        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(sess, trans):
            nonlocal nested
            parent = getattr(trans, "_parent", None)
            if trans.nested and parent is not None and not parent.nested:
                nested = connection.begin_nested()

    yield session

    if event is not None:
        event.remove(session, "after_transaction_end", restart_savepoint)
    session.close()
    if nested.is_active:
        nested.rollback()
    if transaction.is_active:
        transaction.rollback()
    connection.close()

@pytest.fixture(scope="session")
def app_instance():
    from src.bootstrap.app_factory import create_app

    app = create_app()
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session, app_instance):
    fastapi = pytest.importorskip("fastapi.testclient")
    from database import get_db, get_async_session

    class AsyncSessionMock:
        def __init__(self, session):
            self._session = session
            self.identity_map = session.identity_map

        async def execute(self, statement, *args, **kwargs):
            return self._session.execute(statement, *args, **kwargs)

        async def scalars(self, statement, *args, **kwargs):
            result = self._session.execute(statement, *args, **kwargs)
            return result.scalars()

        async def scalar(self, statement, *args, **kwargs):
            return self._session.scalar(statement, *args, **kwargs)

        def add(self, instance):
            self._session.add(instance)

        def add_all(self, instances):
            self._session.add_all(instances)

        async def commit(self):
            self._session.commit()

        async def flush(self):
            self._session.flush()

        async def refresh(self, instance, *args, **kwargs):
            self._session.refresh(instance, *args, **kwargs)

        async def rollback(self):
            self._session.rollback()

        async def close(self):
            self._session.close()

        async def delete(self, instance):
            self._session.delete(instance)

        async def get(self, entity, ident, **kwargs):
            return self._session.get(entity, ident, **kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def begin(self):
            class AsyncCM:
                async def __aenter__(self): return None
                async def __aexit__(self, *a): pass
            return AsyncCM()

    def override_get_db():
        yield db_session

    async def override_get_async_session():
        yield AsyncSessionMock(db_session)

    app_instance.dependency_overrides[get_db] = override_get_db
    app_instance.dependency_overrides[get_async_session] = override_get_async_session
    with fastapi.TestClient(app_instance) as c:
        yield c
    app_instance.dependency_overrides.clear()

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
