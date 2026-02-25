# schemas.py for work_experience
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


class WorkExperienceBase(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: Optional[date] = None
    currently_working: bool = False
    job_description: Optional[str] = None
    leaving_reason: Optional[str] = None
    salary: Optional[Decimal] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد')
        return v
    
    @validator('currently_working')
    def validate_currently_working(cls, v, values):
        if v and 'end_date' in values and values['end_date']:
            raise ValueError('اگر هم‌اکنون مشغول به کار هستید، نباید تاریخ پایان داشته باشد')
        return v


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currently_working: Optional[bool] = None
    job_description: Optional[str] = None
    leaving_reason: Optional[str] = None
    salary: Optional[Decimal] = None


class WorkExperienceResponse(WorkExperienceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkExperienceBulkCreate(BaseModel):
    experiences: List[WorkExperienceCreate]


class TotalExperienceResponse(BaseModel):
    total_months: int
    years: int
    months: int
    formatted: str