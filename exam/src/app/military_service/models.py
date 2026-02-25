from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    Enum,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import MilitaryExemptionTypeEnum


class MilitaryService(Base):
    __tablename__ = "military_services"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    service_start = Column(Date, nullable=True)
    service_end = Column(Date, nullable=True)
    service_duration = Column(String(50), nullable=True)
    shortage_duration = Column(String(50), nullable=True)
    extra_duration = Column(String(50), nullable=True)
    service_org = Column(String(200), nullable=True)
    service_city = Column(String(100), nullable=True)
    
    exemption_type = Column(Enum(MilitaryExemptionTypeEnum), nullable=True)
    exemption_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
