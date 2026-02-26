# models.py for job_applications
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    score = Column(Float, nullable=False)
    
    priority = Column(Integer, nullable=False) 
    
    # وضعیت
    status = Column(String(50), default="pending")  # pending, reviewed, accepted, rejected, withdrawn
    
    # تاریخ‌ها
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # روابط
    # job = relationship("JobDB" , backref='job_application')
    user = relationship("User",backref="job_application")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='unique_user_job'),
    )
    
    # def validate_priority(self, key, priority):
    #     if priority not in [1, 2, 3]:
    #         raise ValueError("اولویت باید ۱، ۲ یا ۳ باشد")
    #     return priority
    
    # def validate_score(self, key, score):
    #     valid_scores = [5.1, 5.2, 5.3, 5.4]
    #     if score not in valid_scores:
    #         raise ValueError(f"امتیاز باید یکی از {valid_scores} باشد")