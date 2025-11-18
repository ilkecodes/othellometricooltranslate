from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.models.question import Question, QuestionOption
from app.models.curriculum import Topic, Subject

router = APIRouter()

@router.get('/')
async def list_questions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all questions with their options for exam taking."""
    questions = db.query(Question).limit(100).all()
    
    result = []
    for q in questions:
        # Get topic name
        topic = db.query(Topic).filter(Topic.id == q.topic_id).first()
        topic_name = topic.name if topic else "Unknown Topic"
        
        # Get subject name
        subject = db.query(Subject).filter(Subject.id == q.subject_id).first()
        subject_name = subject.name if subject else "Unknown Subject"
        
        # Get options
        options = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).all()
        
        result.append({
            "id": q.id,
            "stem": q.stem_text,
            "topic_id": q.topic_id,
            "topic_name": topic_name,
            "subject_id": q.subject_id,
            "subject_name": subject_name,
            "options": [
                {
                    "id": opt.id,
                    "label": opt.option_label,
                    "text": opt.text,
                    "is_correct": opt.is_correct
                }
                for opt in options
            ]
        })
    
    return result

@router.get('/exam/full')
async def get_full_exam(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all available questions for exam organized by subject."""
    # Get all questions (10 Sosyal + 8 Din + 107 Türkçe)
    questions = db.query(Question).order_by(Question.subject_id, Question.id).all()
    
    result = []
    for q in questions:
        # Get topic name
        topic = db.query(Topic).filter(Topic.id == q.topic_id).first()
        topic_name = topic.name if topic else "Unknown Topic"
        
        # Get subject name
        subject = db.query(Subject).filter(Subject.id == q.subject_id).first()
        subject_name = subject.name if subject else "Unknown Subject"
        
        # Get options
        options = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).all()
        
        result.append({
            "id": q.id,
            "stem": q.stem_text,
            "topic_id": q.topic_id,
            "topic_name": topic_name,
            "subject_id": q.subject_id,
            "subject_name": subject_name,
            "options": [
                {
                    "id": opt.id,
                    "label": opt.option_label,
                    "text": opt.text,
                    "is_correct": opt.is_correct
                }
                for opt in options
            ]
        })
    
    return result

@router.post('/')
async def create_question(payload: dict):
    return {"id":2, **payload}
