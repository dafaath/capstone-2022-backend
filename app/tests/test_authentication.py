from essential_generators import DocumentGenerator
from fastapi.testclient import TestClient

from app.utils.jwt import decrypt_access_token, decrypt_refresh_token
from app.utils.test import (USER_RESPONSE_KEYS, have_base_templates,
                            have_correct_data_properties, have_correct_status,
                            have_correct_status_and_message,
                            have_error_message, random_char)

common_var = {}
main = DocumentGenerator()


async def test_register(test_db, client: TestClient):
    body = {
        "email": main.email(),
        "fullname": main.name(),
        "password": random_char(4)
    }
    response = client.post("/users/", json=body)
    resp = response.json()
    common_var["user"] = resp["data"]
    common_var["user"]["password"] = body["password"]

    have_base_templates(response)
    have_correct_status_and_message(response, 201, "Registration successful")
    have_correct_data_properties(
        response, USER_RESPONSE_KEYS)


def check_access_token(result):
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.id
    assert result.payload.email
    assert result.payload.is_active
    assert result.payload.time_created
    assert result.payload.time_updated


def check_refresh_token(result):
    assert result.valid
    assert not result.expired
    assert result.payload is not None
    assert result.payload.user_id
    assert result.payload.session_id


async def test_login(test_db, client: TestClient):
    response = client.post("/authentications/login", data={
        "username": common_var["user"]["email"],
        "password": common_var["user"]["password"]
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200

    supposed_keys = set(["access_token", "refresh_token", "token_type",
                        "expires_in", "scope", "message"] + USER_RESPONSE_KEYS)
    current_keys = set(resp.keys())
    assert supposed_keys == current_keys
    # Ensure valid token
    result = decrypt_access_token(resp['access_token'])
    check_access_token(result)

    payload_dict = result.payload.dict(by_alias=True)
    for k in USER_RESPONSE_KEYS:
        assert resp[k] == payload_dict[k]

    result = decrypt_refresh_token(resp['refresh_token'])
    check_refresh_token(result)

    common_var["refreshToken"] = resp['refresh_token']
    common_var["accessToken"] = resp['access_token']


async def test_refresh(test_db, client: TestClient):
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


async def test_delete_created_user(test_db, client: TestClient):
    user_id = common_var["user"]["id"]
    access_token = common_var["accessToken"]
    response = client.delete(f"/users/{user_id}", headers={"Authorization": "bearer " + access_token})
    print(response.json())
    have_correct_status_and_message(response, 200, "delete user")
    have_base_templates(response)
    have_correct_data_properties(response, USER_RESPONSE_KEYS)

    response = client.get(f"/users/{user_id}", headers={"Authorization": "bearer " + access_token})
    have_correct_status(response, 404)
    have_error_message(response)
