from typing import Optional
from xmlrpc.client import Boolean

from jose import ExpiredSignatureError, JWTError, jwt

from app.schema.authentication import AccessToken, RefreshToken
from app.utils.schema import TemplateModel
from config import get_settings

settings = get_settings()


class JWTDecrypt(TemplateModel):
    valid: Boolean
    expired: Boolean
    payload: None


class AccessTokenDecrypt(JWTDecrypt):
    payload: Optional[AccessToken]


class RefreshTokenDecrypt(JWTDecrypt):
    payload: Optional[RefreshToken]


def decrypt_access_token(access_token):
    try:
        payload: AccessToken = jwt.decode(access_token, settings.jwt_access_token_secret_key,
                                          algorithms=settings.jwt_algorithm)
        return AccessTokenDecrypt(valid=True, expired=False, payload=payload)
    except ExpiredSignatureError:
        return AccessTokenDecrypt(valid=False, expired=True, payload=None)
    except JWTError:
        return AccessTokenDecrypt(valid=False, expired=False, payload=None)


def decrypt_refresh_token(refresh_token: str):
    try:
        payload: RefreshToken = jwt.decode(refresh_token, settings.jwt_refresh_token_secret_key,
                                           algorithms=settings.jwt_algorithm)
        return RefreshTokenDecrypt(valid=True, expired=False, payload=payload)
    except ExpiredSignatureError:
        return RefreshTokenDecrypt(valid=False, expired=True, payload=None)
    except JWTError:
        return RefreshTokenDecrypt(valid=False, expired=False, payload=None)
