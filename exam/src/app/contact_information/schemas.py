# schemas.py for contact_information
from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import Address
from .enums import HousingStatusEnum
from  datetime import datetime

class ContactInfoBase(BaseModel):
    phone: str
    emergency_phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ContactCreate(ContactInfoBase): ...

class ContactInfoUpdate(BaseModel):
    phone: Optional[str] = None
    emergency_phone: Optional[str] = None
    email: Optional[EmailStr] = None




class ContactInfoResponse(ContactInfoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class AddressBase(BaseModel):
    province: str
    city: str
    address: str
    postal_code: Optional[str] = None
    housing_status: HousingStatusEnum
    ownership_duration: Optional[int] = None


class AddressCreate(AddressBase): ...

class AddressUpdate(BaseModel):
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    housing_status: Optional[HousingStatusEnum] = None
    ownership_duration: Optional[int] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
