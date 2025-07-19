import pytest
from fastapi.testclient import TestClient
from app.main import app as pay_app
from services.user_service.app.main import app as user_app
from fastapi.testclient import TestClient as UserClient

client = TestClient(pay_app)
user_client = UserClient(user_app)

@pytest.fixture(scope='module')
def pay_token():
    reg = user_client.post("/register", json={
        "username": "payuser", "email": "payuser@ex.com",
        "password": "Payuser123", "full_name": "Pay User", "language_pref": "en"
    })
    if reg.status_code not in (201, 409):
        raise AssertionError("user registration failed")
    res = user_client.post("/login", json={"username": "payuser", "password": "Payuser123"})
    return res.json()["access_token"]

def test_initiate_payment_cash(pay_token):
    headers = {"Authorization": f"Bearer {pay_token}"}
    payment = {
        "amount": 150.0,
        "method": "CASH"
    }
    resp = client.post("/payments", json=payment, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["method"] == "CASH"
    assert resp.json()["status"] == "PENDING"

def test_initiate_payment_upi(pay_token):
    headers = {"Authorization": f"Bearer {pay_token}"}
    payment = {
        "amount": 400.0,
        "method": "UPI",
        "upi_vpa": "test@upi"
    }
    resp = client.post("/payments", json=payment, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["method"] == "UPI"
    assert resp.json()["status"] == "PENDING"
    assert resp.json()["upi_vpa"] == "test@upi"

def test_get_my_payments(pay_token):
    headers = {"Authorization": f"Bearer {pay_token}"}
    resp = client.get("/payments", headers=headers)
    assert resp.status_code == 200
    assert type(resp.json()) == list

def test_get_payment_status(pay_token):
    headers = {"Authorization": f"Bearer {pay_token}"}
    # Get first payment id
    resp = client.get("/payments", headers=headers)
    pid = resp.json()[0]["id"]
    resp2 = client.get(f"/payments/{pid}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == pid
