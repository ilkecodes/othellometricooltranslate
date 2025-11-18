#!/usr/bin/env python3
"""
Simplified FastAPI backend for testing teacher dashboard
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import random

app = FastAPI(title="LGS Platform - Simple Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for teacher dashboard
MOCK_TEACHER_DASHBOARD = {
    "teacher_id": "teacher_001",
    "summary_metrics": {
        "total_students": 25,
        "total_classes": 3,
        "questions_this_week": 128,
        "avg_accuracy_week": 0.76,
        "critical_alerts_count": 2
    },
    "top_struggling_topics": [
        {
            "subject": "Matematik",
            "topic": "Rasyonel Sayılar",
            "student_count": 8
        },
        {
            "subject": "Fen Bilimleri", 
            "topic": "Hücre Bölünmesi",
            "student_count": 5
        },
        {
            "subject": "Matematik",
            "topic": "Cebirsel İfadeler", 
            "student_count": 3
        }
    ],
    "recent_critical_alerts": [
        {
            "alert_id": "alert_001",
            "alert_type": "low_accuracy",
            "student_id": "student_002",
            "message": "Matematik performansında düşüş",
            "severity": "critical",
            "created_at": time.time() - 3600
        },
        {
            "alert_id": "alert_002", 
            "alert_type": "activity_drop",
            "student_id": "student_005",
            "message": "Son 3 günde aktivite yok",
            "severity": "high",
            "created_at": time.time() - 7200
        }
    ],
    "last_updated": time.time()
}

MOCK_STUDENT_DASHBOARD = {
    "student_id": "student_001",
    "performance_summary": {
        "total_questions_solved": 245,
        "accuracy_rate": 0.78,
        "current_streak": 5,
        "weekly_goal_progress": 0.65
    },
    "subject_performance": [
        {
            "subject": "Matematik",
            "accuracy": 0.82,
            "questions_solved": 98,
            "time_spent_minutes": 420
        },
        {
            "subject": "Fen Bilimleri",
            "accuracy": 0.74,
            "questions_solved": 87,
            "time_spent_minutes": 380
        },
        {
            "subject": "Türkçe",
            "accuracy": 0.79,
            "questions_solved": 60,
            "time_spent_minutes": 240
        }
    ],
    "recent_achievements": [
        {
            "achievement": "Matematik Ustası",
            "description": "50 matematik sorusunu doğru çözdün",
            "earned_at": time.time() - 86400
        }
    ],
    "recommendations": [
        {
            "type": "topic_practice",
            "subject": "Matematik",
            "topic": "Rasyonel Sayılar",
            "reason": "Bu konuda gelişim gösterebilirsin"
        }
    ]
}

@app.get("/")
def health_check():
    return {"status": "ok", "message": "LGS Platform Backend is running"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/v1/teachers/dashboard-summary")
def get_teacher_dashboard_summary():
    """Get teacher dashboard summary with mock data"""
    # Add some randomness to make it feel more real
    dashboard = MOCK_TEACHER_DASHBOARD.copy()
    dashboard["summary_metrics"]["questions_this_week"] = random.randint(100, 200)
    dashboard["summary_metrics"]["avg_accuracy_week"] = round(random.uniform(0.6, 0.9), 2)
    dashboard["last_updated"] = time.time()
    
    return {
        "status": "success",
        "data": dashboard
    }

@app.get("/api/v1/student/dashboard")
def get_student_dashboard():
    """Get student dashboard with mock data"""
    dashboard = MOCK_STUDENT_DASHBOARD.copy()
    dashboard["performance_summary"]["total_questions_solved"] = random.randint(200, 300)
    dashboard["performance_summary"]["accuracy_rate"] = round(random.uniform(0.7, 0.9), 2)
    
    return {
        "status": "success", 
        "data": dashboard
    }

@app.get("/api/v1/exams/bundles")
def get_exam_bundles():
    """Get available exam bundles"""
    return {
        "bundles": [
            {
                "id": "lgs-karma-v2",
                "title": "LGS Karma Deneme v2",
                "description": "Kapsamlı LGS hazırlık testi - Matematik, Fen Bilimleri, Türkçe",
                "version": "2.0",
                "total_questions": 20,
                "subjects": ["Matematik", "Fen Bilimleri", "Türkçe"],
                "distribution": {
                    "Matematik": 8,
                    "Fen Bilimleri": 7,
                    "Türkçe": 5
                },
                "source_stats": {
                    "MEB": 15,
                    "ÖSYM": 5
                },
                "difficulty_stats": {
                    "KOLAY": 6,
                    "ORTA": 10,
                    "ZOR": 4
                },
                "generated_date": "2025-11-18",
                "available": True
            },
            {
                "id": "matematik-ozel",
                "title": "Matematik Özel Deneme",
                "description": "Sadece matematik konularına odaklanan yoğun deneme",
                "version": "1.0", 
                "total_questions": 15,
                "subjects": ["Matematik"],
                "distribution": {
                    "Matematik": 15
                },
                "source_stats": {
                    "MEB": 10,
                    "ÖSYM": 5
                },
                "difficulty_stats": {
                    "KOLAY": 4,
                    "ORTA": 7,
                    "ZOR": 4
                },
                "generated_date": "2025-11-18",
                "available": True
            }
        ]
    }

@app.post("/api/v1/exams/bundles/{bundle_id}/sessions")
def create_exam_session(bundle_id: str):
    """Create a new exam session"""
    return {
        "session_id": f"session_{random.randint(10000, 99999)}",
        "bundle_id": bundle_id,
        "user_id": 1,
        "started_at": time.time(),
        "status": "active",
        "time_limit_minutes": 90,
        "instructions": "Bu sınav 20 sorudan oluşmaktadır. Her soru için tek doğru cevap vardır. Süreniz 90 dakikadır."
    }

@app.get("/api/v1/exams/bundles/{bundle_id}/questions")
def get_bundle_questions(bundle_id: str):
    """Get questions for an exam bundle"""
    # Mock questions for the exam
    mock_questions = []
    question_templates = [
        # Matematik soruları
        {
            "stem": "Bir sayının 3 katının 5 fazlası 23 ise, bu sayı kaçtır?",
            "options": [
                {"key": "A", "text": "4"},
                {"key": "B", "text": "5"}, 
                {"key": "C", "text": "6"},
                {"key": "D", "text": "7"}
            ],
            "correct_answer": "C",
            "subject": "Matematik",
            "explanation": "3x + 5 = 23 → 3x = 18 → x = 6"
        },
        {
            "stem": "0.25 × 16 işleminin sonucu kaçtır?",
            "options": [
                {"key": "A", "text": "3"},
                {"key": "B", "text": "4"},
                {"key": "C", "text": "5"},
                {"key": "D", "text": "6"}
            ],
            "correct_answer": "B",
            "subject": "Matematik",
            "explanation": "0.25 = 1/4, 1/4 × 16 = 4"
        },
        # Fen Bilimleri soruları
        {
            "stem": "Mitoz bölünme sonucunda oluşan hücre sayısı kaçtır?",
            "options": [
                {"key": "A", "text": "1"},
                {"key": "B", "text": "2"},
                {"key": "C", "text": "3"},
                {"key": "D", "text": "4"}
            ],
            "correct_answer": "B",
            "subject": "Fen Bilimleri",
            "explanation": "Mitoz bölünme sonucunda 1 ana hücreden 2 yavru hücre oluşur"
        },
        {
            "stem": "Işığın hızı yaklaşık olarak saniyede kaç km'dir?",
            "options": [
                {"key": "A", "text": "200.000 km"},
                {"key": "B", "text": "250.000 km"},
                {"key": "C", "text": "300.000 km"},
                {"key": "D", "text": "350.000 km"}
            ],
            "correct_answer": "C",
            "subject": "Fen Bilimleri",
            "explanation": "Işık hızı yaklaşık 300.000 km/sn'dir"
        },
        # Türkçe soruları
        {
            "stem": "Aşağıdaki cümlelerin hangisinde özne yoktur?",
            "options": [
                {"key": "A", "text": "Yarın okula gideceğim."},
                {"key": "B", "text": "Kar yağıyor."},
                {"key": "C", "text": "Kitap okudum."},
                {"key": "D", "text": "Ali koşuyor."}
            ],
            "correct_answer": "A",
            "subject": "Türkçe", 
            "explanation": "1. tekil şahıs (-m) eki özneyi karşılar, ayrı bir özne yoktur"
        }
    ]
    
    # Generate questions based on bundle
    question_count = 15 if bundle_id == "matematik-ozel" else 20
    
    for i in range(question_count):
        template = question_templates[i % len(question_templates)]
        question = {
            "id": f"q_{bundle_id}_{i+1:03d}",
            "question_number": i + 1,
            "stem": template["stem"],
            "options": template["options"],
            "correct_answer": template["correct_answer"],
            "subject": template["subject"],
            "difficulty_level": random.choice(["KOLAY", "ORTA", "ZOR"]),
            "kazanim_code": f"K.{random.randint(1,8)}.{random.randint(1,4)}.{random.randint(1,3)}",
            "stamp": f"stamp_{i+1}",
            "source": random.choice(["MEB", "ÖSYM"]),
            "confidence": round(random.uniform(0.8, 1.0), 2),
            "explanation": template["explanation"]
        }
        mock_questions.append(question)
    
    return {
        "questions": mock_questions,
        "total_count": len(mock_questions)
    }

@app.post("/api/v1/exams/sessions/{session_id}/answers")
def submit_answer(session_id: str, answer_data: dict = None):
    """Submit an answer for a question"""
    # Mock answer submission
    return {
        "status": "success",
        "message": "Answer recorded",
        "question_id": "q_001",
        "timestamp": time.time()
    }

@app.post("/api/v1/exams/sessions/{session_id}/complete")
def complete_exam(session_id: str):
    """Complete an exam session"""
    # Mock completion with results
    return {
        "status": "completed",
        "session_id": session_id,
        "score": random.randint(60, 95),
        "correct_answers": random.randint(12, 19),
        "total_questions": 20,
        "completion_time_minutes": random.randint(45, 90),
        "accuracy_rate": round(random.uniform(0.6, 0.95), 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)