from fastapi.testclient import TestClient

import controllers.AppealController as appeal_controller
from app import app

def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint(monkeypatch):
    def fake_predict_label(title, text, tokenizer, model):
        assert title == "Cannot login"
        assert text == "Code does not arrive"
        assert tokenizer == "fake-tokenizer"
        assert model == "fake-model"
        return {"pred_label": "APP_LOGIN", "confidence": 0.87654}

    def fake_create_appeal(title, text, department, percent_of_confidence):
        return {
            "id": 1,
            "title": title,
            "text": text,
            "department": department,
            "percent_of_confidence": percent_of_confidence,
        }

    monkeypatch.setattr(appeal_controller, "predict_label", fake_predict_label)
    monkeypatch.setattr(appeal_controller, "create_appeal", fake_create_appeal)
    app.state.tokenizer = "fake-tokenizer"
    app.state.model = "fake-model"

    client = TestClient(app)
    response = client.post(
        "/appeals/predict",
        json={"title": "Cannot login", "text": "Code does not arrive"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Cannot login",
        "text": "Code does not arrive",
        "department": "APP_LOGIN",
        "percent_of_confidence": 87.65,
    }

