from datetime import timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User

API = "/api/v1"
PASSWORD = "Password123"

def register(client, **overrides):
    body = {"custom_username": "newuser", "email": "new@example.com", "password": "Password123"}
    body.update(overrides)
    return client.post(f"{API}/users/register", json=body)

# --- Registration ---

def test_register_always_creates_staff_even_if_admin_requested(client, db):
    response = register(client, role="admin")
    assert response.status_code == 201
    assert response.json()["role"] == "staff"
    user = db.query(User).filter_by(email="new@example.com").one()
    assert user.role == "staff"

def test_register_duplicate_email_returns_400(client):
    assert register(client).status_code == 201
    response = register(client, custom_username="another")
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_register_duplicate_username_returns_400(client):
    assert register(client).status_code == 201
    response = register(client, email="another@example.com")
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

@pytest.mark.parametrize("overrides", [
    {"password": "short"},
    {"email": "not-an-email"},
    {"custom_username": "ab"},
    {"custom_username": "x" * 51},
])
def test_register_invalid_input_returns_422(client, overrides):
    assert register(client, **overrides).status_code == 422

# --- Login ---

def test_login_with_correct_details_returns_token(client, staff_user):
    response = client.post(f"{API}/login/access-token", data={"username": "staff@example.com", "password": PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    me = client.get(f"{API}/users/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "staff@example.com"

@pytest.mark.parametrize("email, password", [
    ("staff@example.com", "WrongPassword1"),
    ("nobody@example.com", PASSWORD),
])
def test_login_with_wrong_details_returns_400(client, staff_user, email, password):
    response = client.post(f"{API}/login/access-token", data={"username": email, "password": password})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

# --- Tokens ---

def test_me_without_token_returns_401(client):
    response = client.get(f"{API}/users/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

def test_me_with_invalid_token_returns_401(client):
    response = client.get(f"{API}/users/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

def test_expired_token_returns_401(client, staff_user):
    token = create_access_token(staff_user.id, expires_delta=timedelta(minutes=-1))
    response = client.get(f"{API}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

def test_token_signed_with_another_key_returns_401(client, staff_user):
    token = jwt.encode({"sub": str(staff_user.id)}, "some-other-secret", algorithm=settings.ALGORITHM)
    response = client.get(f"{API}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

def test_tampered_token_payload_returns_401(client, staff_user, admin_user):
    # Keep the staff user's valid signature but swap in the admin's payload
    staff_token = create_access_token(staff_user.id)
    admin_token = create_access_token(admin_user.id)
    header, _, signature = staff_token.split(".")
    tampered = ".".join([header, admin_token.split(".")[1], signature])
    response = client.get(f"{API}/users/me", headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == 401

def test_token_for_deleted_user_returns_401(client, db, staff_user, staff_headers):
    db.delete(staff_user)
    db.commit()
    response = client.get(f"{API}/users/me", headers=staff_headers)
    assert response.status_code == 401

def test_token_for_deactivated_user_returns_401(client, db, staff_user, staff_headers):
    staff_user.is_active = False
    db.commit()
    response = client.get(f"{API}/users/me", headers=staff_headers)
    assert response.status_code == 401

# --- Role checks on users ---

def test_staff_cannot_list_users(client, staff_headers):
    assert client.get(f"{API}/users/", headers=staff_headers).status_code == 403

def test_admin_can_list_users(client, admin_headers, staff_user):
    response = client.get(f"{API}/users/", headers=admin_headers)
    assert response.status_code == 200
    assert {u["email"] for u in response.json()} == {"admin@example.com", "staff@example.com"}

@pytest.mark.parametrize("params", [{"skip": -1}, {"limit": 0}, {"limit": -1}, {"limit": 500}])
def test_list_users_with_invalid_paging_returns_422(client, admin_headers, params):
    # Negative values would otherwise reach the database (a SQL error on MySQL)
    assert client.get(f"{API}/users/", headers=admin_headers, params=params).status_code == 422
