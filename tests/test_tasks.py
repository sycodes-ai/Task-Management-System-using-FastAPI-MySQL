import pytest

API = "/api/v1"

def task_body(assignee, **overrides):
    body = {"title": "Write report", "description": "Q4 numbers", "assignee_id": assignee.id}
    body.update(overrides)
    return body

# --- Create ---

def test_admin_creates_task(client, admin_headers, admin_user, staff_user):
    response = client.post(f"{API}/tasks/", json=task_body(staff_user), headers=admin_headers)
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Write report"
    assert task["status"] == "pending"
    assert task["assignee_id"] == staff_user.id
    assert task["assigned_by_id"] == admin_user.id

def test_staff_cannot_create_task(client, staff_headers, staff_user):
    response = client.post(f"{API}/tasks/", json=task_body(staff_user), headers=staff_headers)
    assert response.status_code == 403

def test_create_task_for_missing_assignee_returns_404(client, admin_headers, staff_user):
    response = client.post(f"{API}/tasks/", json=task_body(staff_user, assignee_id=9999), headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Assignee not found"

@pytest.mark.parametrize("overrides", [
    {"status": "done"},
    {"title": ""},
    {"title": "   "},
    {"title": "x" * 101},
    {"description": "x" * 256},
])
def test_create_task_with_invalid_input_returns_422(client, admin_headers, staff_user, overrides):
    response = client.post(f"{API}/tasks/", json=task_body(staff_user, **overrides), headers=admin_headers)
    assert response.status_code == 422

# --- Read ---

def test_staff_see_only_their_own_tasks_admin_sees_all(
    client, make_task, staff_user, other_staff_user, admin_headers, staff_headers
):
    own = make_task("Own task", staff_user)
    make_task("Someone else's task", other_staff_user)

    staff_tasks = client.get(f"{API}/tasks/", headers=staff_headers).json()
    assert [t["id"] for t in staff_tasks] == [own.id]

    admin_tasks = client.get(f"{API}/tasks/", headers=admin_headers).json()
    assert len(admin_tasks) == 2

def test_staff_cannot_read_another_users_task(client, make_task, other_staff_user, staff_headers):
    task = make_task("Someone else's task", other_staff_user)
    assert client.get(f"{API}/tasks/{task.id}", headers=staff_headers).status_code == 403

# --- Update ---

def test_staff_can_change_status_of_own_task(client, make_task, staff_user, staff_headers):
    task = make_task("Own task", staff_user)
    response = client.put(f"{API}/tasks/{task.id}", json={"status": "completed"}, headers=staff_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["title"] == "Own task"

def test_staff_may_send_unchanged_fields_with_status(client, make_task, staff_user, staff_headers):
    task = make_task("Own task", staff_user, description="Details")
    body = {"title": "Own task", "description": "Details", "status": "in_progress"}
    response = client.put(f"{API}/tasks/{task.id}", json=body, headers=staff_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

def test_staff_cannot_change_title(client, make_task, staff_user, staff_headers, admin_headers):
    task = make_task("Original title", staff_user)
    response = client.put(
        f"{API}/tasks/{task.id}", json={"title": "Hacked", "status": "completed"}, headers=staff_headers
    )
    assert response.status_code == 403
    stored = client.get(f"{API}/tasks/{task.id}", headers=admin_headers).json()
    assert stored["title"] == "Original title"
    assert stored["status"] == "pending"

def test_staff_update_without_status_returns_422(client, make_task, staff_user, staff_headers):
    task = make_task("Own task", staff_user)
    assert client.put(f"{API}/tasks/{task.id}", json={}, headers=staff_headers).status_code == 422

def test_staff_cannot_update_another_users_task(client, make_task, other_staff_user, staff_headers):
    task = make_task("Someone else's task", other_staff_user)
    response = client.put(f"{API}/tasks/{task.id}", json={"status": "completed"}, headers=staff_headers)
    assert response.status_code == 403

@pytest.mark.parametrize("body", [
    {"title": None},
    {"status": None},
    {"assignee_id": None},
    {"title": "   "},
    {"status": "done"},
])
def test_admin_update_with_invalid_values_returns_422(client, make_task, staff_user, admin_headers, body):
    task = make_task("Task", staff_user)
    assert client.put(f"{API}/tasks/{task.id}", json=body, headers=admin_headers).status_code == 422

def test_staff_explicit_null_status_returns_422(client, make_task, staff_user, staff_headers):
    task = make_task("Own task", staff_user)
    assert client.put(f"{API}/tasks/{task.id}", json={"status": None}, headers=staff_headers).status_code == 422

def test_admin_can_update_all_fields(client, make_task, staff_user, other_staff_user, admin_headers):
    task = make_task("Task", staff_user)
    body = {"title": "New title", "description": "New", "status": "in_progress", "assignee_id": other_staff_user.id}
    response = client.put(f"{API}/tasks/{task.id}", json=body, headers=admin_headers)
    assert response.status_code == 200
    updated = response.json()
    assert {field: updated[field] for field in body} == body

def test_reassign_to_missing_user_returns_404(client, make_task, staff_user, admin_headers):
    task = make_task("Task", staff_user)
    response = client.put(f"{API}/tasks/{task.id}", json={"assignee_id": 9999}, headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Assignee not found"

# --- Delete ---

def test_staff_cannot_delete_task(client, make_task, staff_user, staff_headers):
    task = make_task("Own task", staff_user)
    assert client.delete(f"{API}/tasks/{task.id}", headers=staff_headers).status_code == 403

def test_admin_deletes_task_then_it_is_gone(client, make_task, staff_user, admin_headers):
    task = make_task("Task", staff_user)
    assert client.delete(f"{API}/tasks/{task.id}", headers=admin_headers).status_code == 204
    assert client.get(f"{API}/tasks/{task.id}", headers=admin_headers).status_code == 404
