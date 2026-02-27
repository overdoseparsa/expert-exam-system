# models.py for application_details
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    Enum,
    Boolean,
    Text,
    Numeric
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import ConnectionTypeEnum , WorkScheduleEnum

from auth.models import User


class ApplicationDetails(Base):
    __tablename__ = "application_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    connection_type = Column(Enum(ConnectionTypeEnum), nullable=False)
    
    referrer_name = Column(String(200), nullable=True)
    referrer_relationship = Column(String(100), nullable=True)  # نسبت
    referrer_phone = Column(String(11), nullable=True)
    
    has_relatives_in_company = Column(Boolean, default=False)
    relative_name = Column(String(200), nullable=True)
    relative_position = Column(String(100), nullable=True)
    relative_relationship = Column(String(100), nullable=True)
    
    available_from_date = Column(Date, nullable=False)
    
    preferred_work_schedule = Column(Enum(WorkScheduleEnum), nullable=False)
    
    expected_salary = Column(Numeric(12, 2), nullable=False)
    salary_currency = Column(String(10), default="تومان")
    salary_period = Column(String(20), default="ماهانه")  
    
    has_health_issue = Column(Boolean, default=False)
    health_issue_description = Column(Text, nullable=True)
    
    has_disability = Column(Boolean, default=False)
    disability_description = Column(Text, nullable=True)
    
    takes_medication = Column(Boolean, default=False)
    medication_details = Column(Text, nullable=True)
    
    has_criminal_record = Column(Boolean, default=False)
    criminal_record_details = Column(Text, nullable=True)
    
    favorite_sport = Column(String(100), nullable=True)
    
    has_transportation = Column(Boolean, default=True) 
    willing_to_relocate = Column(Boolean, default=False)  
    other_comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", backref="application_details")


