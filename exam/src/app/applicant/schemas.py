from pydantic import BaseModel ,Field ,ConfigDict
from typing import Optional
from .enums import (
    GenderEnum,
    BloodTypeEnum,
    MaritalStatusEnum,
)
from datetime import (date , datetime)

class ApplicantBase(BaseModel):
    """Base schema for Applicant with common fields"""
    id : Optional[int] 
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    family: Optional[str] = Field(None, min_length=3, max_length=200)
    national_code: str = Field(..., min_length=10, max_length=10, description="کد ملی 10 رقمی")
    id_number: str = Field(..., min_length=1, max_length=20, description="شماره شناسنامه")
    insurance_number: Optional[str] = Field(None, max_length=30, description="شماره بیمه")
    id_place: str = Field(..., min_length=2, max_length=100, description="محل صدور شناسنامه")
    father_name: str = Field(..., min_length=2, max_length=100, description="نام پدر")
    father_job: Optional[str] = Field(None, max_length=100, description="شغل پدر")
    birth_date: date = Field(..., description="تاریخ تولد")
    nationality: Optional[str] = Field("ایرانی", max_length=50, description="ملیت")
    birth_place: str = Field(..., min_length=2, max_length=100, description="محل تولد")
    religion: Optional[str] = Field("اسلام", max_length=50, description="دین")
    gender: GenderEnum = Field(..., description="جنسیت")
    blood_type: Optional[BloodTypeEnum] = Field(None, description="گروه خونی")
    marital_status: MaritalStatusEnum = Field(MaritalStatusEnum.SINGLE, description="وضعیت تأهل")
    marriage_date: Optional[date] = Field(None, description="تاریخ ازدواج")
    user_id: Optional[int] 
  


class ApplicantResponse(ApplicantBase):
    """Complete response schema for Applicant"""
    # فیلدهای اصلی از مدل
    id: int
    user_id: int
    name: str
    family: str
    national_code: str
    father_name: str
    id_number: str
    insurance_number: Optional[str] = None
    id_place: str
    father_job: Optional[str] = None
    birth_date: date
    nationality: Optional[str] = "ایرانی"
    birth_place: str
    religion: Optional[str] = "اسلام"
    gender: GenderEnum
    blood_type: Optional[BloodTypeEnum] = None
    marital_status: MaritalStatusEnum
    marriage_date: Optional[date] = None
    tracking_code: Optional[str] = None
    submitted_at: Optional[datetime] = None
    
    # اطلاعات کاربر (اختیاری - اگه نیاز داری)
    # user: Optional['UserResponse'] = None
    
    model_config = ConfigDict(from_attributes=True)

    @property
    def full_name(self) -> str:
        """Return full name (name + family)"""
        return f"{self.name} {self.family}"
class ApplicantUpdate(BaseModel):
    """Schema for updating an applicant (partial update)"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    family: Optional[str] = Field(None, min_length=3, max_length=200)
    id_number: Optional[str] = Field(None, min_length=1, max_length=20)
    insurance_number: Optional[str] = Field(None, max_length=30)
    id_place: Optional[str] = Field(None, min_length=2, max_length=100)
    father_name: Optional[str] = Field(None, min_length=2, max_length=100)
    father_job: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=50)
    birth_place: Optional[str] = Field(None, min_length=2, max_length=100)
    religion: Optional[str] = Field(None, max_length=50)
    gender: Optional[GenderEnum] = None
    blood_type: Optional[BloodTypeEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    marriage_date: Optional[date] = None

class ApplicantCreate(ApplicantBase):
    """Schema for creating a new applicant"""
    
    def validate_national_code(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError('کدملی باید 10 رقم باشد')
        return v