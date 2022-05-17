from fastapi.testclient import TestClient

from app.main import app
from app.utils.test import (USER_RESPONSE_KEYS, have_base_templates,
                            have_correct_data_properties, have_correct_status,
                            have_correct_status_and_message,
                            have_data_list_with_correct_properties,
                            have_error_detail, random_char, random_digit)
from config import get_settings

client = TestClient(app)
common_var = {}
settings = get_settings()


async def test_get_all_users(test_db, admin_token):
    response = client.get("/users", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp)
    have_base_templates(response)
    have_data_list_with_correct_properties(response, USER_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all users")

    common_var["users"] = resp["data"]


async def test_error_get_all_users_without_admin(test_db, user_token):
    response = client.get("/users")
    resp = response.json()
    print(resp)
    have_correct_status(response, 401)
    have_error_detail(response)

    response = client.get("/users/", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    print(resp)
    have_correct_status(response, 403)
    have_error_detail(response)


async def test_get_one_user(test_db, admin_token):
    for user in common_var["users"]:
        response = client.get(f"/users/{user['id']}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status_and_message(response, 200, "get user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_get_one_user_reguler(test_db, user_token):
    test_user_id = next(item for item in common_var["users"] if item["email"] == settings.test_account_email)["id"]
    response = client.get(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token})
    have_correct_status_and_message(response, 200, "get user")
    have_base_templates(response)
    have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_get_one_user_forbidden(test_db, user_token):
    for user in common_var["users"]:
        if user["email"] == settings.test_account_email:
            continue

        response = client.get(f"/users/{user['id']}", headers={"Authorization": "bearer " + user_token})
        have_correct_status(response, 403)
        have_error_detail(response)


async def test_update_user_admin(test_db, admin_token):
    for user in common_var["users"]:
        if user["email"] == settings.test_account_email:
            continue

        new_email = f"{random_char(15)}@gmail.com"
        new_phone_number = f"+6181{random_digit(10)}"
        data = {
            "email": new_email,
            "phone": new_phone_number,
        }
        response = client.patch(f"/users/{user['id']}", headers={"Authorization": "bearer " + admin_token}, json=data)
        resp = response.json()
        print(resp)
        assert resp["data"]["email"] == new_email
        assert resp["data"]["phone"] == new_phone_number
        have_correct_status_and_message(response, 201, "update user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_update_regular(test_db, user_token):
    test_user_id = next(item for item in common_var["users"] if item["email"] == settings.test_account_email)["id"]
    new_email = "haha@gmail.com"
    new_phone_number = "+6189234120324"
    new_password = "new_pass"
    common_var["test_user_new_email"] = new_email
    common_var["test_user_new_phone"] = new_phone_number
    common_var["test_user_new_password"] = new_password
    body = {
        "email": new_email,
        "phone": new_phone_number,
        "newPassword": new_password,
        "currentPassword": settings.test_account_password,
    }
    print(body)
    response = client.patch(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token}, json=body)
    resp = response.json()
    print(resp)
    assert resp["data"]["phone"] == new_phone_number
    have_correct_status_and_message(response, 201, "update user")
    have_base_templates(response)
    have_correct_data_properties(response, USER_RESPONSE_KEYS)

    # can login with new pass
    response = client.post("/authentications/login", data={
        "username": new_email,
        "password": new_password
    })
    resp = response.json()
    print(resp)
    assert response.status_code == 200


async def test_update_user_password_wrong(test_db, user_token):
    test_user_id = next(item for item in common_var["users"] if item["email"] == settings.test_account_email)["id"]
    new_password = "new_pass_2"
    body = {
        "newPassword": new_password,
        "currentPassword": "randomstring",
    }
    response = client.patch(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token}, json=body)
    have_correct_status(response, 403)
    have_error_detail(response)


async def test_update_user_forbidden(test_db, user_token):
    for user in common_var["users"]:
        if user["email"] == settings.test_account_email:
            continue

        new_email = f"{random_char(15)}@gmail.com"
        new_phone_number = f"+6181{random_digit(10)}"
        data = {
            "email": new_email,
            "phone": new_phone_number,
        }
        response = client.patch(f"/users/{user['id']}", headers={"Authorization": "bearer " + user_token}, json=data)
        have_correct_status(response, 403)
        have_error_detail(response)


async def test_delete_one_user_forbidden(test_db, user_token):
    for user in common_var["users"]:
        if user["email"] == settings.test_account_email:
            continue
        print(user["id"], common_var["test_user_new_email"])

        response = client.delete(f"/users/{user['id']}", headers={"Authorization": "bearer " + user_token})
        print(response.json())
        have_correct_status(response, 403)
        have_error_detail(response)


async def test_delete_one_user(test_db, admin_token):
    for user in common_var["users"]:
        if user["email"] == settings.test_account_email:
            continue

        response = client.delete(f"/users/{user['id']}", headers={"Authorization": "bearer " + admin_token})
        print(response.json())
        have_correct_status_and_message(response, 200, "delete user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)

        response = client.get(f"/users/{user['id']}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status(response, 404)
        have_error_detail(response)


async def test_delete_one_user_reguler(test_db, user_token):
    test_user_id = next(item for item in common_var["users"]
                        if item["email"] == settings.test_account_email)["id"]
    response = client.delete(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token})
    print(response.json())
    have_correct_status_and_message(response, 200, "delete user")
    have_base_templates(response)
    have_correct_data_properties(response, USER_RESPONSE_KEYS)

    response = client.get(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token})
    have_correct_status(response, 404)
    have_error_detail(response)