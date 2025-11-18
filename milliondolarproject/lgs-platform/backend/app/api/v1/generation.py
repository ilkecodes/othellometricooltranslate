from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import asyncio
import time

from app.api.v1.deps import get_db, get_current_user
from app.core.question_generation import (
    EnhancedQuestionGenerator, 
    GenerationRequest, 
    DifficultyLevel, 
    QuestionType
)
from app.core.caching import get_cache_manager
from app.core.performance import get_adaptive_engine

router = APIRouter()

# Global generator instance (in production, use dependency injection)
generator = EnhancedQuestionGenerator()

class QuestionGenerationRequest(BaseModel):
    """API request model for question generation"""
    subject: str
    topic: str
    learning_outcome: str
    difficulty: DifficultyLevel
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    count: int = 1

class BatchGenerationRequest(BaseModel):
    """API request model for batch generation"""
    requests: List[QuestionGenerationRequest]
    
class CustomExamRequest(BaseModel):
    """API request for custom exam generation"""
    title: str
    subject_distribution: Dict[str, int]  # {"Matematik": 10, "Türkçe": 5}
    difficulty_distribution: Dict[str, float]  # {"KOLAY": 0.4, "ORTA": 0.4, "ZOR": 0.2}
    total_questions: int
    time_limit_minutes: int = 90

@router.post('/generate')
async def generate_single_question(
    request: QuestionGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate a single question with full validation pipeline and caching"""
    
    try:
        # Get cache manager
        cache_manager = await get_cache_manager()
        
        # Check cache first
        cached_question = await cache_manager.get_cached_question(
            request.subject,
            request.topic, 
            request.learning_outcome,
            request.difficulty.value
        )
        
        if cached_question and not cached_question.get('is_placeholder'):
            return {
                'success': True,
                'question': cached_question,
                'generation_metadata': {
                    'method': 'cached',
                    'validation_passed': True,
                    'cache_used': True,
                    'cached_at': cached_question.get('cached_at')
                }
            }
        
        # Check pre-generation pool
        pool_question = await cache_manager.get_from_pool(
            request.subject,
            request.difficulty.value
        )
        
        if pool_question:
            # Cache the pool question for future use
            await cache_manager.cache_question(
                pool_question,
                request.subject,
                request.topic,
                request.learning_outcome,
                request.difficulty.value
            )
            
            return {
                'success': True,
                'question': pool_question,
                'generation_metadata': {
                    'method': 'pre_generated_pool',
                    'validation_passed': True,
                    'cache_used': False,
                    'from_pool': True
                }
            }
        
        # Generate new question
        generation_request = GenerationRequest(
            subject=request.subject,
            topic=request.topic,
            learning_outcome=request.learning_outcome,
            difficulty=request.difficulty,
            question_type=request.question_type,
            user_id=str(current_user.id)
        )
        
        question = await generator.generate_question(generation_request)
        
        if 'error' in question:
            raise HTTPException(status_code=500, detail="Question generation failed")
        
        # Cache the generated question
        await cache_manager.cache_question(
            question,
            request.subject,
            request.topic,
            request.learning_outcome,
            request.difficulty.value,
            ttl=3600  # 1 hour TTL
        )
        
        return {
            'success': True,
            'question': question,
            'generation_metadata': {
                'method': 'enhanced_pipeline_v2',
                'validation_passed': True,
                'cache_used': False,
                'newly_generated': True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@router.post('/generate/batch')
async def generate_question_batch(
    request: BatchGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate multiple questions efficiently"""
    
    if len(request.requests) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 questions per batch")
    
    try:
        generation_requests = [
            GenerationRequest(
                subject=req.subject,
                topic=req.topic,
                learning_outcome=req.learning_outcome,
                difficulty=req.difficulty,
                question_type=req.question_type,
                user_id=str(current_user.id)
            )
            for req in request.requests
        ]
        
        questions = await generator.generate_question_batch(generation_requests)
        
        successful_questions = [q for q in questions if 'error' not in q]
        failed_count = len(questions) - len(successful_questions)
        
        return {
            'success': True,
            'questions': successful_questions,
            'statistics': {
                'requested': len(request.requests),
                'successful': len(successful_questions),
                'failed': failed_count,
                'success_rate': len(successful_questions) / len(request.requests) * 100
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation error: {str(e)}")

@router.post('/generate/custom-exam')
async def generate_custom_exam(
    request: CustomExamRequest,
    current_user = Depends(get_current_user)
):
    """Generate a complete custom exam with specified distribution"""
    
    try:
        # Validate distribution
        total_subject_questions = sum(request.subject_distribution.values())
        if total_subject_questions != request.total_questions:
            raise HTTPException(
                status_code=400, 
                detail=f"Subject distribution ({total_subject_questions}) doesn't match total ({request.total_questions})"
            )
        
        # Create generation requests based on distribution
        generation_requests = []
        
        for subject, count in request.subject_distribution.items():
            for i in range(count):
                # Determine difficulty based on distribution
                difficulty = _select_difficulty_by_distribution(request.difficulty_distribution)
                
                # TODO: Map subjects to actual topics and learning outcomes
                # For now, use placeholder values
                generation_requests.append(GenerationRequest(
                    subject=subject,
                    topic=f"{subject} Genel Konular",
                    learning_outcome=f"{subject} temel kavramları",
                    difficulty=difficulty,
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    user_id=str(current_user.id)
                ))
        
        # Generate all questions
        questions = await generator.generate_question_batch(generation_requests)
        successful_questions = [q for q in questions if 'error' not in q]
        
        # Create exam bundle
        exam_bundle = {
            'exam_id': f"custom-{current_user.id}-{int(time.time())}",
            'title': request.title,
            'created_by': current_user.id,
            'total_questions': len(successful_questions),
            'time_limit_minutes': request.time_limit_minutes,
            'questions': successful_questions,
            'target_distribution': request.subject_distribution,
            'actual_distribution': _calculate_actual_distribution(successful_questions),
            'difficulty_breakdown': _calculate_difficulty_breakdown(successful_questions),
            'created_at': time.time()
        }
        
        return {
            'success': True,
            'exam_bundle': exam_bundle,
            'statistics': {
                'requested_questions': request.total_questions,
                'generated_questions': len(successful_questions),
                'generation_rate': len(successful_questions) / request.total_questions * 100
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom exam generation error: {str(e)}")

@router.get('/cache/stats')
async def get_cache_statistics(
    current_user = Depends(get_current_user)
):
    """Get comprehensive cache statistics"""
    
    try:
        cache_manager = await get_cache_manager()
        cache_stats = await cache_manager.get_cache_statistics()
        
        # Add generation statistics from the generator
        generation_stats = generator.get_cache_stats()
        
        return {
            'cache_statistics': cache_stats,
            'generation_cache': generation_stats,
            'timestamp': time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats error: {str(e)}")

@router.post('/cache/warm-up')
async def warm_up_cache(
    current_user = Depends(get_current_user)
):
    """Warm up cache with common question combinations"""
    
    try:
        from app.core.caching import warm_up_common_questions
        results = await warm_up_common_questions()
        
        return {
            'success': True,
            'warm_up_results': results,
            'message': f"Cache warmed up: {results['success']} successful, {results['failed']} failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache warm-up error: {str(e)}")

@router.delete('/cache/clear')
async def clear_cache(
    pattern: str = None,
    current_user = Depends(get_current_user)
):
    """Clear cache entries (admin operation)"""
    
    # In production, add admin role check here
    
    try:
        cache_manager = await get_cache_manager()
        success = await cache_manager.clear_cache(pattern)
        
        return {
            'success': success,
            'message': f"Cache cleared {f'with pattern {pattern}' if pattern else 'completely'}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")

@router.get('/generate/cache-stats')
async def get_generation_cache_stats(
    current_user = Depends(get_current_user)
):
    """Get generation cache statistics for monitoring (legacy endpoint)"""
    
    try:
        cache_manager = await get_cache_manager()
        cache_stats = await cache_manager.get_cache_statistics()
        
        stats = generator.get_cache_stats()
        
        return {
            'cache_statistics': cache_stats,
            'fingerprint_stats': {
                'loaded_authentic_questions': len(generator.authentic_questions),
                'style_patterns_extracted': len(generator.style_conditioner.fingerprints.get('common_phrases', []))
            },
            'generation_cache': stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats error: {str(e)}")

@router.post('/generate/validate-question')
async def validate_existing_question(
    question_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Validate an existing question using the validation pipeline"""
    
    try:
        validation_result = await generator.validator.validate_question(question_data)
        
        return {
            'is_valid': validation_result.is_valid,
            'confidence_score': validation_result.confidence_score,
            'validation_errors': validation_result.validation_errors,
            'quality_metrics': validation_result.quality_metrics,
            'similarity_score': validation_result.similarity_score,
            'recommendations': _generate_improvement_recommendations(validation_result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post('/generate/adaptive')
async def generate_adaptive_question(
    request: QuestionGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate question with adaptive difficulty based on student performance"""
    
    try:
        # Get adaptive difficulty recommendation
        adaptive_engine = get_adaptive_engine()
        recommended_difficulty = adaptive_engine.get_adaptive_difficulty(
            str(current_user.id), 
            request.subject
        )
        
        # Override the requested difficulty with adaptive recommendation
        adaptive_request = QuestionGenerationRequest(
            subject=request.subject,
            topic=request.topic,
            learning_outcome=request.learning_outcome,
            difficulty=DifficultyLevel(recommended_difficulty),
            question_type=request.question_type,
            count=request.count
        )
        
        # Use the regular generation pipeline with adaptive difficulty
        cache_manager = await get_cache_manager()
        
        # Check cache first
        cached_question = await cache_manager.get_cached_question(
            adaptive_request.subject,
            adaptive_request.topic,
            adaptive_request.learning_outcome,
            adaptive_request.difficulty.value
        )
        
        if cached_question and not cached_question.get('is_placeholder'):
            return {
                'success': True,
                'question': cached_question,
                'adaptive_metadata': {
                    'requested_difficulty': request.difficulty.value,
                    'recommended_difficulty': recommended_difficulty,
                    'difficulty_adjusted': request.difficulty.value != recommended_difficulty
                },
                'generation_metadata': {
                    'method': 'cached_adaptive',
                    'validation_passed': True,
                    'cache_used': True
                }
            }
        
        # Generate new adaptive question
        generation_request = GenerationRequest(
            subject=adaptive_request.subject,
            topic=adaptive_request.topic,
            learning_outcome=adaptive_request.learning_outcome,
            difficulty=adaptive_request.difficulty,
            question_type=adaptive_request.question_type,
            user_id=str(current_user.id)
        )
        
        question = await generator.generate_question(generation_request)
        
        if 'error' in question:
            raise HTTPException(status_code=500, detail="Adaptive question generation failed")
        
        # Cache the generated question
        await cache_manager.cache_question(
            question,
            adaptive_request.subject,
            adaptive_request.topic,
            adaptive_request.learning_outcome,
            adaptive_request.difficulty.value
        )
        
        return {
            'success': True,
            'question': question,
            'adaptive_metadata': {
                'requested_difficulty': request.difficulty.value,
                'recommended_difficulty': recommended_difficulty,
                'difficulty_adjusted': request.difficulty.value != recommended_difficulty,
                'student_profile_used': True
            },
            'generation_metadata': {
                'method': 'enhanced_adaptive_pipeline',
                'validation_passed': True,
                'cache_used': False,
                'newly_generated': True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive generation error: {str(e)}")

@router.post('/generate/personalized-exam')
async def generate_personalized_exam(
    request: CustomExamRequest,
    current_user = Depends(get_current_user)
):
    """Generate a personalized exam with adaptive difficulty per subject"""
    
    try:
        adaptive_engine = get_adaptive_engine()
        
        # Generate adaptive exam based on student performance
        adaptive_distribution = {}
        adaptive_difficulty_distribution = {}
        
        for subject, count in request.subject_distribution.items():
            adaptive_distribution[subject] = count
            
            # Get recommended difficulty for this student and subject
            recommended_difficulty = adaptive_engine.get_adaptive_difficulty(
                str(current_user.id), subject
            )
            
            # Use adaptive difficulty instead of requested distribution
            adaptive_difficulty_distribution[recommended_difficulty] = (
                adaptive_difficulty_distribution.get(recommended_difficulty, 0) + count / len(request.subject_distribution)
            )
        
        # Create adaptive custom exam request
        adaptive_exam_request = CustomExamRequest(
            title=f"Personalized {request.title}",
            subject_distribution=adaptive_distribution,
            difficulty_distribution=adaptive_difficulty_distribution,
            total_questions=request.total_questions,
            time_limit_minutes=request.time_limit_minutes
        )
        
        # Generate the exam using adaptive parameters
        generation_requests = []
        
        for subject, count in adaptive_distribution.items():
            recommended_difficulty = adaptive_engine.get_adaptive_difficulty(
                str(current_user.id), subject
            )
            
            for i in range(count):
                generation_requests.append(GenerationRequest(
                    subject=subject,
                    topic=f"{subject} Genel Konular",
                    learning_outcome=f"{subject} temel kavramları",
                    difficulty=DifficultyLevel(recommended_difficulty),
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    user_id=str(current_user.id)
                ))
        
        # Generate all questions
        questions = await generator.generate_question_batch(generation_requests)
        successful_questions = [q for q in questions if 'error' not in q]
        
        # Create personalized exam bundle
        exam_bundle = {
            'exam_id': f"personalized-{current_user.id}-{int(time.time())}",
            'title': adaptive_exam_request.title,
            'created_by': current_user.id,
            'total_questions': len(successful_questions),
            'time_limit_minutes': adaptive_exam_request.time_limit_minutes,
            'questions': successful_questions,
            'target_distribution': adaptive_distribution,
            'actual_distribution': _calculate_actual_distribution(successful_questions),
            'difficulty_breakdown': _calculate_difficulty_breakdown(successful_questions),
            'personalization_metadata': {
                'adaptive_difficulty_used': True,
                'difficulty_recommendations': {
                    subject: adaptive_engine.get_adaptive_difficulty(str(current_user.id), subject)
                    for subject in adaptive_distribution.keys()
                },
                'original_request': request.difficulty_distribution,
                'adaptive_adjustments': adaptive_difficulty_distribution
            },
            'created_at': time.time()
        }
        
        return {
            'success': True,
            'exam_bundle': exam_bundle,
            'personalization_insights': {
                'difficulty_adjustments_made': True,
                'subjects_analyzed': list(adaptive_distribution.keys()),
                'adaptive_algorithm_version': 'v1.0'
            },
            'statistics': {
                'requested_questions': request.total_questions,
                'generated_questions': len(successful_questions),
                'generation_rate': len(successful_questions) / request.total_questions * 100
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalized exam generation error: {str(e)}")

@router.get('/adaptive/student-profile')
async def get_student_adaptive_profile(
    current_user = Depends(get_current_user)
):
    """Get student's adaptive learning profile"""
    
    try:
        adaptive_engine = get_adaptive_engine()
        performance_tracker = adaptive_engine.tracker
        
        student_profile = performance_tracker.get_student_profile(str(current_user.id))
        
        if not student_profile:
            return {
                'student_id': str(current_user.id),
                'status': 'new_student',
                'message': 'No performance history available yet',
                'default_recommendations': {
                    'difficulty': 'ORTA',
                    'suggestion': 'Start with medium difficulty questions to establish baseline performance'
                }
            }
        
        # Get adaptive recommendations for each subject
        adaptive_recommendations = {}
        for subject in student_profile.estimated_ability.keys():
            recommended_difficulty = adaptive_engine.get_adaptive_difficulty(
                str(current_user.id), subject
            )
            should_adjust, current, recommended = adaptive_engine.should_adjust_difficulty(
                str(current_user.id), subject
            )
            
            adaptive_recommendations[subject] = {
                'current_ability': student_profile.estimated_ability[subject],
                'recommended_difficulty': recommended_difficulty,
                'current_preference': current,
                'adjustment_needed': should_adjust,
                'improvement_trend': student_profile.improvement_trend.get(subject, 'stable'),
                'recent_performance': student_profile.recent_performance.get(subject, [])[-5:]  # Last 5
            }
        
        return {
            'student_id': str(current_user.id),
            'profile_status': 'active',
            'total_questions_answered': student_profile.total_questions_answered,
            'last_updated': student_profile.last_updated,
            'adaptive_recommendations': adaptive_recommendations,
            'learning_insights': {
                'strongest_subjects': [
                    subject for subject, ability in student_profile.estimated_ability.items()
                    if ability > 0.7
                ],
                'subjects_needing_practice': [
                    subject for subject, ability in student_profile.estimated_ability.items()
                    if ability < 0.5
                ],
                'improving_subjects': [
                    subject for subject, trend in student_profile.improvement_trend.items()
                    if trend == 'improving'
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive profile error: {str(e)}")

def _select_difficulty_by_distribution(distribution: Dict[str, float]) -> DifficultyLevel:
    """Select difficulty level based on probability distribution"""
    import random
    
    rand = random.random()
    cumulative = 0.0
    
    for difficulty, probability in distribution.items():
        cumulative += probability
        if rand <= cumulative:
            return DifficultyLevel(difficulty)
    
    # Fallback
    return DifficultyLevel.MEDIUM

def _calculate_actual_distribution(questions: List[Dict]) -> Dict[str, int]:
    """Calculate actual subject distribution from generated questions"""
    distribution = {}
    for question in questions:
        subject = question.get('subject', 'Unknown')
        distribution[subject] = distribution.get(subject, 0) + 1
    return distribution

def _calculate_difficulty_breakdown(questions: List[Dict]) -> Dict[str, int]:
    """Calculate difficulty breakdown from generated questions"""
    breakdown = {}
    for question in questions:
        difficulty = question.get('difficulty_level', 'ORTA')
        breakdown[difficulty] = breakdown.get(difficulty, 0) + 1
    return breakdown

def _generate_improvement_recommendations(validation: Any) -> List[str]:
    """Generate specific improvement recommendations based on validation"""
    recommendations = []
    
    if validation.quality_metrics.get('ambiguity_score', 0) > 0.3:
        recommendations.append("Consider making the question stem more specific and clear")
    
    if validation.similarity_score > 0.25:
        recommendations.append("Question is very similar to existing questions - consider different wording")
    
    if validation.confidence_score < 0.7:
        recommendations.append("Overall question quality could be improved - review options and explanations")
    
    if not recommendations:
        recommendations.append("Question meets quality standards")
    
    return recommendations