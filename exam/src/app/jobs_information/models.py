# models.py for jobs_information
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


class Factory:
    """کلاس کمکی برای فیلد company"""
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200), nullable=False)  # شرکت
    location = Column(String(100), nullable=False)  # موقعیت مکانی


class JobDB(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # اطلاعات اصلی
    title = Column(String(200), nullable=False)  # عنوان شغل
    company = Column(String(200), nullable=False)  # شرکت
    location = Column(String(100), nullable=False)  # موقعیت مکانی
    
    # تاریخ‌ها
    posted_date = Column(Date, nullable=False)  # تاریخ انتشار
    deadline = Column(Date, nullable=True)  # مهلت درخواست
    
    # جزئیات
    description = Column(Text, nullable=False)  # توضیحات شغل
    requirements = Column(Text, nullable=True)  # شرایط مورد نیاز
    salary = Column(String(100), nullable=True)  # حقوق
    
    # وضعیت
    is_active = Column(Boolean, default=True)  # آیا فعال است؟
    job_type = Column(String(50), nullable=True)  # نوع شغل (تمام وقت، پاره وقت، دورکاری)
    
    # زمان‌سنج
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    admin_assignments = relationship("AdminJobAssignment", back_populates="job")
