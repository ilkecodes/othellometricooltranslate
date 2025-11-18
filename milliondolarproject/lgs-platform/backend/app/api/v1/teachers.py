"""
Teacher API Endpoints - Comprehensive Student Performance Analytics
Provides all teacher dashboard views and analytics capabilities
"""

from typing import List, Dict, Any, Optional
import time

try:
    from fastapi import APIRouter, Depends, HTTPException
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    Depends = None
    HTTPException = None

from app.core.teacher_analytics import (
    TeacherAnalyticsEngine, 
    QuestionSubmission,
    VideoRecommendation,
    ClassAlert,
    AlertType,
    PerformanceTrend,
    get_teacher_analytics
)

from app.models.teacher_responses import (
    ClassOverviewResponse,
    StudentProfileResponse,
    LearningOutcomeAnalysisResponse,
    VideoRecommendationResponse,
    MiniTestResponse,
    AlertResponse,
    SubmissionRequest,
    TeacherAccessRequest,
    MiniTestRequest,
    VideoAssignmentRequest,
    AlertResolutionRequest
)

# Mock auth dependency for standalone operation
def get_current_user():
    return {"user_id": "teacher_001", "role": "teacher"}

if not FASTAPI_AVAILABLE:
    # Provide standalone functions for testing
    def create_mock_router():
        return None
    router = create_mock_router()
else:
    router = APIRouter(tags=["teachers"])

# Define all route handlers only if FastAPI is available
if FASTAPI_AVAILABLE:
    @router.post("/classes/{class_id}/submissions")
    async def record_student_submission(
    class_id: str,
    submission_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Record a student's question submission for real-time analysis"""
    
    teacher_id = current_user["user_id"]
    
    # Create submission object
    submission = QuestionSubmission(
        submission_id=submission_data["submission_id"],
        student_id=submission_data["student_id"],
        question_id=submission_data["question_id"],
        class_id=class_id,
        subject=submission_data["subject"],
        topic=submission_data["topic"],
        learning_outcome=submission_data["learning_outcome"],
        difficulty=submission_data["difficulty"],
        selected_answer=submission_data["selected_answer"],
        correct_answer=submission_data["correct_answer"],
        is_correct=submission_data["is_correct"],
        time_spent_seconds=submission_data["time_spent_seconds"],
        timestamp=submission_data.get("timestamp", time.time()),
        session_id=submission_data["session_id"],
        teacher_id=teacher_id
    )
    
    # Record and analyze submission
    try:
        analytics.record_question_submission(submission)
        
        return {
            "status": "success",
            "message": "Submission recorded and analyzed",
            "submission_id": submission.submission_id,
            "instant_analysis": {
                "topic_performance": "calculated",
                "lo_performance": "calculated",
                "alerts_checked": "completed"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record submission: {str(e)}")

@router.get("/classes/{class_id}/overview")
async def get_class_overview(
    class_id: str,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get comprehensive class overview dashboard"""
    
    teacher_id = current_user["user_id"]
    
    try:
        overview = analytics.get_class_overview(teacher_id, class_id)
        
        return {
            "status": "success",
            "data": overview,
            "generated_at": time.time()
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate overview: {str(e)}")

@router.get("/students/{student_id}/profile")
async def get_student_profile(
    student_id: str,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get detailed student performance profile"""
    
    teacher_id = current_user["user_id"]
    
    try:
        profile = analytics.get_student_profile(teacher_id, student_id)
        
        return {
            "status": "success",
            "data": profile,
            "generated_at": time.time()
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate profile: {str(e)}")

@router.get("/learning-outcomes/{learning_outcome}/analysis")
async def get_lo_deep_analysis(
    learning_outcome: str,
    subject: str,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get deep analysis for a specific Learning Outcome"""
    
    teacher_id = current_user["user_id"]
    
    try:
        analysis = analytics.get_lo_deep_analysis(teacher_id, learning_outcome, subject)
        
        return {
            "status": "success",
            "data": {
                "learning_outcome": analysis.learning_outcome,
                "subject": analysis.subject,
                "topic": analysis.topic,
                "class_performance": analysis.class_performance,
                "worst_performers": analysis.worst_performers,
                "top_performers": analysis.top_performers,
                "avg_accuracy": analysis.avg_accuracy,
                "difficulty_breakdown": analysis.difficulty_breakdown,
                "common_mistakes": analysis.common_mistakes,
                "recommended_interventions": analysis.recommended_interventions
            },
            "generated_at": time.time()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate LO analysis: {str(e)}")

@router.get("/students/{student_id}/video-recommendations")
async def get_video_recommendations(
    student_id: str,
    limit: int = 5,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get video recommendations for struggling student"""
    
    teacher_id = current_user["user_id"]
    
    # Validate access
    if not analytics._validate_teacher_student_access(teacher_id, student_id):
        raise HTTPException(status_code=403, detail="Access denied to this student")
    
    try:
        recommendations = analytics.generate_video_recommendations(student_id, limit)
        
        return {
            "status": "success",
            "student_id": student_id,
            "recommendations": [
                {
                    "video_id": rec.video_id,
                    "title": rec.title,
                    "subject": rec.subject,
                    "topic": rec.topic,
                    "learning_outcome": rec.learning_outcome,
                    "difficulty": rec.difficulty,
                    "duration_minutes": rec.duration_minutes,
                    "description": rec.description,
                    "relevance_score": rec.relevance_score
                } for rec in recommendations
            ],
            "count": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/videos/{video_id}/assign")
async def assign_video_to_student(
    video_id: str,
    student_id: str,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Teacher assigns a video to a student"""
    
    teacher_id = current_user["user_id"]
    
    try:
        success = analytics.assign_video_to_student(teacher_id, video_id, student_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Video {video_id} assigned to student {student_id}",
                "assigned_by": teacher_id,
                "assigned_at": time.time()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to assign video")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment failed: {str(e)}")

@router.post("/mini-tests/generate")
async def generate_mini_test(
    test_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Generate LO-aligned mini-test for struggling students"""
    
    teacher_id = current_user["user_id"]
    student_ids = test_request["student_ids"]
    learning_outcome = test_request["learning_outcome"]
    question_count = test_request.get("question_count", 5)
    
    try:
        mini_test = analytics.generate_mini_test(
            teacher_id, student_ids, learning_outcome, question_count
        )
        
        return {
            "status": "success",
            "mini_test": mini_test,
            "message": f"Mini-test generated for {len(student_ids)} students"
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

@router.get("/alerts")
async def get_active_alerts(
    class_id: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get active alerts for teacher's classes"""
    
    teacher_id = current_user["user_id"]
    
    try:
        # Get teacher's accessible students
        teacher_students = analytics._get_all_teacher_students(teacher_id)
        
        # Filter alerts
        active_alerts = [
            alert for alert in analytics.active_alerts 
            if alert.is_active and alert.student_id in teacher_students
        ]
        
        # Apply filters
        if class_id:
            active_alerts = [alert for alert in active_alerts if alert.class_id == class_id]
        
        if severity:
            active_alerts = [alert for alert in active_alerts if alert.severity == severity]
        
        # Sort by severity and creation time
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        active_alerts.sort(
            key=lambda x: (severity_order.get(x.severity, 0), x.created_at), 
            reverse=True
        )
        
        return {
            "status": "success",
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "student_id": alert.student_id,
                    "class_id": alert.class_id,
                    "subject": alert.subject,
                    "topic": alert.topic,
                    "learning_outcome": alert.learning_outcome,
                    "severity": alert.severity,
                    "message": alert.message,
                    "created_at": alert.created_at,
                    "recommended_actions": alert.recommended_actions
                } for alert in active_alerts
            ],
            "total_count": len(active_alerts),
            "critical_count": len([a for a in active_alerts if a.severity == "critical"]),
            "high_count": len([a for a in active_alerts if a.severity == "high"])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_note: str,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Mark an alert as resolved"""
    
    teacher_id = current_user["user_id"]
    
    # Find and resolve alert
    alert = next((a for a in analytics.active_alerts if a.alert_id == alert_id), None)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Validate teacher has access to this student
    if not analytics._validate_teacher_student_access(teacher_id, alert.student_id):
        raise HTTPException(status_code=403, detail="Access denied to this alert")
    
    try:
        alert.is_active = False
        
        return {
            "status": "success",
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "resolved_by": teacher_id,
            "resolved_at": time.time(),
            "resolution_note": resolution_note
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.get("/classes/{class_id}/performance-trends")
async def get_class_performance_trends(
    class_id: str,
    days: int = 30,
    subject: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get detailed performance trends for the class"""
    
    teacher_id = current_user["user_id"]
    
    # Validate access
    if not analytics._validate_teacher_access(teacher_id, class_id):
        raise HTTPException(status_code=403, detail="Access denied to this class")
    
    try:
        # Get class submissions for the period
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        student_ids = analytics.class_rosters[teacher_id][class_id]
        
        submissions = [
            s for s in analytics.submissions 
            if s.student_id in student_ids 
            and s.class_id == class_id 
            and s.timestamp >= cutoff_time
        ]
        
        if subject:
            submissions = [s for s in submissions if s.subject == subject]
        
        if not submissions:
            return {
                "status": "success",
                "data": {
                    "message": "No data available for the specified period",
                    "period_days": days,
                    "class_id": class_id
                }
            }
        
        # Calculate daily trends
        daily_trends = analytics._calculate_class_7day_trend(submissions)
        
        # Calculate subject breakdown
        subject_performance = {}
        for subj in set(s.subject for s in submissions):
            subj_submissions = [s for s in submissions if s.subject == subj]
            accuracy = sum(s.is_correct for s in subj_submissions) / len(subj_submissions)
            subject_performance[subj] = {
                "accuracy": accuracy,
                "total_questions": len(subj_submissions),
                "improvement_areas": analytics._calculate_topic_struggles(subj_submissions)[:3]
            }
        
        return {
            "status": "success",
            "data": {
                "period_days": days,
                "class_id": class_id,
                "subject_filter": subject,
                "total_submissions": len(submissions),
                "overall_trends": daily_trends,
                "subject_performance": subject_performance,
                "generated_at": time.time()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate trends: {str(e)}")

@router.post("/register-access")
async def register_teacher_access(
    access_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Register teacher's class and subject access permissions"""
    
    teacher_id = current_user["user_id"]
    class_ids = access_data["class_ids"]
    subjects = access_data["subjects"]
    is_homeroom = access_data.get("is_homeroom", False)
    
    try:
        analytics.register_teacher_access(teacher_id, class_ids, subjects, is_homeroom)
        
        # Add students to classes if provided
        if "class_students" in access_data:
            for class_id, student_ids in access_data["class_students"].items():
                analytics.add_students_to_class(teacher_id, class_id, student_ids)
        
        return {
            "status": "success",
            "message": "Teacher access registered successfully",
            "teacher_id": teacher_id,
            "class_ids": class_ids,
            "subjects": subjects,
            "is_homeroom": is_homeroom,
            "registered_at": time.time()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register access: {str(e)}")

@router.get("/dashboard-summary")
async def get_teacher_dashboard_summary(
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Get summary dashboard for teacher showing key metrics"""
    
    teacher_id = current_user["user_id"]
    
    try:
        # Get teacher's classes and students
        teacher_students = analytics._get_all_teacher_students(teacher_id)
        
        if not teacher_students:
            return {
                "status": "success",
                "data": {
                    "message": "No classes assigned",
                    "setup_required": True
                }
            }
        
        # Get recent submissions (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        recent_submissions = [
            s for s in analytics.submissions 
            if s.student_id in teacher_students and s.timestamp >= cutoff_time
        ]
        
        # Calculate summary metrics
        total_students = len(teacher_students)
        total_classes = len(analytics.class_rosters.get(teacher_id, {}))
        total_questions_week = len(recent_submissions)
        avg_accuracy_week = (
            sum(s.is_correct for s in recent_submissions) / len(recent_submissions)
            if recent_submissions else 0
        )
        
        # Critical alerts
        critical_alerts = [
            alert for alert in analytics.active_alerts 
            if alert.is_active 
            and alert.student_id in teacher_students 
            and alert.severity in ["critical", "high"]
        ]
        
        # Top struggling topics
        struggling_topics = analytics._calculate_topic_struggles(recent_submissions)[:3]
        
        return {
            "status": "success",
            "data": {
                "teacher_id": teacher_id,
                "summary_metrics": {
                    "total_students": total_students,
                    "total_classes": total_classes,
                    "questions_this_week": total_questions_week,
                    "avg_accuracy_week": avg_accuracy_week,
                    "critical_alerts_count": len(critical_alerts)
                },
                "top_struggling_topics": struggling_topics,
                "recent_critical_alerts": [
                    {
                        "student_id": alert.student_id,
                        "message": alert.message,
                        "severity": alert.severity,
                        "created_at": alert.created_at
                    } for alert in critical_alerts[:5]
                ],
                "quick_actions": [
                    "Review critical alerts",
                    "Generate video recommendations",
                    "Create mini-tests for struggling topics",
                    "Check class performance trends"
                ],
                "last_updated": time.time()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

# Add sample data population for demonstration
@router.post("/demo/populate-sample-data")
async def populate_sample_data(
    current_user: Dict = Depends(get_current_user),
    analytics: TeacherAnalyticsEngine = Depends(get_teacher_analytics)
):
    """Populate sample data for demonstration (dev only)"""
    
    teacher_id = current_user["user_id"]
    
    try:
        # Register teacher access
        analytics.register_teacher_access(
            teacher_id, 
            ["class_8A", "class_8B"], 
            ["Matematik", "Fen Bilimleri"], 
            is_homeroom=True
        )
        
        # Add sample students
        analytics.add_students_to_class(teacher_id, "class_8A", ["student_001", "student_002", "student_003"])
        analytics.add_students_to_class(teacher_id, "class_8B", ["student_004", "student_005", "student_006"])
        
        # Add sample video library
        sample_videos = [
            VideoRecommendation(
                video_id="vid_001",
                title="Rasyonel Sayılar - Temel Kavramlar",
                subject="Matematik",
                topic="Rasyonel Sayılar",
                learning_outcome="Rasyonel sayıları tanır ve örnekler verir",
                difficulty="KOLAY",
                duration_minutes=15,
                description="Rasyonel sayıların temel özelliklerini açıklayan video",
                relevance_score=0.85,
                assigned_to=[]
            ),
            VideoRecommendation(
                video_id="vid_002",
                title="Hücre Bölünmesi ve Mitoz",
                subject="Fen Bilimleri",
                topic="Hücre Bölünmesi",
                learning_outcome="Mitoz bölünme evrelerini sıralar",
                difficulty="ORTA",
                duration_minutes=20,
                description="Mitoz bölünme sürecini detaylı anlatan video",
                relevance_score=0.90,
                assigned_to=[]
            )
        ]
        
        analytics.video_library.extend(sample_videos)
        
        # Generate sample submissions with various performance patterns
        import random
        
        sample_submissions = []
        current_time = time.time()
        
        topics = [
            ("Matematik", "Rasyonel Sayılar", "Rasyonel sayıları tanır"),
            ("Matematik", "Cebirsel İfadeler", "Cebirsel ifadeleri sadeleştirir"),
            ("Fen Bilimleri", "Hücre Bölünmesi", "Mitoz bölünme evrelerini sıralar"),
            ("Fen Bilimleri", "Kalıtım", "Kalıtım kanunlarını açıklar")
        ]
        
        students = ["student_001", "student_002", "student_003", "student_004", "student_005", "student_006"]
        
        for i in range(200):  # Generate 200 sample submissions
            student_id = random.choice(students)
            subject, topic, lo = random.choice(topics)
            class_id = "class_8A" if student_id in ["student_001", "student_002", "student_003"] else "class_8B"
            
            # Create performance patterns for different students
            if student_id == "student_001":  # High performer
                is_correct = random.random() < 0.85
            elif student_id == "student_002":  # Struggling in math
                is_correct = random.random() < 0.4 if subject == "Matematik" else random.random() < 0.75
            elif student_id == "student_003":  # Declining performance
                is_correct = random.random() < max(0.3, 0.8 - (i / 200) * 0.5)
            else:  # Average performers
                is_correct = random.random() < 0.65
            
            submission = QuestionSubmission(
                submission_id=f"sub_{i:03d}_{student_id}",
                student_id=student_id,
                question_id=f"q_{random.randint(1000, 9999)}",
                class_id=class_id,
                subject=subject,
                topic=topic,
                learning_outcome=lo,
                difficulty=random.choice(["KOLAY", "ORTA", "ZOR"]),
                selected_answer=random.choice(["A", "B", "C", "D"]),
                correct_answer=random.choice(["A", "B", "C", "D"]),
                is_correct=is_correct,
                time_spent_seconds=random.randint(30, 300),
                timestamp=current_time - random.randint(0, 14 * 24 * 60 * 60),  # Last 14 days
                session_id=f"session_{random.randint(100, 999)}",
                teacher_id=teacher_id
            )
            
            sample_submissions.append(submission)
        
        # Process all submissions
        for submission in sample_submissions:
            analytics.record_question_submission(submission)
        
        return {
            "status": "success",
            "message": "Sample data populated successfully",
            "data": {
                "submissions_created": len(sample_submissions),
                "students_added": len(students),
                "classes_added": 2,
                "videos_added": len(sample_videos),
                "alerts_generated": len([a for a in analytics.active_alerts if a.is_active])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to populate data: {str(e)}")