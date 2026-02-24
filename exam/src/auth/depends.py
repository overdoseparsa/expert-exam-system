from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .constants import (
    ACCESS_TOKEN_COOKIE_NAME,
    CSRF_ACCESS_TOKEN_KEY,
    CSRF_REFRESH_TOKEN_KEY,
    REFRESH_TOKEN_COOKIE_NAME,
)
from .exceptions import ForbiddenException
from .jwt_handler import jwt_handler
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .models import User
from .selectors import get_user_by_id


http_bearer = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    if credentials.scheme != "Bearer":
        raise ForbiddenException("Invalid header")

    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if not access_token:
        raise ForbiddenException("Access token is not provided")

    token = jwt_handler.decode(access_token)
    user_id = token.get("sub")
    token_type = token.get("type")
    if not user_id or token_type != "access":
        raise ForbiddenException("Invalid access token")

    csrf_token = jwt_handler.decode(credentials.credentials)
    if csrf_token.get(CSRF_ACCESS_TOKEN_KEY) != access_token:
        raise ForbiddenException("Invalid CSRF token")

    return str(user_id)


async def get_current_user_with_refresh(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    if credentials.scheme != "Bearer":
        raise ForbiddenException("Invalid header")

    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise ForbiddenException("Refresh token is not provided")

    token = jwt_handler.decode(refresh_token)
    user_id = token.get("sub")
    token_type = token.get("type")
    if not user_id or token_type != "refresh":
        raise ForbiddenException("Invalid refresh token")

    csrf_token = jwt_handler.decode(credentials.credentials)
    if csrf_token.get(CSRF_REFRESH_TOKEN_KEY) != refresh_token:
        raise ForbiddenException("Invalid CSRF token")

    return str(user_id)


async def get_current_user_obj(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> User:
    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise ForbiddenException("User not found")
    return user
