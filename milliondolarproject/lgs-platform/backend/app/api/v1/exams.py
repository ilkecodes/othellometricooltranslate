from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import time

from app.api.v1.deps import get_db, get_current_user
from app.core.performance import get_performance_tracker, get_adaptive_engine, StudentAnswer

router = APIRouter()

@router.get('/bundles')
async def list_exam_bundles():
    """Get available exam bundles"""
    try:
        # Load the generated exam bundle
        with open('complete_lgs_exam_bundle_v2.json', 'r', encoding='utf-8') as f:
            bundle_data = json.load(f)
        
        bundle_info = bundle_data.get('bundle_info', {})
        stats = bundle_data.get('statistics', {})
        
        return {
            'bundles': [
                {
                    'id': 'lgs-karma-v2',
                    'title': bundle_info.get('title', 'LGS Karma Deneme'),
                    'description': bundle_info.get('description', 'Complete LGS exam bundle'),
                    'version': bundle_info.get('version', '2.0'),
                    'total_questions': stats.get('total_questions', 0),
                    'subjects': bundle_info.get('subjects', []),
                    'distribution': bundle_data.get('target_distribution', {}),
                    'source_stats': stats.get('by_source', {}),
                    'difficulty_stats': stats.get('by_difficulty', {}),
                    'generated_date': bundle_info.get('generation_date', '2024-11-14'),
                    'available': True
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading exam bundles: {str(e)}")

@router.get('/bundles/{bundle_id}')
async def get_exam_bundle(bundle_id: str):
    """Get specific exam bundle details"""
    if bundle_id != 'lgs-karma-v2':
        raise HTTPException(status_code=404, detail="Bundle not found")
    
    try:
        with open('/app/complete_lgs_exam_bundle_v2.json', 'r', encoding='utf-8') as f:
            bundle_data = json.load(f)
        return bundle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading bundle: {str(e)}")

@router.get('/bundles/{bundle_id}/questions')
async def get_bundle_questions(bundle_id: str, shuffle: bool = True):
    """Get questions from a specific bundle for exam taking"""
    if bundle_id != 'lgs-karma-v2':
        raise HTTPException(status_code=404, detail="Bundle not found")
    
    try:
        with open('complete_lgs_exam_bundle_v2.json', 'r', encoding='utf-8') as f:
            bundle_data = json.load(f)
        
        questions = bundle_data.get('questions', [])
        
        # Format questions for frontend
        formatted_questions = []
        for i, q in enumerate(questions):
            formatted_questions.append({
                'id': f"bundle-{bundle_id}-{i}",
                'question_number': i + 1,
                'stem': q.get('stem', ''),
                'options': q.get('options', []),
                'correct_answer': q.get('correct_answer', ''),
                'subject': q.get('subject', ''),
                'difficulty_level': q.get('difficulty_level', ''),
                'kazanim_code': q.get('kazanim_code', ''),
                'stamp': q.get('stamp', ''),
                'source': q.get('source', ''),
                'confidence': q.get('confidence', 0),
                'explanation': q.get('explanation', '')
            })
        
        if shuffle:
            import random
            random.shuffle(formatted_questions)
            # Re-number after shuffle
            for i, q in enumerate(formatted_questions):
                q['question_number'] = i + 1
        
        return {
            'bundle_id': bundle_id,
            'total_questions': len(formatted_questions),
            'questions': formatted_questions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading bundle questions: {str(e)}")

@router.post('/bundles/{bundle_id}/sessions')
async def start_bundle_exam(
    bundle_id: str,
    current_user = Depends(get_current_user)
):
    """Start a new exam session with a bundle"""
    if bundle_id != 'lgs-karma-v2':
        raise HTTPException(status_code=404, detail="Bundle not found")
    
    # In a real implementation, you'd create a session record in the database
    # For now, return session info
    
    return {
        'session_id': f"session-{bundle_id}-{current_user.id}",
        'bundle_id': bundle_id,
        'user_id': current_user.id,
        'started_at': '2024-11-14T10:00:00Z',
        'status': 'active',
        'time_limit_minutes': 120,  # 2 hours for full LGS
        'instructions': 'LGS Karma Deneme - Bu deneme sınavı gerçek LGS sorularını ve MILK yapay zeka soruları karışımını içerir.'
    }

@router.post('/sessions/{session_id}/answers')
async def submit_answer(
    session_id: str,
    answer_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Submit answer for a question in exam session with performance tracking"""
    
    question_id = answer_data.get('question_id')
    selected_answer = answer_data.get('selected_answer')
    time_spent = answer_data.get('time_spent_seconds', 0)
    
    if not question_id or not selected_answer:
        raise HTTPException(status_code=400, detail="Missing question_id or selected_answer")
    
    try:
        # Get question details (in production, fetch from database)
        # For demo, extract from question_id format
        question_parts = question_id.split('-')
        if len(question_parts) >= 3:
            subject = question_parts[1] if len(question_parts) > 1 else "Unknown"
            difficulty = question_parts[2] if len(question_parts) > 2 else "ORTA"
        else:
            subject = "Unknown"
            difficulty = "ORTA"
        
        # TODO: Get actual correct answer from database/bundle
        correct_answer = answer_data.get('correct_answer', 'A')  # Fallback
        is_correct = selected_answer == correct_answer
        
        # Record answer in performance tracker
        tracker = get_performance_tracker()
        
        student_answer = StudentAnswer(
            student_id=str(current_user.id),
            question_id=question_id,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            timestamp=time.time(),
            session_id=session_id,
            subject=subject,
            topic="General",  # TODO: Extract from question
            difficulty=difficulty,
            question_source="LGS"  # TODO: Extract actual source
        )
        
        tracker.record_answer(student_answer)
        
        # Get adaptive difficulty recommendation
        adaptive_engine = get_adaptive_engine()
        should_adjust, current_diff, recommended_diff = adaptive_engine.should_adjust_difficulty(
            str(current_user.id), subject
        )
        
        response = {
            'session_id': session_id,
            'question_id': question_id,
            'answer_recorded': True,
            'time_spent': time_spent,
            'is_correct': is_correct,
            'performance_update': {
                'recorded': True,
                'adaptive_difficulty': {
                    'should_adjust': should_adjust,
                    'current_difficulty': current_diff,
                    'recommended_difficulty': recommended_diff
                }
            }
        }
        
        # Add student profile update
        student_profile = tracker.get_student_profile(str(current_user.id))
        if student_profile:
            response['student_profile'] = {
                'estimated_ability': student_profile.estimated_ability.get(subject, 0.5),
                'improvement_trend': student_profile.improvement_trend.get(subject, "stable"),
                'total_questions': student_profile.total_questions_answered
            }
        
        return response
        
    except Exception as e:
        # Still record the answer even if analytics fail
        return {
            'session_id': session_id,
            'question_id': question_id,
            'answer_recorded': True,
            'time_spent': time_spent,
            'error': f"Analytics error: {str(e)}"
        }

@router.post('/sessions/{session_id}/complete')
async def complete_exam_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Complete exam session and get results"""
    
    # In a real implementation, you'd calculate final score from database
    # For now, return mock results
    
    return {
            'session_id': session_id,
            'completed_at': '2024-11-14T12:00:00Z',
            'total_time_minutes': 120,
            'total_questions': 90,
            'answered_questions': 90,
            'correct_answers': 72,
            'score_percentage': 80,
            'subject_breakdown': {
                'Türkçe': {'total': 20, 'correct': 16, 'percentage': 80},
                'Matematik': {'total': 20, 'correct': 15, 'percentage': 75},
                'Din Kültürü ve Ahlak Bilgisi': {'total': 10, 'correct': 8, 'percentage': 80},
                'Fen Bilimleri': {'total': 20, 'correct': 17, 'percentage': 85},
                'Sosyal Bilgiler': {'total': 10, 'correct': 8, 'percentage': 80},
                'İngilizce': {'total': 10, 'correct': 8, 'percentage': 80}
            },
            'difficulty_breakdown': {
                'Kolay': {'total': 27, 'correct': 24, 'percentage': 89},
                'Orta': {'total': 29, 'correct': 22, 'percentage': 76},
                'Zor': {'total': 13, 'correct': 8, 'percentage': 62}
            },
            'source_breakdown': {
                'LGS': {'total': 21, 'correct': 17, 'percentage': 81},
                'MILK': {'total': 69, 'correct': 55, 'percentage': 80}
            },
            'performance_insights': get_performance_insights_for_user(current_user.id)
        }

def get_performance_insights_for_user(user_id: int) -> Dict[str, Any]:
        """Get performance insights for session completion"""
        tracker = get_performance_tracker()
        adaptive_engine = get_adaptive_engine()
        
        student_profile = tracker.get_student_profile(str(user_id))
        
        insights = {
            'recommendations': [],
            'strengths': [],
            'areas_for_improvement': []
        }
        
        if student_profile:
            # Analyze performance by subject
            for subject, ability in student_profile.estimated_ability.items():
                trend = student_profile.improvement_trend.get(subject, "stable")
                
                if ability > 0.8:
                    insights['strengths'].append(f"{subject} - Excellent performance ({ability:.1%})")
                elif ability < 0.5:
                    insights['areas_for_improvement'].append(f"{subject} - Needs practice ({ability:.1%})")
                
                if trend == "declining":
                    insights['recommendations'].append(f"Focus on {subject} - recent performance declining")
                elif trend == "improving":
                    insights['strengths'].append(f"{subject} - showing improvement")
            
            # Difficulty recommendations
            for subject in student_profile.estimated_ability.keys():
                should_adjust, current, recommended = adaptive_engine.should_adjust_difficulty(
                    str(user_id), subject
                )
                if should_adjust:
                    insights['recommendations'].append(
                        f"{subject}: Try {recommended.lower()} difficulty questions next"
                    )
        else:
            insights['recommendations'].append("Continue practicing to build your performance profile")
        
        return insights

@router.get('/analytics/performance/{student_id}')
async def get_student_performance_analytics(
    student_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed performance analytics for a student"""
    
    # In production, add authorization check
    if str(current_user.id) != student_id:
        # Only allow students to see their own data or admin/teacher access
        pass
    
    try:
        tracker = get_performance_tracker()
        adaptive_engine = get_adaptive_engine()
        
        student_profile = tracker.get_student_profile(student_id)
        
        if not student_profile:
            return {
                'student_id': student_id,
                'status': 'no_data',
                'message': 'No performance data available'
            }
        
        analytics = {
            'student_id': student_id,
            'profile': {
                'estimated_ability': student_profile.estimated_ability,
                'recent_performance': student_profile.recent_performance,
                'improvement_trends': student_profile.improvement_trend,
                'total_questions_answered': student_profile.total_questions_answered,
                'preferred_difficulty': student_profile.preferred_difficulty
            },
            'adaptive_recommendations': {},
            'performance_timeline': tracker.get_subject_performance_trends(),
            'last_updated': student_profile.last_updated
        }
        
        # Get adaptive difficulty recommendations for each subject
        for subject in student_profile.estimated_ability.keys():
            should_adjust, current, recommended = adaptive_engine.should_adjust_difficulty(
                student_id, subject
            )
            analytics['adaptive_recommendations'][subject] = {
                'should_adjust': should_adjust,
                'current_difficulty': current,
                'recommended_difficulty': recommended
            }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@router.get('/analytics/questions/{question_id}')
async def get_question_analytics(
    question_id: str,
    current_user = Depends(get_current_user)
):
    """Get performance analytics for a specific question"""
    
    try:
        tracker = get_performance_tracker()
        
        performance = tracker.get_question_quality_metrics(question_id)
        distractor_analysis = tracker.analyze_distractor_effectiveness(question_id)
        
        if not performance:
            return {
                'question_id': question_id,
                'status': 'no_data',
                'message': 'No performance data available for this question'
            }
        
        return {
            'question_id': question_id,
            'performance_metrics': {
                'total_attempts': performance.total_attempts,
                'correct_rate': performance.correct_rate,
                'empirical_difficulty': performance.empirical_difficulty,
                'discrimination_index': performance.discrimination_index,
                'quality_score': performance.quality_score,
                'flagged_for_review': performance.flagged_for_review,
                'avg_time_seconds': performance.avg_time_seconds,
                'median_time_seconds': performance.median_time_seconds
            },
            'distractor_analysis': distractor_analysis,
            'recommendations': generate_question_recommendations(performance)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question analytics error: {str(e)}")

def generate_question_recommendations(performance: Any) -> List[str]:
    """Generate recommendations for question improvement"""
    recommendations = []
    
    if performance.quality_score < 0.3:
        recommendations.append("Question flagged for review due to low quality score")
    
    if performance.correct_rate > 0.9:
        recommendations.append("Question may be too easy - consider increasing difficulty")
    elif performance.correct_rate < 0.3:
        recommendations.append("Question may be too difficult - consider decreasing difficulty or reviewing distractors")
    
    if performance.discrimination_index < 0.1:
        recommendations.append("Poor discrimination - question doesn't differentiate between strong and weak students")
    
    if performance.avg_time_seconds > 300:  # 5 minutes
        recommendations.append("Students taking unusually long - question may be confusing or overly complex")
    
    return recommendations

@router.get('/analytics/system/overview')
async def get_system_analytics_overview(
    current_user = Depends(get_current_user)
):
    """Get system-wide analytics overview"""
    
    try:
        tracker = get_performance_tracker()
        
        analytics = tracker.export_analytics()
        
        # Add quality insights
        low_quality_questions = tracker.get_low_quality_questions()
        subject_trends = tracker.get_subject_performance_trends()
        
        return {
            'system_overview': analytics['summary'],
            'quality_metrics': {
                'low_quality_questions_count': len(low_quality_questions),
                'low_quality_question_ids': low_quality_questions[:10],  # Sample
                'avg_quality_score': sum(
                    perf.quality_score for perf in tracker.question_performance.values()
                ) / len(tracker.question_performance) if tracker.question_performance else 0
            },
            'subject_performance': subject_trends,
            'recommendations': {
                'questions_to_review': len(low_quality_questions),
                'active_students': len(analytics['student_profiles']),
                'total_data_points': analytics['summary']['total_answers']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System analytics error: {str(e)}")@router.get('/generate/new-bundle')
async def generate_new_bundle(
    current_user = Depends(get_current_user)
):
    """Generate a new exam bundle on demand"""
    import subprocess
    
    try:
        # Run the bundle generator
        result = subprocess.run(
            ['python', 'generate_complete_lgs_bundle_v2.py'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Generation failed: {result.stderr}")
        
        return {
            'success': True,
            'message': 'New exam bundle generated successfully',
            'output': result.stdout
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bundle: {str(e)}")