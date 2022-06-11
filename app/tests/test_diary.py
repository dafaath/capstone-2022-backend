from essential_generators import DocumentGenerator
from fastapi.testclient import TestClient

from app.schema.diary import EmotionCategory
from app.utils.test import (DIARY_RESPONSE_KEYS,
                            decrypt_access_token_without_verification,
                            have_base_templates, have_correct_data_properties,
                            have_correct_status,
                            have_correct_status_and_message,
                            have_data_list_with_exact_properties,
                            have_data_list_with_minimum_properties,
                            have_error_message, have_minimum_data_properties)
from config import get_settings

common_var = {}
settings = get_settings()
DIARY_COUNT = 2
main = DocumentGenerator()
diaries = []
admin_diaries = []
user_diaries = []
translated_diaries = []


async def test_emotion_summary_null(test_db, user_token, client: TestClient):
    response = client.get("/diaries", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    assert isinstance(resp["data"], list)
    if len(resp["data"]) == 0:
        response = client.get(
            f"/diaries/emotions",
            headers={
                "Authorization": "bearer " +
                user_token})
        have_correct_status_and_message(response, 200, "emotion summary")
        have_base_templates(response)
        data = response.json()["data"]
        assert data["emotion"] is None


async def test_create_diaries_regular(test_db, user_token, client: TestClient):
    for i in range(DIARY_COUNT):
        data = {
            "title": main.sentence(),
            "content": main.sentence()
        }
        response = client.post(
            f"/diaries/",
            headers={
                "Authorization": "bearer " +
                user_token},
            json=data,
            params={
                "translate": False,
                "emotion": EmotionCategory.ANGER.value})
        have_correct_status_and_message(response, 201, "create diary")
        have_base_templates(response)
        have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)
        data = response.json()["data"]
        assert data["content"] == data["translatedContent"]
        assert isinstance(data["articles"], list)
        assert len(data["articles"]) > 0
        diaries.append(data)
        user_diaries.append(data)


async def test_emotion_summary_regular(test_db, user_token, client: TestClient):
    response = client.get(
        f"/diaries/emotions",
        headers={
            "Authorization": "bearer " +
            user_token})
    have_correct_status_and_message(response, 200, "emotion summary")
    have_base_templates(response)
    data = response.json()["data"]
    assert data["emotion"]


async def test_create_diaries_admin(test_db, admin_token, client: TestClient):
    for i in range(DIARY_COUNT):
        data = {
            "title": main.sentence(),
            "content": main.sentence()
        }
        response = client.post(
            f"/diaries/",
            headers={
                "Authorization": "bearer " +
                admin_token},
            json=data,
            params={
                "emotion": EmotionCategory.JOY.value,
                "translate": False})
        have_correct_status_and_message(response, 201, "create diary")
        have_base_templates(response)
        have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)
        data = response.json()["data"]
        assert data["content"] == data["translatedContent"]
        assert isinstance(data["articles"], list)
        assert len(data["articles"]) > 0
        diaries.append(data)
        admin_diaries.append(data)


async def test_emotion_summary_admin(test_db, admin_token, client: TestClient):
    response = client.get(
        f"/diaries/emotions",
        headers={
            "Authorization": "bearer " +
            admin_token})
    have_correct_status_and_message(response, 200, "emotion summary")
    have_base_templates(response)
    data = response.json()["data"]
    assert data["emotion"]


async def test_create_translated_diaries_admin(test_db, admin_token, client: TestClient):
    body = {
        "title": "My first diary",
        "content": "Aku sangat marah pada temanku"
    }
    response = client.post(
        f"/diaries/",
        headers={
            "Authorization": "bearer " +
            admin_token},
        json=body)
    have_correct_status_and_message(response, 201, "create diary")
    have_base_templates(response)
    have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)
    data = response.json()["data"]
    assert data["title"] == data["title"]
    assert data["content"] == data["content"]
    assert data["translatedContent"] == "I'm so mad at my friend"
    assert data["emotion"] == "anger"
    assert isinstance(data["articles"], list)
    assert len(data["articles"]) > 0
    for article in data["articles"]:
        assert article["emotion"] == "anger"

    diaries.append(data)
    admin_diaries.append(data)
    translated_diaries.append(data)


async def test_get_all_diaries(test_db, admin_token, client: TestClient):
    response = client.get("/diaries/all", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()
    print(resp)

    assert isinstance(resp["data"], list)
    common_var["many_diary"] = len(resp["data"]) - (DIARY_COUNT * 2 + 1)

    have_base_templates(response)
    have_data_list_with_exact_properties(response, DIARY_RESPONSE_KEYS)
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
    have_data_list_with_exact_properties(response, DIARY_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all diaries")

    data = resp["data"]
    data = sorted(data, key=lambda x: x["id"])
    admin_diaries_ids = list(map(lambda x: x["id"], admin_diaries.copy()))
    new_admin_diaries = sorted(admin_diaries.copy(), key=lambda x: x["id"])
    data = list(filter(lambda x: x["id"] in admin_diaries_ids, data))
    assert len(data) == len(admin_diaries)
    for i in range(len(data)):
        new_admin_diaries[i]["timeUpdated"] = ""
        data[i]["timeUpdated"] = ""
        new_admin_diaries[i]["timeCreated"] = ""
        data[i]["timeCreated"] = ""
        new_admin_diaries[i]["articles"] = None
        data[i]["articles"] = None
        assert new_admin_diaries[i] == data[i]


async def test_get_test_user_diaries(test_db, user_token, client: TestClient):
    response = client.get("/diaries", headers={"Authorization": "bearer " + user_token})
    resp = response.json()
    print(resp)
    have_base_templates(response)
    have_data_list_with_exact_properties(response, DIARY_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get all diaries")

    data = resp["data"]
    data = sorted(data, key=lambda x: x["id"])
    user_diaries_ids = list(map(lambda x: x["id"], user_diaries.copy()))
    new_user_diaries = sorted(user_diaries.copy(), key=lambda x: x["id"])
    data = list(filter(lambda x: x["id"] in user_diaries_ids, data))
    assert len(data) == len(new_user_diaries)
    for i in range(len(data)):
        new_user_diaries[i]["timeUpdated"] = ""
        data[i]["timeUpdated"] = ""
        new_user_diaries[i]["timeCreated"] = ""
        data[i]["timeCreated"] = ""
        new_user_diaries[i]["articles"] = None
        data[i]["articles"] = None
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
            json=body,
            params={"translate": False})
        resp = response.json()
        print(resp)
        assert resp["data"]["title"] == diary["title"]
        assert resp["data"]["content"] == new_content
        assert resp["data"]["content"] == resp["data"]["translatedContent"]
        have_correct_status_and_message(response, 201, "update diary")
        have_base_templates(response)
        have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)


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
            params={"translate": False},
            json=data)
        resp = response.json()
        print(resp)
        assert resp["data"]["title"] == new_title
        assert resp["data"]["content"] == new_content
        assert resp["data"]["content"] == resp["data"]["translatedContent"]
        have_correct_status_and_message(response, 201, "update diary")
        have_base_templates(response)
        have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_update_translated_diary_admin(test_db, admin_token, user_token, client: TestClient):
    diary = translated_diaries[0]
    new_title = "My updated diary"
    new_content = "Aku sangat senang"
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
    assert resp["data"]["translatedContent"] == "I am very happy"
    assert resp["data"]["emotion"] == "joy"
    assert isinstance(resp["data"]["articles"], list)
    assert len(resp["data"]["articles"]) > 0

    have_correct_status_and_message(response, 201, "update diary")
    have_base_templates(response)
    have_minimum_data_properties(response, DIARY_RESPONSE_KEYS)


async def test_update_diary_forbidden(test_db, user_token, client: TestClient):
    decrypt_access_token_without_verification(user_token)
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
            params={"translate": False},
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
