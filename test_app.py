# test_app.py - Unit Tests
import pytest
from app import app, tasks

@pytest.fixture
def client():
    # Creates a test client - simulates HTTP requests without a real server
    app.config["TESTING"] = True
    with app.test_client() as client:
        tasks.clear()  # Reset tasks before each test
        yield client


def get_token(client):
    """Helper: login and return JWT token"""
    res = client.post("/login", json={"username": "admin", "password": "password123"})
    return res.get_json()["access_token"]


# ─── Test 1: Login with correct credentials ──────────────────────────
def test_login_success(client):
    res = client.post("/login", json={"username": "admin", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()  # Token must be returned


# ─── Test 2: Login with wrong password ───────────────────────────────
def test_login_fail(client):
    res = client.post("/login", json={"username": "admin", "password": "wrongpass"})
    assert res.status_code == 401  # Unauthorized


# ─── Test 3: Access protected route without token ────────────────────
def test_get_tasks_no_token(client):
    res = client.get("/tasks")
    assert res.status_code == 401  # Should be blocked


# ─── Test 4: Create a task with valid token ───────────────────────────
def test_create_task(client):
    token = get_token(client)
    res = client.post(
        "/tasks",
        json={"title": "Buy groceries"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    assert res.get_json()["title"] == "Buy groceries"


# ─── Test 5: Get tasks returns list ──────────────────────────────────
def test_get_tasks(client):
    token = get_token(client)
    client.post("/tasks", json={"title": "Test task"},
                headers={"Authorization": f"Bearer {token}"})

    res = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.get_json()["tasks"]) == 1
