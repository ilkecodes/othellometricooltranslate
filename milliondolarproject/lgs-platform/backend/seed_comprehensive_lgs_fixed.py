#!/usr/bin/env python3
"""
Fixed seeder for comprehensive LGS questions from 2018-2025
Maps questions to existing curriculum structure in the database
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


def map_subject_code(extracted_subject: str) -> str:
    """Map extracted subject codes to database subject codes"""
    mapping = {
        'TURKISH': 'TURKISH',
        'MATH': 'MATH', 
        'SCIENCE': 'SCIENCE',
        'SOCIAL_STUDIES': 'SOCIAL',  # Map to existing SOCIAL subject
        'RELIGION': 'DIN',           # Map to existing DIN subject
        'ENGLISH': 'ENG'             # Map to existing ENG subject
    }
    return mapping.get(extracted_subject, 'TURKISH')


def map_topic_name(subject_code: str, extracted_topic: str, year: int) -> str:
    """Map extracted topic names to existing database topic names"""
    
    # Turkish topic mappings based on existing database structure
    if subject_code == 'TURKISH':
        turkish_mapping = {
            'Paragraf – Okuma Anlama': 'Paragraf – Okuma Anlama',
            'Sözcükte Anlam': 'Sözcükte Anlam', 
            'Cümlede Anlam': 'Cümlede Anlam',
            'Yazım ve Noktalama': 'Yazım ve Noktalama',
            'Türkçe – Diğer': 'Dil Bilgisi Konusu 1',  # Map generic Turkish to Dil Bilgisi
            'TURKISH Konusu': 'Dil Bilgisi Konusu 1',  # Default Turkish mapping
        }
        
        # Try direct mapping first
        for pattern, topic in turkish_mapping.items():
            if pattern in extracted_topic:
                return topic
        
        # Default Turkish fallback
        return 'Dil Bilgisi Konusu 1'
    
    # Math mappings
    elif subject_code == 'MATH':
        return 'Sayılar Konusu 1'  # Default math topic
    
    # Science mappings  
    elif subject_code == 'SCIENCE':
        return 'Fizik Konusu 1'    # Default science topic
    
    # Social Studies mappings
    elif subject_code == 'SOCIAL':
        return 'Tarih Konusu 1'    # Default social topic
    
    # Religion mappings
    elif subject_code == 'DIN':
        return 'İslam İnancı'      # Default religion topic
    
    # English mappings
    elif subject_code == 'ENG':
        return 'Reading Comprehension'  # Default English topic
    
    # Ultimate fallback
    return 'Dil Bilgisi Konusu 1'


def convert_to_seed_format(question_data: Dict) -> Dict:
    """Convert comprehensive question format to seed_questions format"""
    try:
        # Map subject to database format
        extracted_subject = question_data.get('subject', 'TURKISH')
        subject_code = map_subject_code(extracted_subject)
        
        # Map topic to database format
        year = question_data.get('year', 2024)
        extracted_topic = question_data.get('topic_name', '')
        topic_name = map_topic_name(subject_code, extracted_topic, year)
        
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
        
        # Clean stem text
        stem_text = question_data.get('stem', '').strip()
        
        # Skip if stem is too short or problematic
        if len(stem_text) < 10:
            return None
        
        # Clean problematic stems
        if 'Bu testte' in stem_text and 'soru vardır' in stem_text:
            # This is metadata, skip
            return None
            
        question = {
            'subject_code': subject_code,
            'topic_name': topic_name,
            'difficulty': question_data.get('difficulty', 'MEDIUM'),
            'stem_text': stem_text,
            'estimated_time_seconds': question_data.get('estimated_time_seconds', 90),
            'options': options,
            # Add metadata as comments
            'source_info': f"LGS {year} - {extracted_subject} - {question_data.get('processing_method', 'unknown')}"
        }
        
        # Final validation
        if not question['stem_text'] or len(question['options']) < 4:
            return None
        
        # Check for meaningful question
        valid_options = [opt for opt in options if opt['text'] and len(opt['text']) > 3 and opt['text'] != 'Görsel A']
        if len(valid_options) < 2:
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
        'by_topic': {},
        'by_difficulty': {},
        'by_year': {}
    }
    
    for q in questions:
        # Subject distribution
        subject = q.get('subject_code', 'UNKNOWN')
        stats['by_subject'][subject] = stats['by_subject'].get(subject, 0) + 1
        
        # Topic distribution
        topic = q.get('topic_name', 'UNKNOWN')
        stats['by_topic'][topic] = stats['by_topic'].get(topic, 0) + 1
        
        # Difficulty distribution
        difficulty = q.get('difficulty', 'UNKNOWN')
        stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
        
        # Year distribution (extract from source_info)
        source_info = q.get('source_info', '')
        if 'LGS' in source_info:
            try:
                year = source_info.split('LGS ')[1].split(' ')[0]
                stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
            except:
                pass
    
    return stats


def print_analysis(stats: Dict):
    """Print comprehensive analysis of the questions"""
    print(f"\n📊 FIXED LGS QUESTIONS ANALYSIS")
    print("=" * 60)
    print(f"📝 Total Valid Questions: {stats['total']}")
    
    print(f"\n📚 By Subject:")
    for subject, count in sorted(stats['by_subject'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {subject}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n📝 By Topic (Top 10):")
    top_topics = sorted(stats['by_topic'].items(), key=lambda x: x[1], reverse=True)[:10]
    for topic, count in top_topics:
        percentage = (count / stats['total']) * 100
        print(f"   {topic}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n⭐ By Difficulty:")
    for difficulty, count in sorted(stats['by_difficulty'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {difficulty}: {count} questions ({percentage:.1f}%)")
    
    print(f"\n📅 By Year:")
    for year, count in sorted(stats['by_year'].items()):
        percentage = (count / stats['total']) * 100
        print(f"   {year}: {count} questions ({percentage:.1f}%)")


def main():
    """Main seeding function"""
    file_path = "comprehensive_lgs_2018_2025.jsonl"
    
    print("🌱 FIXED COMPREHENSIVE LGS QUESTIONS SEEDER")
    print("=" * 60)
    print(f"📖 Loading questions from: {file_path}")
    
    # Load questions
    raw_questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    raw_questions.append(json.loads(line))
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    print(f"📄 Loaded {len(raw_questions)} raw questions")
    
    # Convert and filter questions
    questions = []
    for q_data in raw_questions:
        question = convert_to_seed_format(q_data)
        if question:
            questions.append(question)
    
    print(f"✅ Converted {len(questions)} valid questions")
    
    if not questions:
        print("❌ No valid questions to seed")
        return
    
    # Analyze questions
    stats = analyze_questions(questions)
    print_analysis(stats)
    
    print(f"\n📋 Sample Questions:")
    for i, q in enumerate(questions[:3]):
        print(f"\n   Q{i+1}: [{q['difficulty']}] [{q['subject_code']}] → {q['topic_name']}")
        print(f"      {q['stem_text'][:80]}...")
        for opt in q['options'][:2]:  # Show first 2 options
            flag = "✅" if opt['is_correct'] else "  "
            print(f"      {flag} {opt['label']}) {opt['text'][:50]}...")
    
    # Confirm before seeding
    print(f"\n🤔 Ready to seed {len(questions)} valid LGS questions to database")
    
    response = input(f"\n❓ Proceed with seeding {len(questions)} comprehensive LGS questions? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Seeding cancelled")
        return
    
    # Seed the questions
    print(f"\n🌱 Seeding {len(questions)} questions to database...")
    
    try:
        seed_questions(questions)
        print(f"\n✅ Successfully seeded {len(questions)} comprehensive LGS questions!")
        print("📊 Database now contains authentic questions from LGS exams 2018-2025")
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