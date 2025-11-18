from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QuestionOptionBase(BaseModel):
    id: int
    option_label: str
    text: str

    model_config = {"from_attributes": True}


class QuestionBase(BaseModel):
    id: int
    stem_text: str
    difficulty: str

    model_config = {"from_attributes": True}


class ExamQuestionOut(BaseModel):
    exam_question_id: int
    question: QuestionBase
    options: List[QuestionOptionBase]


class ExamStartRequest(BaseModel):
    mode: str  # ADAPTIVE_TOPIC_PRACTICE | FULL_LGS_SIM ...
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    target_question_count: int = 20


class ExamStartResponse(BaseModel):
    exam_instance_id: int
    first_question: ExamQuestionOut


class ExamAnswerRequest(BaseModel):
    exam_question_id: int
    selected_option_id: Optional[int] = None
    time_spent_seconds: int


class ExamAnswerResponse(BaseModel):
    is_correct: Optional[bool]
    next_question: Optional[ExamQuestionOut] = None
    exam_completed: bool = False


class ExamFinishResponse(BaseModel):
    exam_instance_id: int
    total_score: float
    estimated_lgs_score: Optional[float]
    completed_at: datetime

    model_config = {"from_attributes": True}

class ExamBase(BaseModel):
    title: str
    scheduled_at: Optional[datetime] = None
    created_by: Optional[str] = None

class ExamCreate(ExamBase):
    pass

class ExamRead(ExamBase):
    id: int

    model_config = {"from_attributes": True}
