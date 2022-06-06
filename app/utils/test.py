import random
import string

from fastapi.testclient import TestClient
from jose import jwt
from requests import Response

from app.schema.user import UserResponse

USER_RESPONSE_KEYS = ["id", "email", "phone", "isActive", "timeCreated", "photo", "timeUpdated", "role", "fullname"]
DIARY_RESPONSE_KEYS = [
    "id",
    "title",
    "content",
    "translatedContent",
    "emotion",
    "timeCreated",
    "timeUpdated",
    "userId"]
ARTICLE_RESPONSE_KEYS = ["id",
                         "language",
                         "position",
                         "title",
                         "link",
                         "displayedLink"]


def have_error_message(response: Response):
    resp = response.json()
    assert resp["message"]
    assert isinstance(resp["message"], str)


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
    dict_have_exact_properties(resp["data"], keys)


def have_minimum_data_properties(response: Response, keys: list[str]):
    resp = response.json()
    dict_have_minimum_properties(resp["data"], keys)


def have_data_list_with_minimum_properties(response: Response, keys: list[str]):
    resp = response.json()
    assert isinstance(resp["data"], list)
    for item in resp["data"]:
        dict_have_minimum_properties(item, keys)


def have_data_list_with_exact_properties(response: Response, keys: list[str]):
    resp = response.json()
    assert isinstance(resp["data"], list)
    for item in resp["data"]:
        dict_have_exact_properties(item, keys)


def is_sub_array(A: list, B: list):
    n = len(A)
    m = len(B)

    # Two pointers to traverse the arrays
    i = 0
    j = 0

    # Traverse both arrays simultaneously
    while (i < n and j < m):

        # If element matches
        # increment both pointers
        if (A[i] == B[j]):

            i += 1
            j += 1

            # If array B is completely
            # traversed
            if (j == m):
                return True

        # If not,
        # increment i and reset j
        else:
            i = i - j + 1
            j = 0
    return False


def dict_have_minimum_properties(data: dict, keys: list[str]):
    supposed_keys = keys
    current_keys = list(data.keys())
    print(supposed_keys, current_keys)
    for sk in supposed_keys:
        assert sk in current_keys


def dict_have_exact_properties(data: dict, keys: list[str]):
    supposed_keys = set(keys)
    current_keys = set(data.keys())
    print(supposed_keys, current_keys)
    assert supposed_keys == current_keys


def have_no_undefined(response: Response, keys: list[str]):
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


def decrypt_access_token_without_verification(token: str):
    data = decrypt_jwt_without_verification(token)
    return UserResponse(**data)


def decrypt_jwt_without_verification(token: str) -> dict:
    return jwt.get_unverified_claims(token)


def get_access_token_login(client: TestClient, username: str, password: str):
    response = client.post("/authentications/login", data={
        "username": username,
        "password": password
    })
    resp = response.json()
    print(username, password, resp)

    assert response.status_code == 200
    return resp["access_token"]


class UserResponsePlus(UserResponse):
    password: str
    access_token: str
