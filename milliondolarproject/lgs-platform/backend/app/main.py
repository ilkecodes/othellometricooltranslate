from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, student, teacher, admin, curriculum, questions, exams, generation, teachers

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod'da daraltılabilir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(student.router, prefix=f"{settings.API_V1_STR}/student", tags=["student"])
app.include_router(teacher.router, prefix=f"{settings.API_V1_STR}/teacher", tags=["teacher"])
app.include_router(teachers.router, prefix=f"{settings.API_V1_STR}/teachers", tags=["teachers"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(curriculum.router, prefix=f"{settings.API_V1_STR}/curriculum", tags=["curriculum"])
app.include_router(questions.router, prefix=f"{settings.API_V1_STR}/questions", tags=["questions"])
app.include_router(exams.router, prefix=f"{settings.API_V1_STR}/exams", tags=["exams"])
app.include_router(generation.router, prefix=f"{settings.API_V1_STR}/generation", tags=["generation"])


@app.get("/")
def health_check():
    return {"status": "ok"}
