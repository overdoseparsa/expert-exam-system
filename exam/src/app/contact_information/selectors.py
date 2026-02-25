from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import ContactInfo,  Address


def get_contact_by_user_id(db: Session, user_id: int) -> ContactInfo | None:
    stmt = select(ContactInfo).where(ContactInfo.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def get_contact_by_id(db: Session, contact_id: int) -> ContactInfo | None:
    stmt = select(ContactInfo).where(ContactInfo.id == contact_id)
    return db.execute(stmt).scalar_one_or_none()



def get_addresses_by_user_id(db: Session, user_id: int) -> list[Address]:
    stmt = select(Address).where(Address.user_id == user_id)
    return db.execute(stmt).scalars().all()


def get_address_by_id(db: Session, address_id: int) -> Address | None:
    stmt = select(Address).where(Address.id == address_id)
    return db.execute(stmt).scalar_one_or_none()