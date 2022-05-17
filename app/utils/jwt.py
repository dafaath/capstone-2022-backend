from xmlrpc.client import Boolean

from fastapi import Depends
from jose import ExpiredSignatureError, JWTError, jwt

from app.schema.authentication import AccessToken, RefreshToken
from app.utils.schema import AutoCamelModel
from config import get_settings

settings = get_settings()


class JWTDecrypt(AutoCamelModel):
    valid: Boolean
    expired: Boolean
    payload: None


class AccessTokenDecrypt(JWTDecrypt):
    payload: AccessToken


class RefreshTokenDecrypt(JWTDecrypt):
    payload: RefreshToken


def decrypt_access_token(access_token):
    try:
        payload: AccessToken = jwt.decode(access_token, settings.jwt_access_token_secret_key,
                                          algorithms=settings.jwt_algorithm)
        return AccessTokenDecrypt(valid=True, expired=False, payload=payload)
    except ExpiredSignatureError:
        return AccessTokenDecrypt(valid=False, expired=True, payload=payload)
    except JWTError:
        return AccessTokenDecrypt(valid=False, expired=False, payload=payload)


def decrypt_refresh_token(refresh_token: str):
    try:
        payload: RefreshToken = jwt.decode(refresh_token, settings.jwt_refresh_token_secret_key,
                                           algorithms=settings.jwt_algorithm)
        return RefreshTokenDecrypt(valid=True, expired=False, payload=payload)
    except ExpiredSignatureError:
        return RefreshTokenDecrypt(valid=False, expired=True, payload=payload)
    except JWTError:
        return RefreshTokenDecrypt(valid=False, expired=False, payload=payload)
