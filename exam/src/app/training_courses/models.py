# models.py for training_courses
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class TrainingCourse(Base):
    __tablename__ = "training_courses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200), nullable=False)  # عنوان دوره
    institute = Column(String(200), nullable=False)  # مؤسسه/محل برگزاری
    duration = Column(String(50), nullable=False)  # مدت دوره (مثال: 80 ساعت)
    start_date = Column(Date, nullable=False)  # تاریخ شروع
    end_date = Column(Date, nullable=True)  # تاریخ پایان
    
    has_certificate = Column(Boolean, default=False)  # اخذ گواهینامه
    certificate_id = Column(String(100), nullable=True)  # شماره گواهینامه
    certificate_date = Column(Date, nullable=True)  # تاریخ اخذ گواهینامه
    
    description = Column(Text, nullable=True)  # توضیحات دوره
    skills_learned = Column(Text, nullable=True)  # مهارت‌های کسب شده
    instructor = Column(String(100), nullable=True)  # نام مدرس
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    applicant = relationship("Applicant", back_populates="training_courses")