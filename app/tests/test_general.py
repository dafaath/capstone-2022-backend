from fastapi.testclient import TestClient


async def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Server is ok", "data": None}
