# schemas.py for training_courses
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import re


class TrainingCourseBase(BaseModel):
    title: str
    institute: str
    duration: str
    start_date: date
    end_date: Optional[date] = None
    has_certificate: bool = False
    certificate_id: Optional[str] = None
    certificate_date: Optional[date] = None
    description: Optional[str] = None
    skills_learned: Optional[str] = None
    instructor: Optional[str] = None
    
    # @validator('end_date')
    # def validate_end_date(cls, v, values):
    #     if v and 'start_date' in values and v < values['start_date']:
    #         raise ValueError('تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد')
    #     return v
    
    # @validator('certificate_date')
    # def validate_certificate_date(cls, v, values):
    #     if v and 'end_date' in values and values['end_date'] and v < values['end_date']:
    #         raise ValueError('تاریخ گواهینامه نمی‌تواند قبل از تاریخ پایان دوره باشد')
    #     return v
    
    # @validator('certificate_id')
    # def validate_certificate(cls, v, values):
    #     if 'has_certificate' in values and values['has_certificate']:
    #         if not v:
    #             raise ValueError('برای دوره‌ای که گواهینامه دارد، شماره گواهینامه الزامی است')
    #         if 'certificate_date' not in values or not values['certificate_date']:
    #             raise ValueError('برای دوره‌ای که گواهینامه دارد، تاریخ گواهینامه الزامی است')
    #     return v


class TrainingCourseCreate(TrainingCourseBase):
    pass


class TrainingCourseUpdate(BaseModel):
    title: Optional[str] = None
    institute: Optional[str] = None
    duration: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    has_certificate: Optional[bool] = None
    certificate_id: Optional[str] = None
    certificate_date: Optional[date] = None
    description: Optional[str] = None
    skills_learned: Optional[str] = None
    instructor: Optional[str] = None


class TrainingCourseResponse(TrainingCourseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TrainingCourseBulkCreate(BaseModel):
    courses: List[TrainingCourseCreate]


class TrainingSummaryResponse(BaseModel):
    total_courses: int
    courses_with_certificate: int
    certificate_percentage: float
    total_hours: int
    average_hours_per_course: float
    courses_by_year: Dict[int, int]
    institutes: List[str]