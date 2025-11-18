from fastapi import APIRouter
from app.api.v1 import admin_exams

router = APIRouter()

@router.get('/')
async def admin_index():
    return {"status":"ok"}

# Include admin exam routes
router.include_router(admin_exams.router, prefix="/exams")
