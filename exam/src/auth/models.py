from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from datetime import datetime

class AbstractModel(Base):
    """
    Common base model for all tables.
    """

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )


class User(AbstractModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # TODO: better be uuid
    mobile = Column(String(11), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(125), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_verified_phone = Column(
        Boolean,
        default=False,
        nullable=True,
    )

    # Relationship to Applicant model (defined elsewhere)
    # applicant = relationship(
    #     "Applicant",
    #     back_populates="user",
    #     uselist=False,
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self) -> str:
        return f"<User id={self.id} mobile={self.mobile!r}>"




class UserLog(AbstractModel):
    
    __tablename__ = "user_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  
    changes = Column(JSON, nullable=True) 
    ip_address = Column(String(45), nullable=True) 
    user_agent = Column(String(255), nullable=True)  
    status = Column(String(20), nullable=False) 
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
  
    user = relationship("User", backref="logs")
    
    def __repr__(self):
        return f"<UserLog id={self.id} user_id={self.user_id} action={self.action}>"
