
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

class AdminJobAssignment(Base):
    __tablename__ = "admin_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )
    job_id = Column(
        Integer, 
        ForeignKey('jobs.id', ondelete="CASCADE"),  # Fixed: using table name 'jobs'
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

    job = relationship("JobDB")