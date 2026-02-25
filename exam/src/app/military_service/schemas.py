# schemas.py for military_service
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

from .enums import MilitaryExemptionTypeEnum


class MilitaryServiceBase(BaseModel):
    service_start: Optional[date] = None
    service_end: Optional[date] = None
    service_duration: Optional[str] = None
    shortage_duration: Optional[str] = None
    extra_duration: Optional[str] = None
    service_org: Optional[str] = None
    service_city: Optional[str] = None
    exemption_type: Optional[MilitaryExemptionTypeEnum] = None
    exemption_reason: Optional[str] = None


class MilitaryServiceCreate(MilitaryServiceBase):
    pass


class MilitaryServiceUpdate(BaseModel):
    service_start: Optional[date] = None
    service_end: Optional[date] = None
    service_duration: Optional[str] = None
    shortage_duration: Optional[str] = None
    extra_duration: Optional[str] = None
    service_org: Optional[str] = None
    service_city: Optional[str] = None
    exemption_type: Optional[MilitaryExemptionTypeEnum] = None
    exemption_reason: Optional[str] = None


class MilitaryServiceResponse(MilitaryServiceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True