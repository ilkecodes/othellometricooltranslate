from typing import Dict, List
from pydantic import BaseModel


class TopicStat(BaseModel):
    topic_id: int
    topic_name: str
    mastery_score: float
    total_attempts: int


class StudentDashboardResponse(BaseModel):
    recent_questions_solved: int
    recent_correct_ratio: float
    subject_mastery: Dict[str, float]  # {"MATH": 0.72, ...}
    weak_topics: List[TopicStat]
    recommended_focus_topics: List[TopicStat]

    model_config = {"from_attributes": True}
