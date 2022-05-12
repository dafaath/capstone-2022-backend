from fastapi.testclient import TestClient

from app.main import app
from app.utils.jwt import decrypt_access_token, decrypt_refresh_token

client = TestClient(app)
common_var = {}


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
    response = client.post("/authentications/login", data={
        "username": "dafa@gmail.com",
        "password": "123"
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200

    supposed_keys = set(["access_token", "refresh_token", "token_type", "expires_in", "scope"])
    current_keys = set(resp.keys())
    assert supposed_keys == current_keys
    # Ensure valid token
    result = decrypt_access_token(resp['access_token'])
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.id
    assert result.payload.email
    assert result.payload.phone
    assert result.payload.is_active

    result = decrypt_refresh_token(resp['refresh_token'])
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.user_id
    assert result.payload.session_id

    common_var["refreshToken"] = resp['refresh_token']
    common_var["accessToken"] = resp['access_token']


def test_refresh():
    response = client.post("/authentications/refresh", json={
        "refreshToken": common_var["refreshToken"]
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200
    assert resp['status'] == response.status_code
    assert "Access token successfully renewed" in resp['message']

    supposed_keys = set(["accessToken"])
    current_keys = set(resp['data'].keys())
    assert supposed_keys == current_keys
    # Ensure valid token
    result = decrypt_access_token(resp['data']['accessToken'])
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.id
    assert result.payload.email
    assert result.payload.phone
    assert result.payload.is_active
