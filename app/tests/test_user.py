import os
import urllib.request

from essential_generators import DocumentGenerator
from fastapi.testclient import TestClient

from app.utils.test import (USER_RESPONSE_KEYS, UserResponsePlus,
                            decrypt_access_token_without_verification,
                            get_access_token_login, have_base_templates,
                            have_correct_data_properties, have_correct_status,
                            have_correct_status_and_message,
                            have_data_list_with_exact_properties,
                            have_error_message, random_char, random_digit)
from config import get_settings

settings = get_settings()
USER_COUNT = 3
common_var = {}
main = DocumentGenerator()
users_list: list[UserResponsePlus] = []


async def test_create_user(test_db, client: TestClient):
    for i in range(USER_COUNT):
        body = {
            "email": main.email(),
            "fullname": main.name(),
            "password": random_char(4)
        }
        response = client.post("/users/", json=body)
        resp = response.json()
        data = resp["data"]
        print(resp, body["password"])

        have_base_templates(response)
        have_correct_status_and_message(response, 201, "Registration successful")
        have_correct_data_properties(response, USER_RESPONSE_KEYS)
        access_token = get_access_token_login(client, data["email"], body["password"])
        users_list.append(UserResponsePlus(**data, access_token=access_token, password=body["password"]))


async def test_get_all_users(test_db, admin_token, client: TestClient):
    response = client.get("/users", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    assert isinstance(resp["data"], list)
    common_var["many_user"] = len(resp["data"]) - USER_COUNT
    print(resp)
    have_base_templates(response)
    have_data_list_with_exact_properties(response, USER_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all users")


async def test_error_get_all_users_without_admin(test_db, user_token, client: TestClient):
    response = client.get("/users")
    resp = response.json()
    print(resp)
    have_correct_status(response, 401)
    have_error_message(response)

    response = client.get("/users/", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    print(resp)
    have_correct_status(response, 403)
    have_error_message(response)


async def test_change_user_photo(test_db, client: TestClient):
    user = users_list[0]
    user_id = user.id
    access_token = user.access_token

    filenames = ["image1.png", "image2.jpg", "image3.jpeg"]
    old_photo = user.photo
    for filename in filenames:
        full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'image', filename)
        print(f"---filename = {full_path_filename}---")
        with open(full_path_filename, "rb") as f:
            response = client.post(
                f"/users/{user_id}/photo",
                headers={
                    "Authorization": "bearer " +
                    access_token},
                files={
                    "file": (
                        filename,
                        f,
                        "image/jpg")})

        resp = response.json()
        print(resp)
        have_correct_status_and_message(response, 201, "change the user profile picture")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)

        new_photo = resp["data"]["photo"]

        assert old_photo != new_photo

        # try:
        #     # ensure old photo deleted
        #     print(old_photo)
        #     request_old_photo = urllib.request.Request(old_photo, method="GET")
        #     with urllib.request.urlopen(request_old_photo) as req_op:
        #         print(req_op.status)
        #         assert req_op.status == 404
        #     assert False
        # except HTTPError as e:
        #     assert e.status == 404
        #     assert True

        # can get new photo
        print(new_photo)
        request_new_photo = urllib.request.Request(new_photo, method="GET")
        with urllib.request.urlopen(request_new_photo) as req_np:
            print(req_np.status)
            assert req_np.status == 200

        old_photo = new_photo


async def test_change_user_photo_forbidden(test_db, user_token, admin_token, client: TestClient):
    admin = decrypt_access_token_without_verification(admin_token)
    admin_id = admin.id

    filename = 'image1.png'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'image', filename)
    with open(full_path_filename, "rb") as file:
        response = client.post(
            f"/users/{admin_id}/photo",
            headers={
                "Authorization": "bearer " +
                user_token},
            files={
                "file": (
                    filename,
                    file,
                    "image/jpg")})

    have_correct_status(response, 403)
    have_error_message(response)


async def test_change_user_photo_wrong_format(test_db, user_token, client: TestClient):
    test_user = decrypt_access_token_without_verification(user_token)
    test_user_id = test_user.id

    filename = 'not_image.html'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'image', filename)
    with open(full_path_filename, "rb") as f:
        response = client.post(
            f"/users/{test_user_id}/photo",
            headers={
                "Authorization": "bearer " +
                user_token},
            files={
                "file": (
                    filename,
                    f,
                    "image/jpg")})

    have_correct_status(response, 400)
    have_error_message(response)


async def test_get_one_user(test_db, admin_token, client: TestClient):
    for user in users_list:
        response = client.get(f"/users/{user.id}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status_and_message(response, 200, "get user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_get_one_user_reguler(test_db, user_token, client: TestClient):
    test_user_id = decrypt_access_token_without_verification(user_token).id
    response = client.get(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token})
    have_correct_status_and_message(response, 200, "get user")
    have_base_templates(response)
    have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_get_one_user_forbidden(test_db, user_token, client: TestClient):
    for user in users_list:
        if user.email == settings.test_account_email:
            continue

        response = client.get(f"/users/{user.id}", headers={"Authorization": "bearer " + user_token})
        have_correct_status(response, 403)
        have_error_message(response)


async def test_update_user_admin(test_db, admin_token, client: TestClient):
    for user in users_list:
        new_email = f"{random_char(15)}@gmail.com"
        new_phone_number = f"+6181{random_digit(10)}"
        new_fullname = f"Dafa A"
        data = {
            "email": new_email,
            "phone": new_phone_number,
            "fullname": new_fullname
        }
        response = client.patch(f"/users/{user.id}", headers={"Authorization": "bearer " + admin_token}, json=data)
        resp = response.json()
        print(resp)
        assert resp["data"]["email"] == new_email
        assert resp["data"]["phone"] == new_phone_number
        assert resp["data"]["fullname"] == new_fullname
        have_correct_status_and_message(response, 201, "update user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)


async def test_update_regular(test_db, client: TestClient):
    for user in users_list:
        user_id = user.id
        new_email = random_char(8) + "@gmail.com"
        new_phone_number = "+6281" + random_digit(9)
        new_password = random_char(4)
        new_fullname = f"Eren jeger"
        body = {
            "email": new_email,
            "phone": new_phone_number,
            "newPassword": new_password,
            "currentPassword": user.password,
            "fullname": new_fullname
        }
        print(body)
        response = client.patch(
            f"/users/{user_id}",
            headers={
                "Authorization": "bearer " +
                user.access_token},
            json=body)
        resp = response.json()
        print(resp)
        assert resp["data"]["phone"] == new_phone_number
        assert resp["data"]["fullname"] == new_fullname
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


async def test_update_user_password_wrong(test_db, user_token, client: TestClient):
    test_user_id = decrypt_access_token_without_verification(user_token).id
    new_password = "new_pass_2"
    body = {
        "newPassword": new_password,
        "currentPassword": "randomstring",
    }
    response = client.patch(f"/users/{test_user_id}", headers={"Authorization": "bearer " + user_token}, json=body)
    have_correct_status(response, 403)
    have_error_message(response)


async def test_update_user_forbidden(test_db, user_token, client: TestClient):
    for user in users_list:
        new_email = f"{random_char(15)}@gmail.com"
        new_phone_number = f"+6181{random_digit(10)}"
        data = {
            "email": new_email,
            "phone": new_phone_number,
        }
        response = client.patch(f"/users/{user.id}", headers={"Authorization": "bearer " + user_token}, json=data)
        have_correct_status(response, 403)
        have_error_message(response)


async def test_delete_one_user_forbidden(test_db, user_token, client: TestClient):
    for user in users_list:
        response = client.delete(f"/users/{user.id}", headers={"Authorization": "bearer " + user_token})
        print(response.json())
        have_correct_status(response, 403)
        have_error_message(response)


async def test_delete_user_admin(test_db, admin_token, client: TestClient):
    for user in users_list:
        response = client.delete(f"/users/{user.id}", headers={"Authorization": "bearer " + admin_token})
        print(response.json())
        have_correct_status_and_message(response, 200, "delete user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)

        response = client.get(f"/users/{user.id}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status(response, 404)
        have_error_message(response)
        break
    users_list.pop(0)


async def test_delete_user_regular(test_db, client: TestClient):
    for user in users_list:
        user_id = user.id
        access_token = user.access_token
        response = client.delete(f"/users/{user_id}", headers={"Authorization": "bearer " + access_token})
        print(response.json())
        have_correct_status_and_message(response, 200, "delete user")
        have_base_templates(response)
        have_correct_data_properties(response, USER_RESPONSE_KEYS)

        response = client.get(f"/users/{user_id}", headers={"Authorization": "bearer " + access_token})
        have_correct_status(response, 404)
        have_error_message(response)


async def test_no_leftover(test_db, client: TestClient, admin_token):
    response = client.get("/users", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp["data"])
    assert isinstance(resp["data"], list)
    assert common_var["many_user"] == len(resp["data"])


async def test_no_admin_data_change(test_db, client: TestClient, admin_token):
    admin = decrypt_access_token_without_verification(admin_token)
    response = client.get(f"/users/{admin.id}", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    admin_dict = admin.dict(by_alias=True)
    admin_dict["id"] = str(admin_dict["id"])
    admin_dict["timeCreated"] = ""
    admin_dict["timeUpdated"] = ""
    resp["data"]["timeCreated"] = ""
    resp["data"]["timeUpdated"] = ""
    assert admin_dict == resp["data"]


async def test_no_admin_data_change(test_db, client: TestClient, user_token):
    user = decrypt_access_token_without_verification(user_token)
    response = client.get(f"/users/{user.id}", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    user_dict = user.dict(by_alias=True)
    user_dict["id"] = str(user_dict["id"])
    user_dict["timeCreated"] = ""
    user_dict["timeUpdated"] = ""
    resp["data"]["timeCreated"] = ""
    resp["data"]["timeUpdated"] = ""
    assert user_dict == resp["data"]
