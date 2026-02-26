from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import EducationDegreeEnum , EducationStudyStatusEnum


class Education(Base):
    __tablename__ = "educations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    degree = Column(Enum(EducationDegreeEnum), nullable=False)
    field = Column(String(200), nullable=False)
    university = Column(String(200), nullable=False)
    average = Column(Float, nullable=True)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)
    study_status = Column(Enum(EducationStudyStatusEnum), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    user = relationship("User", backref="educations")