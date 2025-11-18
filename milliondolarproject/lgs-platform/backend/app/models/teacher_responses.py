"""
Response Models for Teacher Analytics System
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClassOverviewResponse(BaseModel):
    """Response model for class overview dashboard"""
    class_id: str
    teacher_id: str
    student_count: int
    total_submissions: int
    topics_with_highest_struggle: List[Dict[str, Any]]
    los_with_dropping_performance: List[Dict[str, Any]]
    top_mistake_patterns: List[Dict[str, Any]]
    difficulty_distribution: Dict[str, Dict[str, Any]]
    seven_day_trend: Dict[str, Any]
    active_alerts: List[Dict[str, Any]]
    last_updated: float

class StudentProfileResponse(BaseModel):
    """Response model for student profile"""
    student_id: str
    total_questions_solved: int
    overall_accuracy: float
    strongest_topics: List[Dict[str, Any]]
    weakest_topics: List[Dict[str, Any]]
    repeatedly_failed_los: List[Dict[str, Any]]
    last_50_questions: List[Dict[str, Any]]
    time_analysis: Dict[str, Any]
    difficulty_trend: Dict[str, Any]
    lo_accuracy_percentages: Dict[str, float]
    active_alerts: List[Dict[str, Any]]
    last_updated: float

class LearningOutcomeAnalysisResponse(BaseModel):
    """Response model for LO deep analysis"""
    learning_outcome: str
    subject: str
    topic: str
    class_performance: Dict[str, float]
    worst_performers: List[str]
    top_performers: List[str]
    avg_accuracy: float
    difficulty_breakdown: Dict[str, Dict[str, int]]
    common_mistakes: List[str]
    recommended_interventions: List[str]

class VideoRecommendationResponse(BaseModel):
    """Response model for video recommendations"""
    video_id: str
    title: str
    subject: str
    topic: str
    learning_outcome: str
    difficulty: str
    duration_minutes: int
    description: str
    relevance_score: float

class MiniTestResponse(BaseModel):
    """Response model for mini-test generation"""
    test_id: str
    created_by: str
    assigned_to: List[str]
    learning_outcome: str
    question_count: int
    difficulty_recommendations: Dict[str, str]
    created_at: float
    instructions: str
    time_limit_minutes: int
    auto_grade: bool

class AlertResponse(BaseModel):
    """Response model for alerts"""
    alert_id: str
    alert_type: str
    student_id: str
    class_id: str
    subject: str
    topic: str
    learning_outcome: str
    severity: str
    message: str
    created_at: float
    recommended_actions: List[str]

class SubmissionRequest(BaseModel):
    """Request model for recording submissions"""
    submission_id: str
    student_id: str
    question_id: str
    subject: str
    topic: str
    learning_outcome: str
    difficulty: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    time_spent_seconds: int
    session_id: str
    timestamp: Optional[float] = None

class TeacherAccessRequest(BaseModel):
    """Request model for teacher access registration"""
    class_ids: List[str]
    subjects: List[str]
    is_homeroom: bool = False
    class_students: Optional[Dict[str, List[str]]] = None

class MiniTestRequest(BaseModel):
    """Request model for mini-test generation"""
    student_ids: List[str]
    learning_outcome: str
    question_count: int = 5

class VideoAssignmentRequest(BaseModel):
    """Request model for video assignment"""
    student_id: str

class AlertResolutionRequest(BaseModel):
    """Request model for alert resolution"""
    resolution_note: str