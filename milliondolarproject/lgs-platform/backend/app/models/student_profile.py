from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    grade_level = Column(Integer, nullable=True)
    total_questions_solved = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    last_exam_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="student_profile")
