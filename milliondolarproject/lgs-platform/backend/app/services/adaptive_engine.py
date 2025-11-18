from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.exam import ExamInstance, ExamQuestion
from app.models.question import Question, QuestionOption
from app.schemas.exam import (
    ExamAnswerResponse,
    ExamFinishResponse,
)
from app.models.user import User


def start_exam(
    db: Session,
    student_id: int,
    mode: str,
    subject_id: Optional[int],
    topic_id: Optional[int],
    target_question_count: int,
) -> Tuple[ExamInstance, ExamQuestion]:
    """Start a new adaptive exam for a student.
    
    Raises:
        ValueError: If no questions are available for the requested criteria.
    """
    try:
        # 1) ExamInstance oluştur
        exam = ExamInstance(
            student_id=student_id,
            type="SYSTEM_ADAPTIVE",
            status="IN_PROGRESS",
        )
        db.add(exam)
        db.flush()

        # 2) İlk soruyu seç
        first_question = pick_question(
            db, student_id, subject_id, topic_id, difficulty="MEDIUM"
        )
        
        if not first_question:
            db.rollback()
            raise ValueError(
                f"No questions available for subject_id={subject_id}, "
                f"topic_id={topic_id}, difficulty=MEDIUM"
            )

        exam_question = ExamQuestion(
            exam_instance_id=exam.id,
            question_id=first_question.id,
            display_order=1,
            difficulty_at_assignment=first_question.difficulty,
            subject_id=first_question.subject_id,
        )
        db.add(exam_question)
        db.commit()
        db.refresh(exam)
        db.refresh(exam_question)

        return exam, exam_question
    except Exception as e:
        db.rollback()
        raise


def pick_question(
    db: Session,
    student_id: int,
    subject_id: Optional[int],
    topic_id: Optional[int],
    difficulty: str,
) -> Optional[Question]:
    """Pick a question based on filters.
    
    Returns:
        The Question object, or None if no match is found.
    """
    q = db.query(Question).filter(
        Question.is_active == True,
        Question.difficulty == difficulty,
    )
    if subject_id:
        q = q.filter(Question.subject_id == subject_id)
    if topic_id:
        q = q.filter(Question.topic_id == topic_id)

    # TODO: exclude questions already answered by student
    return q.order_by(Question.id.desc()).first()


def exam_question_to_schema(eq: ExamQuestion):
    """Convert ExamQuestion ORM object to schema dict."""
    return {
        "exam_question_id": eq.id,
        "question": {
            "id": eq.question.id,
            "stem_text": eq.question.stem_text,
            "difficulty": eq.question.difficulty,
        },
        "options": [
            {
                "id": opt.id,
                "option_label": opt.option_label,
                "text": opt.text,
            }
            for opt in eq.question.options
        ],
    }


def answer_question(
    db: Session,
    exam_id: int,
    student_id: int,
    exam_question_id: int,
    selected_option_id: Optional[int],
    time_spent_seconds: int,
) -> ExamAnswerResponse:
    """Record student's answer to a question."""
    try:
        is_correct = None
        if selected_option_id:
            option = db.query(QuestionOption).filter(
                QuestionOption.id == selected_option_id
            ).first()
            if option:
                is_correct = option.is_correct
        
        db.commit()

        # TODO: adaptif kısım henüz yok, next_question None
        return ExamAnswerResponse(
            is_correct=is_correct,
            next_question=None,
            exam_completed=False,
        )
    except Exception as e:
        db.rollback()
        raise


def finish_exam(db: Session, exam_id: int, student_id: int) -> ExamFinishResponse:
    """Finish an exam and calculate scores."""
    try:
        exam = db.query(ExamInstance).filter(
            ExamInstance.id == exam_id,
            ExamInstance.student_id == student_id,
        ).first()

        if not exam:
            raise ValueError(f"Exam {exam_id} not found for student {student_id}")

        # TODO: skor hesapla, estimated_lgs_score hesapla
        # şimdilik dummy değerler
        exam.status = "COMPLETED"
        db.commit()
        db.refresh(exam)

        return ExamFinishResponse(
            exam_instance_id=exam.id,
            total_score=0.0,
            estimated_lgs_score=None,
            completed_at=exam.updated_at,
        )
    except Exception as e:
        db.rollback()
        raise


def build_student_dashboard(db: Session, student_id: int):
    """Build dashboard data for a student (placeholder)."""
    # TODO: StudentTopicStats ve benzeri tablolardan gerçek veri çek
    return {
        "recent_questions_solved": 0,
        "recent_correct_ratio": 0.0,
        "subject_mastery": {},
        "weak_topics": [],
        "recommended_focus_topics": [],
    }
