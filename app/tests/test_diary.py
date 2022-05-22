from essential_generators import DocumentGenerator
from fastapi.testclient import TestClient

from app.utils.test import (DIARY_RESPONSE_KEYS, USER_RESPONSE_KEYS,
                            decrypt_access_token_without_verification,
                            have_base_templates, have_correct_data_properties,
                            have_correct_status,
                            have_correct_status_and_message,
                            have_data_list_with_correct_properties,
                            have_error_message)
from config import get_settings

common_var = {}
settings = get_settings()
DIARY_COUNT = 2
main = DocumentGenerator()
diaries = []
admin_diaries = []
user_diaries = []


async def test_create_diaries_regular(test_db, user_token, client: TestClient):
    for i in range(DIARY_COUNT):
        data = {
            "title": main.sentence(),
            "content": main.sentence()
        }
        response = client.post(f"/diaries/", headers={"Authorization": "bearer " + user_token}, json=data)
        have_correct_status_and_message(response, 201, "create diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)
        data = response.json()["data"]
        diaries.append(data)
        user_diaries.append(data)


async def test_create_diaries_admin(test_db, admin_token, client: TestClient):
    for i in range(DIARY_COUNT):
        data = {
            "title": main.sentence(),
            "content": main.sentence()
        }
        response = client.post(f"/diaries/", headers={"Authorization": "bearer " + admin_token}, json=data)
        have_correct_status_and_message(response, 201, "create diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)
        data = response.json()["data"]
        diaries.append(data)
        admin_diaries.append(data)


async def test_get_all_diaries(test_db, admin_token, client: TestClient):
    response = client.get("/diaries/all", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp)

    assert isinstance(resp["data"], list)
    common_var["many_diary"] = len(resp["data"]) - (DIARY_COUNT * 2)

    have_base_templates(response)
    have_data_list_with_correct_properties(response, DIARY_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all diaries")


async def test_error_get_all_diaries_without_admin(test_db, user_token, client: TestClient):
    response = client.get("/diaries/all")
    resp = response.json()
    print(resp)
    have_correct_status(response, 401)
    have_error_message(response)

    response = client.get("/diaries/all", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    print(resp)
    have_correct_status(response, 403)
    have_error_message(response)


async def test_get_user_diaries_error(test_db, client: TestClient):
    response = client.get("/diaries")
    resp = response.json()
    print(resp)
    have_correct_status(response, 401)
    have_error_message(response)


async def test_get_admin_user_diaries(test_db, admin_token, client: TestClient):
    response = client.get("/diaries", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp)
    have_base_templates(response)
    have_data_list_with_correct_properties(response, DIARY_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all diaries")

    data = resp["data"]
    data = sorted(data, key=lambda x: x["id"])
    new_admin_diaries = sorted(admin_diaries.copy(), key=lambda x: x["id"])
    assert len(data) == len(admin_diaries)
    for i in range(len(data)):
        new_admin_diaries[i]["timeUpdated"] = ""
        data[i]["timeUpdated"] = ""
        new_admin_diaries[i]["timeCreated"] = ""
        data[i]["timeCreated"] = ""
        assert new_admin_diaries[i] == data[i]


async def test_get_test_user_diaries(test_db, user_token, client: TestClient):
    response = client.get("/diaries", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    print(resp)
    have_base_templates(response)
    have_data_list_with_correct_properties(response, DIARY_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all diaries")

    data = resp["data"]
    data = sorted(data, key=lambda x: x["id"])
    new_user_diaries = sorted(user_diaries.copy(), key=lambda x: x["id"])
    assert len(data) == len(user_diaries)
    for i in range(len(data)):
        new_user_diaries[i]["timeUpdated"] = ""
        data[i]["timeUpdated"] = ""
        new_user_diaries[i]["timeCreated"] = ""
        data[i]["timeCreated"] = ""
        assert new_user_diaries[i] == data[i]


async def test_get_one_diary(test_db, admin_token, client: TestClient):
    for diary in diaries:
        response = client.get(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status_and_message(response, 200, "get diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_get_one_diary_reguler(test_db, user_token, client: TestClient):
    for diary in user_diaries:
        response = client.get(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + user_token})
        have_correct_status_and_message(response, 200, "get diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_get_one_diary_forbidden(test_db, user_token, client: TestClient):
    for diary in admin_diaries:
        response = client.get(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + user_token})
        print(response.json())
        have_correct_status(response, 403)
        have_error_message(response)


async def test_update_regular(test_db, user_token, client: TestClient):
    for diary in user_diaries:
        new_content = "new regular content"
        body = {
            "content": new_content
        }
        print(body)
        response = client.patch(
            f"/diaries/{diary['id']}",
            headers={
                "Authorization": "bearer " +
                user_token},
            json=body)
        resp = response.json()
        print(resp)
        assert resp["data"]["title"] == diary["title"]
        assert resp["data"]["content"] == new_content
        have_correct_status_and_message(response, 201, "update diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_update_diary_admin(test_db, admin_token, user_token, client: TestClient):
    user = decrypt_access_token_without_verification(user_token)
    for diary in diaries:
        if diary["userId"] == user.id:
            continue

        new_title = "new title"
        new_content = "new content"
        data = {
            "title": new_title,
            "content": new_content
        }
        response = client.patch(
            f"/diaries/{diary['id']}",
            headers={
                "Authorization": "bearer " +
                admin_token},
            json=data)
        resp = response.json()
        print(resp)
        assert resp["data"]["title"] == new_title
        assert resp["data"]["content"] == new_content
        have_correct_status_and_message(response, 201, "update diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_update_diary_forbidden(test_db, user_token, client: TestClient):
    user = decrypt_access_token_without_verification(user_token)
    for diary in admin_diaries:
        new_content = "new content forbidden"
        data = {
            "content": new_content
        }
        response = client.patch(
            f"/diaries/{diary['id']}",
            headers={
                "Authorization": "bearer " +
                user_token},
            json=data)

        have_correct_status(response, 403)
        have_error_message(response)


async def test_delete_one_diary_forbidden(test_db, user_token, client: TestClient):
    for diary in admin_diaries:
        response = client.delete(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + user_token})
        print(response.json())
        have_correct_status(response, 403)
        have_error_message(response)


async def test_delete_one_diary(test_db, admin_token, client: TestClient):
    for diary in admin_diaries:
        response = client.delete(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + admin_token})
        print(response.json())
        have_correct_status_and_message(response, 200, "delete diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)

        response = client.get(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + admin_token})
        have_correct_status(response, 404)
        have_error_message(response)


async def test_delete_one_diary_reguler(test_db, user_token, client: TestClient):
    for diary in user_diaries:
        response = client.delete(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + user_token})
        print(response.json())
        have_correct_status_and_message(response, 200, "delete diary")
        have_base_templates(response)
        have_correct_data_properties(response, DIARY_RESPONSE_KEYS)

        response = client.get(f"/diaries/{diary['id']}", headers={"Authorization": "bearer " + user_token})
        have_correct_status(response, 404)
        have_error_message(response)


async def test_no_leftover(test_db, client: TestClient, admin_token):
    response = client.get("/diaries/all", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp["data"])
    assert isinstance(resp["data"], list)
    assert common_var["many_diary"] == len(resp["data"])
