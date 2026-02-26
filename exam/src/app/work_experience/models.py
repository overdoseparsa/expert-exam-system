from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Boolean,
    Numeric
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class WorkExperience(Base):
    __tablename__ = "work_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    currently_working = Column(Boolean, default=False)
    job_description = Column(Text, nullable=True)
    leaving_reason = Column(Text, nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)  # مبلغ به تومان یا ریال
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    # applicant = relationship("Applicant", back_populates="apli")