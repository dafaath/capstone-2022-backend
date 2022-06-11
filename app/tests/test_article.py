from fastapi.testclient import TestClient
from app.schema.diary import EmotionCategory

from app.utils.test import (ARTICLE_RESPONSE_KEYS, have_base_templates,
                            have_correct_status_and_message,
                            have_data_list_with_minimum_properties)


async def test_get_all_diaries(test_db, admin_token, client: TestClient):
    response = client.get("/articles", headers={"Authorization": "bearer " + admin_token})
    resp = response.json()

    assert isinstance(resp["data"], list)
    print(resp["data"])
    emotion_list = set([e.value for e in EmotionCategory])
    emotion_current = set([])
    for a in resp["data"]:
        emotion_current.add(a["emotion"])
    assert emotion_list == emotion_current

    have_base_templates(response)
    have_data_list_with_minimum_properties(response, ARTICLE_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get articles")


async def test_get_all_diaries_specific_emotion(test_db, admin_token, client: TestClient):
    response = client.get("/articles", headers={"Authorization": "bearer " + admin_token}, params={
        "emotions": ["anger", "sadness"]
    })
    resp = response.json()
    print(resp)

    assert isinstance(resp["data"], list)
    data = resp["data"]
    for d in data:
        assert d["emotion"] == "anger" or d["emotion"] == "sadness"

    have_base_templates(response)
    have_data_list_with_minimum_properties(response, ARTICLE_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get articles")


async def test_get_all_diaries_specific_pagination(test_db, admin_token, client: TestClient):
    id_before = []
    response = client.get("/articles", headers={"Authorization": "bearer " + admin_token}, params={
        "page": 1,
        "size": 10
    })
    resp = response.json()
    print(resp)

    assert isinstance(resp["data"], list)
    data = resp["data"]
    assert len(data) == 10

    have_base_templates(response)
    have_data_list_with_minimum_properties(response, ARTICLE_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get articles")

    response = client.get("/articles", headers={"Authorization": "bearer " + admin_token}, params={
        "page": 2,
        "size": 10
    })
    resp = response.json()
    print(resp)

    assert isinstance(resp["data"], list)
    data = resp["data"]
    assert len(data) == 10
    for d in data:
        assert d["id"] not in id_before

    have_base_templates(response)
    have_data_list_with_minimum_properties(response, ARTICLE_RESPONSE_KEYS)
    have_correct_status_and_message(response, 200, "get articles")
