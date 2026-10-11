"""
Shared test fixtures.

Every setting is pinned through an environment variable *before* the app is
imported. pydantic-settings always prefers environment variables over the
.env file, so a developer's local .env (for example a MySQL DATABASE_URL)
never reaches the tests, and the tests behave the same locally and in CI.
test_settings.py fails if a new setting is added without a value here.
"""
import os
from pathlib import Path

TEST_SETTINGS = {
    "ENVIRONMENT": "development",
    "DATABASE_URL": "sqlite://",
    "SECRET_KEY": "test-secret-key",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "API_V1_STR": "/api/v1",
    "CORS_ORIGINS": "http://localhost:5173",
    "DEMO_MODE": "false",
    # A folder that never exists: the app runs API-only unless a test builds a frontend
    "STATIC_DIR": str(Path(__file__).parent / "_no_frontend_build"),
}
os.environ.update(TEST_SETTINGS)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api import deps  # noqa: E402
from app.core.security import create_access_token, get_password_hash  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import create_db_engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.models.user import User  # noqa: E402

API = "/api/v1"
PASSWORD = "Password123"

@pytest.fixture
def test_settings():
    return TEST_SETTINGS

@pytest.fixture
def engine():
    # One shared in-memory database per test
    engine = create_db_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db(session_factory):
    session = session_factory()
    yield session
    session.close()

def build_app(session_factory):
    """Create the app with get_db pointing at the test database."""
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[deps.get_db] = override_get_db
    return application

@pytest.fixture
def app_factory():
    """build_app(session_factory) for tests that need their own app."""
    return build_app

@pytest.fixture
def app(session_factory):
    return build_app(session_factory)

@pytest.fixture
def client(app):
    # Not used as a context manager, so the lifespan (create_all/seed on the
    # real engine) does not run; tables come from the engine fixture.
    return TestClient(app)

@pytest.fixture(scope="session")
def password_hash():
    # bcrypt is slow on purpose: hash the shared test password once
    return get_password_hash(PASSWORD)

def _create_user(db, username, email, role, hashed_password):
    user = User(custom_username=username, email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_user(db, password_hash):
    return _create_user(db, "admin_user", "admin@example.com", "admin", password_hash)

@pytest.fixture
def staff_user(db, password_hash):
    return _create_user(db, "staff_user", "staff@example.com", "staff", password_hash)

@pytest.fixture
def other_staff_user(db, password_hash):
    return _create_user(db, "other_staff", "other@example.com", "staff", password_hash)

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(admin_user.id)

@pytest.fixture
def staff_token(staff_user):
    return create_access_token(staff_user.id)

@pytest.fixture
def other_staff_token(other_staff_user):
    return create_access_token(other_staff_user.id)

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def staff_headers(staff_token):
    return {"Authorization": f"Bearer {staff_token}"}

@pytest.fixture
def other_staff_headers(other_staff_token):
    return {"Authorization": f"Bearer {other_staff_token}"}

@pytest.fixture
def make_task(db, admin_user):
    """Insert a task directly in the database."""
    def _make_task(title, assignee, status="pending", description=None):
        task = Task(
            title=title,
            description=description,
            status=status,
            assignee_id=assignee.id,
            assigned_by_id=admin_user.id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    return _make_task
