from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship

from app.models.base import Base


class ExamInstance(Base):
    __tablename__ = "exam_instances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_template_id = Column(Integer, nullable=True)
    type = Column(String, nullable=False)   # SYSTEM_ADAPTIVE | TEACHER_ASSIGNED
    status = Column(String, nullable=False) # NOT_STARTED | IN_PROGRESS | COMPLETED
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Numeric, nullable=True)
    estimated_lgs_score = Column(Numeric, nullable=True)

    student = relationship("User")
    exam_questions = relationship("ExamQuestion", back_populates="exam_instance")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_instance_id = Column(
        Integer, ForeignKey("exam_instances.id"), nullable=False
    )
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    display_order = Column(Integer, nullable=False)
    difficulty_at_assignment = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    exam_instance = relationship("ExamInstance", back_populates="exam_questions")
    question = relationship("Question")
