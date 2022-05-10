import os
from fastapi.testclient import TestClient

from app.main import app
from app.utils.jwt import decrypt_access_token, decrypt_refresh_token
from config import get_settings

client = TestClient(app)


def test_register():
    response = client.post("/authentications/register", json={
        "email": "dafa@gmail.com",
        "phone": "+62813290823141",
        "password": "123"
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 201
    assert resp['status'] == response.status_code
    assert "Registration successful" in resp['message']

    supposed_keys = set(["id", "email", "phone", "isActive"])
    current_keys = set(resp['data'].keys())
    assert supposed_keys == current_keys

    assert resp['data']['isActive'] == True


def test_login():
    response = client.post("/authentications/login", json={
        "email": "dafa@gmail.com",
        "password": "123"
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200
    assert resp['status'] == response.status_code
    assert "Login successful" in resp['message']

    supposed_keys = set(["accessToken", "refreshToken"])
    current_keys = set(resp['data'].keys())
    assert supposed_keys == current_keys
    # Ensure valid token
    assert decrypt_access_token(resp['data']['accessToken']) is not None
    assert decrypt_refresh_token(resp['data']['refreshToken']) is not None
