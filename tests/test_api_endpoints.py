from fastapi.testclient import TestClient

from control_api.app import app as control_app
from website_api.app import app as website_app


def test_control_api_status_and_secure_data():
    client = TestClient(control_app)
    headers = {"Authorization": "Bearer MakeThisBetter.txt"}

    status_response = client.get("/status")

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "ok"

    secure_response = client.get("/secure-data/", headers=headers)

    assert secure_response.status_code == 200
    assert secure_response.json()["data"] == "This is some secure data!"


def test_website_api_proxies_settings(monkeypatch):
    async def fake_forward(method, path, *, params=None, json_body=None):
        assert method == "GET"
        assert path == "/settings/"
        assert params == {"config_name": "engine"}
        return {"settings": "proxied"}

    monkeypatch.setattr("website_api.routes.forward_to_control_api", fake_forward)

    client = TestClient(website_app)
    response = client.get("/api/control/settings", params={"config_name": "engine"})

    assert response.status_code == 200
    assert response.json()["settings"] == "proxied"