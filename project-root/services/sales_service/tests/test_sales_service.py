import pytest
from fastapi.testclient import TestClient
from app.main import app as sales_app
from services.user_service.app.main import app as user_app
from fastapi.testclient import TestClient as UserClient

client = TestClient(sales_app)
user_client = UserClient(user_app)

@pytest.fixture(scope="module")
def auth_token():
    reg = user_client.post("/register", json={
        "username": "salesuser", "email": "salesuser@ex.com",
        "password": "Sales1234", "full_name": "Sales Tester", "language_pref": "en"
    })
    if reg.status_code not in (201, 409):  # Ok if already exists
        raise AssertionError("user registration failed")
    res = user_client.post("/login", json={"username": "salesuser", "password": "Sales1234"})
    return res.json()["access_token"]

def test_create_sale(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    sale = {
        "item_name": "Pen",
        "quantity": 10,
        "price_per_unit": 5,
        "payment_method": "UPI"
    }
    resp = client.post("/sales", json=sale, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["item_name"] == "Pen"
    assert data["total_price"] == 50

def test_get_sales(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.get("/sales", headers=headers)
    assert resp.status_code == 200
    assert type(resp.json()) is list
    assert any(sale["item_name"] == "Pen" for sale in resp.json())
