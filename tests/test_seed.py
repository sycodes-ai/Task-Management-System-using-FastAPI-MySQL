from fastapi.testclient import TestClient

from app import main
from app.core.config import settings
from app.core.security import verify_password
from app.db.seed import DEMO_TASKS, seed_demo_data
from app.models.task import Task
from app.models.user import User

def test_seed_creates_demo_users_and_tasks(db):
    assert seed_demo_data(db) is True

    users = {u.email: u for u in db.query(User).all()}
    assert {email: u.role for email, u in users.items()} == {
        "admin@demo.com": "admin",
        "staff@demo.com": "staff",
        "alex@demo.com": "staff",
    }
    assert verify_password("Admin123!", users["admin@demo.com"].hashed_password)

    tasks = db.query(Task).all()
    assert len(tasks) == len(DEMO_TASKS) == 10
    assert {t.status for t in tasks} == {"pending", "in_progress", "completed"}
    assert {t.assignee_id for t in tasks} == {users["staff@demo.com"].id, users["alex@demo.com"].id}

def test_seed_twice_does_not_create_duplicates(db):
    assert seed_demo_data(db) is True
    assert seed_demo_data(db) is False
    assert db.query(User).count() == 3
    assert db.query(Task).count() == 10

def test_seed_skips_a_database_that_already_has_users(db, staff_user):
    assert seed_demo_data(db) is False
    assert db.query(User).count() == 1
    assert db.query(Task).count() == 0

def test_startup_seeds_once_when_demo_mode_is_on(monkeypatch, engine, session_factory, app_factory):
    # Run the real start-up (create tables + seed) twice, against the test database
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", session_factory)
    monkeypatch.setattr(settings, "DEMO_MODE", True)

    for _ in range(2):
        with TestClient(app_factory(session_factory)) as client:
            login = client.post(
                "/api/v1/login/access-token",
                data={"username": "staff@demo.com", "password": "Staff123!"},
            )
            assert login.status_code == 200

    with session_factory() as db:
        assert db.query(User).count() == 3
        assert db.query(Task).count() == 10

def test_startup_does_not_seed_when_demo_mode_is_off(monkeypatch, engine, session_factory, app_factory):
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", session_factory)
    assert settings.DEMO_MODE is False

    with TestClient(app_factory(session_factory)):
        pass

    with session_factory() as db:
        assert db.query(User).count() == 0
