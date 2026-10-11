import pytest

API = "/api/v1"

@pytest.fixture
def tasks(make_task, staff_user, other_staff_user):
    """Four tasks, oldest first."""
    return [
        make_task("Prepare sales report", staff_user, status="pending"),
        make_task("Fix login bug", staff_user, status="in_progress", description="Safari only"),
        make_task("Update FAQ", other_staff_user, status="completed", description="Customer REPORT questions"),
        make_task("Plan offsite", other_staff_user, status="pending", description="100% attendance"),
    ]

def get_tasks(client, headers, **params):
    response = client.get(f"{API}/tasks/", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return [t["title"] for t in response.json()], int(response.headers["x-total-count"])

def test_list_is_newest_first_by_default(client, admin_headers, tasks):
    titles, total = get_tasks(client, admin_headers)
    assert titles == ["Plan offsite", "Update FAQ", "Fix login bug", "Prepare sales report"]
    assert total == 4

def test_sort_oldest_first(client, admin_headers, tasks):
    titles, _ = get_tasks(client, admin_headers, sort="created_at")
    assert titles == ["Prepare sales report", "Fix login bug", "Update FAQ", "Plan offsite"]

def test_filter_by_status(client, admin_headers, tasks):
    titles, total = get_tasks(client, admin_headers, status="pending")
    assert titles == ["Plan offsite", "Prepare sales report"]
    assert total == 2

def test_search_title_and_description_case_insensitive(client, admin_headers, tasks):
    titles, total = get_tasks(client, admin_headers, q="report")
    assert titles == ["Update FAQ", "Prepare sales report"]
    assert total == 2

def test_search_treats_percent_literally(client, admin_headers, tasks):
    titles, total = get_tasks(client, admin_headers, q="%")
    assert titles == ["Plan offsite"]
    assert total == 1

def test_admin_filter_by_assignee(client, admin_headers, tasks, other_staff_user):
    titles, total = get_tasks(client, admin_headers, assignee_id=other_staff_user.id)
    assert titles == ["Plan offsite", "Update FAQ"]
    assert total == 2

def test_filters_combine(client, admin_headers, tasks, other_staff_user):
    titles, total = get_tasks(client, admin_headers, assignee_id=other_staff_user.id, status="pending", q="offsite")
    assert titles == ["Plan offsite"]
    assert total == 1

def test_staff_assignee_filter_is_ignored(client, staff_headers, tasks, other_staff_user):
    titles, total = get_tasks(client, staff_headers, assignee_id=other_staff_user.id)
    assert titles == ["Fix login bug", "Prepare sales report"]
    assert total == 2

def test_pagination_keeps_total_count(client, admin_headers, tasks):
    titles, total = get_tasks(client, admin_headers, skip=1, limit=2)
    assert titles == ["Update FAQ", "Fix login bug"]
    assert total == 4

@pytest.mark.parametrize("params", [
    {"limit": 500},
    {"limit": 0},
    {"skip": -1},
    {"status": "done"},
    {"sort": "title"},
])
def test_invalid_query_parameters_return_422(client, admin_headers, params):
    response = client.get(f"{API}/tasks/", headers=admin_headers, params=params)
    assert response.status_code == 422

def test_stats_for_admin_count_all_tasks(client, admin_headers, tasks):
    response = client.get(f"{API}/tasks/stats", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == {"pending": 2, "in_progress": 1, "completed": 1, "total": 4}

def test_stats_for_staff_count_own_tasks(client, staff_headers, other_staff_headers, tasks):
    staff = client.get(f"{API}/tasks/stats", headers=staff_headers).json()
    assert staff == {"pending": 1, "in_progress": 1, "completed": 0, "total": 2}
    other = client.get(f"{API}/tasks/stats", headers=other_staff_headers).json()
    assert other == {"pending": 1, "in_progress": 0, "completed": 1, "total": 2}

def test_stats_with_no_tasks_are_zero(client, admin_headers):
    response = client.get(f"{API}/tasks/stats", headers=admin_headers)
    assert response.json() == {"pending": 0, "in_progress": 0, "completed": 0, "total": 0}
