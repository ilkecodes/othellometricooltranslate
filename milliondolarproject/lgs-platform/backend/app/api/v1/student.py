from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .deps import get_current_student, get_db
from app.schemas.user import UserRead
from app.schemas.stats import StudentDashboardResponse
from app.services import adaptive_engine

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def student_me(current_student=Depends(get_current_student)):
    """Get current student's profile."""
    return current_student


@router.get("/dashboard", response_model=StudentDashboardResponse)
async def student_dashboard(
    current_student=Depends(get_current_student), db: Session = Depends(get_db)
):
    """Get student's dashboard with performance stats."""
    dashboard_data = adaptive_engine.build_student_dashboard(
        db=db, student_id=current_student.id
    )
    return dashboard_data
