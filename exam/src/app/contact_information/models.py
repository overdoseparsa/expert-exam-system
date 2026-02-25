from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .enums import HousingStatusEnum
from database import Base


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

class ContactInfo(AbstractModel):
    __tablename__ = "contact_infos"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    phone = Column(String(11), nullable=False)
    emergency_phone = Column(String(11), nullable=True)
    email = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="contact_info")


class Address(AbstractModel):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=True)


    housing_status = Column(
        Enum(HousingStatusEnum, name="housing_status_enum"),
        nullable=False
    )

    ownership_duration = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="addresses")