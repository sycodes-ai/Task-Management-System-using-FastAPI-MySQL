"""
Optional: run a short end-to-end flow against a real database (MySQL in CI).

Skipped unless TEST_DATABASE_URL is set, for example:
    TEST_DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/tms_test pytest
Use an empty, throwaway database: the tables are dropped at the end.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import create_db_engine
from app.models.user import User

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
API = "/api/v1"

pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set")

@pytest.fixture
def real_db_session_factory():
    engine = create_db_engine(TEST_DATABASE_URL)
    existing = set(inspect(engine).get_table_names()) & {"users", "tasks"}
    with engine.connect() as conn:
        for table in existing:
            if conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar():
                pytest.fail(f"TEST_DATABASE_URL must point to an empty test database ({table} has rows)")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(engine)
    engine.dispose()

def test_end_to_end_on_real_database(real_db_session_factory, app_factory):
    with real_db_session_factory() as db:
        db.add(User(custom_username="admin", email="admin@example.com",
                    hashed_password=get_password_hash("Password123"), role="admin"))
        db.commit()

    client = TestClient(app_factory(real_db_session_factory))

    def login(email):
        response = client.post(f"{API}/login/access-token", data={"username": email, "password": "Password123"})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    # Registration always creates staff
    response = client.post(f"{API}/users/register", json={
        "custom_username": "staff", "email": "staff@example.com", "password": "Password123", "role": "admin",
    })
    assert response.status_code == 201
    assert response.json()["role"] == "staff"
    staff_id = response.json()["id"]

    admin, staff = login("admin@example.com"), login("staff@example.com")

    for title, status in [("Prepare report", "pending"), ("Fix bug", "in_progress"), ("Write FAQ", "completed")]:
        response = client.post(f"{API}/tasks/", headers=admin, json={
            "title": title, "description": "Quarterly REPORT", "status": status, "assignee_id": staff_id,
        })
        assert response.status_code == 201

    # Enum columns, case-insensitive search, filters and X-Total-Count
    response = client.get(f"{API}/tasks/", headers=admin, params={"q": "report", "status": "pending"})
    assert [t["title"] for t in response.json()] == ["Prepare report"]
    assert response.headers["x-total-count"] == "1"
    assert client.get(f"{API}/tasks/", headers=admin, params={"status": "done"}).status_code == 422

    stats = client.get(f"{API}/tasks/stats", headers=staff).json()
    assert stats == {"pending": 1, "in_progress": 1, "completed": 1, "total": 3}

    task_id = client.get(f"{API}/tasks/", headers=staff).json()[0]["id"]
    response = client.put(f"{API}/tasks/{task_id}", headers=staff, json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert client.put(f"{API}/tasks/{task_id}", headers=staff, json={"title": "x"}).status_code == 403
    assert client.delete(f"{API}/tasks/{task_id}", headers=admin).status_code == 204
