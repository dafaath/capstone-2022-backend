from fastapi import Depends, HTTPException
from app import oauth2_scheme
from app.models import UserRole
from app.schema.authentication import AccessToken
from app.utils.jwt import decrypt_access_token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    result = decrypt_access_token(token)
    payload = result.payload
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_admin(user: AccessToken = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin is allowed to access this.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
