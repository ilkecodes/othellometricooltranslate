#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LGS Questions JSONL -> Database Seeder

Reads questions from JSONL format and seeds them to the database.
Supports automatic topic assignment based on question content.

Usage:
    python seed_from_jsonl.py input.jsonl [--subject TURKISH] [--auto-topic]

Example:
    python seed_from_jsonl.py lgs_2025_sozel.jsonl --subject TURKISH --auto-topic
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

# Import settings for database connection
sys.path.insert(0, str(Path(__file__).parent))
try:
    from app.core.config import settings
except ImportError:
    try:
        from app.config import settings
    except ImportError:
        # Fallback for testing
        class Settings:
            DATABASE_URL = "postgresql://lgs_user:lgs_password@db:5432/lgs_db"
        settings = Settings()


# Topic inference keywords for Turkish questions
TOPIC_KEYWORDS = {
    "Paragraf – Okuma Anlama": [
        "parçada", "bu parça", "metinde", "paragrafta", "yazara göre",
        "metne göre", "parçaya göre", "yazar", "ana fikir", "konu"
    ],
    "Sözcükte Anlam": [
        "sözcük", "sözcüğü", "kelime", "anlamı", "deyim", "atasözü",
        "atasözünün", "deyimin", "ifadesinin", "söylemek istemek"
    ],
    "Cümlede Anlam": [
        "cümlede", "cümlelerin", "cümlesinde", "cümlesiyle", "ifadesi",
        "anlatılmak istenen", "amaç", "ilişkisi"
    ],
    "Yazım ve Noktalama": [
        "yazım", "noktalama", "virgül", "kesme işareti", "nokta", "iki nokta",
        "hyphens", "hyphenation", "doğru", "yanlış", "hangisi doğru"
    ],
}


def infer_topic_from_stem(stem: str) -> str:
    """
    Soru kökü içinden anahtar kelimeler arayarak konu atama.
    
    Returns:
        Topic name (e.g., "Paragraf – Okuma Anlama")
    """
    stem_lower = stem.lower()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in stem_lower:
                return topic
    
    # Fallback
    return "Türkçe – Diğer"


def infer_difficulty_from_stem(stem: str) -> str:
    """
    Soru kökü uzunluğuna göre zorluk seviyesi atama.
    
    Returns:
        Difficulty level (EASY, MEDIUM, HARD, VERY_HARD)
    """
    word_count = len(stem.split())
    
    if word_count < 15:
        return "EASY"
    elif word_count < 30:
        return "MEDIUM"
    elif word_count < 60:
        return "HARD"
    else:
        return "VERY_HARD"


def get_db_connection():
    """PostgreSQL'e psycopg2 ile bağlanır."""
    try:
        # Try to get database URL from settings
        if hasattr(settings, 'DATABASE_URL'):
            db_url = settings.DATABASE_URL
            conn = psycopg2.connect(db_url)
        else:
            # Use individual connection parameters
            conn = psycopg2.connect(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD
            )
    except (psycopg2.OperationalError, AttributeError) as e:
        print(f"❌ Database connection error: {e}")
        raise
    
    return conn


def ensure_curriculum(conn, subject_code: str = "TURKISH"):
    """
    Curriculum yapısının var olduğundan emin ol.
    Yoksa oluştur.
    
    Returns:
        dict: {subject_id, topic_ids}
    """
    cur = conn.cursor()
    
    # Subjects
    subjects = {
        "TURKISH": "Türkçe",
        "MATH": "Matematik",
        "SCIENCE": "Fen Bilgisi",
        "SOCIAL": "Sosyal Bilgiler"
    }
    
    # Check if subject exists
    cur.execute("SELECT id FROM subjects WHERE code = %s", (subject_code,))
    result = cur.fetchone()
    
    if result:
        subject_id = result[0]
    else:
        # Create subject
        cur.execute(
            "INSERT INTO subjects (code, name) VALUES (%s, %s) RETURNING id",
            (subject_code, subjects[subject_code])
        )
        subject_id = cur.fetchone()[0]
    
    # Check for units
    cur.execute("SELECT COUNT(*) FROM units WHERE subject_id = %s", (subject_id,))
    unit_count = cur.fetchone()[0]
    
    # Create standard units if not exist
    if unit_count == 0:
        units = ["Dil Bilgisi", "Yazın", "Okuma Anlama"]
        unit_ids = []
        for order, unit_name in enumerate(units, start=1):
            cur.execute(
                "INSERT INTO units (subject_id, name, order_index) VALUES (%s, %s, %s) RETURNING id",
                (subject_id, unit_name, order)
            )
            unit_ids.append(cur.fetchone()[0])
    else:
        cur.execute(
            "SELECT id FROM units WHERE subject_id = %s ORDER BY order_index",
            (subject_id,)
        )
        unit_ids = [row[0] for row in cur.fetchall()]
    
    # Ensure topics exist in first unit
    topic_ids = {}
    for order_index, topic_name in enumerate(TOPIC_KEYWORDS.keys(), start=1):
        cur.execute(
            "SELECT id FROM topics WHERE name = %s AND unit_id = %s",
            (topic_name, unit_ids[0])
        )
        result = cur.fetchone()
        
        if result:
            topic_ids[topic_name] = result[0]
        else:
            cur.execute(
                "INSERT INTO topics (unit_id, name, order_index) VALUES (%s, %s, %s) RETURNING id",
                (unit_ids[0], topic_name, order_index)
            )
            topic_ids[topic_name] = cur.fetchone()[0]
    
    # Fallback topic
    cur.execute(
        "SELECT id FROM topics WHERE name = %s AND unit_id = %s",
        ("Türkçe – Diğer", unit_ids[0])
    )
    result = cur.fetchone()
    if result:
        topic_ids["Türkçe – Diğer"] = result[0]
    else:
        cur.execute(
            "INSERT INTO topics (unit_id, name, order_index) VALUES (%s, %s, %s) RETURNING id",
            (unit_ids[0], "Türkçe – Diğer", len(TOPIC_KEYWORDS) + 1)
        )
        topic_ids["Türkçe – Diğer"] = cur.fetchone()[0]
    
    conn.commit()
    
    return {
        "subject_id": subject_id,
        "topic_ids": topic_ids,
        "unit_id": unit_ids[0]
    }


def seed_questions_from_jsonl(
    jsonl_path: Path,
    subject_code: str = "TURKISH",
    auto_topic: bool = True,
    created_by: int = 1,
    dry_run: bool = False
):
    """
    JSONL dosyasından soruları oku ve seed et.
    """
    
    if not jsonl_path.exists():
        print(f"❌ JSONL dosyası bulunamadı: {jsonl_path}")
        return
    
    conn = get_db_connection()
    
    try:
        # Curriculum'u hazırla
        print("🔧 Curriculum yapısı kontrol ediliyor...")
        curriculum = ensure_curriculum(conn, subject_code)
        subject_id = curriculum["subject_id"]
        topic_ids = curriculum["topic_ids"]
        print(f"✅ Subject ID: {subject_id}")
        
        # JSONL'yi oku
        print(f"\n📖 Reading JSONL: {jsonl_path}")
        questions = []
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    q = json.loads(line)
                    questions.append(q)
        
        print(f"✅ Loaded {len(questions)} questions")
        
        # Preview
        print("\n📋 Preview (first 2 questions):")
        for q in questions[:2]:
            topic = infer_topic_from_stem(q["stem"]) if auto_topic else "Türkçe Konusu 1"
            difficulty = infer_difficulty_from_stem(q["stem"]) if auto_topic else "MEDIUM"
            print(f"\n  Q{q['number']}:")
            print(f"    Topic: {topic}")
            print(f"    Difficulty: {difficulty}")
            print(f"    Stem: {q['stem'][:80]}...")
            for choice in q['choices']:
                print(f"      {choice['label']}) {choice['text'][:60]}...")
        
        if dry_run:
            print(f"\n(Dry run - no changes made)")
            conn.close()
            return
        
        # Confirmation
        response = input(f"\n💾 Seed {len(questions)} questions? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled")
            conn.close()
            return
        
        # Seed questions
        print(f"\n🌱 Seeding {len(questions)} questions...")
        
        cur = conn.cursor()
        added = 0
        
        for q in questions:
            topic_name = infer_topic_from_stem(q["stem"]) if auto_topic else "Türkçe – Diğer"
            difficulty = infer_difficulty_from_stem(q["stem"]) if auto_topic else "MEDIUM"
            
            topic_id = topic_ids.get(topic_name, topic_ids.get("Türkçe – Diğer"))
            
            # Get a learning outcome for this topic
            cur.execute(
                "SELECT id FROM learning_outcomes WHERE topic_id = %s LIMIT 1",
                (topic_id,)
            )
            outcome_result = cur.fetchone()
            learning_outcome_id = outcome_result[0] if outcome_result else None
            
            if not learning_outcome_id:
                # Create one if not exist
                cur.execute(
                    "INSERT INTO learning_outcomes (topic_id, description) VALUES (%s, %s) RETURNING id",
                    (topic_id, f"{topic_name} Learning Outcome")
                )
                learning_outcome_id = cur.fetchone()[0]
            
            # Insert question
            cur.execute(
                """
                INSERT INTO questions
                (subject_id, topic_id, main_learning_outcome_id, difficulty, stem_text, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    subject_id,
                    topic_id,
                    learning_outcome_id,
                    difficulty,
                    q["stem"],
                    created_by,
                    datetime.utcnow()
                )
            )
            question_id = cur.fetchone()[0]
            
            # Insert options
            for choice in q["choices"]:
                # Mark first option as correct by default (you might want to ask)
                is_correct = (choice["label"] == "A")
                
                cur.execute(
                    """
                    INSERT INTO question_options
                    (question_id, option_label, text, is_correct)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (question_id, choice["label"], choice["text"], is_correct)
                )
            
            added += 1
            if added % 10 == 0:
                print(f"  ✓ Seeded {added}/{len(questions)} questions")
        
        conn.commit()
        print(f"\n✅ Successfully seeded {added} questions!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed LGS questions from JSONL file to database"
    )
    parser.add_argument("jsonl_file", help="Path to JSONL file")
    parser.add_argument(
        "--subject",
        default="TURKISH",
        choices=["TURKISH", "MATH", "SCIENCE", "SOCIAL"],
        help="Subject code (default: TURKISH)"
    )
    parser.add_argument(
        "--auto-topic",
        action="store_true",
        default=True,
        help="Auto-assign topics based on question content (default: True)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, don't seed"
    )
    
    args = parser.parse_args()
    
    jsonl_path = Path(args.jsonl_file)
    seed_questions_from_jsonl(
        jsonl_path,
        subject_code=args.subject,
        auto_topic=args.auto_topic,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
