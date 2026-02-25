# schemas.py for jobs_information
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    posted_date: date
    deadline: Optional[date] = None
    description: str
    requirements: Optional[str] = None
    salary: Optional[str] = None
    is_active: bool = True
    job_type: Optional[str] = None
    
    @validator('deadline')
    def validate_deadline(cls, v, values):
        if v and 'posted_date' in values and v < values['posted_date']:
            raise ValueError('مهلت درخواست نمی‌تواند قبل از تاریخ انتشار باشد')
        return v


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[date] = None
    deadline: Optional[date] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary: Optional[str] = None
    is_active: Optional[bool] = None
    job_type: Optional[str] = None


class JobResponse(JobBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminJobAssignmentBase(BaseModel):
    admin_id: int
    job_id: int


class AdminJobAssignmentCreate(AdminJobAssignmentBase):
    pass


class AdminJobAssignmentResponse(AdminJobAssignmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobWithAssignmentsResponse(JobResponse):
    admin_assignments: List[AdminJobAssignmentResponse] = []