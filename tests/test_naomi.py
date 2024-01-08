from starlette.testclient import TestClient

from naomi import app

client = TestClient(app)


def test_home() -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_challenges_truth() -> None:
    params = {"rating": '["PG", "R"]'}
    response = client.get("/api/challenges/truth", params=params)
    assert response.status_code == 200
    data = response.json()

    assert data["rating"] in ["PG", "R"]
    assert data["type"] == "truth"


def test_actions_hug() -> None:
    response = client.get("/api/actions/hug")
    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "hug"
