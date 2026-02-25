from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional
from enum import Enum
from decimal import Decimal


from enums import ConnectionTypeEnum , WorkScheduleEnum


class ApplicationDetailsBase(BaseModel):
    # ۱. نحوه آشنایی
    connection_type: ConnectionTypeEnum
    
    # ۲. مشخصات معرف
    referrer_name: Optional[str] = None
    referrer_relationship: Optional[str] = None
    referrer_phone: Optional[str] = Field(None, pattern=r'^\d{11}$')
    
    # ۳. بستگان در شرکت
    has_relatives_in_company: bool = False
    relative_name: Optional[str] = None
    relative_position: Optional[str] = None
    relative_relationship: Optional[str] = None
    
    # ۴. تاریخ آمادگی
    available_from_date: date
    
    # ۵. نوع ساعت کاری
    preferred_work_schedule: WorkScheduleEnum
    
    # ۶. حقوق درخواستی
    expected_salary: Decimal = Field(..., gt=0)
    salary_currency: str = "تومان"
    salary_period: str = "ماهانه"
    
    # ۷. وضعیت سلامتی
    has_health_issue: bool = False
    health_issue_description: Optional[str] = None
    
    has_disability: bool = False
    disability_description: Optional[str] = None
    
    # ۸. داروها
    takes_medication: bool = False
    medication_details: Optional[str] = None
    
    # ۹. سابقه کیفری
    has_criminal_record: bool = False
    criminal_record_details: Optional[str] = None
    
    # ۱۰. ورزش مورد علاقه
    favorite_sport: Optional[str] = None
    
    # ۱۱. سرویس
    has_transportation: bool = True
    willing_to_relocate: bool = False
    
    # ۱۲. سایر توضیحات
    other_comments: Optional[str] = None
    
    @validator('available_from_date')
    def validate_available_from_date(cls, v):
        if v < date.today():
            raise ValueError('تاریخ آمادگی نمی‌تواند از امروز عقب‌تر باشد')
        return v
    
    @validator('referrer_name', 'referrer_relationship', 'referrer_phone')
    def validate_referrer_fields(cls, v, values):
        if 'connection_type' in values and values['connection_type'] == ConnectionTypeEnum.REFERRAL:
            if v is None:
                raise ValueError('برای نحوه آشنایی "معرف", مشخصات معرف الزامی است')
        return v
    
    @validator('relative_name', 'relative_position', 'relative_relationship')
    def validate_relative_fields(cls, v, values):
        if 'has_relatives_in_company' in values and values['has_relatives_in_company']:
            if v is None:
                raise ValueError('در صورت داشتن بستگان در شرکت، مشخصات ایشان الزامی است')
        return v
    
    @validator('health_issue_description')
    def validate_health_issue(cls, v, values):
        if 'has_health_issue' in values and values['has_health_issue'] and not v:
            raise ValueError('در صورت داشتن مشکل سلامتی، توضیحات الزامی است')
        return v
    
    @validator('disability_description')
    def validate_disability(cls, v, values):
        if 'has_disability' in values and values['has_disability'] and not v:
            raise ValueError('در صورت داشتن معلولیت، توضیحات الزامی است')
        return v
    
    @validator('medication_details')
    def validate_medication(cls, v, values):
        if 'takes_medication' in values and values['takes_medication'] and not v:
            raise ValueError('در صورت مصرف دارو، توضیحات الزامی است')
        return v
    
    @validator('criminal_record_details')
    def validate_criminal_record(cls, v, values):
        if 'has_criminal_record' in values and values['has_criminal_record'] and not v:
            raise ValueError('در صورت داشتن سابقه کیفری، توضیحات الزامی است')
        return v


class ApplicationDetailsCreate(ApplicationDetailsBase):
    pass


class ApplicationDetailsUpdate(BaseModel):
    connection_type: Optional[ConnectionTypeEnum] = None
    referrer_name: Optional[str] = None
    referrer_relationship: Optional[str] = None
    referrer_phone: Optional[str] = Field(None, pattern=r'^\d{11}$')
    has_relatives_in_company: Optional[bool] = None
    relative_name: Optional[str] = None
    relative_position: Optional[str] = None
    relative_relationship: Optional[str] = None
    available_from_date: Optional[date] = None
    preferred_work_schedule: Optional[WorkScheduleEnum] = None
    expected_salary: Optional[Decimal] = Field(None, gt=0)
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    has_health_issue: Optional[bool] = None
    health_issue_description: Optional[str] = None
    has_disability: Optional[bool] = None
    disability_description: Optional[str] = None
    takes_medication: Optional[bool] = None
    medication_details: Optional[str] = None
    has_criminal_record: Optional[bool] = None
    criminal_record_details: Optional[str] = None
    favorite_sport: Optional[str] = None
    has_transportation: Optional[bool] = None
    willing_to_relocate: Optional[bool] = None
    other_comments: Optional[str] = None


class ApplicationDetailsResponse(ApplicationDetailsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DetailsSummaryResponse(BaseModel):
    connection_info: dict
    relatives_info: dict
    health_info: dict
    salary_info: dict
    record_info: dict
    available_from: str
    work_schedule: str
    favorite_sport: Optional[str]
    days_until_available: int