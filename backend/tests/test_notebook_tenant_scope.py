from uuid import UUID, uuid4


def _create_user(db_session, tenant_id, *, email: str, role: str = "student", password: str = "pass123!"):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="Tenant Scoped User",
        role=role,
        hashed_password=pwd_context.hash(password),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _login(client, email: str, password: str = "pass123!") -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    return token


def test_notebook_creation_persists_tenant_id(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    _create_user(db_session, active_tenant.id, email="tenant-notebook@testschool.edu")
    token = _login(client, "tenant-notebook@testschool.edu")

    response = client.post(
        "/api/notebooks",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Biology", "subject": "Science", "color": "#112233", "icon": "Book"},
    )

    assert response.status_code == 201
    notebook_id = response.json()["id"]

    notebook = db_session.query(Notebook).filter(Notebook.id == UUID(notebook_id)).first()
    assert notebook is not None
    assert notebook.tenant_id == active_tenant.id


def test_cross_tenant_notebook_is_hidden_from_same_user_id(client, db_session, active_tenant):
    from src.domains.identity.models.tenant import Tenant
    from src.domains.platform.models.notebook import Notebook

    user = _create_user(db_session, active_tenant.id, email="tenant-guard@testschool.edu")
    token = _login(client, "tenant-guard@testschool.edu")

    foreign_tenant = Tenant(id=uuid4(), name="Other School", domain="otherschool.edu")
    db_session.add(foreign_tenant)
    db_session.commit()

    leaked_notebook = Notebook(
        id=uuid4(),
        tenant_id=foreign_tenant.id,
        user_id=user.id,
        name="Should Be Hidden",
        color="#6366f1",
        icon="Book",
        is_active=True,
    )
    db_session.add(leaked_notebook)
    db_session.commit()

    response = client.get(
        f"/api/notebooks/{leaked_notebook.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_generated_content_creation_uses_notebook_tenant(client, db_session, active_tenant):
    from src.domains.platform.models.generated_content import GeneratedContent
    from src.domains.platform.models.notebook import Notebook

    user = _create_user(db_session, active_tenant.id, email="tenant-content@testschool.edu")
    token = _login(client, "tenant-content@testschool.edu")

    notebook = Notebook(
        id=uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Chemistry",
        color="#6366f1",
        icon="Book",
        is_active=True,
    )
    db_session.add(notebook)
    db_session.commit()

    response = client.post(
        "/api/generated-content",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "notebook_id": str(notebook.id),
            "type": "quiz",
            "title": "Atomic Structure Quiz",
            "content": {"questions": []},
            "source_query": "Generate a quiz",
            "parent_conversation_id": None,
        },
    )

    assert response.status_code == 201
    content_id = response.json()["id"]

    content = db_session.query(GeneratedContent).filter(GeneratedContent.id == UUID(content_id)).first()
    assert content is not None
    assert content.tenant_id == active_tenant.id
