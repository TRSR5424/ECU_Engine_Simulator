from fastapi.testclient import TestClient

from control_api.app import app as control_app
import control_api.results.results_service as results_service
import control_api.scripts.scripts_service as scripts_service
import control_api.settings.settings_service as settings_service
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


def test_control_api_scripts_endpoint_returns_service_data(monkeypatch):
    monkeypatch.setattr(
        scripts_service,
        "get_scripts",
        lambda: {"scripts": [{"name": "simulation"}], "active_experiment": "demo"},
    )

    client = TestClient(control_app)
    headers = {"Authorization": "Bearer MakeThisBetter.txt"}
    response = client.get("/scripts/", headers=headers)

    assert response.status_code == 200
    assert response.json()["scripts"][0]["name"] == "simulation"


def test_control_api_settings_update_global_endpoint_calls_service(monkeypatch):
    captured: dict[str, dict] = {}

    def fake_update_global_settings(new_settings: dict[str, str]):
        captured["new_settings"] = new_settings
        return {"message": "updated", "settings": new_settings}

    monkeypatch.setattr(settings_service, "update_global_settings", fake_update_global_settings)

    client = TestClient(control_app)
    headers = {"Authorization": "Bearer MakeThisBetter.txt"}
    response = client.post(
        "/settings/updateGlobal/",
        headers=headers,
        json={"logging": {"output_csv": "data/custom/"}},
    )

    assert response.status_code == 200
    assert captured["new_settings"] == {"logging": {"output_csv": "data/custom/"}}
    assert response.json()["message"] == "updated"


def test_control_api_results_endpoint_returns_service_data(monkeypatch):
    monkeypatch.setattr(results_service, "get_results", lambda: {"active_experiment": "demo", "results": []})

    client = TestClient(control_app)
    headers = {"Authorization": "Bearer MakeThisBetter.txt"}
    response = client.get("/results/", headers=headers)

    assert response.status_code == 200
    assert response.json()["active_experiment"] == "demo"


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