from fastapi import HTTPException, status  # TODO remove fastapi layer from service

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserCreate, UserUpdate, UserLogin, PasswordUpdate

from .security import get_password_hash, verify_password, create_access_token
from . import selectors as user_selector
from . import repositores as user_repository


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        mobile=user_in.mobile,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
        is_verified=user_in.is_verified,
        is_verified_phone=user_in.is_verified_phone,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user: User,
    user_in: UserUpdate,
) -> User:
    data = user_in.dict(exclude_unset=True)

    password: Optional[str] = data.pop("password", None)

    for field, value in data.items():
        setattr(user, field, value)

    if password is not None:
        user.password_hash = get_password_hash(password)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def set_user_active(
    db: AsyncSession,
    user: User,
    is_active: bool,
) -> User:
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user



async def register_user(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    
    # بررسی وجود کاربر
    existing_user = await user_selector.check_existing_user(
        db, 
        mobile=user_data.mobile,
        email=user_data.email
    )
    
    if existing_user:
        if existing_user.mobile == user_data.mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="کاربر با این شماره موبایل قبلاً ثبت‌نام کرده است"
            )
        if user_data.email and existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این ایمیل قبلاً ثبت شده است"
            )
    
    # ایجاد کاربر جدید
    try:
        user = await user_repository.create_user(
            db,
            mobile=user_data.mobile,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت کاربر: {str(e)}"
        )

async def login_user(
    db: AsyncSession,
    login_data: UserLogin
) -> tuple[User, str]:
    """ورود کاربر"""
    
    # پیدا کردن کاربر
    user = await user_selector.get_user_by_mobile(db, login_data.mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شماره موبایل یا رمز عبور نادرست است"
        )
    
    # بررسی فعال بودن کاربر
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حساب کاربری غیرفعال است"
        )
    
    # بررسی رمز عبور
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شماره موبایل یا رمز عبور نادرست است"
        )
    
    # تولید توکن
    access_token = create_access_token(
        data={"sub": str(user.id), "mobile": user.mobile}
    )
    
    return user, access_token

async def update_user_password(
    db: AsyncSession,
    current_user: User,
    password_data: PasswordUpdate
) -> None:
    """تغییر رمز عبور"""
    
    # بررسی رمز فعلی
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز عبور فعلی نادرست است"
        )
    
    # بررسی رمز جدید
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز عبور جدید باید حداقل ۶ کاراکتر باشد"
        )
    
    try:
        await user_repository.update_user_password(
            db,
            user=current_user,
            new_password=password_data.new_password
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در تغییر رمز عبور: {str(e)}"
        )