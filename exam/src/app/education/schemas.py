# schemas.py for education
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum
from .enums import (
    EducationDegreeEnum,
    EducationStudyStatusEnum,
    
)


class EducationBase(BaseModel):
    degree: EducationDegreeEnum
    field: str
    university: str
    average: Optional[float] = None
    start_year: int = Field(..., ge=1300, le=1500)
    end_year: Optional[int] = Field(None, ge=1300, le=1500)
    study_status: EducationStudyStatusEnum
    description: Optional[str] = None
    
    @validator('end_year')
    def validate_end_year(cls, v, values):
        if v and 'start_year' in values and v < values['start_year']:
            raise ValueError('سال پایان نمی‌تواند قبل از سال شروع باشد')
        return v


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    degree: Optional[EducationDegreeEnum] = None
    field: Optional[str] = None
    university: Optional[str] = None
    average: Optional[float] = None
    start_year: Optional[int] = Field(None, ge=1300, le=1500)
    end_year: Optional[int] = Field(None, ge=1300, le=1500)
    study_status: Optional[EducationStudyStatusEnum] = None
    description: Optional[str] = None


class EducationResponse(EducationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EducationBulkCreate(BaseModel):
    educations: List[EducationCreate]