from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    license_plan = Column(String, default="basic")
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="school")
