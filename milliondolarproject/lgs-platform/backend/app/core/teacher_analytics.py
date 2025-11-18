#!/usr/bin/env python3
"""
Teacher Analytics System - Comprehensive Student Performance Analysis
Tracks every question, identifies weaknesses, and generates actionable insights for teachers
"""

import json
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from enum import Enum
import logging

class AlertType(str, Enum):
    LOW_ACCURACY = "low_accuracy"
    CONSECUTIVE_ERRORS = "consecutive_errors"
    ACTIVITY_DROP = "activity_drop"
    TREND_DECLINE = "trend_decline"

class PerformanceTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"

@dataclass
class QuestionSubmission:
    """Individual question submission record"""
    submission_id: str
    student_id: str
    question_id: str
    class_id: str
    subject: str
    topic: str
    learning_outcome: str
    difficulty: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    time_spent_seconds: int
    timestamp: float
    session_id: str
    teacher_id: str

@dataclass
class StudentTopicPerformance:
    """Student performance on a specific topic"""
    student_id: str
    topic: str
    subject: str
    total_attempts: int
    correct_attempts: int
    accuracy_rate: float
    avg_time_seconds: float
    last_attempt: float
    trend: PerformanceTrend
    struggling_los: List[str]
    mastered_los: List[str]

@dataclass
class LearningOutcomeAnalysis:
    """Deep analysis of student performance on a specific LO"""
    learning_outcome: str
    subject: str
    topic: str
    class_performance: Dict[str, float]  # student_id -> accuracy
    worst_performers: List[str]  # student_ids
    top_performers: List[str]  # student_ids
    avg_accuracy: float
    difficulty_breakdown: Dict[str, Dict[str, int]]  # difficulty -> {correct, total}
    common_mistakes: List[str]
    recommended_interventions: List[str]

@dataclass
class ClassAlert:
    """Alert for teachers about student performance issues"""
    alert_id: str
    alert_type: AlertType
    student_id: str
    class_id: str
    subject: str
    topic: str
    learning_outcome: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    created_at: float
    is_active: bool
    recommended_actions: List[str]

@dataclass
class VideoRecommendation:
    """Video recommendation for struggling students"""
    video_id: str
    title: str
    subject: str
    topic: str
    learning_outcome: str
    difficulty: str
    duration_minutes: int
    description: str
    relevance_score: float
    assigned_to: List[str]  # student_ids

class TeacherAnalyticsEngine:
    """Core analytics engine for teacher insights"""
    
    def __init__(self):
        self.submissions: List[QuestionSubmission] = []
        self.class_rosters: Dict[str, Dict[str, List[str]]] = {}  # teacher_id -> {class_id: [student_ids]}
        self.subject_assignments: Dict[str, List[str]] = {}  # teacher_id -> [subjects]
        self.homeroom_teachers: Dict[str, str] = {}  # class_id -> teacher_id
        self.active_alerts: List[ClassAlert] = []
        self.video_library: List[VideoRecommendation] = []
        
        # Performance caches for real-time updates
        self.student_performance_cache: Dict[str, Dict] = {}
        self.topic_performance_cache: Dict[str, Dict] = {}
        self.lo_analysis_cache: Dict[str, LearningOutcomeAnalysis] = {}
    
    def register_teacher_access(self, teacher_id: str, class_ids: List[str], 
                               subjects: List[str], is_homeroom: bool = False):
        """Register teacher access permissions"""
        self.class_rosters[teacher_id] = {}
        for class_id in class_ids:
            self.class_rosters[teacher_id][class_id] = []
            if is_homeroom:
                self.homeroom_teachers[class_id] = teacher_id
        
        self.subject_assignments[teacher_id] = subjects
    
    def add_students_to_class(self, teacher_id: str, class_id: str, student_ids: List[str]):
        """Add students to a teacher's class"""
        if teacher_id in self.class_rosters and class_id in self.class_rosters[teacher_id]:
            self.class_rosters[teacher_id][class_id].extend(student_ids)
    
    def record_question_submission(self, submission: QuestionSubmission):
        """Record and analyze a question submission in real-time"""
        self.submissions.append(submission)
        
        # Perform instant analysis
        self._instant_analysis(submission)
        
        # Update caches
        self._update_performance_cache(submission)
        
        # Check for alerts
        self._check_alert_conditions(submission)
        
        print(f"📝 Recorded submission: Student {submission.student_id} - {submission.subject}/{submission.topic}")
    
    def _instant_analysis(self, submission: QuestionSubmission):
        """Perform instant analysis when a question is submitted"""
        student_id = submission.student_id
        topic = submission.topic
        lo = submission.learning_outcome
        
        # Get student's performance on this topic
        topic_performance = self._calculate_topic_performance(student_id, topic, submission.subject)
        
        # Get classmate comparison
        class_performance = self._get_class_topic_performance(submission.class_id, topic, submission.subject)
        
        # Update LO performance
        lo_performance = self._calculate_lo_performance(student_id, lo)
        
        print(f"   📊 Instant Analysis:")
        print(f"      Topic accuracy: {topic_performance.accuracy_rate:.1%}")
        print(f"      LO accuracy: {lo_performance:.1%}")
        print(f"      Class avg: {statistics.mean(class_performance.values()) if class_performance else 0:.1%}")
    
    def _update_performance_cache(self, submission: QuestionSubmission):
        """Update real-time performance caches"""
        student_id = submission.student_id
        
        if student_id not in self.student_performance_cache:
            self.student_performance_cache[student_id] = {
                'topics': {},
                'los': {},
                'recent_submissions': [],
                'last_updated': time.time()
            }
        
        cache = self.student_performance_cache[student_id]
        
        # Update recent submissions (keep last 50)
        cache['recent_submissions'].append(submission)
        cache['recent_submissions'] = cache['recent_submissions'][-50:]
        
        # Update topic performance
        topic_key = f"{submission.subject}:{submission.topic}"
        if topic_key not in cache['topics']:
            cache['topics'][topic_key] = {'correct': 0, 'total': 0, 'time_spent': []}
        
        cache['topics'][topic_key]['total'] += 1
        if submission.is_correct:
            cache['topics'][topic_key]['correct'] += 1
        cache['topics'][topic_key]['time_spent'].append(submission.time_spent_seconds)
        
        # Update LO performance
        lo_key = f"{submission.subject}:{submission.learning_outcome}"
        if lo_key not in cache['los']:
            cache['los'][lo_key] = {'correct': 0, 'total': 0}
        
        cache['los'][lo_key]['total'] += 1
        if submission.is_correct:
            cache['los'][lo_key]['correct'] += 1
        
        cache['last_updated'] = time.time()
    
    def _check_alert_conditions(self, submission: QuestionSubmission):
        """Check if submission triggers any alerts"""
        student_id = submission.student_id
        
        # Check LO accuracy < 50%
        lo_accuracy = self._calculate_lo_performance(student_id, submission.learning_outcome)
        if lo_accuracy < 0.5 and self._get_lo_attempt_count(student_id, submission.learning_outcome) >= 5:
            self._create_alert(
                AlertType.LOW_ACCURACY,
                submission,
                "critical",
                f"Student accuracy on {submission.learning_outcome} is {lo_accuracy:.1%} (below 50%)"
            )
        
        # Check consecutive errors on same LO
        consecutive_errors = self._count_consecutive_lo_errors(student_id, submission.learning_outcome)
        if consecutive_errors >= 3:
            self._create_alert(
                AlertType.CONSECUTIVE_ERRORS,
                submission,
                "high",
                f"Student has {consecutive_errors} consecutive errors on {submission.learning_outcome}"
            )
        
        # Check 7-day trend decline
        trend_decline = self._calculate_7day_trend_decline(student_id, submission.subject)
        if trend_decline >= 0.2:  # 20% decline
            self._create_alert(
                AlertType.TREND_DECLINE,
                submission,
                "medium",
                f"Student performance declined {trend_decline:.1%} over 7 days in {submission.subject}"
            )
    
    def _create_alert(self, alert_type: AlertType, submission: QuestionSubmission, 
                     severity: str, message: str):
        """Create a new alert"""
        alert = ClassAlert(
            alert_id=f"alert_{int(time.time())}_{submission.student_id}",
            alert_type=alert_type,
            student_id=submission.student_id,
            class_id=submission.class_id,
            subject=submission.subject,
            topic=submission.topic,
            learning_outcome=submission.learning_outcome,
            severity=severity,
            message=message,
            created_at=time.time(),
            is_active=True,
            recommended_actions=self._generate_alert_recommendations(alert_type, submission)
        )
        
        self.active_alerts.append(alert)
        print(f"🚨 ALERT: {alert.message}")
    
    def _generate_alert_recommendations(self, alert_type: AlertType, 
                                      submission: QuestionSubmission) -> List[str]:
        """Generate recommended actions for alerts"""
        recommendations = []
        
        if alert_type == AlertType.LOW_ACCURACY:
            recommendations.extend([
                f"Assign remedial videos for {submission.learning_outcome}",
                "Create mini-test focusing on fundamental concepts",
                "Schedule one-on-one review session",
                "Check prerequisite knowledge gaps"
            ])
        
        elif alert_type == AlertType.CONSECUTIVE_ERRORS:
            recommendations.extend([
                "Immediate intervention required",
                f"Review {submission.topic} concepts with student",
                "Assign easier difficulty questions to rebuild confidence",
                "Consider peer tutoring"
            ])
        
        elif alert_type == AlertType.TREND_DECLINE:
            recommendations.extend([
                "Monitor student engagement levels",
                "Check for external factors affecting performance",
                "Adjust difficulty level temporarily",
                "Increase feedback frequency"
            ])
        
        return recommendations
    
    # === TEACHER DASHBOARD VIEWS ===
    
    def get_class_overview(self, teacher_id: str, class_id: str) -> Dict[str, Any]:
        """Generate Class Overview dashboard"""
        
        # Validate teacher access
        if not self._validate_teacher_access(teacher_id, class_id):
            raise PermissionError("Teacher does not have access to this class")
        
        student_ids = self.class_rosters[teacher_id][class_id]
        class_submissions = [s for s in self.submissions 
                           if s.student_id in student_ids and s.class_id == class_id]
        
        # Topics with highest struggle
        topic_struggles = self._calculate_topic_struggles(class_submissions)
        
        # LOs with dropping performance
        dropping_los = self._find_dropping_los(class_submissions)
        
        # Top frequent mistake patterns
        mistake_patterns = self._analyze_mistake_patterns(class_submissions)
        
        # Difficulty distribution
        difficulty_dist = self._calculate_difficulty_distribution(class_submissions)
        
        # 7-day trend
        seven_day_trend = self._calculate_class_7day_trend(class_submissions)
        
        return {
            'class_id': class_id,
            'teacher_id': teacher_id,
            'student_count': len(student_ids),
            'total_submissions': len(class_submissions),
            'topics_with_highest_struggle': topic_struggles,
            'los_with_dropping_performance': dropping_los,
            'top_mistake_patterns': mistake_patterns,
            'difficulty_distribution': difficulty_dist,
            'seven_day_trend': seven_day_trend,
            'active_alerts': [alert for alert in self.active_alerts 
                            if alert.class_id == class_id and alert.is_active],
            'last_updated': time.time()
        }
    
    def get_student_profile(self, teacher_id: str, student_id: str) -> Dict[str, Any]:
        """Generate detailed Student Profile"""
        
        # Validate teacher access to this student
        if not self._validate_teacher_student_access(teacher_id, student_id):
            raise PermissionError("Teacher does not have access to this student")
        
        student_submissions = [s for s in self.submissions if s.student_id == student_id]
        
        if not student_submissions:
            return {
                'student_id': student_id,
                'status': 'no_data',
                'message': 'No submission data available'
            }
        
        # Strongest/weakest topics
        topic_strengths = self._analyze_student_topic_strengths(student_submissions)
        
        # Repeatedly failed LOs
        failed_los = self._find_repeatedly_failed_los(student_submissions)
        
        # Last 50 solved questions
        recent_questions = student_submissions[-50:] if len(student_submissions) >= 50 else student_submissions
        
        # Time analysis
        time_analysis = self._analyze_student_time_patterns(student_submissions)
        
        # Difficulty trend
        difficulty_trend = self._calculate_student_difficulty_trend(student_submissions)
        
        # LO accuracy percentages
        lo_accuracies = self._calculate_student_lo_accuracies(student_submissions)
        
        return {
            'student_id': student_id,
            'total_questions_solved': len(student_submissions),
            'overall_accuracy': sum(s.is_correct for s in student_submissions) / len(student_submissions),
            'strongest_topics': topic_strengths['strongest'],
            'weakest_topics': topic_strengths['weakest'],
            'repeatedly_failed_los': failed_los,
            'last_50_questions': [
                {
                    'question_id': s.question_id,
                    'subject': s.subject,
                    'topic': s.topic,
                    'is_correct': s.is_correct,
                    'time_spent': s.time_spent_seconds,
                    'difficulty': s.difficulty,
                    'timestamp': s.timestamp
                } for s in recent_questions
            ],
            'time_analysis': time_analysis,
            'difficulty_trend': difficulty_trend,
            'lo_accuracy_percentages': lo_accuracies,
            'active_alerts': [alert for alert in self.active_alerts 
                            if alert.student_id == student_id and alert.is_active],
            'last_updated': time.time()
        }
    
    def get_lo_deep_analysis(self, teacher_id: str, learning_outcome: str, 
                            subject: str) -> LearningOutcomeAnalysis:
        """Generate deep analysis for a specific Learning Outcome"""
        
        # Get all submissions for this LO from teacher's classes
        teacher_students = self._get_all_teacher_students(teacher_id)
        lo_submissions = [s for s in self.submissions 
                         if s.student_id in teacher_students 
                         and s.learning_outcome == learning_outcome 
                         and s.subject == subject]
        
        if not lo_submissions:
            return LearningOutcomeAnalysis(
                learning_outcome=learning_outcome,
                subject=subject,
                topic="",
                class_performance={},
                worst_performers=[],
                top_performers=[],
                avg_accuracy=0,
                difficulty_breakdown={},
                common_mistakes=[],
                recommended_interventions=[]
            )
        
        # Calculate student performances
        student_performances = {}
        for student_id in teacher_students:
            student_lo_submissions = [s for s in lo_submissions if s.student_id == student_id]
            if student_lo_submissions:
                accuracy = sum(s.is_correct for s in student_lo_submissions) / len(student_lo_submissions)
                student_performances[student_id] = accuracy
        
        # Find worst and top performers
        sorted_performances = sorted(student_performances.items(), key=lambda x: x[1])
        worst_performers = [sid for sid, acc in sorted_performances[:3] if acc < 0.5]
        top_performers = [sid for sid, acc in sorted_performances[-3:] if acc > 0.8]
        
        # Calculate difficulty breakdown
        difficulty_breakdown = defaultdict(lambda: {'correct': 0, 'total': 0})
        for submission in lo_submissions:
            difficulty_breakdown[submission.difficulty]['total'] += 1
            if submission.is_correct:
                difficulty_breakdown[submission.difficulty]['correct'] += 1
        
        # Analyze common mistakes
        common_mistakes = self._analyze_lo_common_mistakes(lo_submissions)
        
        # Generate recommendations
        recommendations = self._generate_lo_recommendations(student_performances, difficulty_breakdown)
        
        return LearningOutcomeAnalysis(
            learning_outcome=learning_outcome,
            subject=subject,
            topic=lo_submissions[0].topic if lo_submissions else "",
            class_performance=student_performances,
            worst_performers=worst_performers,
            top_performers=top_performers,
            avg_accuracy=statistics.mean(student_performances.values()) if student_performances else 0,
            difficulty_breakdown=dict(difficulty_breakdown),
            common_mistakes=common_mistakes,
            recommended_interventions=recommendations
        )
    
    # === RECOMMENDATION ENGINE ===
    
    def generate_video_recommendations(self, student_id: str, limit: int = 5) -> List[VideoRecommendation]:
        """Generate video recommendations based on student's weakest LOs"""
        
        if student_id not in self.student_performance_cache:
            return []
        
        cache = self.student_performance_cache[student_id]
        
        # Find weakest LOs
        weak_los = []
        for lo_key, performance in cache['los'].items():
            if performance['total'] >= 3:  # Minimum attempts
                accuracy = performance['correct'] / performance['total']
                if accuracy < 0.6:  # Below 60% accuracy
                    subject, lo = lo_key.split(':', 1)
                    weak_los.append((subject, lo, accuracy))
        
        # Sort by accuracy (weakest first)
        weak_los.sort(key=lambda x: x[2])
        
        recommendations = []
        for subject, lo, accuracy in weak_los[:limit]:
            # Find matching videos
            matching_videos = [v for v in self.video_library 
                             if v.learning_outcome == lo and v.subject == subject]
            
            if matching_videos:
                # Sort by relevance score
                matching_videos.sort(key=lambda x: x.relevance_score, reverse=True)
                video = matching_videos[0]
                
                # Adjust relevance based on student's specific weakness
                video.relevance_score = video.relevance_score * (1 - accuracy)  # Lower accuracy = higher relevance
                recommendations.append(video)
        
        return recommendations[:limit]
    
    def assign_video_to_student(self, teacher_id: str, video_id: str, student_id: str) -> bool:
        """Teacher assigns a video to a student"""
        
        if not self._validate_teacher_student_access(teacher_id, student_id):
            return False
        
        # Find the video
        video = next((v for v in self.video_library if v.video_id == video_id), None)
        if not video:
            return False
        
        # Add student to assigned list
        if student_id not in video.assigned_to:
            video.assigned_to.append(student_id)
        
        print(f"📺 Video '{video.title}' assigned to student {student_id} by teacher {teacher_id}")
        return True
    
    # === MINI-TEST GENERATION ===
    
    def generate_mini_test(self, teacher_id: str, student_ids: List[str], 
                          learning_outcome: str, question_count: int = 5) -> Dict[str, Any]:
        """Generate LO-aligned mini-test for struggling students"""
        
        # Validate teacher access to all students
        for student_id in student_ids:
            if not self._validate_teacher_student_access(teacher_id, student_id):
                raise PermissionError(f"Teacher does not have access to student {student_id}")
        
        # Analyze student weaknesses to balance difficulty
        difficulty_recommendations = {}
        for student_id in student_ids:
            lo_accuracy = self._calculate_lo_performance(student_id, learning_outcome)
            if lo_accuracy < 0.4:
                difficulty_recommendations[student_id] = "KOLAY"
            elif lo_accuracy < 0.7:
                difficulty_recommendations[student_id] = "ORTA"
            else:
                difficulty_recommendations[student_id] = "ZOR"
        
        # Generate test metadata
        test_id = f"minitest_{teacher_id}_{int(time.time())}"
        
        mini_test = {
            'test_id': test_id,
            'created_by': teacher_id,
            'assigned_to': student_ids,
            'learning_outcome': learning_outcome,
            'question_count': question_count,
            'difficulty_recommendations': difficulty_recommendations,
            'created_at': time.time(),
            'instructions': f"Mini-test focusing on {learning_outcome}",
            'time_limit_minutes': question_count * 2,  # 2 minutes per question
            'auto_grade': True
        }
        
        print(f"📝 Mini-test created: {test_id} for {len(student_ids)} students")
        return mini_test
    
    # === HELPER METHODS ===
    
    def _validate_teacher_access(self, teacher_id: str, class_id: str) -> bool:
        """Validate teacher has access to specific class"""
        return (teacher_id in self.class_rosters and 
                class_id in self.class_rosters[teacher_id])
    
    def _validate_teacher_student_access(self, teacher_id: str, student_id: str) -> bool:
        """Validate teacher has access to specific student"""
        if teacher_id not in self.class_rosters:
            return False
        
        for class_students in self.class_rosters[teacher_id].values():
            if student_id in class_students:
                return True
        
        return False
    
    def _get_all_teacher_students(self, teacher_id: str) -> List[str]:
        """Get all student IDs accessible to this teacher"""
        students = []
        if teacher_id in self.class_rosters:
            for class_students in self.class_rosters[teacher_id].values():
                students.extend(class_students)
        return students
    
    def _calculate_topic_performance(self, student_id: str, topic: str, subject: str) -> StudentTopicPerformance:
        """Calculate student's performance on a specific topic"""
        topic_submissions = [s for s in self.submissions 
                           if s.student_id == student_id 
                           and s.topic == topic 
                           and s.subject == subject]
        
        if not topic_submissions:
            return StudentTopicPerformance(
                student_id=student_id,
                topic=topic,
                subject=subject,
                total_attempts=0,
                correct_attempts=0,
                accuracy_rate=0,
                avg_time_seconds=0,
                last_attempt=0,
                trend=PerformanceTrend.STABLE,
                struggling_los=[],
                mastered_los=[]
            )
        
        total_attempts = len(topic_submissions)
        correct_attempts = sum(s.is_correct for s in topic_submissions)
        accuracy_rate = correct_attempts / total_attempts
        avg_time = statistics.mean(s.time_spent_seconds for s in topic_submissions)
        last_attempt = max(s.timestamp for s in topic_submissions)
        
        # Calculate trend (simplified)
        if len(topic_submissions) >= 5:
            recent_accuracy = sum(s.is_correct for s in topic_submissions[-5:]) / 5
            if recent_accuracy > accuracy_rate * 1.1:
                trend = PerformanceTrend.IMPROVING
            elif recent_accuracy < accuracy_rate * 0.9:
                trend = PerformanceTrend.DECLINING
            else:
                trend = PerformanceTrend.STABLE
        else:
            trend = PerformanceTrend.STABLE
        
        return StudentTopicPerformance(
            student_id=student_id,
            topic=topic,
            subject=subject,
            total_attempts=total_attempts,
            correct_attempts=correct_attempts,
            accuracy_rate=accuracy_rate,
            avg_time_seconds=avg_time,
            last_attempt=last_attempt,
            trend=trend,
            struggling_los=[],  # TODO: Implement LO analysis
            mastered_los=[]
        )
    
    def _calculate_lo_performance(self, student_id: str, learning_outcome: str) -> float:
        """Calculate student's accuracy on a specific learning outcome"""
        lo_submissions = [s for s in self.submissions 
                         if s.student_id == student_id 
                         and s.learning_outcome == learning_outcome]
        
        if not lo_submissions:
            return 0.0
        
        return sum(s.is_correct for s in lo_submissions) / len(lo_submissions)
    
    def _get_class_topic_performance(self, class_id: str, topic: str, subject: str) -> Dict[str, float]:
        """Get topic performance for all students in class"""
        class_submissions = [s for s in self.submissions 
                           if s.class_id == class_id 
                           and s.topic == topic 
                           and s.subject == subject]
        
        student_performances = {}
        for student_id in set(s.student_id for s in class_submissions):
            student_topic_submissions = [s for s in class_submissions if s.student_id == student_id]
            accuracy = sum(s.is_correct for s in student_topic_submissions) / len(student_topic_submissions)
            student_performances[student_id] = accuracy
        
        return student_performances
    
    def _count_consecutive_lo_errors(self, student_id: str, learning_outcome: str) -> int:
        """Count consecutive errors on the same LO"""
        lo_submissions = [s for s in self.submissions 
                         if s.student_id == student_id 
                         and s.learning_outcome == learning_outcome]
        
        if not lo_submissions:
            return 0
        
        # Sort by timestamp (most recent first)
        lo_submissions.sort(key=lambda x: x.timestamp, reverse=True)
        
        consecutive_errors = 0
        for submission in lo_submissions:
            if not submission.is_correct:
                consecutive_errors += 1
            else:
                break
        
        return consecutive_errors
    
    def _get_lo_attempt_count(self, student_id: str, learning_outcome: str) -> int:
        """Get total attempt count for a learning outcome"""
        return len([s for s in self.submissions 
                   if s.student_id == student_id 
                   and s.learning_outcome == learning_outcome])
    
    def _calculate_7day_trend_decline(self, student_id: str, subject: str) -> float:
        """Calculate performance decline over last 7 days"""
        now = time.time()
        week_ago = now - (7 * 24 * 60 * 60)
        
        recent_submissions = [s for s in self.submissions 
                            if s.student_id == student_id 
                            and s.subject == subject 
                            and s.timestamp >= week_ago]
        
        if len(recent_submissions) < 10:  # Need sufficient data
            return 0.0
        
        # Split into first half and second half of the week
        mid_point = len(recent_submissions) // 2
        first_half = recent_submissions[:mid_point]
        second_half = recent_submissions[mid_point:]
        
        first_accuracy = sum(s.is_correct for s in first_half) / len(first_half)
        second_accuracy = sum(s.is_correct for s in second_half) / len(second_half)
        
        return max(0, first_accuracy - second_accuracy)  # Return decline amount
    
    def _calculate_topic_struggles(self, submissions: List[QuestionSubmission]) -> List[Dict[str, Any]]:
        """Find topics with highest struggle rates"""
        topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for submission in submissions:
            topic_key = f"{submission.subject}:{submission.topic}"
            topic_stats[topic_key]['total'] += 1
            if submission.is_correct:
                topic_stats[topic_key]['correct'] += 1
        
        # Calculate struggle rates and sort
        struggles = []
        for topic_key, stats in topic_stats.items():
            if stats['total'] >= 5:  # Minimum sample size
                accuracy = stats['correct'] / stats['total']
                struggle_rate = 1 - accuracy
                subject, topic = topic_key.split(':', 1)
                
                struggles.append({
                    'subject': subject,
                    'topic': topic,
                    'struggle_rate': struggle_rate,
                    'accuracy': accuracy,
                    'total_attempts': stats['total']
                })
        
        return sorted(struggles, key=lambda x: x['struggle_rate'], reverse=True)[:5]
    
    def _find_dropping_los(self, submissions: List[QuestionSubmission]) -> List[Dict[str, Any]]:
        """Find LOs with dropping performance"""
        lo_trends = {}
        
        for submission in submissions:
            lo_key = f"{submission.subject}:{submission.learning_outcome}"
            if lo_key not in lo_trends:
                lo_trends[lo_key] = []
            lo_trends[lo_key].append(submission)
        
        dropping_los = []
        for lo_key, lo_submissions in lo_trends.items():
            if len(lo_submissions) >= 10:  # Need sufficient data
                # Sort by timestamp
                lo_submissions.sort(key=lambda x: x.timestamp)
                
                # Compare first and last quarters
                quarter_size = len(lo_submissions) // 4
                first_quarter = lo_submissions[:quarter_size]
                last_quarter = lo_submissions[-quarter_size:]
                
                first_accuracy = sum(s.is_correct for s in first_quarter) / len(first_quarter)
                last_accuracy = sum(s.is_correct for s in last_quarter) / len(last_quarter)
                
                drop_amount = first_accuracy - last_accuracy
                if drop_amount > 0.1:  # 10% drop
                    subject, lo = lo_key.split(':', 1)
                    dropping_los.append({
                        'subject': subject,
                        'learning_outcome': lo,
                        'drop_amount': drop_amount,
                        'current_accuracy': last_accuracy,
                        'previous_accuracy': first_accuracy
                    })
        
        return sorted(dropping_los, key=lambda x: x['drop_amount'], reverse=True)[:5]
    
    def _analyze_mistake_patterns(self, submissions: List[QuestionSubmission]) -> List[Dict[str, Any]]:
        """Analyze most common mistake patterns"""
        incorrect_submissions = [s for s in submissions if not s.is_correct]
        
        # Group by topic and selected answer
        mistake_patterns = defaultdict(int)
        
        for submission in incorrect_submissions:
            pattern_key = f"{submission.subject}:{submission.topic}:{submission.selected_answer}"
            mistake_patterns[pattern_key] += 1
        
        # Convert to list and sort
        patterns = []
        for pattern_key, count in mistake_patterns.items():
            if count >= 3:  # Minimum frequency
                subject, topic, selected = pattern_key.split(':')
                patterns.append({
                    'subject': subject,
                    'topic': topic,
                    'selected_answer': selected,
                    'frequency': count,
                    'pattern': f"Students often select '{selected}' incorrectly in {topic}"
                })
        
        return sorted(patterns, key=lambda x: x['frequency'], reverse=True)[:5]
    
    def _calculate_difficulty_distribution(self, submissions: List[QuestionSubmission]) -> Dict[str, Dict[str, Any]]:
        """Calculate difficulty distribution and performance"""
        difficulty_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_time': []})
        
        for submission in submissions:
            difficulty_stats[submission.difficulty]['total'] += 1
            difficulty_stats[submission.difficulty]['avg_time'].append(submission.time_spent_seconds)
            if submission.is_correct:
                difficulty_stats[submission.difficulty]['correct'] += 1
        
        result = {}
        for difficulty, stats in difficulty_stats.items():
            result[difficulty] = {
                'total_questions': stats['total'],
                'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                'avg_time_seconds': statistics.mean(stats['avg_time']) if stats['avg_time'] else 0,
                'percentage_of_total': stats['total'] / len(submissions) * 100 if submissions else 0
            }
        
        return result
    
    def _calculate_class_7day_trend(self, submissions: List[QuestionSubmission]) -> Dict[str, Any]:
        """Calculate class performance trend over 7 days"""
        now = time.time()
        daily_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for submission in submissions:
            days_ago = int((now - submission.timestamp) / (24 * 60 * 60))
            if days_ago <= 7:
                daily_stats[days_ago]['total'] += 1
                if submission.is_correct:
                    daily_stats[days_ago]['correct'] += 1
        
        # Calculate daily accuracies
        daily_accuracies = {}
        for day in range(8):  # 0-7 days ago
            if daily_stats[day]['total'] > 0:
                daily_accuracies[day] = daily_stats[day]['correct'] / daily_stats[day]['total']
        
        if len(daily_accuracies) < 3:
            return {'trend': 'insufficient_data', 'change_rate': 0}
        
        # Calculate trend
        recent_days = [acc for day, acc in daily_accuracies.items() if day <= 2]  # Last 3 days
        older_days = [acc for day, acc in daily_accuracies.items() if day >= 5]   # 5-7 days ago
        
        if recent_days and older_days:
            recent_avg = statistics.mean(recent_days)
            older_avg = statistics.mean(older_days)
            change_rate = recent_avg - older_avg
            
            if change_rate > 0.05:
                trend = 'improving'
            elif change_rate < -0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
            change_rate = 0
        
        return {
            'trend': trend,
            'change_rate': change_rate,
            'daily_accuracies': daily_accuracies,
            'total_submissions_7days': sum(stats['total'] for stats in daily_stats.values())
        }
    
    def _analyze_student_topic_strengths(self, submissions: List[QuestionSubmission]) -> Dict[str, List[Dict]]:
        """Analyze student's strongest and weakest topics"""
        topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for submission in submissions:
            topic_key = f"{submission.subject}:{submission.topic}"
            topic_stats[topic_key]['total'] += 1
            if submission.is_correct:
                topic_stats[topic_key]['correct'] += 1
        
        # Calculate accuracies
        topic_accuracies = []
        for topic_key, stats in topic_stats.items():
            if stats['total'] >= 3:  # Minimum sample size
                subject, topic = topic_key.split(':', 1)
                accuracy = stats['correct'] / stats['total']
                topic_accuracies.append({
                    'subject': subject,
                    'topic': topic,
                    'accuracy': accuracy,
                    'total_attempts': stats['total']
                })
        
        # Sort by accuracy
        topic_accuracies.sort(key=lambda x: x['accuracy'])
        
        return {
            'weakest': topic_accuracies[:3],
            'strongest': topic_accuracies[-3:]
        }
    
    def _find_repeatedly_failed_los(self, submissions: List[QuestionSubmission]) -> List[Dict[str, Any]]:
        """Find learning outcomes with repeated failures"""
        lo_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'consecutive_errors': 0})
        
        # Group by LO
        lo_submissions = defaultdict(list)
        for submission in submissions:
            lo_submissions[submission.learning_outcome].append(submission)
        
        failed_los = []
        for lo, lo_subs in lo_submissions.items():
            if len(lo_subs) >= 3:  # Minimum attempts
                # Sort by timestamp
                lo_subs.sort(key=lambda x: x.timestamp)
                
                # Count consecutive errors from most recent
                consecutive_errors = 0
                for sub in reversed(lo_subs):
                    if not sub.is_correct:
                        consecutive_errors += 1
                    else:
                        break
                
                accuracy = sum(s.is_correct for s in lo_subs) / len(lo_subs)
                
                if consecutive_errors >= 2 or accuracy < 0.4:
                    failed_los.append({
                        'learning_outcome': lo,
                        'subject': lo_subs[0].subject,
                        'accuracy': accuracy,
                        'consecutive_errors': consecutive_errors,
                        'total_attempts': len(lo_subs),
                        'severity': 'high' if consecutive_errors >= 3 else 'medium'
                    })
        
        return sorted(failed_los, key=lambda x: (x['consecutive_errors'], 1-x['accuracy']), reverse=True)
    
    def _analyze_student_time_patterns(self, submissions: List[QuestionSubmission]) -> Dict[str, Any]:
        """Analyze student's time spending patterns"""
        times = [s.time_spent_seconds for s in submissions]
        
        if not times:
            return {}
        
        return {
            'avg_time_per_question': statistics.mean(times),
            'median_time_per_question': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_deviation': statistics.stdev(times) if len(times) > 1 else 0,
            'time_efficiency_trend': 'stable'  # TODO: Calculate trend
        }
    
    def _calculate_student_difficulty_trend(self, submissions: List[QuestionSubmission]) -> Dict[str, Any]:
        """Calculate how student's performance changes with difficulty"""
        difficulty_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for submission in submissions:
            difficulty_performance[submission.difficulty]['total'] += 1
            if submission.is_correct:
                difficulty_performance[submission.difficulty]['correct'] += 1
        
        trend = {}
        for difficulty, stats in difficulty_performance.items():
            if stats['total'] > 0:
                trend[difficulty] = stats['correct'] / stats['total']
        
        return trend
    
    def _calculate_student_lo_accuracies(self, submissions: List[QuestionSubmission]) -> Dict[str, float]:
        """Calculate student's accuracy for each learning outcome"""
        lo_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for submission in submissions:
            lo_stats[submission.learning_outcome]['total'] += 1
            if submission.is_correct:
                lo_stats[submission.learning_outcome]['correct'] += 1
        
        return {lo: stats['correct'] / stats['total'] 
                for lo, stats in lo_stats.items() if stats['total'] > 0}
    
    def _analyze_lo_common_mistakes(self, submissions: List[QuestionSubmission]) -> List[str]:
        """Analyze common mistakes for a specific LO"""
        incorrect_submissions = [s for s in submissions if not s.is_correct]
        
        # Count selected answers
        answer_counts = Counter(s.selected_answer for s in incorrect_submissions)
        
        # Generate mistake descriptions
        mistakes = []
        for answer, count in answer_counts.most_common(3):
            if count >= 2:  # Minimum frequency
                mistakes.append(f"Students often select '{answer}' ({count} times)")
        
        return mistakes
    
    def _generate_lo_recommendations(self, student_performances: Dict[str, float], 
                                   difficulty_breakdown: Dict) -> List[str]:
        """Generate recommendations for LO improvement"""
        recommendations = []
        
        avg_accuracy = statistics.mean(student_performances.values()) if student_performances else 0
        
        if avg_accuracy < 0.5:
            recommendations.append("Overall LO performance is low - consider fundamental concept review")
        
        struggling_students = sum(1 for acc in student_performances.values() if acc < 0.5)
        if struggling_students > len(student_performances) * 0.3:  # More than 30% struggling
            recommendations.append("High number of struggling students - consider class-wide intervention")
        
        # Check difficulty distribution
        easy_total = difficulty_breakdown.get('KOLAY', {}).get('total', 0)
        hard_total = difficulty_breakdown.get('ZOR', {}).get('total', 0)
        
        if easy_total == 0:
            recommendations.append("Consider adding easier questions to build confidence")
        
        if hard_total > easy_total * 2:
            recommendations.append("Questions may be too difficult - balance with easier questions")
        
        return recommendations

# Global teacher analytics instance
teacher_analytics = TeacherAnalyticsEngine()

def get_teacher_analytics() -> TeacherAnalyticsEngine:
    """Get global teacher analytics instance"""
    return teacher_analytics