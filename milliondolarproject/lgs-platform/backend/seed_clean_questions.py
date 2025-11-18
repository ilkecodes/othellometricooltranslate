#!/usr/bin/env python3
"""
Seed clean questions from JSONL into the database.
This replaces the corrupted questions with proper 20-question sets.
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database connection
DATABASE_URL = "postgresql://lgs_user:lgs_pass@db:5432/lgs_db"

def get_subject_id(session, subject_name):
    """Get subject ID by name."""
    result = session.execute(
        text("SELECT id FROM subjects WHERE name = :name"),
        {"name": subject_name}
    )
    row = result.fetchone()
    return row[0] if row else None

def get_topic_id(session, subject_id, order_index=1):
    """Get or create a topic for a subject."""
    # Get first unit for the subject
    result = session.execute(
        text("SELECT id FROM units WHERE subject_id = :subject_id LIMIT 1"),
        {"subject_id": subject_id}
    )
    unit_row = result.fetchone()
    if not unit_row:
        # Create unit if none exists
        result = session.execute(
            text("""
                INSERT INTO units (subject_id, name, order_index)
                VALUES (:subject_id, :name, :order_index)
                RETURNING id
            """),
            {
                "subject_id": subject_id,
                "name": f"Unit 1",
                "order_index": 1
            }
        )
        session.commit()
        unit_id = result.fetchone()[0]
    else:
        unit_id = unit_row[0]
    
    # Try to get existing topic for this unit
    result = session.execute(
        text("SELECT id FROM topics WHERE unit_id = :unit_id ORDER BY id LIMIT 1"),
        {"unit_id": unit_id}
    )
    row = result.fetchone()
    if row:
        return row[0]
    
    # Create default topic if none exists
    result = session.execute(
        text("""
            INSERT INTO topics (unit_id, name, order_index)
            VALUES (:unit_id, :name, :order_index)
            RETURNING id
        """),
        {
            "unit_id": unit_id,
            "name": f"Topic {order_index}",
            "order_index": order_index
        }
    )
    session.commit()
    return result.fetchone()[0]

def seed_questions():
    """Load and seed questions from JSONL."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        jsonl_path = Path(__file__).parent / "questions_clean.jsonl"
        
        # Get or create a default learning outcome
        result = session.execute(
            text("SELECT id FROM learning_outcomes LIMIT 1")
        )
        outcome_row = result.fetchone()
        if outcome_row:
            learning_outcome_id = outcome_row[0]
        else:
            # Create default learning outcome
            result = session.execute(
                text("""
                    INSERT INTO learning_outcomes (topic_id, name, order_index)
                    SELECT id, 'Default Outcome', 1 FROM topics LIMIT 1
                    RETURNING id
                """)
            )
            session.commit()
            learning_outcome_id = result.fetchone()[0]
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            questions_added = 0
            for line_num, line in enumerate(f, 1):
                try:
                    q_data = json.loads(line)
                    
                    # Map subject names to database subjects
                    subject_map = {
                        "Türkçe": "Türkçe",
                        "Sosyal": "Sosyal Bilgiler",
                        "Din": "Din Kültürü ve Ahlak Bilgisi",
                        "İngilizce": "İngilizce"
                    }
                    
                    subject_name = subject_map.get(q_data['subject'], q_data['subject'])
                    subject_id = get_subject_id(session, subject_name)
                    
                    if not subject_id:
                        print(f"⚠️  Line {line_num}: Subject '{subject_name}' not found in database")
                        continue
                    
                    topic_id = get_topic_id(session, subject_id)
                    
                    # Insert question - without answer_key column
                    result = session.execute(
                        text("""
                            INSERT INTO questions (
                                subject_id, topic_id, stem_text, difficulty, 
                                main_learning_outcome_id
                            ) VALUES (
                                :subject_id, :topic_id, :stem_text, :difficulty,
                                :learning_outcome_id
                            )
                            RETURNING id
                        """),
                        {
                            "subject_id": subject_id,
                            "topic_id": topic_id,
                            "stem_text": q_data['stem'],
                            "difficulty": "medium",
                            "learning_outcome_id": learning_outcome_id
                        }
                    )
                    session.commit()
                    question_id = result.fetchone()[0]
                    
                    # Insert choices
                    for choice in q_data['choices']:
                        is_correct = choice['label'] == q_data.get('answer', 'A')
                        session.execute(
                            text("""
                                INSERT INTO question_options (
                                    question_id, option_label, text, is_correct
                                ) VALUES (:question_id, :label, :text, :is_correct)
                            """),
                            {
                                "question_id": question_id,
                                "label": choice['label'],
                                "text": choice['text'],
                                "is_correct": is_correct
                            }
                        )
                    session.commit()
                    questions_added += 1
                    print(f"✓ Added Q{q_data['number']} ({q_data['subject']})")
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Line {line_num}: JSON parse error - {e}")
                except Exception as e:
                    print(f"✗ Line {line_num}: {e}")
                    session.rollback()
        
        print(f"\n✅ Successfully added {questions_added} questions!")
        
        # Show summary
        result = session.execute(
            text("""
                SELECT s.name, COUNT(q.id) as count
                FROM subjects s
                LEFT JOIN questions q ON s.id = q.subject_id
                GROUP BY s.id, s.name
                ORDER BY s.name
            """)
        )
        print("\nQuestion count by subject:")
        for subject, count in result:
            print(f"  {subject}: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_questions()
