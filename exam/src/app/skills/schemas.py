# schemas.py for skills
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from .enums import SkillLevelEnum




class SkillBase(BaseModel):
    skill_name: str
    skill_level: SkillLevelEnum
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    skill_name: Optional[str] = None
    skill_level: Optional[SkillLevelEnum] = None
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    description: Optional[str] = None


class SkillResponse(SkillBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SkillBulkCreate(BaseModel):
    skills: List[SkillCreate]