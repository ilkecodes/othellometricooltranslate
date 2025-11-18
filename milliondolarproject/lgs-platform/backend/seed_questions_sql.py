"""
Seed script to populate the database with test questions using raw SQL.
Avoids ORM model loading issues and is more efficient for bulk seeding.

Usage:
    python seed_questions_sql.py
"""
import os
import sys
import psycopg2
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import settings to get database URL
from app.core.config import settings


def get_db_connection():
    """Create a psycopg2 connection to the database."""
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD
    )


def seed_curriculum():
    """Create curriculum structure using raw SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM subjects;")
        if cursor.fetchone()[0] > 0:
            print("Curriculum already seeded, skipping...")
            conn.close()
            return
        
        # Define curriculum data
        curriculum_data = {
            "Matematik": ["Sayılar", "Cebir", "Geometri"],
            "Fen Bilgisi": ["Fizik", "Kimya", "Biyoloji"],
            "Türkçe": ["Dil Bilgisi", "Yazın", "Okuma Anlama"],
            "Sosyal Bilgiler": ["Tarih", "Coğrafya", "Sosyal Bilgiler"],
        }
        
        print("🌱 Starting database seed...\n")
        
        # Create subjects and units and topics
        for subject_name, unit_names in curriculum_data.items():
            # Insert subject
            cursor.execute(
                "INSERT INTO subjects (code, name, created_at) VALUES (%s, %s, %s) RETURNING id;",
                (subject_name.upper(), subject_name, datetime.now())
            )
            subject_id = cursor.fetchone()[0]
            print(f"✓ Created subject: {subject_name}")
            
            # Create units and topics for this subject
            for order_idx, unit_name in enumerate(unit_names, 1):
                cursor.execute(
                    "INSERT INTO units (subject_id, name, order_index, created_at) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (subject_id, unit_name, order_idx, datetime.now())
                )
                unit_id = cursor.fetchone()[0]
                print(f"    ✓ Created unit: {unit_name}")
                
                # Create 3 topics per unit
                for topic_idx in range(1, 4):
                    topic_name = f"{unit_name} Konusu {topic_idx}"
                    cursor.execute(
                        "INSERT INTO topics (unit_id, name, order_index, created_at) VALUES (%s, %s, %s, %s) RETURNING id;",
                        (unit_id, topic_name, topic_idx, datetime.now())
                    )
                    topic_id = cursor.fetchone()[0]
                    print(f"        ✓ Created topic: {topic_name}")
                    
                    # Create a learning outcome for this topic
                    cursor.execute(
                        "INSERT INTO learning_outcomes (topic_id, code, description, created_at) VALUES (%s, %s, %s, %s);",
                        (topic_id, f"LO_{topic_name.replace(' ', '_')}", f"Learning outcome for {topic_name}", datetime.now())
                    )
        
        conn.commit()
        print(f"\n✅ Curriculum seeded successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding curriculum: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def seed_questions(questions_list):
    """Seed questions using raw SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created_count = 0
    
    try:
        print("\n📝 Seeding questions...")
        
        for q_data in questions_list:
            # Get subject ID
            cursor.execute("SELECT id FROM subjects WHERE code = %s;", (q_data["subject_code"],))
            result = cursor.fetchone()
            if not result:
                print(f"⚠️  Subject {q_data['subject_code']} not found, skipping question")
                continue
            subject_id = result[0]
            
            # Get topic ID
            cursor.execute("SELECT id FROM topics WHERE name = %s;", (q_data["topic_name"],))
            result = cursor.fetchone()
            if not result:
                print(f"⚠️  Topic {q_data['topic_name']} not found, skipping question")
                continue
            topic_id = result[0]
            
            # Get learning outcome ID for this topic
            cursor.execute("SELECT id FROM learning_outcomes WHERE topic_id = %s;", (topic_id,))
            result = cursor.fetchone()
            if not result:
                print(f"⚠️  Learning outcome for topic {q_data['topic_name']} not found")
                continue
            outcome_id = result[0]
            
            # Insert question
            cursor.execute(
                """INSERT INTO questions 
                   (subject_id, topic_id, main_learning_outcome_id, difficulty, stem_text, 
                    has_image, image_url, source_type, estimated_time_seconds, is_active, created_by, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id;""",
                (
                    subject_id,
                    topic_id,
                    outcome_id,
                    q_data.get("difficulty", "MEDIUM"),
                    q_data["stem_text"],
                    q_data.get("has_image", False),
                    q_data.get("image_url"),
                    q_data.get("source_type", "LGS_STYLE"),
                    q_data.get("estimated_time_seconds", 60),
                    True,
                    None,
                    datetime.now()
                )
            )
            question_id = cursor.fetchone()[0]
            
            # Insert question options
            for opt_data in q_data.get("options", []):
                cursor.execute(
                    """INSERT INTO question_options 
                       (question_id, option_label, text, is_correct, created_at)
                       VALUES (%s, %s, %s, %s, %s);""",
                    (
                        question_id,
                        opt_data["label"],
                        opt_data["text"],
                        opt_data.get("is_correct", False),
                        datetime.now()
                    )
                )
            
            created_count += 1
            print(f"✓ Created question {created_count}: {q_data['stem_text'][:50]}...")
        
        conn.commit()
        print(f"\n✅ Seeded {created_count} questions successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding questions: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main seed function."""
    
    # Seed curriculum
    seed_curriculum()
    
    # Turkish questions from PDF (Sorular 1-4)
    turkish_questions = [
        {
            "subject_code": "TURKISH",
            "topic_name": "Okuma Anlama Konusu 3",
            "difficulty": "MEDIUM",
            "stem_text": (
                "Hiç tanımadığımız ancak görür görmez içimizin ısındığı, şöyle bir kucaklayıp da "
                "sarmalamak istediğimiz insanlar vardır. Onların gülüşlerinde duygularının yıpranmış, "
                "çok acı çekmiş olduklarını görürsünüz. Fakat bu kişiler yine de - - - -, yaşama "
                "direncini ve umudunu yitirmemiş insanlardır. Üzüntülerinde de mutluluklarında da her "
                "daim samimilerdir. Onları değerli yapan özellikleri samimiyetleridir. Yalanı dolanı "
                "olmayan, riyakârlığa tamah etmeyen, dostlarına karşı - - - - ve paylaşımcı olan bu "
                "insanlar ilk bakışta kendilerini belli eder.\n\n"
                "Bu metinde boş bırakılan yerlere düşüncenin akışına göre sırasıyla aşağıdakilerin "
                "hangisi getirilmelidir?"
            ),
            "estimated_time_seconds": 90,
            "options": [
                {"label": "A", "text": "rahata kavuşmamış - duyarlı", "is_correct": False},
                {"label": "B", "text": "pes etmemiş - koruyucu", "is_correct": True},
                {"label": "C", "text": "yenik düşmemiş - gururlu", "is_correct": False},
                {"label": "D", "text": "taviz vermemiş - baskıcı", "is_correct": False},
            ],
        },
        {
            "subject_code": "TURKISH",
            "topic_name": "Yazın Konusu 1",
            "difficulty": "HARD",
            "stem_text": (
                "Vatanına borçlu olarak ölmek istemez Fazıl Hüsnü Dağlarca. O ki şairdir, nefesiyle "
                "dalgalandırmalıdır bayrağını. O ki eski bir askerdir, cepheleri bir şahin gibi "
                "gözlemelidir. Silahlar ateşlenir de dağ taş ateşlenmez mi! Bir millet ayağa kalkar da "
                "kurt, kuş, ağaç, böcek sessiz mi kalır! Bir destan yazılmaktadır madem Anadolu'da, "
                "'Dağlarca' yazılmalıdır. 'Üç Şehitler Destanı' denilmelidir en fırtınalısına.\n\n"
                "Bu metindeki altı çizili ifadeyle anlatılmak istenen aşağıdakilerden hangisidir?"
            ),
            "estimated_time_seconds": 90,
            "options": [
                {
                    "label": "A",
                    "text": "Bağımsızlık mücadelesine şiirleriyle katılmak",
                    "is_correct": True,
                },
                {
                    "label": "B",
                    "text": "Özgürlüğe giden yolda şiirlerine önem vermek",
                    "is_correct": False,
                },
                {
                    "label": "C",
                    "text": "Vatan sevgisini şiirlerinde ana tema yapmak",
                    "is_correct": False,
                },
                {
                    "label": "D",
                    "text": "Şiirlerinde millî değerlere öncelik vermek",
                    "is_correct": False,
                },
            ],
        },
        {
            "subject_code": "TURKISH",
            "topic_name": "Dil Bilgisi Konusu 1",
            "difficulty": "EASY",
            "stem_text": (
                '"Birçok türde yazdım ama kendimi en iyi ifade ettiğim tür şiir oldu." diyen bir sanatçı '
                "için aşağıdakilerden hangisi kesinlikle söylenir?"
            ),
            "estimated_time_seconds": 60,
            "options": [
                {
                    "label": "A",
                    "text": "Sanatçı, kendini rahat ifade ettiği için şiir türünü seçer.",
                    "is_correct": False,
                },
                {
                    "label": "B",
                    "text": "Sanatçının kendini iyi ifade edemediği türler vardır.",
                    "is_correct": False,
                },
                {
                    "label": "C",
                    "text": "Şiir, sanatçının kendini iyi ifade ettiği türler arasındadır.",
                    "is_correct": True,
                },
                {
                    "label": "D",
                    "text": "Şiir, sanatçının kendini iyi ifade etmesini kolaylaştıran bir türdür.",
                    "is_correct": False,
                },
            ],
        },
        {
            "subject_code": "TURKISH",
            "topic_name": "Dil Bilgisi Konusu 2",
            "difficulty": "MEDIUM",
            "stem_text": (
                "Yabancı kültür unsurlarını bire bir kopyalamak yerine bunları millî "
                "değerlerimizle yorumlayarak yeni tasarımlar ortaya koymamız gerekir.\n\n"
                "Bu cümlede anlatılmak istenen aşağıdakilerden hangisidir?"
            ),
            "estimated_time_seconds": 60,
            "options": [
                {
                    "label": "A",
                    "text": "Yeni eserler, geleneksel konular ele alınarak özgün bir üslupla oluşturulmalıdır.",
                    "is_correct": False,
                },
                {
                    "label": "B",
                    "text": "Geçmişle bağları koparmadan modern kültürün evrensel değerlerine uygun eserler üretilmelidir.",
                    "is_correct": False,
                },
                {
                    "label": "C",
                    "text": "Başka milletlere ait değerler günümüz değerleriyle yeniden yorumlanarak aktarılmalıdır.",
                    "is_correct": False,
                },
                {
                    "label": "D",
                    "text": "Farklı kültürlere ait ögeler milletimize özgü bir bakış açısıyla işlenerek özgün eserler verilmelidir.",
                    "is_correct": True,
                },
            ],
        },
    ]
    
    # Seed the Turkish questions
    seed_questions(turkish_questions)


if __name__ == "__main__":
    main()
