# models.py for skills
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import SkillLevelEnum




class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    skill_name = Column(String(100), nullable=False)
    skill_level = Column(Enum(SkillLevelEnum), nullable=False)
    years_of_experience = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    # applicant = relationship("Applicant", back_populates="skills")
    user = relationship("User", backref="Skill")
    