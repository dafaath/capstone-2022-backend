from fastapi.testclient import TestClient

from app.main import app
from app.utils.jwt import decrypt_access_token, decrypt_refresh_token
from app.utils.test import (USER_RESPONSE_KEYS, have_base_templates,
                            have_correct_data_properties,
                            have_correct_status_and_message,
                            have_not_undefined)
from config import RunningENV, get_settings

client = TestClient(app)
common_var = {}


async def test_register(test_db):
    response = client.post("/users/", json={
        "email": "dafa@gmail.com",
        "phone": "+62813290823141",
        "password": "123"
    })
    resp = response.json()
    print(resp)

    have_base_templates(response)
    have_correct_status_and_message(response, 201, "Registration successful")
    have_correct_data_properties(
        response, USER_RESPONSE_KEYS)
    have_not_undefined(response, USER_RESPONSE_KEYS)


def check_access_token(result):
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.id
    assert result.payload.email
    assert result.payload.phone
    assert result.payload.is_active
    assert result.payload.time_created
    assert result.payload.time_updated


def check_refresh_token(result):
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.user_id
    assert result.payload.session_id


async def test_login(test_db):
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
    check_access_token(result)

    result = decrypt_refresh_token(resp['refresh_token'])
    check_refresh_token(result)

    common_var["refreshToken"] = resp['refresh_token']
    common_var["accessToken"] = resp['access_token']


async def test_refresh(test_db):
    response = client.post("/authentications/refresh", json={
        "refreshToken": common_var["refreshToken"]
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200
    assert "Access token successfully renewed" in resp['message']

    supposed_keys = set(["accessToken"])
    current_keys = set(resp['data'].keys())
    assert supposed_keys == current_keys
    # Ensure valid token
    result = decrypt_access_token(resp['data']['accessToken'])
    check_access_token(result)
