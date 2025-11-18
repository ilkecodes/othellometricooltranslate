#!/usr/bin/env python3
"""
Teacher Analytics System - Comprehensive Demo
Demonstrates all teacher dashboard features and analytics capabilities
"""

import os
import sys
import time
import random
import json
from typing import Dict, List

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.teacher_analytics import (
    TeacherAnalyticsEngine,
    QuestionSubmission,
    VideoRecommendation,
    AlertType,
    PerformanceTrend
)

def create_sample_data():
    """Create comprehensive sample data for demonstration"""
    print("🎯 Creating Teacher Analytics Demo Environment...")
    
    # Initialize analytics engine
    analytics = TeacherAnalyticsEngine()
    
    # Setup teachers and classes
    print("\n📚 Setting up Teachers and Classes...")
    
    # Teacher 1: Math teacher (also homeroom for 8A)
    analytics.register_teacher_access(
        teacher_id="teacher_math_001",
        class_ids=["class_8A", "class_8B"],
        subjects=["Matematik"],
        is_homeroom=True
    )
    
    # Teacher 2: Science teacher
    analytics.register_teacher_access(
        teacher_id="teacher_science_001",
        class_ids=["class_8A", "class_8B", "class_8C"],
        subjects=["Fen Bilimleri"]
    )
    
    # Teacher 3: Turkish teacher
    analytics.register_teacher_access(
        teacher_id="teacher_turkish_001",
        class_ids=["class_8A"],
        subjects=["Türkçe"]
    )
    
    # Add students to classes
    print("👥 Adding Students to Classes...")
    
    # Class 8A students
    class_8a_students = [f"student_8a_{i:03d}" for i in range(1, 26)]  # 25 students
    analytics.add_students_to_class("teacher_math_001", "class_8A", class_8a_students)
    analytics.add_students_to_class("teacher_science_001", "class_8A", class_8a_students)
    analytics.add_students_to_class("teacher_turkish_001", "class_8A", class_8a_students)
    
    # Class 8B students  
    class_8b_students = [f"student_8b_{i:03d}" for i in range(1, 24)]  # 23 students
    analytics.add_students_to_class("teacher_math_001", "class_8B", class_8b_students)
    analytics.add_students_to_class("teacher_science_001", "class_8B", class_8b_students)
    
    # Class 8C students
    class_8c_students = [f"student_8c_{i:03d}" for i in range(1, 27)]  # 26 students
    analytics.add_students_to_class("teacher_science_001", "class_8C", class_8c_students)
    
    print(f"   ✅ Added {len(class_8a_students)} students to Class 8A")
    print(f"   ✅ Added {len(class_8b_students)} students to Class 8B") 
    print(f"   ✅ Added {len(class_8c_students)} students to Class 8C")
    
    # Create video library
    print("\n📺 Setting up Video Library...")
    
    sample_videos = [
        # Math videos
        VideoRecommendation(
            video_id="math_001",
            title="Rasyonel Sayılar - Temel Kavramlar",
            subject="Matematik",
            topic="Rasyonel Sayılar",
            learning_outcome="Rasyonel sayıları tanır ve örnekler verir",
            difficulty="KOLAY",
            duration_minutes=15,
            description="Rasyonel sayıların temel özelliklerini açıklayan interaktif video",
            relevance_score=0.85,
            assigned_to=[]
        ),
        VideoRecommendation(
            video_id="math_002",
            title="Cebirsel İfadeler ve Özdeşlikler",
            subject="Matematik",
            topic="Cebirsel İfadeler", 
            learning_outcome="Cebirsel ifadeleri sadeleştirir ve çarpanlarına ayırır",
            difficulty="ORTA",
            duration_minutes=22,
            description="Cebirsel ifadelerin sadeleştirilmesi ve çarpanlara ayırma teknikleri",
            relevance_score=0.78,
            assigned_to=[]
        ),
        VideoRecommendation(
            video_id="math_003",
            title="Üçgenlerde Açı-Kenar İlişkileri",
            subject="Matematik",
            topic="Üçgenler",
            learning_outcome="Üçgenlerde açı ve kenar arasındaki ilişkileri açıklar",
            difficulty="ZOR",
            duration_minutes=28,
            description="Üçgenlerde açı-kenar ilişkileri ve uygulamaları",
            relevance_score=0.82,
            assigned_to=[]
        ),
        
        # Science videos
        VideoRecommendation(
            video_id="sci_001",
            title="Hücre Bölünmesi ve Mitoz",
            subject="Fen Bilimleri",
            topic="Hücre Bölünmesi",
            learning_outcome="Mitoz bölünme evrelerini sıralar ve açıklar",
            difficulty="ORTA",
            duration_minutes=18,
            description="Mitoz bölünme sürecini animasyonlarla detaylı anlatan video",
            relevance_score=0.90,
            assigned_to=[]
        ),
        VideoRecommendation(
            video_id="sci_002", 
            title="Kalıtım ve Mendel Kanunları",
            subject="Fen Bilimleri",
            topic="Kalıtım",
            learning_outcome="Kalıtım kanunlarını örneklerle açıklar",
            difficulty="ZOR",
            duration_minutes=25,
            description="Mendel'in kalıtım kanunları ve modern genetik uygulamaları",
            relevance_score=0.88,
            assigned_to=[]
        ),
        VideoRecommendation(
            video_id="sci_003",
            title="Asit-Baz Tepkimeleri",
            subject="Fen Bilimleri", 
            topic="Asit-Baz",
            learning_outcome="Asit ve bazların özelliklerini karşılaştırır",
            difficulty="KOLAY",
            duration_minutes=16,
            description="Asit-baz kavramları ve günlük yaşamdaki örnekleri",
            relevance_score=0.86,
            assigned_to=[]
        ),
        
        # Turkish videos
        VideoRecommendation(
            video_id="tur_001",
            title="Metin Analizi ve Ana Fikir Bulma",
            subject="Türkçe",
            topic="Metin Analizi",
            learning_outcome="Metnin ana fikrini ve yan fikirlerini belirler",
            difficulty="ORTA",
            duration_minutes=20,
            description="Farklı metin türlerinde ana fikir bulma teknikleri",
            relevance_score=0.84,
            assigned_to=[]
        ),
        VideoRecommendation(
            video_id="tur_002",
            title="Yazım ve Noktalama Kuralları",
            subject="Türkçe",
            topic="Yazım Kuralları",
            learning_outcome="Yazım ve noktalama kurallarını doğru uygular",
            difficulty="KOLAY",
            duration_minutes=14,
            description="Temel yazım ve noktalama kurallarının uygulamalı anlatımı",
            relevance_score=0.80,
            assigned_to=[]
        )
    ]
    
    analytics.video_library.extend(sample_videos)
    print(f"   ✅ Added {len(sample_videos)} videos to library")
    
    return analytics

def generate_realistic_submissions(analytics: TeacherAnalyticsEngine):
    """Generate realistic question submissions with various performance patterns"""
    
    print("\n📝 Generating Realistic Student Submissions...")
    
    # Define curriculum topics and learning outcomes
    curriculum = {
        "Matematik": {
            "Rasyonel Sayılar": [
                "Rasyonel sayıları tanır ve örnekler verir",
                "Rasyonel sayılarla işlemler yapar",
                "Rasyonel sayıları sayı doğrusunda gösterir"
            ],
            "Cebirsel İfadeler": [
                "Cebirsel ifadeleri sadeleştirir ve çarpanlarına ayırır",
                "Özdeşlikleri kullanarak çarpanlara ayırır",
                "Cebirsel ifadelerde işlemler yapar"
            ],
            "Üçgenler": [
                "Üçgenlerde açı ve kenar arasındaki ilişkileri açıklar",
                "Üçgen eşitsizliğini uygular",
                "Özel üçgenlerin özelliklerini kullanır"
            ],
            "Denklemler": [
                "Birinci dereceden denklemleri çözer",
                "Denklem kurma problemlerini çözer",
                "Eşitsizlikleri çözer ve grafik üzerinde gösterir"
            ]
        },
        "Fen Bilimleri": {
            "Hücre Bölünmesi": [
                "Mitoz bölünme evrelerini sıralar ve açıklar",
                "Mayoz bölünmenin önemini açıklar",
                "Hücre döngüsünü analiz eder"
            ],
            "Kalıtım": [
                "Kalıtım kanunlarını örneklerle açıklar",
                "Dominant ve çekinik karakterleri ayırt eder",
                "Kalıtsal hastalıkları açıklar"
            ],
            "Asit-Baz": [
                "Asit ve bazların özelliklerini karşılaştırır",
                "pH kavramını açıklar ve ölçer",
                "Asit-baz tepkimelerini yazar"
            ],
            "Kuvvet ve Hareket": [
                "Newton'un hareket yasalarını açıklar",
                "Kuvvet ve hareket arasındaki ilişkiyi analiz eder",
                "Hız ve ivme kavramlarını kullanır"
            ]
        },
        "Türkçe": {
            "Metin Analizi": [
                "Metnin ana fikrini ve yan fikirlerini belirler",
                "Metnin türünü ve özelliklerini belirler",
                "Metindeki olay örgüsünü çıkarır"
            ],
            "Yazım Kuralları": [
                "Yazım ve noktalama kurallarını doğru uygular",
                "Büyük-küçük harf kurallarını uygular",
                "Kesme işaretini doğru kullanır"
            ],
            "Sözcük Türleri": [
                "Sözcükleri türlerine göre ayırt eder",
                "İsim tamlamalarını çözümler",
                "Fiil çekimlerini yapar"
            ]
        }
    }
    
    # Define student performance profiles
    all_students = []
    for class_id in ["class_8A", "class_8B", "class_8C"]:
        if class_id == "class_8A":
            all_students.extend([f"student_8a_{i:03d}" for i in range(1, 26)])
        elif class_id == "class_8B":
            all_students.extend([f"student_8b_{i:03d}" for i in range(1, 24)])
        else:
            all_students.extend([f"student_8c_{i:03d}" for i in range(1, 27)])
    
    # Create diverse student performance profiles
    student_profiles = {}
    
    for student_id in all_students:
        # Randomly assign performance characteristics
        profile_type = random.choice([
            "high_performer",      # 15% - consistently high performance
            "average_steady",      # 35% - steady average performance  
            "math_struggling",     # 20% - struggles specifically with math
            "science_strong",      # 15% - strong in science, average elsewhere
            "declining",           # 10% - performance declining over time
            "inconsistent"         # 5% - very inconsistent performance
        ])
        
        if profile_type == "high_performer":
            base_accuracy = 0.85
            subject_modifiers = {"Matematik": 0.05, "Fen Bilimleri": 0.03, "Türkçe": 0.02}
        elif profile_type == "average_steady":
            base_accuracy = 0.65
            subject_modifiers = {"Matematik": 0.0, "Fen Bilimleri": 0.0, "Türkçe": 0.0}
        elif profile_type == "math_struggling":
            base_accuracy = 0.60
            subject_modifiers = {"Matematik": -0.25, "Fen Bilimleri": 0.05, "Türkçe": 0.10}
        elif profile_type == "science_strong":
            base_accuracy = 0.65
            subject_modifiers = {"Matematik": 0.0, "Fen Bilimleri": 0.20, "Türkçe": -0.05}
        elif profile_type == "declining":
            base_accuracy = 0.70
            subject_modifiers = {"Matematik": 0.0, "Fen Bilimleri": 0.0, "Türkçe": 0.0}
        else:  # inconsistent
            base_accuracy = 0.55
            subject_modifiers = {"Matematik": 0.0, "Fen Bilimleri": 0.0, "Türkçe": 0.0}
        
        student_profiles[student_id] = {
            "type": profile_type,
            "base_accuracy": base_accuracy,
            "subject_modifiers": subject_modifiers
        }
    
    # Generate submissions over the past 30 days
    current_time = time.time()
    start_time = current_time - (30 * 24 * 60 * 60)  # 30 days ago
    
    submissions_generated = 0
    difficulties = ["KOLAY", "ORTA", "ZOR"]
    
    for day in range(30):  # Generate for each of the past 30 days
        day_timestamp = start_time + (day * 24 * 60 * 60)
        
        # Vary daily activity (more on weekdays, less on weekends)
        day_of_week = day % 7
        if day_of_week >= 5:  # Weekend
            daily_questions_per_student = random.randint(2, 6)
        else:  # Weekday
            daily_questions_per_student = random.randint(8, 20)
        
        for student_id in all_students:
            profile = student_profiles[student_id]
            
            # Determine which subjects this student has today
            class_id = student_id.split('_')[1].upper()
            available_subjects = []
            
            if class_id in ["8A", "8B"]:
                available_subjects = ["Matematik", "Fen Bilimleri"]
            if class_id == "8A":
                available_subjects.append("Türkçe")
            if class_id == "8C":
                available_subjects = ["Fen Bilimleri"]
            
            for _ in range(daily_questions_per_student):
                subject = random.choice(available_subjects)
                topic = random.choice(list(curriculum[subject].keys()))
                learning_outcome = random.choice(curriculum[subject][topic])
                difficulty = random.choice(difficulties)
                
                # Calculate accuracy based on student profile
                base_acc = profile["base_accuracy"]
                subject_modifier = profile["subject_modifiers"].get(subject, 0)
                
                # Apply profile-specific modifications
                if profile["type"] == "declining":
                    decline_factor = day / 30 * 0.3  # Decline by up to 30% over 30 days
                    accuracy = base_acc - decline_factor
                elif profile["type"] == "inconsistent":
                    accuracy = base_acc + random.uniform(-0.4, 0.4)  # High variance
                else:
                    accuracy = base_acc + subject_modifier
                
                # Apply difficulty modifier
                if difficulty == "KOLAY":
                    accuracy += 0.15
                elif difficulty == "ZOR":
                    accuracy -= 0.20
                
                # Ensure accuracy stays in valid range
                accuracy = max(0.05, min(0.98, accuracy))
                
                # Determine if correct
                is_correct = random.random() < accuracy
                
                # Generate realistic timing (30 seconds to 8 minutes)
                base_time = 120  # 2 minutes base
                if difficulty == "KOLAY":
                    time_spent = random.randint(30, 180)
                elif difficulty == "ORTA":
                    time_spent = random.randint(60, 300)
                else:  # ZOR
                    time_spent = random.randint(90, 480)
                
                # Add individual variation
                time_spent = int(time_spent * random.uniform(0.7, 1.5))
                
                # Create submission
                submission = QuestionSubmission(
                    submission_id=f"sub_{day:02d}_{student_id}_{submissions_generated:04d}",
                    student_id=student_id,
                    question_id=f"q_{random.randint(10000, 99999)}",
                    class_id=f"class_{class_id}",
                    subject=subject,
                    topic=topic,
                    learning_outcome=learning_outcome,
                    difficulty=difficulty,
                    selected_answer=random.choice(["A", "B", "C", "D"]),
                    correct_answer=random.choice(["A", "B", "C", "D"]),
                    is_correct=is_correct,
                    time_spent_seconds=time_spent,
                    timestamp=day_timestamp + random.randint(0, 24*60*60),  # Random time during the day
                    session_id=f"session_{day}_{student_id}_{random.randint(100, 999)}",
                    teacher_id="teacher_math_001" if subject == "Matematik" else (
                        "teacher_science_001" if subject == "Fen Bilimleri" else "teacher_turkish_001"
                    )
                )
                
                analytics.record_question_submission(submission)
                submissions_generated += 1
        
        # Show progress
        if (day + 1) % 5 == 0:
            print(f"   📊 Generated submissions for day {day + 1}/30...")
    
    print(f"   ✅ Generated {submissions_generated:,} realistic submissions")
    print(f"   📈 Created {len(analytics.active_alerts)} alerts")
    
    return submissions_generated

def demonstrate_teacher_dashboards(analytics: TeacherAnalyticsEngine):
    """Demonstrate all teacher dashboard features"""
    
    print("\n" + "="*80)
    print("🎯 TEACHER ANALYTICS SYSTEM DEMONSTRATION")
    print("="*80)
    
    # 1. Class Overview Dashboard
    print("\n📊 1. CLASS OVERVIEW DASHBOARD")
    print("-" * 50)
    
    try:
        class_overview = analytics.get_class_overview("teacher_math_001", "class_8A")
        
        print(f"📚 Class: {class_overview['class_id']}")
        print(f"👥 Students: {class_overview['student_count']}")
        print(f"📝 Total Submissions: {class_overview['total_submissions']:,}")
        
        print(f"\n🔥 Topics with Highest Struggle:")
        for i, topic in enumerate(class_overview['topics_with_highest_struggle'][:3], 1):
            print(f"   {i}. {topic['subject']} - {topic['topic']}: {topic['struggle_rate']:.1%} struggle rate")
        
        print(f"\n📉 Learning Outcomes with Dropping Performance:")
        for i, lo in enumerate(class_overview['los_with_dropping_performance'][:3], 1):
            print(f"   {i}. {lo['learning_outcome']}: {lo['drop_amount']:.1%} decline")
        
        print(f"\n❌ Top Mistake Patterns:")
        for i, pattern in enumerate(class_overview['top_mistake_patterns'][:3], 1):
            print(f"   {i}. {pattern['pattern']} ({pattern['frequency']} times)")
        
        print(f"\n📈 7-Day Trend: {class_overview['seven_day_trend']['trend']} "
              f"({class_overview['seven_day_trend']['change_rate']:+.1%})")
        
        print(f"\n🚨 Active Alerts: {len(class_overview['active_alerts'])}")
        for alert in class_overview['active_alerts'][:3]:
            print(f"   • {alert['severity'].upper()}: {alert['message']}")
            
    except Exception as e:
        print(f"❌ Error in class overview: {e}")
    
    # 2. Student Profile Dashboard
    print("\n👤 2. STUDENT PROFILE DASHBOARD")
    print("-" * 50)
    
    # Select a student who has some interesting patterns
    sample_student = "student_8a_005"
    
    try:
        student_profile = analytics.get_student_profile("teacher_math_001", sample_student)
        
        print(f"🎓 Student: {student_profile['student_id']}")
        print(f"📊 Questions Solved: {student_profile['total_questions_solved']:,}")
        print(f"🎯 Overall Accuracy: {student_profile['overall_accuracy']:.1%}")
        
        print(f"\n💪 Strongest Topics:")
        for i, topic in enumerate(student_profile['strongest_topics'][-3:], 1):
            print(f"   {i}. {topic['subject']} - {topic['topic']}: {topic['accuracy']:.1%}")
        
        print(f"\n😰 Weakest Topics:")
        for i, topic in enumerate(student_profile['weakest_topics'][:3], 1):
            print(f"   {i}. {topic['subject']} - {topic['topic']}: {topic['accuracy']:.1%}")
        
        print(f"\n🔄 Repeatedly Failed Learning Outcomes:")
        for i, lo in enumerate(student_profile['repeatedly_failed_los'][:3], 1):
            print(f"   {i}. {lo['learning_outcome']}: {lo['accuracy']:.1%} "
                  f"({lo['consecutive_errors']} consecutive errors)")
        
        print(f"\n⏱️ Time Analysis:")
        time_analysis = student_profile['time_analysis']
        if time_analysis:
            print(f"   Average time per question: {time_analysis['avg_time_per_question']:.0f}s")
            print(f"   Fastest question: {time_analysis['min_time']}s")
            print(f"   Slowest question: {time_analysis['max_time']}s")
        
        print(f"\n🚨 Active Alerts: {len(student_profile['active_alerts'])}")
        for alert in student_profile['active_alerts']:
            print(f"   • {alert['severity'].upper()}: {alert['message']}")
            
    except Exception as e:
        print(f"❌ Error in student profile: {e}")
    
    # 3. Learning Outcome Deep Analysis
    print("\n🔍 3. LEARNING OUTCOME DEEP ANALYSIS")
    print("-" * 50)
    
    try:
        lo_analysis = analytics.get_lo_deep_analysis(
            "teacher_math_001", 
            "Rasyonel sayıları tanır ve örnekler verir",
            "Matematik"
        )
        
        print(f"📚 Learning Outcome: {lo_analysis.learning_outcome}")
        print(f"📊 Average Class Accuracy: {lo_analysis.avg_accuracy:.1%}")
        
        print(f"\n🔝 Top Performers:")
        for i, student_id in enumerate(lo_analysis.top_performers, 1):
            accuracy = lo_analysis.class_performance.get(student_id, 0)
            print(f"   {i}. {student_id}: {accuracy:.1%}")
        
        print(f"\n😟 Struggling Students:")
        for i, student_id in enumerate(lo_analysis.worst_performers, 1):
            accuracy = lo_analysis.class_performance.get(student_id, 0)
            print(f"   {i}. {student_id}: {accuracy:.1%}")
        
        print(f"\n📊 Difficulty Breakdown:")
        for difficulty, stats in lo_analysis.difficulty_breakdown.items():
            total = stats['total']
            correct = stats['correct']
            accuracy = correct / total if total > 0 else 0
            print(f"   {difficulty}: {accuracy:.1%} ({correct}/{total})")
        
        print(f"\n❌ Common Mistakes:")
        for i, mistake in enumerate(lo_analysis.common_mistakes, 1):
            print(f"   {i}. {mistake}")
        
        print(f"\n💡 Recommended Interventions:")
        for i, intervention in enumerate(lo_analysis.recommended_interventions, 1):
            print(f"   {i}. {intervention}")
            
    except Exception as e:
        print(f"❌ Error in LO analysis: {e}")
    
    # 4. Video Recommendation Engine
    print("\n📺 4. VIDEO RECOMMENDATION ENGINE")
    print("-" * 50)
    
    try:
        recommendations = analytics.generate_video_recommendations(sample_student, limit=3)
        
        if recommendations:
            print(f"🎯 Recommendations for {sample_student}:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec.title}")
                print(f"      📚 {rec.subject} - {rec.topic}")
                print(f"      🎯 LO: {rec.learning_outcome}")
                print(f"      ⭐ Relevance: {rec.relevance_score:.2f}")
                print(f"      ⏱️ Duration: {rec.duration_minutes} minutes")
                print()
        else:
            print("No recommendations available (insufficient data)")
            
    except Exception as e:
        print(f"❌ Error in video recommendations: {e}")
    
    # 5. Alert System Demonstration
    print("\n🚨 5. ALERT SYSTEM (RED ZONE)")
    print("-" * 50)
    
    active_alerts = [alert for alert in analytics.active_alerts if alert.is_active]
    
    print(f"Total Active Alerts: {len(active_alerts)}")
    
    # Group by severity
    by_severity = {}
    for alert in active_alerts:
        by_severity.setdefault(alert.severity, []).append(alert)
    
    for severity in ["critical", "high", "medium", "low"]:
        if severity in by_severity:
            print(f"\n🚨 {severity.upper()} ALERTS ({len(by_severity[severity])}):")
            for alert in by_severity[severity][:3]:  # Show top 3
                print(f"   • Student {alert.student_id} - {alert.subject}")
                print(f"     {alert.message}")
                print(f"     Recommended Actions:")
                for action in alert.recommended_actions[:2]:
                    print(f"       - {action}")
                print()
    
    # 6. Mini-Test Generation
    print("\n📝 6. MINI-TEST GENERATION")
    print("-" * 50)
    
    try:
        # Find students struggling with a specific LO
        struggling_students = []
        for student_id in ["student_8a_001", "student_8a_002", "student_8a_003"]:
            lo_accuracy = analytics._calculate_lo_performance(
                student_id, 
                "Rasyonel sayıları tanır ve örnekler verir"
            )
            if lo_accuracy < 0.6:
                struggling_students.append(student_id)
        
        if struggling_students:
            mini_test = analytics.generate_mini_test(
                "teacher_math_001",
                struggling_students,
                "Rasyonel sayıları tanır ve örnekler verir",
                question_count=7
            )
            
            print(f"📝 Mini-test Generated: {mini_test['test_id']}")
            print(f"🎯 Learning Outcome: {mini_test['learning_outcome']}")
            print(f"👥 Assigned to: {len(mini_test['assigned_to'])} students")
            print(f"❓ Questions: {mini_test['question_count']}")
            print(f"⏰ Time Limit: {mini_test['time_limit_minutes']} minutes")
            
            print(f"\n📊 Difficulty Recommendations:")
            for student_id, difficulty in mini_test['difficulty_recommendations'].items():
                print(f"   {student_id}: {difficulty}")
        else:
            print("No struggling students found for mini-test generation")
            
    except Exception as e:
        print(f"❌ Error in mini-test generation: {e}")

def demonstrate_analytics_insights(analytics: TeacherAnalyticsEngine):
    """Demonstrate advanced analytics insights"""
    
    print("\n" + "="*80)
    print("📈 ADVANCED ANALYTICS INSIGHTS")
    print("="*80)
    
    # Performance Statistics
    print("\n📊 SYSTEM STATISTICS")
    print("-" * 50)
    
    total_submissions = len(analytics.submissions)
    total_students = len(set(s.student_id for s in analytics.submissions))
    total_teachers = len(analytics.class_rosters)
    
    print(f"📝 Total Submissions: {total_submissions:,}")
    print(f"👥 Total Students: {total_students}")
    print(f"👨‍🏫 Total Teachers: {total_teachers}")
    print(f"🎯 Total Learning Outcomes: {len(set(s.learning_outcome for s in analytics.submissions))}")
    print(f"📚 Total Topics: {len(set(f'{s.subject}:{s.topic}' for s in analytics.submissions))}")
    
    # Subject Performance Breakdown
    print(f"\n📚 SUBJECT PERFORMANCE BREAKDOWN")
    print("-" * 50)
    
    subject_stats = {}
    for submission in analytics.submissions:
        if submission.subject not in subject_stats:
            subject_stats[submission.subject] = {'correct': 0, 'total': 0}
        subject_stats[submission.subject]['total'] += 1
        if submission.is_correct:
            subject_stats[submission.subject]['correct'] += 1
    
    for subject, stats in subject_stats.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        print(f"{subject:15}: {accuracy:.1%} accuracy ({stats['correct']:,}/{stats['total']:,} questions)")
    
    # Difficulty Analysis
    print(f"\n🎯 DIFFICULTY ANALYSIS")
    print("-" * 50)
    
    difficulty_stats = {}
    for submission in analytics.submissions:
        if submission.difficulty not in difficulty_stats:
            difficulty_stats[submission.difficulty] = {'correct': 0, 'total': 0, 'times': []}
        difficulty_stats[submission.difficulty]['total'] += 1
        difficulty_stats[submission.difficulty]['times'].append(submission.time_spent_seconds)
        if submission.is_correct:
            difficulty_stats[submission.difficulty]['correct'] += 1
    
    for difficulty, stats in difficulty_stats.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
        print(f"{difficulty:8}: {accuracy:.1%} accuracy, {avg_time:.0f}s avg time ({stats['total']:,} questions)")
    
    # Alert Analysis
    print(f"\n🚨 ALERT ANALYSIS")
    print("-" * 50)
    
    alert_stats = {}
    for alert in analytics.active_alerts:
        if alert.alert_type not in alert_stats:
            alert_stats[alert.alert_type] = {'total': 0, 'by_severity': {}}
        alert_stats[alert.alert_type]['total'] += 1
        
        severity = alert.severity
        if severity not in alert_stats[alert.alert_type]['by_severity']:
            alert_stats[alert.alert_type]['by_severity'][severity] = 0
        alert_stats[alert.alert_type]['by_severity'][severity] += 1
    
    for alert_type, stats in alert_stats.items():
        print(f"{alert_type:20}: {stats['total']} alerts")
        for severity, count in stats['by_severity'].items():
            print(f"  └─ {severity:8}: {count}")
    
    # Top Problematic Learning Outcomes
    print(f"\n❌ MOST PROBLEMATIC LEARNING OUTCOMES")
    print("-" * 50)
    
    lo_performance = {}
    for submission in analytics.submissions:
        lo = submission.learning_outcome
        if lo not in lo_performance:
            lo_performance[lo] = {'correct': 0, 'total': 0}
        lo_performance[lo]['total'] += 1
        if submission.is_correct:
            lo_performance[lo]['correct'] += 1
    
    # Calculate accuracy and sort by worst performance
    lo_accuracies = []
    for lo, stats in lo_performance.items():
        if stats['total'] >= 10:  # Minimum sample size
            accuracy = stats['correct'] / stats['total']
            lo_accuracies.append((lo, accuracy, stats['total']))
    
    lo_accuracies.sort(key=lambda x: x[1])  # Sort by accuracy (worst first)
    
    for i, (lo, accuracy, total) in enumerate(lo_accuracies[:5], 1):
        print(f"{i}. {accuracy:.1%} - {lo} ({total} attempts)")
    
    # Time Efficiency Analysis
    print(f"\n⏱️ TIME EFFICIENCY ANALYSIS")
    print("-" * 50)
    
    # Calculate time vs accuracy correlation
    fast_submissions = [s for s in analytics.submissions if s.time_spent_seconds <= 60]
    medium_submissions = [s for s in analytics.submissions if 60 < s.time_spent_seconds <= 180]
    slow_submissions = [s for s in analytics.submissions if s.time_spent_seconds > 180]
    
    def calc_accuracy(submissions):
        return sum(s.is_correct for s in submissions) / len(submissions) if submissions else 0
    
    print(f"Quick answers (≤60s): {calc_accuracy(fast_submissions):.1%} accuracy ({len(fast_submissions):,} questions)")
    print(f"Medium time (60-180s): {calc_accuracy(medium_submissions):.1%} accuracy ({len(medium_submissions):,} questions)")
    print(f"Slow answers (>180s): {calc_accuracy(slow_submissions):.1%} accuracy ({len(slow_submissions):,} questions)")

def main():
    """Main demonstration function"""
    print("🚀 Starting Teacher Analytics System Demo...")
    
    # Create sample data
    analytics = create_sample_data()
    
    # Generate realistic submissions
    generate_realistic_submissions(analytics)
    
    # Demonstrate teacher dashboards
    demonstrate_teacher_dashboards(analytics)
    
    # Show analytics insights
    demonstrate_analytics_insights(analytics)
    
    print("\n" + "="*80)
    print("🎉 TEACHER ANALYTICS SYSTEM DEMO COMPLETE")
    print("="*80)
    
    print(f"\n📋 SUMMARY:")
    print(f"   📝 {len(analytics.submissions):,} question submissions processed")
    print(f"   👥 {len(set(s.student_id for s in analytics.submissions))} students analyzed")
    print(f"   🚨 {len([a for a in analytics.active_alerts if a.is_active])} active alerts generated")
    print(f"   📺 {len(analytics.video_library)} videos available for recommendations")
    print(f"   🎯 Real-time performance tracking and adaptive recommendations working")
    
    print(f"\n💡 KEY FEATURES DEMONSTRATED:")
    print(f"   ✅ Class Overview Dashboard with struggle analysis")
    print(f"   ✅ Detailed Student Performance Profiles")
    print(f"   ✅ Learning Outcome Deep Analysis")
    print(f"   ✅ Intelligent Video Recommendation Engine")
    print(f"   ✅ Real-time Alert System (Red Zone)")
    print(f"   ✅ Adaptive Mini-test Generation")
    print(f"   ✅ Comprehensive Analytics and Insights")
    
    print(f"\n🎓 The system successfully tracks every solved question, identifies")
    print(f"   weaknesses, and generates actionable insights for teachers!")

if __name__ == "__main__":
    main()