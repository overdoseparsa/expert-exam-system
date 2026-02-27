from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import ContactInfo,  Address

async def get_contact_by_user_id(
        db: AsyncSession,
        user_id: int,
        content_id :int ,

        ) -> ContactInfo | None:
    stmt = select(ContactInfo).where(
        ContactInfo.user_id == user_id,
        ContactInfo.id == content_id
        )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  

async def get_contact_by_user_all(
        db: AsyncSession,
        user_id: int,

        ) -> ContactInfo | None:
    stmt = select(ContactInfo).where(
        ContactInfo.user_id == user_id,
        )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_by_id(db: AsyncSession, contact_id: int) -> ContactInfo | None:
    stmt = select(ContactInfo).where(ContactInfo.id == contact_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_addresses_by_user_id(
        db: AsyncSession,
        user_id: int,
        address_id : int 
        )-> list[Address]:
    
    stmt = select(Address).where(
        Address.user_id == user_id,
        Address.id == address_id,

        )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_address_by_id(
        db: AsyncSession,
        address_id: int
        ) -> Address | None:
    stmt = select(Address).where(Address.id == address_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_addresses_by_all(
        db: AsyncSession,
        user_id: int,
        )-> list[Address]:
    
    stmt = select(Address).where(
        Address.user_id == user_id,

        )
    result = await db.execute(stmt)
    return result.scalars().all()
