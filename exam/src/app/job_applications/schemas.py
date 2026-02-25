# schemas.py for job_applications
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict
from enums import JobApplicationStatus





class JobApplicationBase(BaseModel):
    job_id: int
    score: float = Field(..., ge=5.1, le=5.4)
    priority: int = Field(..., ge=1, le=3)
    
    @validator('score')
    def validate_score(cls, v):
        valid_scores = [5.1, 5.2, 5.3, 5.4]
        if v not in valid_scores:
            raise ValueError(f'امتیاز باید یکی از {valid_scores} باشد')
        return v


class SingleJobApplication(JobApplicationBase):
    pass


class JobApplicationBatch(BaseModel):
    applications: List[SingleJobApplication]
    
    @validator('applications')
    def validate_count(cls, v):
        if len(v) != 3:
            raise ValueError('باید دقیقاً ۳ شغل انتخاب کنید')
        
        # بررسی تکراری نبودن job_id
        job_ids = [app.job_id for app in v]
        if len(job_ids) != len(set(job_ids)):
            raise ValueError('شغل‌ها نباید تکراری باشند')
        
        # بررسی تکراری نبودن priority
        priorities = [app.priority for app in v]
        if len(priorities) != len(set(priorities)):
            raise ValueError('اولویت‌ها نباید تکراری باشند')
        
        return v


class JobApplicationUpdate(BaseModel):
    status: Optional[JobApplicationStatus] = None
    score: Optional[float] = None
    priority: Optional[int] = Field(None, ge=1, le=3)


class JobApplicationResponse(JobApplicationBase):
    id: int
    user_id: int
    status: str
    applied_at: datetime
    updated_at: Optional[datetime] = None
    
    # فیلدهای اضافه از Job
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


class AvailableJobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    posted_date: datetime
    deadline: Optional[datetime] = None
    job_type: Optional[str] = None
    salary: Optional[str] = None


class ApplicationsSummaryResponse(BaseModel):
    total_applications: int
    status_distribution: Dict[str, int]
    average_score: float
    last_application: Optional[datetime] = None
    can_apply_more: bool