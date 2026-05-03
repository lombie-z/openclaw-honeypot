from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list():
    response = client.post("/items", json={"name": "Widget", "quantity": 10, "price": 4.99})
    assert response.status_code == 201
    item = response.json()
    assert item["name"] == "Widget"

    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404
