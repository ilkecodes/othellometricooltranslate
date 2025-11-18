#!/usr/bin/env python3
"""
Seed questions extracted by extract_pdf_with_llm.py into the database.

Reads JSONL file with questions and inserts them into PostgreSQL
with proper schema matching and validation.
"""

import json
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

# Setup path to import models
sys.path.insert(0, '/app')

from app.models.curriculum import Subject, Unit, Topic, LearningOutcome
from app.models.question import Question, QuestionOption

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://lgs_user:lgs_pass@db:5432/lgs_db"
)

engine = create_engine(DATABASE_URL)

# Subject mapping from LLM output to database codes
SUBJECT_MAPPING = {
    "Türkçe": "TURKISH",
    "Turkish": "TURKISH",
    "Matematik": "MATH",
    "Mathematics": "MATH",
    "Fen Bilgisi": "SCIENCE",
    "Science": "SCIENCE",
    "Sosyal Bilgiler": "SOCIAL",
    "Social Studies": "SOCIAL",
    "Din Kültürü": "DIN",
    "Religion": "DIN",
    "Din Kültürü ve Ahlak Bilgisi": "DIN",
    "İngilizce": "ENG",
    "English": "ENG",
}

def get_subject_id(db: Session, subject_name: str) -> int:
    """Get or create subject by name."""
    subject_code = SUBJECT_MAPPING.get(subject_name.strip(), "TURKISH")
    
    subject = db.query(Subject).filter(Subject.code == subject_code).first()
    
    if not subject:
        # Create subject if it doesn't exist
        subject = Subject(code=subject_code, name=subject_name)
        db.add(subject)
        db.commit()
        db.refresh(subject)
    
    return subject.id

def get_or_create_unit(db: Session, subject_id: int, topic_name: str) -> int:
    """Get or create a unit for the subject."""
    unit = db.query(Unit).filter(Unit.subject_id == subject_id).first()
    
    if not unit:
        # Create default unit for this subject
        unit = Unit(subject_id=subject_id, name=f"Unit 1", order_index=1)
        db.add(unit)
        db.commit()
        db.refresh(unit)
    
    return unit.id

def get_or_create_topic(db: Session, unit_id: int, topic_name: str) -> int:
    """Get or create topic within unit."""
    topic = db.query(Topic).filter(
        Topic.unit_id == unit_id,
        Topic.name == topic_name
    ).first()
    
    if not topic:
        # Create topic
        topic = Topic(unit_id=unit_id, name=topic_name, order_index=1)
        db.add(topic)
        db.commit()
        db.refresh(topic)
    
    return topic.id

def get_or_create_learning_outcome(db: Session, topic_id: int) -> int:
    """Get or create a learning outcome for the topic."""
    outcome = db.query(LearningOutcome).filter(
        LearningOutcome.topic_id == topic_id
    ).first()
    
    if not outcome:
        # Create default learning outcome
        outcome = LearningOutcome(
            topic_id=topic_id,
            code="LO_001",
            description="Learning Outcome"
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)
    
    return outcome.id

def seed_questions(jsonl_file: str) -> int:
    """Read JSONL file and seed questions into database."""
    
    if not os.path.exists(jsonl_file):
        print(f"✗ File not found: {jsonl_file}")
        sys.exit(1)
    
    print(f"\n📖 Seeding questions from: {jsonl_file}")
    print("=" * 60)
    
    db = Session(engine)
    questions_added = 0
    questions_failed = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    q_data = json.loads(line)
                    
                    # Extract fields
                    stem = q_data.get("stem", "")
                    subject = q_data.get("subject", "Türkçe")
                    topic_name = q_data.get("topic", "General")
                    options = q_data.get("options", [])
                    correct_answer = q_data.get("correct_answer", "A")
                    
                    # Validate
                    if not stem:
                        print(f"  ⚠️  Line {line_num}: Missing stem, skipping")
                        questions_failed += 1
                        continue
                    
                    if len(options) != 4:
                        print(f"  ⚠️  Line {line_num}: Expected 4 options, got {len(options)}, skipping")
                        questions_failed += 1
                        continue
                    
                    # Get/create subject, unit, topic
                    subject_id = get_subject_id(db, subject)
                    unit_id = get_or_create_unit(db, subject_id, topic_name)
                    topic_id = get_or_create_topic(db, unit_id, topic_name)
                    learning_outcome_id = get_or_create_learning_outcome(db, topic_id)
                    
                    # Create question
                    question = Question(
                        subject_id=subject_id,
                        topic_id=topic_id,
                        main_learning_outcome_id=learning_outcome_id,
                        stem_text=stem,
                        difficulty="MEDIUM",
                        source_type="LGS_STYLE"
                    )
                    db.add(question)
                    db.flush()  # Get the question ID
                    
                    # Add options
                    for option_data in options:
                        label = option_data.get("label", "")
                        text = option_data.get("text", "")
                        is_correct = label == correct_answer
                        
                        option = QuestionOption(
                            question_id=question.id,
                            option_label=label,
                            text=text,
                            is_correct=is_correct
                        )
                        db.add(option)
                    
                    db.commit()
                    questions_added += 1
                    
                    # Print progress
                    if questions_added % 5 == 0:
                        print(f"  ✓ Added {questions_added} questions...")
                    
                except json.JSONDecodeError as e:
                    print(f"  ✗ Line {line_num}: Invalid JSON: {e}")
                    questions_failed += 1
                except Exception as e:
                    print(f"  ✗ Line {line_num}: Error: {e}")
                    questions_failed += 1
                    db.rollback()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"✓ Successfully added: {questions_added} questions")
        print(f"✗ Failed: {questions_failed} questions")
        print(f"📊 Total processed: {questions_added + questions_failed}")
        
        # Show database stats
        total = db.query(Question).count()
        by_subject = db.query(Subject.name, func.count(Question.id)).outerjoin(
            Question, Subject.id == Question.subject_id
        ).group_by(Subject.name).all()
        
        print(f"\n📈 Database Statistics:")
        print(f"  Total questions: {total}")
        for subj, count in by_subject:
            if count > 0:
                print(f"    {subj}: {count}")
        
        return questions_added
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_from_llm.py <jsonl_file>")
        print("\nExample:")
        print("  python seed_from_llm.py extracted_questions.jsonl")
        sys.exit(1)
    
    jsonl_file = sys.argv[1]
    count = seed_questions(jsonl_file)
    
    if count == 0:
        print("\n⚠️  No questions were added.")
        sys.exit(1)
    
    print(f"\n✅ Seeding complete!")
