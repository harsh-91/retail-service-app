from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    item = {
        "name": "Notebook",
        "quantity": 20,
        "min_stock": 5,
        "description": "Ruled"
    }
    resp = client.post("/items", json=item)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Notebook"

def test_get_items():
    resp = client.get("/items")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    found = any(i['name'] == "Notebook" for i in data)
    assert found

def test_update_item():
    # Find item by name
    resp = client.get("/items")
    item = next(i for i in resp.json() if i["name"] == "Notebook")
    iid = item["id"]
    update = {
        "name": "Notebook",
        "quantity": 15,
        "min_stock": 5,
        "description": "College Ruled"
    }
    resp2 = client.put(f"/items/{iid}", json=update)
    assert resp2.status_code == 200
    assert resp2.json()["quantity"] == 15
    assert resp2.json()["description"] == "College Ruled"

def test_delete_item():
    resp = client.get("/items")
    item = next(i for i in resp.json() if i["name"] == "Notebook")
    iid = item["id"]
    resp2 = client.delete(f"/items/{iid}")
    assert resp2.status_code == 204
