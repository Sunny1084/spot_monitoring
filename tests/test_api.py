from fastapi.testclient import TestClient

from src.api.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_predict_validation_error() -> None:
    client = TestClient(app)
    response = client.post("/predict", json={"spot_price": 0.1})
    assert response.status_code == 422
