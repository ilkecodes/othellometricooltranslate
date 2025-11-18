from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Stats(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # point to exam_instances table
    exam_id = Column(Integer, ForeignKey("exam_instances.id"), nullable=True)
    score = Column(Float, nullable=True)
    attempts = Column(Integer, default=0)

    user = relationship("User", backref="stats")
    exam = relationship("ExamInstance", backref="stats")
