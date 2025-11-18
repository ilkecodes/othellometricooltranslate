from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    units = relationship("Unit", back_populates="subject")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)

    subject = relationship("Subject", back_populates="units")
    topics = relationship("Topic", back_populates="unit")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)

    unit = relationship("Unit", back_populates="topics")
    learning_outcomes = relationship("LearningOutcome", back_populates="topic")


class LearningOutcome(Base):
    __tablename__ = "learning_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    code = Column(String, nullable=True)
    description = Column(String, nullable=False)

    topic = relationship("Topic", back_populates="learning_outcomes")
