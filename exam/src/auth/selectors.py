from typing import Optional, List
from sqlalchemy import select, or_ , and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .enums import RoleEnum


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """یافتن کاربر با آیدی"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_mobile(db: AsyncSession, mobile: str) -> Optional[User]:
    """یافتن کاربر با شماره موبایل"""
    result = await db.execute(select(User).where(User.mobile == mobile))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """یافتن کاربر با ایمیل"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def check_existing_user(
    db: AsyncSession, 
    mobile: str, 
    email: Optional[str] = None
) -> Optional[User]:
    print('query check_existing_user')
    """بررسی وجود کاربر با موبایل یا ایمیل"""
    if email:
        query = select(User).where(
            or_(User.mobile == mobile, User.email == email)
        )
    else:
        query = select(User).where(User.mobile == mobile)
    

    result = await db.execute(query)
    print("result  .....query ",result)
    return result.scalar_one_or_none()

async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """لیست کاربران با صفحه‌بندی"""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.id)
    )
    return list(result.scalars().all())


async def get_user_admin(
    db: AsyncSession,
    user_id: int
) -> Optional[User]:

    query = select(User).where(
        and_(
            User.id == user_id,
            User.role == RoleEnum.MANGER
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()