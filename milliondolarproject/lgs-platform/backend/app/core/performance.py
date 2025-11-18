#!/usr/bin/env python3
"""
Student Performance Feedback System
Tracks student performance to improve question quality and enable adaptive difficulty
"""

import json
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime, timedelta
import logging

@dataclass 
class StudentAnswer:
    """Individual answer record"""
    student_id: str
    question_id: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    time_spent_seconds: int
    timestamp: float
    session_id: str
    subject: str
    topic: str
    difficulty: str
    question_source: str  # "LGS", "MILK", etc.

@dataclass
class QuestionPerformance:
    """Performance metrics for a specific question"""
    question_id: str
    total_attempts: int
    correct_attempts: int
    correct_rate: float
    avg_time_seconds: float
    median_time_seconds: float
    std_time_seconds: float
    empirical_difficulty: float  # 0 = very hard, 1 = very easy
    discrimination_index: float  # how well it separates strong vs weak students
    quality_score: float
    flagged_for_review: bool
    wrong_option_distribution: Dict[str, int]
    student_ability_correlation: float
    
@dataclass
class StudentProfile:
    """Student proficiency profile"""
    student_id: str
    estimated_ability: Dict[str, float]  # per subject
    recent_performance: Dict[str, List[float]]  # last 10 scores per subject
    improvement_trend: Dict[str, str]  # "improving", "stable", "declining"
    time_based_decay: float
    last_updated: float
    total_questions_answered: int
    preferred_difficulty: Dict[str, str]

class PerformanceTracker:
    """Tracks and analyzes student performance"""
    
    def __init__(self):
        self.answers: List[StudentAnswer] = []
        self.question_performance: Dict[str, QuestionPerformance] = {}
        self.student_profiles: Dict[str, StudentProfile] = {}
        self.performance_cache: Dict[str, Any] = {}
        
    def record_answer(self, answer: StudentAnswer):
        """Record a student answer and update metrics"""
        self.answers.append(answer)
        
        # Update question performance
        self._update_question_performance(answer)
        
        # Update student profile
        self._update_student_profile(answer)
        
        # Clear relevant caches
        self._invalidate_cache(answer.question_id, answer.student_id)
    
    def _update_question_performance(self, answer: StudentAnswer):
        """Update performance metrics for a question"""
        question_id = answer.question_id
        
        # Get all answers for this question
        question_answers = [a for a in self.answers if a.question_id == question_id]
        
        if not question_answers:
            return
        
        # Calculate basic metrics
        total_attempts = len(question_answers)
        correct_attempts = sum(1 for a in question_answers if a.is_correct)
        correct_rate = correct_attempts / total_attempts
        
        times = [a.time_spent_seconds for a in question_answers]
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        
        # Calculate empirical difficulty (inverse of correct rate)
        empirical_difficulty = 1.0 - correct_rate
        
        # Calculate discrimination index (simplified)
        discrimination_index = self._calculate_discrimination_index(question_answers)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            correct_rate, discrimination_index, total_attempts
        )
        
        # Analyze wrong option distribution
        wrong_option_dist = defaultdict(int)
        for a in question_answers:
            if not a.is_correct:
                wrong_option_dist[a.selected_answer] += 1
        
        # Update question performance record
        self.question_performance[question_id] = QuestionPerformance(
            question_id=question_id,
            total_attempts=total_attempts,
            correct_attempts=correct_attempts,
            correct_rate=correct_rate,
            avg_time_seconds=avg_time,
            median_time_seconds=median_time,
            std_time_seconds=std_time,
            empirical_difficulty=empirical_difficulty,
            discrimination_index=discrimination_index,
            quality_score=quality_score,
            flagged_for_review=quality_score < 0.3,
            wrong_option_distribution=dict(wrong_option_dist),
            student_ability_correlation=0.0  # TODO: Calculate correlation
        )
    
    def _calculate_discrimination_index(self, answers: List[StudentAnswer]) -> float:
        """Calculate discrimination index for a question"""
        if len(answers) < 10:  # Need sufficient data
            return 0.5
        
        # Group students by overall ability (simplified)
        student_scores = defaultdict(list)
        for answer in answers:
            student_id = answer.student_id
            # Get student's overall performance in this subject
            student_answers = [a for a in self.answers 
                             if a.student_id == student_id and a.subject == answer.subject]
            if student_answers:
                overall_score = sum(a.is_correct for a in student_answers) / len(student_answers)
                student_scores[student_id] = overall_score
        
        if len(student_scores) < 6:
            return 0.5
        
        # Split into high and low ability groups
        sorted_students = sorted(student_scores.items(), key=lambda x: x[1])
        n = len(sorted_students)
        
        low_ability = sorted_students[:n//3]
        high_ability = sorted_students[-n//3:]
        
        # Calculate correct rates for each group on this question
        high_ability_ids = set(student_id for student_id, _ in high_ability)
        low_ability_ids = set(student_id for student_id, _ in low_ability)
        
        high_correct = sum(1 for a in answers if a.student_id in high_ability_ids and a.is_correct)
        low_correct = sum(1 for a in answers if a.student_id in low_ability_ids and a.is_correct)
        
        high_total = sum(1 for a in answers if a.student_id in high_ability_ids)
        low_total = sum(1 for a in answers if a.student_id in low_ability_ids)
        
        if high_total == 0 or low_total == 0:
            return 0.5
        
        high_rate = high_correct / high_total
        low_rate = low_correct / low_total
        
        # Discrimination index is difference between high and low ability groups
        return high_rate - low_rate
    
    def _calculate_quality_score(self, correct_rate: float, discrimination: float, attempts: int) -> float:
        """Calculate composite quality score"""
        # Ideal correct rate is around 0.6-0.7 (not too easy, not too hard)
        difficulty_penalty = abs(correct_rate - 0.65) * 0.5
        
        # Good discrimination should be > 0.3
        discrimination_score = min(1.0, discrimination / 0.3) if discrimination > 0 else 0
        
        # More attempts = more reliable statistics
        reliability_bonus = min(0.2, attempts / 100)
        
        quality = 1.0 - difficulty_penalty + discrimination_score * 0.3 + reliability_bonus
        return max(0.0, min(1.0, quality))
    
    def _update_student_profile(self, answer: StudentAnswer):
        """Update student proficiency profile"""
        student_id = answer.student_id
        subject = answer.subject
        
        # Get or create student profile
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = StudentProfile(
                student_id=student_id,
                estimated_ability={},
                recent_performance={},
                improvement_trend={},
                time_based_decay=0.95,  # Older performance counts less
                last_updated=time.time(),
                total_questions_answered=0,
                preferred_difficulty={}
            )
        
        profile = self.student_profiles[student_id]
        
        # Update recent performance
        if subject not in profile.recent_performance:
            profile.recent_performance[subject] = []
        
        score = 1.0 if answer.is_correct else 0.0
        profile.recent_performance[subject].append(score)
        
        # Keep only last 10 performances
        profile.recent_performance[subject] = profile.recent_performance[subject][-10:]
        
        # Calculate estimated ability for this subject
        recent_scores = profile.recent_performance[subject]
        if recent_scores:
            # Weight recent scores more heavily
            weights = [profile.time_based_decay ** i for i in range(len(recent_scores))]
            weights.reverse()  # Most recent gets highest weight
            
            weighted_sum = sum(score * weight for score, weight in zip(recent_scores, weights))
            weight_sum = sum(weights)
            
            profile.estimated_ability[subject] = weighted_sum / weight_sum
        
        # Calculate improvement trend
        if len(recent_scores) >= 5:
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            if second_avg > first_avg + 0.1:
                profile.improvement_trend[subject] = "improving"
            elif second_avg < first_avg - 0.1:
                profile.improvement_trend[subject] = "declining"
            else:
                profile.improvement_trend[subject] = "stable"
        
        # Update preferred difficulty based on performance
        if subject in profile.estimated_ability:
            ability = profile.estimated_ability[subject]
            if ability > 0.8:
                profile.preferred_difficulty[subject] = "ZOR"
            elif ability > 0.6:
                profile.preferred_difficulty[subject] = "ORTA"
            else:
                profile.preferred_difficulty[subject] = "KOLAY"
        
        profile.total_questions_answered += 1
        profile.last_updated = time.time()
    
    def _invalidate_cache(self, question_id: str, student_id: str):
        """Invalidate relevant caches"""
        cache_keys_to_remove = []
        for key in self.performance_cache:
            if question_id in key or student_id in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self.performance_cache[key]
    
    def get_question_quality_metrics(self, question_id: str) -> Optional[QuestionPerformance]:
        """Get quality metrics for a specific question"""
        return self.question_performance.get(question_id)
    
    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Get proficiency profile for a student"""
        return self.student_profiles.get(student_id)
    
    def get_recommended_difficulty(self, student_id: str, subject: str) -> str:
        """Get recommended difficulty for a student in a subject"""
        profile = self.student_profiles.get(student_id)
        if not profile or subject not in profile.estimated_ability:
            return "ORTA"  # Default to medium
        
        return profile.preferred_difficulty.get(subject, "ORTA")
    
    def get_low_quality_questions(self, threshold: float = 0.3) -> List[str]:
        """Get questions flagged for review due to low quality"""
        return [
            qid for qid, perf in self.question_performance.items()
            if perf.quality_score < threshold
        ]
    
    def get_subject_performance_trends(self) -> Dict[str, Dict[str, Any]]:
        """Get performance trends by subject"""
        trends = defaultdict(lambda: {
            'avg_correct_rate': 0.0,
            'avg_time_seconds': 0.0,
            'total_attempts': 0,
            'improving_students': 0,
            'declining_students': 0,
            'stable_students': 0
        })
        
        # Aggregate by subject
        subject_answers = defaultdict(list)
        for answer in self.answers:
            subject_answers[answer.subject].append(answer)
        
        for subject, answers in subject_answers.items():
            if not answers:
                continue
            
            trends[subject]['avg_correct_rate'] = sum(a.is_correct for a in answers) / len(answers)
            trends[subject]['avg_time_seconds'] = statistics.mean(a.time_spent_seconds for a in answers)
            trends[subject]['total_attempts'] = len(answers)
        
        # Count improvement trends
        for profile in self.student_profiles.values():
            for subject, trend in profile.improvement_trend.items():
                if trend == "improving":
                    trends[subject]['improving_students'] += 1
                elif trend == "declining":
                    trends[subject]['declining_students'] += 1
                else:
                    trends[subject]['stable_students'] += 1
        
        return dict(trends)
    
    def analyze_distractor_effectiveness(self, question_id: str) -> Dict[str, Any]:
        """Analyze how effective distractors are for a question"""
        question_answers = [a for a in self.answers if a.question_id == question_id]
        
        if not question_answers:
            return {}
        
        # Count selections for each option
        option_counts = defaultdict(int)
        for answer in question_answers:
            option_counts[answer.selected_answer] += 1
        
        total_attempts = len(question_answers)
        correct_answer = question_answers[0].correct_answer
        
        analysis = {
            'total_attempts': total_attempts,
            'correct_answer': correct_answer,
            'option_distribution': {},
            'distractor_effectiveness': {},
            'most_attractive_distractor': None,
            'least_attractive_distractor': None
        }
        
        # Analyze each option
        distractor_rates = {}
        for option, count in option_counts.items():
            rate = count / total_attempts
            analysis['option_distribution'][option] = {
                'count': count,
                'selection_rate': rate
            }
            
            if option != correct_answer:
                distractor_rates[option] = rate
        
        if distractor_rates:
            # Most/least attractive distractors
            analysis['most_attractive_distractor'] = max(distractor_rates.items(), key=lambda x: x[1])
            analysis['least_attractive_distractor'] = min(distractor_rates.items(), key=lambda x: x[1])
            
            # Effectiveness score (good distractors are chosen by 10-30% of students)
            for option, rate in distractor_rates.items():
                if 0.1 <= rate <= 0.3:
                    effectiveness = 1.0  # Ideal range
                elif rate < 0.05:
                    effectiveness = 0.2  # Too unattractive
                elif rate > 0.4:
                    effectiveness = 0.3  # Too attractive (might be ambiguous)
                else:
                    effectiveness = 0.7  # Acceptable
                
                analysis['distractor_effectiveness'][option] = effectiveness
        
        return analysis
    
    def export_analytics(self) -> Dict[str, Any]:
        """Export comprehensive analytics for reporting"""
        return {
            'summary': {
                'total_answers': len(self.answers),
                'unique_questions': len(self.question_performance),
                'unique_students': len(self.student_profiles),
                'overall_correct_rate': sum(a.is_correct for a in self.answers) / len(self.answers) if self.answers else 0
            },
            'question_performance': {
                qid: asdict(perf) for qid, perf in self.question_performance.items()
            },
            'student_profiles': {
                sid: asdict(profile) for sid, profile in self.student_profiles.items()
            },
            'subject_trends': self.get_subject_performance_trends(),
            'low_quality_questions': self.get_low_quality_questions(),
            'generated_at': time.time()
        }

class AdaptiveDifficultyEngine:
    """Real-time difficulty adjustment based on student performance"""
    
    def __init__(self, performance_tracker: PerformanceTracker):
        self.tracker = performance_tracker
        self.adjustment_thresholds = {
            'increase_difficulty': 0.85,  # If student gets >85% correct
            'decrease_difficulty': 0.4,   # If student gets <40% correct
            'stability_window': 5         # Need 5+ questions to adjust
        }
    
    def get_adaptive_difficulty(self, student_id: str, subject: str) -> str:
        """Get adaptive difficulty for student based on recent performance"""
        profile = self.tracker.get_student_profile(student_id)
        
        if not profile or subject not in profile.recent_performance:
            return "ORTA"  # Default for new students
        
        recent_scores = profile.recent_performance[subject]
        
        if len(recent_scores) < self.adjustment_thresholds['stability_window']:
            return profile.preferred_difficulty.get(subject, "ORTA")
        
        # Calculate recent performance
        recent_avg = statistics.mean(recent_scores[-5:])  # Last 5 questions
        
        current_difficulty = profile.preferred_difficulty.get(subject, "ORTA")
        
        # Adaptive adjustment logic
        if recent_avg >= self.adjustment_thresholds['increase_difficulty']:
            if current_difficulty == "KOLAY":
                return "ORTA"
            elif current_difficulty == "ORTA":
                return "ZOR"
            else:
                return "ZOR"  # Already at hardest
                
        elif recent_avg <= self.adjustment_thresholds['decrease_difficulty']:
            if current_difficulty == "ZOR":
                return "ORTA"
            elif current_difficulty == "ORTA":
                return "KOLAY"
            else:
                return "KOLAY"  # Already at easiest
        
        return current_difficulty  # No change needed
    
    def should_adjust_difficulty(self, student_id: str, subject: str) -> Tuple[bool, str, str]:
        """Check if difficulty should be adjusted and return recommended change"""
        profile = self.tracker.get_student_profile(student_id)
        
        if not profile:
            return False, "", ""
        
        current_difficulty = profile.preferred_difficulty.get(subject, "ORTA")
        recommended_difficulty = self.get_adaptive_difficulty(student_id, subject)
        
        should_adjust = current_difficulty != recommended_difficulty
        
        return should_adjust, current_difficulty, recommended_difficulty

# Global instances
performance_tracker = PerformanceTracker()
adaptive_engine = AdaptiveDifficultyEngine(performance_tracker)

def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance"""
    return performance_tracker

def get_adaptive_engine() -> AdaptiveDifficultyEngine:
    """Get global adaptive difficulty engine instance"""
    return adaptive_engine