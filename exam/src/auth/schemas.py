from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from .enums import RoleEnum

class UserBase(BaseModel):
    mobile: constr(min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = RoleEnum.USER
    is_active: bool = True
    is_verified: bool = False
    is_verified_phone: bool = False


class UserCreate(BaseModel):
    mobile: constr(min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: constr(min_length=8)

    def validate_mobile(cls, v):
        if not v.startswith('09') or len(v) != 11:
            raise ValueError("شماره موبایل باید با 09 شروع شود و 11 رقم باشد")
        return v
    
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("رمز عبور باید حداقل 6 کاراکتر باشد")
        return v

class UserUpdate(BaseModel):
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    mobile: str
    password: str

class UserResponse(BaseModel):
    id: int
    mobile: str
    email: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    role : Optional[str] = None
    is_verified_phone : Optional[bool] = None 

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


