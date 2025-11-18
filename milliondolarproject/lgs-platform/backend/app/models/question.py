from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    main_learning_outcome_id = Column(
        Integer, ForeignKey("learning_outcomes.id"), nullable=False
    )
    difficulty = Column(String, nullable=False)  # EASY|MEDIUM|HARD|VERY_HARD
    stem_text = Column(Text, nullable=False)
    has_image = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    source_type = Column(String, default="LGS_STYLE")
    estimated_time_seconds = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    options = relationship("QuestionOption", back_populates="question")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_label = Column(String, nullable=False)  # A,B,C,D,E
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    question = relationship("Question", back_populates="options")
