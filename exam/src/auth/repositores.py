from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .security import get_password_hash

async def create_user(
    db: AsyncSession,
    mobile: str,
    password: str,
    email: str = None,
    role: str = "user",
    is_active: bool = True,
    is_verified: bool = False
) -> User:

    user = User(
        mobile=mobile,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        is_active=is_active,
        is_verified=is_verified
    )
    db.add(user)
    await db.flush()
    return user

async def update_user_password(
    db: AsyncSession,
    user: User,
    new_password: str
) -> User:
    """به‌روزرسانی رمز عبور"""
    user.password_hash = get_password_hash(new_password)
    await db.flush()
    return user

async def verify_user_account(
    db: AsyncSession,
    user: User
) -> User:
    """تأیید حساب کاربری"""
    user.is_verified = True
    user.verification_code = None
    await db.flush()
    return user

async def set_user_active_status(
    db: AsyncSession,
    user: User,
    is_active: bool
) -> User:
    """فعال/غیرفعال کردن کاربر"""
    user.is_active = is_active
    await db.flush()
    return user