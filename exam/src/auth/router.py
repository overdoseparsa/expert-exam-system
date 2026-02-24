from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from .depends import get_current_user_obj
from .models import User
from .schemas import (
    UserResponse,
    UserCreate,
    UserLogin,
    TokenResponse,
    PasswordUpdate
)
from .services import (
    register_user as register_user_service,
    login_user as login_user_service,
    update_user_password as update_user_password_service,
)
from .utils import set_cookie
from config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await register_user_service(
        db , 
        user_data
    )




@router.post("/login/", response_model=TokenResponse)
async def login_user_endpoint(
    login_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user, access_token = await login_user_service(db, login_data)

    response.delete_cookie(
        key=settings.AUTH_TOKEN_NAME,
        httponly=settings.HTTP_ONLY,
        secure=settings.HTTP_SECURE,
        samesite=settings.SAME_SITE,
        path="/",
    )

    await set_cookie(
        response=response,
        key=settings.AUTH_TOKEN_NAME,
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=settings.HTTP_ONLY,
        secure=settings.HTTP_SECURE,
        path="/",
    )

    return TokenResponse(access_token=access_token, user=user)

@router.put("/update-password/")
async def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    await update_user_password_service(db, current_user, password_data)
    return {"message": "رمز عبور با موفقیت تغییر کرد"}


@router.post("/logout/", status_code=status.HTTP_200_OK)
async def logout_user(response: Response):
    response.delete_cookie(
        key=settings.AUTH_TOKEN_NAME,
        httponly=settings.HTTP_ONLY,
        secure=settings.HTTP_SECURE,
        samesite=settings.SAME_SITE,
        path="/",
    )
    return {
        "success": True,
        "message": "با موفقیت خارج شدید"
    }

@router.get("/debug")
async def debug(request: Request):
    return request.cookies