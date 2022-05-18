import random
import string

from google.cloud.firestore import Client
from requests import Response

USER_RESPONSE_KEYS = ["id", "email", "phone", "isActive", "timeCreated", "photo", "timeUpdated", "role"]
DIARY_RESPONSE_KEYS = [
    "id",
    "content",
    "translatedContent",
    "emotion",
    "timeCreated",
    "timeUpdated",
    "user",
    "userId"]


def delete_all_collection(fs: Client):
    docs = fs.collection('diary').stream()
    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()


def have_error_detail(response: Response):
    resp = response.json()
    assert resp["detail"]
    assert isinstance(resp["detail"], str)


def have_correct_status(response: Response, code: int):
    assert response.status_code == code


def have_correct_message(response: Response, message: str):
    resp = response.json()
    assert message.lower() in resp['message'].lower()


def have_correct_status_and_message(response: Response, code: int, message: str):
    have_correct_status(response, code)
    have_correct_message(response, message)


def have_correct_data_properties(response: Response, keys: list[str]):
    resp = response.json()
    dict_have_correct_properties(resp["data"], keys)


def have_data_list_with_correct_properties(response: Response, keys: list[str]):
    resp = response.json()
    assert isinstance(resp["data"], list)
    for item in resp["data"]:
        dict_have_correct_properties(item, keys)


def dict_have_correct_properties(data: dict, keys: list[str]):
    supposed_keys = set(keys)
    current_keys = set(data.keys())
    print(supposed_keys, current_keys)
    assert supposed_keys == current_keys


def have_not_undefined(response: Response, keys: list[str]):
    resp = response.json()
    for k in keys:
        assert resp["data"][k]


def have_base_templates(response: Response):
    resp = response.json()
    assert "message" in resp
    assert "data" in resp


def random_char(char_num):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))


def random_digit(char_num):
    return ''.join(random.choice(string.digits) for _ in range(char_num))
