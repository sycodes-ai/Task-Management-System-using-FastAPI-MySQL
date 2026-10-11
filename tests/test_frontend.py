"""Phase 5: one service. FastAPI serves the React build and keeps API errors as JSON."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API = "/api/v1"
INDEX_HTML = '<!doctype html><html><body><div id="root"></div><script src="/assets/app.js"></script></body></html>'

@pytest.fixture
def dist(tmp_path):
    """A minimal React build in a temporary folder."""
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text(INDEX_HTML)
    (tmp_path / "assets" / "app.js").write_text("console.log('app');")
    (tmp_path / "vite.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
    return tmp_path

@pytest.fixture
def spa_client(monkeypatch, dist, app_factory, session_factory):
    monkeypatch.setattr(settings, "STATIC_DIR", str(dist))
    return TestClient(app_factory(session_factory))

def is_index(response):
    return (
        response.status_code == 200
        and response.headers["content-type"].startswith("text/html")
        and '<div id="root">' in response.text
    )

def is_json_404(response):
    return (
        response.status_code == 404
        and response.headers["content-type"].startswith("application/json")
        and '<div id="root">' not in response.text
    )

def test_health_returns_ok(client):
    response = client.get(f"{API}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.parametrize("path", ["/", "/login", "/register", "/abc", "/some/deep/route"])
def test_client_routes_return_index_html(spa_client, path):
    assert is_index(spa_client.get(path))

def test_index_html_is_not_cached(spa_client):
    assert spa_client.get("/login").headers["cache-control"] == "no-cache"

@pytest.mark.parametrize("method, path", [
    ("GET", "/api/v1/does-not-exist"),
    ("POST", "/api/v1/does-not-exist"),
    ("DELETE", "/api/v1/does-not-exist"),
    ("GET", "/api"),
    ("GET", "/api/v2/tasks"),
])
def test_unknown_api_paths_return_json_404(spa_client, method, path):
    response = spa_client.request(method, path)
    assert is_json_404(response)
    assert response.json() == {"detail": "Not Found"}

def test_api_errors_keep_their_status_codes(spa_client):
    assert spa_client.get(f"{API}/users/me").status_code == 401
    assert spa_client.put(f"{API}/users/me").status_code == 405
    assert spa_client.get(f"{API}/health").json() == {"status": "ok"}

def test_assets_are_served(spa_client):
    response = spa_client.get("/assets/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]

def test_missing_asset_returns_404_not_index_html(spa_client):
    response = spa_client.get("/assets/missing.js")
    assert response.status_code == 404
    assert '<div id="root">' not in response.text

def test_files_in_build_root_are_served(spa_client):
    response = spa_client.get("/vite.svg")
    assert response.status_code == 200
    assert "svg" in response.headers["content-type"]

def test_docs_and_openapi_still_work(spa_client):
    assert spa_client.get("/docs").status_code == 200
    assert spa_client.get("/openapi.json").json()["info"]["title"] == "Task Management System API"

def test_paths_outside_the_build_folder_are_not_served(spa_client, dist):
    (dist.parent / "secret.txt").write_text("top secret")
    response = spa_client.get("/..%2Fsecret.txt")
    assert "top secret" not in response.text

# --- Without a frontend build (the default in tests) ---

def test_app_without_dist_runs_api_only(client):
    root = client.get("/")
    assert root.status_code == 200
    assert "Welcome" in root.json()["message"]
    assert is_json_404(client.get("/login"))
    assert client.get(f"{API}/health").status_code == 200
    assert client.get("/docs").status_code == 200
