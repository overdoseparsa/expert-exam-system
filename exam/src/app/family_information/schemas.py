# schemas.py for family_information
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from .enums import (
    ChildGenderEnum,
    SiblingTypeEnum,
    SiblingMaritalStatusEnum,
    
)

# ========== Base Models ==========
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True


# ========== Spouse Schema ==========
class SpouseBase(BaseSchema):
    full_name: str
    job: Optional[str] = None


class SpouseCreate(SpouseBase):
    pass


class SpouseUpdate(BaseSchema):
    full_name: Optional[str] = None
    job: Optional[str] = None


class SpouseResponse(SpouseBase):
    id: int
    user_id: int  # تغییر از applicant_id به user_id
    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Child Schema ==========
class ChildBase(BaseSchema):
    full_name: str
    age: int
    gender: ChildGenderEnum


class ChildCreate(ChildBase):
    pass


class ChildUpdate(BaseSchema):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[ChildGenderEnum] = None


class ChildResponse(ChildBase):
    id: int
    user_id: int  # تغییر از applicant_id به user_id
    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Sibling Schema ==========
class SiblingBase(BaseSchema):
    full_name: str
    age: int
    sibling_type: SiblingTypeEnum
    marital_status: SiblingMaritalStatusEnum
    job: Optional[str] = None


class SiblingCreate(SiblingBase):
    pass


class SiblingUpdate(BaseSchema):
    full_name: Optional[str] = None
    age: Optional[int] = None
    sibling_type: Optional[SiblingTypeEnum] = None
    marital_status: Optional[SiblingMaritalStatusEnum] = None
    job: Optional[str] = None


class SiblingResponse(SiblingBase):
    id: int
    user_id: int  # تغییر از applicant_id به user_id
    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Statistics Schema ==========
class ChildStatisticsResponse(BaseSchema):
    total: int
    male: int
    female: int
    average_age: float


class SiblingStatisticsResponse(BaseSchema):
    total: int
    brothers: int
    sisters: int
    single: int
    married: int
    average_age: float


# ========== Family Complete Response ==========
class FamilyInfoResponse(BaseSchema):
    """برای برگرداندن کامل اطلاعات خانواده"""
    spouse: Optional[SpouseResponse] = None
    children: List[ChildResponse] = []
    siblings: List[SiblingResponse] = []
    
    # آمار
    children_count: int = 0
    siblings_count: int = 0
    
    class Config:
        from_attributes = True