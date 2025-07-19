import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope='module')
def user_token():
    user = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "Testpass123",
        "full_name": "Test User 1",
        "language_pref": "en"
    }
    client.post("/register", json=user)
    resp = client.post(
        "/login", 
        json={"username": "testuser1", "password": "Testpass123"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "User Service is running"}

def test_register_duplicate():
    user = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "Testpass123",
        "full_name": "Test User 1",
        "language_pref": "en"
    }
    # First registration
    _ = client.post("/register", json=user)
    # Try to register duplicate
    res = client.post("/register", json=user)
    assert res.status_code == 409

def test_login_success(user_token):
    assert user_token and isinstance(user_token, str)

def test_login_fail():
    res = client.post(
        "/login", 
        json={"username": "invaliduser", "password": "wrong"}
    )
    assert res.status_code == 401

def test_profile_get_and_update(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = client.get("/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser1"

    patch = client.patch("/profile", json={"full_name": "Test User Updated", "language_pref": "hi"}, headers=headers)
    assert patch.status_code == 200
    assert patch.json()["full_name"] == "Test User Updated"
    assert patch.json()["language_pref"] == "hi"

def test_change_password(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"old_password": "Testpass123", "new_password": "Newpass123"}
    resp = client.post("/change-password", params=data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["msg"] == "Password updated"
    # Try login with new password
    res2 = client.post("/login", json={"username": "testuser1", "password": "Newpass123"})
    assert res2.status_code == 200
