# services.py for contact_information
from sqlalchemy.orm import Session
from .models import ContactInfo , Address
from .selectors import get_contact_by_user_id , get_address_by_id


def create_contact(
    db: Session,
    user_id: int,
    phone: str,
    emergency_phone: str | None = None,
    email: str | None = None,
) -> ContactInfo:

    existing = get_contact_by_user_id(db, user_id)
    if existing:
        raise ValueError("Contact info already exists for this user")

    contact = ContactInfo(
        user_id=user_id,
        phone=phone,
        emergency_phone=emergency_phone,
        email=email,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(
    db: Session,
    user_id: int,
    **kwargs,
) -> ContactInfo:

    contact = get_contact_by_user_id(db, user_id)
    if not contact:
        raise ValueError("Contact info not found")

    for key, value in kwargs.items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact




def create_address(
    db: Session,
    user_id: int,
    province: str,
    city: str,
    address: str,
    housing_status,
    postal_code: str | None = None,
    ownership_duration: int | None = None,
) -> Address:

    new_address = Address(
        user_id=user_id,
        province=province,
        city=city,
        address=address,
        postal_code=postal_code,
        housing_status=housing_status,
        ownership_duration=ownership_duration,
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


def delete_address(db: Session, address_id: int) -> None:
    address = get_address_by_id(db, address_id)
    if not address:
        raise ValueError("Address not found")

    db.delete(address)
    db.commit()