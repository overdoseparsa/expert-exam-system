# models.py for language_skills
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import LanguageEnum , ProficiencyEnum





class LanguageSkill(Base):
    __tablename__ = "language_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    language = Column(Enum(LanguageEnum), nullable=False)
    other_language = Column(String(100), nullable=True)
    reading = Column(Enum(ProficiencyEnum), nullable=False)
    writing = Column(Enum(ProficiencyEnum), nullable=False)
    speaking = Column(Enum(ProficiencyEnum), nullable=False)
    listening = Column(Enum(ProficiencyEnum), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    applicant = relationship("Applicant", back_populates="language_skills")