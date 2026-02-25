# schemas.py for language_skills
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from .enums import LanguageEnum , ProficiencyEnum




class LanguageSkillBase(BaseModel):
    language: LanguageEnum
    other_language: Optional[str] = None
    reading: ProficiencyEnum
    writing: ProficiencyEnum
    speaking: ProficiencyEnum
    listening: ProficiencyEnum
    
    @validator('other_language')
    def validate_other_language(cls, v, values):
        if 'language' in values and values['language'] == LanguageEnum.OTHER and not v:
            raise ValueError('برای زبان دیگر، نام زبان را مشخص کنید')
        return v


class LanguageSkillCreate(LanguageSkillBase):
    pass


class LanguageSkillUpdate(BaseModel):
    language: Optional[LanguageEnum] = None
    other_language: Optional[str] = None
    reading: Optional[ProficiencyEnum] = None
    writing: Optional[ProficiencyEnum] = None
    speaking: Optional[ProficiencyEnum] = None
    listening: Optional[ProficiencyEnum] = None


class LanguageSkillResponse(LanguageSkillBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LanguageSkillBulkCreate(BaseModel):
    skills: List[LanguageSkillCreate]


class ProficiencySummaryResponse(BaseModel):
    native: List[Dict[str, Any]]
    advanced: List[Dict[str, Any]]
    intermediate: List[Dict[str, Any]]
    basic: List[Dict[str, Any]]