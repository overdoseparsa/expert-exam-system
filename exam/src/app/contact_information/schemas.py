# schemas.py for contact_information
from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import Address




class ContactCreate(BaseModel):
    phone: str
    emergency_phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ContactUpdate(BaseModel):
    phone: Optional[str] = None
    emergency_phone: Optional[str] = None
    email: Optional[EmailStr] = None


class AddressCreate(BaseModel):
    province: str
    city: str
    address: str
    housing_status: Address.HousingStatusEnum
    postal_code: Optional[str] = None
    ownership_duration: Optional[int] = None