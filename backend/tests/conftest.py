import pytest
import os
import sys

# Ensure backend modules can be imported when tests are run from backend dir.
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DEBUG"] = "true"
os.environ["DEBUG"] = "true"
os.environ["DEMO_MODE"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

from main import app
from database import Base, get_db

engine = create_engine(
    os.getenv("DATABASE_URL"),
    connect_args={"check_same_thread": False}
)
engine.dialect.insert_returning = False
engine.dialect.update_returning = False

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
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
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def active_tenant(db_session):
    from models.tenant import Tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test School",
        domain="testschool.edu"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant
