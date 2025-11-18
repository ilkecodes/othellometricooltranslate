#!/usr/bin/env python3
"""
Seed the comprehensive LGS questions from 2018-2025 into the database
"""

import sys
import os
import json
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from seed_questions_sql import seed_questions
except ImportError:
    print("❌ Error: Could not import seed_questions_sql")
    print("   Make sure you're running this from the backend directory")
    sys.exit(1)


def load_comprehensive_questions(file_path: str) -> List[Dict]:
    """Load questions from the comprehensive JSONL file"""
    questions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    question_data = json.loads(line.strip())
                    
                    # Convert to the expected format for seed_questions
                    question = convert_to_seed_format(question_data)
                    if question:
                        questions.append(question)
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ Warning: Skipping invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    print(f"⚠️ Warning: Error processing line {line_num}: {e}")
    
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []
    
    return questions


def convert_to_seed_format(question_data: Dict) -> Dict:
    """Convert comprehensive question format to seed_questions format"""
    try:
        # Map subjects to the expected format
        subject_mapping = {
            'TURKISH': 'TURKISH',
            'MATH': 'MATH',
            'SCIENCE': 'SCIENCE',
            'SOCIAL_STUDIES': 'SOCIAL_STUDIES',
            'RELIGION': 'RELIGION',
            'ENGLISH': 'ENGLISH'
        }
        
        subject_code = subject_mapping.get(question_data.get('subject', ''), 'TURKISH')
        
        # Create topic name based on subject and year
        topic_base = question_data.get('topic_name', f"{subject_code} Konusu")
        year = question_data.get('year', 2024)
        topic_name = f"{topic_base} ({year} LGS)"
        
        # Build options in the expected format
        options = []
        for opt in question_data.get('options', []):
            option = {
                'label': opt.get('key', 'A'),
                'text': opt.get('text', ''),
                'is_correct': opt.get('is_correct', False)
            }
            options.append(option)
        
        # Ensure we have 4 options
        while len(options) < 4:
            options.append({
                'label': chr(ord('A') + len(options)),
                'text': 'Seçenek mevcut değil',
                'is_correct': False
            })
        
        question = {
            'subject_code': subject_code,
            'topic_name': topic_name,
            'difficulty': question_data.get('difficulty', 'MEDIUM'),
            'stem_text': question_data.get('stem', ''),
            'estimated_time_seconds': question_data.get('estimated_time_seconds', 90),
            'options': options,
            # Add metadata
            'source_year': year,
            'extraction_method': question_data.get('processing_method', 'comprehensive'),
            'confidence': question_data.get('confidence', 'high'),
            'question_number': question_data.get('question_number'),
        }
        
        # Validate question
        if not question['stem_text'].strip() or len(question['options']) < 4:
            return None
        
        return question
        
    except Exception as e:
        print(f"⚠️ Error converting question: {e}")
        return None


def analyze_questions(questions: List[Dict]) -> Dict:
    """Analyze the questions to show distribution"""
    stats = {
        'total': len(questions),
        'by_subject': {},
        'by_year': {},
        'by_difficulty': {},
        'by_method': {},
        'by_confidence': {}
    }
    
    for q in questions:
        # Subject distribution
        subject = q.get('subject_code', 'UNKNOWN')
        stats['by_subject'][subject] = stats['by_subject'].get(subject, 0) + 1
        
        # Year distribution
        year = q.get('source_year', 'UNKNOWN')
        stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        # Difficulty distribution
        difficulty = q.get('difficulty', 'UNKNOWN')
        stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
        
        # Method distribution
        method = q.get('extraction_method', 'UNKNOWN')
        stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
        
        # Confidence distribution
        confidence = q.get('confidence', 'UNKNOWN')
        stats['by_confidence'][confidence] = stats['by_confidence'].get(confidence, 0) + 1
    
    return stats


def print_analysis(stats: Dict):
    """Print comprehensive analysis of the questions"""
    print(f"\n📊 COMPREHENSIVE LGS QUESTIONS ANALYSIS")
    print("=" * 60)
    print(f"📝 Total Questions: {stats['total']}")
    
    print(f"\n📚 By Subject:")
    for subject, count in sorted(stats['by_subject'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {subject}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n📅 By Year:")
    for year, count in sorted(stats['by_year'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {year}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n⭐ By Difficulty:")
    for difficulty, count in sorted(stats['by_difficulty'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {difficulty}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n🔬 By Extraction Method:")
    for method, count in sorted(stats['by_method'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {method}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n🎯 By Confidence Level:")
    for confidence, count in sorted(stats['by_confidence'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {confidence}: {count} questions ({percentage:.1f}%)")


def main():
    """Main seeding function"""
    file_path = "comprehensive_lgs_2018_2025.jsonl"
    
    print("🌱 COMPREHENSIVE LGS QUESTIONS SEEDER")
    print("=" * 50)
    print(f"📖 Loading questions from: {file_path}")
    
    # Load questions
    questions = load_comprehensive_questions(file_path)
    if not questions:
        print("❌ No valid questions found to seed")
        return
    
    # Analyze questions
    stats = analyze_questions(questions)
    print_analysis(stats)
    
    print(f"\n📋 Sample Questions:")
    for i, q in enumerate(questions[:3]):
        print(f"\n   Q{i+1}: [{q['difficulty']}] [{q['subject_code']}]")
        print(f"      {q['stem_text'][:80]}...")
        for opt in q['options']:
            flag = "✅" if opt['is_correct'] else "  "
            print(f"      {flag} {opt['label']}) {opt['text'][:50]}...")
    
    # Confirm before seeding
    print(f"\n🤔 Ready to seed {len(questions)} questions to database")
    print("   This will add questions with topics like:")
    
    # Show unique topics
    topics = set()
    for q in questions:
        topics.add(q['topic_name'])
    
    for i, topic in enumerate(sorted(list(topics))[:10]):
        print(f"   • {topic}")
    
    if len(topics) > 10:
        print(f"   • ... and {len(topics) - 10} more topics")
    
    response = input(f"\n❓ Proceed with seeding {len(questions)} comprehensive LGS questions? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Seeding cancelled")
        return
    
    # Seed the questions
    print(f"\n🌱 Seeding {len(questions)} questions to database...")
    
    try:
        seed_questions(questions)
        print(f"\n✅ Successfully seeded {len(questions)} comprehensive LGS questions!")
        print("📊 Database now contains questions from LGS exams 2018-2025")
        print("🎯 Next steps:")
        print("   1. Generate new LGS bundles with expanded authentic content")
        print("   2. Test the platform with the enhanced question database")
        print("   3. Review question quality and adjust as needed")
        
    except Exception as e:
        print(f"❌ Error seeding questions: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()