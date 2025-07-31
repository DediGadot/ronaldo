from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_parts():
    response = client.get("/api/parts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_part():
    # First, get a valid part ID
    response = client.get("/api/parts/")
    assert response.status_code == 200
    parts = response.json()
    if not parts:
        # If no parts, we can't test this endpoint
        return
    part_id = parts[0]["id"]

    response = client.get(f"/api/parts/{part_id}")
    assert response.status_code == 200
    assert response.json()["id"] == part_id

def test_read_part_not_found():
    response = client.get("/api/parts/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Part not found"}
