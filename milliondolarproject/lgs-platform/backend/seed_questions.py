"""
Seed script to populate the database with test questions using raw SQL.

Usage:
    python seed_questions.py
"""
import os
import sys
import psycopg2
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import settings to get database URL
from app.core.config import settings


def seed_curriculum():
    """Create curriculum structure (subjects, units, topics, outcomes)."""
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing = db.query(Subject).count()
        if existing > 0:
            print("Curriculum already seeded, skipping...")
            return
        
        # LGS typically has 4 main subjects
        subjects_data = [
            {"code": "MATH", "name": "Matematik"},
            {"code": "SCIENCE", "name": "Fen Bilgisi"},
            {"code": "TURKISH", "name": "Türkçe"},
            {"code": "SOCIAL", "name": "Sosyal Bilgiler"},
        ]
        
        subjects = {}
        for subject_data in subjects_data:
            subject = Subject(**subject_data)
            db.add(subject)
            db.flush()
            subjects[subject.code] = subject
            print(f"✓ Created subject: {subject.name}")
        
        # Create units and topics for each subject
        units_data = {
            "MATH": [
                {"name": "Sayılar", "order_index": 1},
                {"name": "Cebir", "order_index": 2},
                {"name": "Geometri", "order_index": 3},
            ],
            "SCIENCE": [
                {"name": "Fizik", "order_index": 1},
                {"name": "Kimya", "order_index": 2},
                {"name": "Biyoloji", "order_index": 3},
            ],
            "TURKISH": [
                {"name": "Dil Bilgisi", "order_index": 1},
                {"name": "Yazın", "order_index": 2},
                {"name": "Okuma Anlama", "order_index": 3},
            ],
            "SOCIAL": [
                {"name": "Tarih", "order_index": 1},
                {"name": "Coğrafya", "order_index": 2},
                {"name": "Sosyal Bilgiler", "order_index": 3},
            ],
        }
        
        for subject_code, units_list in units_data.items():
            subject = subjects[subject_code]
            for unit_data in units_list:
                unit = Unit(subject_id=subject.id, **unit_data)
                db.add(unit)
                db.flush()
                print(f"  ✓ Created unit: {unit.name}")
                
                # Create topics for each unit
                for i in range(3):  # 3 topics per unit
                    topic = Topic(
                        unit_id=unit.id,
                        name=f"{unit.name} Konusu {i+1}",
                        order_index=i+1
                    )
                    db.add(topic)
                    db.flush()
                    
                    # Create learning outcome for each topic
                    outcome = LearningOutcome(
                        topic_id=topic.id,
                        code=f"LO-{subject_code}-{unit.id}-{topic.id}",
                        description=f"{topic.name} öğrenme çıktısı"
                    )
                    db.add(outcome)
                    db.flush()
                    print(f"    ✓ Created topic: {topic.name}")
        
        db.commit()
        print("\n✅ Curriculum seeded successfully!")
        return subjects
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding curriculum: {e}")
        raise
    finally:
        db.close()


def seed_questions(questions_list: list):
    """
    Seed questions into the database.
    
    Args:
        questions_list: List of question dictionaries with structure:
        {
            "subject_code": "MATH",
            "topic_name": "Sayılar Konusu 1",
            "difficulty": "MEDIUM",
            "stem_text": "Question text here",
            "options": [
                {"label": "A", "text": "Option A", "is_correct": True},
                {"label": "B", "text": "Option B", "is_correct": False},
                ...
            ]
        }
    """
    db = SessionLocal()
    
    try:
        if not questions_list:
            print("No questions provided to seed.")
            return
        
        created_count = 0
        
        for q_data in questions_list:
            # Find subject
            subject = db.query(Subject).filter(
                Subject.code == q_data["subject_code"]
            ).first()
            
            if not subject:
                print(f"⚠️  Subject {q_data['subject_code']} not found, skipping question")
                continue
            
            # Find topic
            topic = db.query(Topic).filter(
                Topic.name == q_data["topic_name"]
            ).first()
            
            if not topic:
                print(f"⚠️  Topic {q_data['topic_name']} not found, skipping question")
                continue
            
            # Find learning outcome for this topic
            outcome = db.query(LearningOutcome).filter(
                LearningOutcome.topic_id == topic.id
            ).first()
            
            if not outcome:
                print(f"⚠️  Learning outcome for topic {q_data['topic_name']} not found")
                continue
            
            # Create question
            question = Question(
                subject_id=subject.id,
                topic_id=topic.id,
                main_learning_outcome_id=outcome.id,
                difficulty=q_data.get("difficulty", "MEDIUM"),
                stem_text=q_data["stem_text"],
                has_image=q_data.get("has_image", False),
                image_url=q_data.get("image_url"),
                source_type=q_data.get("source_type", "LGS_STYLE"),
                estimated_time_seconds=q_data.get("estimated_time_seconds", 60),
                is_active=True,
                created_by=None,
            )
            db.add(question)
            db.flush()
            
            # Add options
            for opt_data in q_data.get("options", []):
                option = QuestionOption(
                    question_id=question.id,
                    option_label=opt_data["label"],
                    text=opt_data["text"],
                    is_correct=opt_data.get("is_correct", False)
                )
                db.add(option)
            
            db.flush()
            created_count += 1
            print(f"✓ Created question {created_count}: {question.stem_text[:50]}...")
        
        db.commit()
        print(f"\n✅ Seeded {created_count} questions successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding questions: {e}")
        raise
    finally:
        db.close()


def main():
    """Main seed function."""
    print("🌱 Starting database seed...\n")
    
    # Seed curriculum
    seed_curriculum()
    
    print("\n📝 Ready to seed questions!")
    print("Provide a Python list of question dictionaries to seed_questions()\n")
    
    # Turkish questions from PDF (Sorular 1-4)
    turkish_questions = [
        {
            "subject_code": "TURKISH",
            "topic_name": "Okuma Anlama Konusu 3",  # Maps to "Okuma Anlama" auto-created topic
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
            "topic_name": "Yazın Konusu 1",  # Maps to "Yazın" auto-created topic (for poetry)
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
            "topic_name": "Dil Bilgisi Konusu 1",  # Maps to "Dil Bilgisi" auto-created topic
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
            "topic_name": "Dil Bilgisi Konusu 2",  # Maps to another "Dil Bilgisi" topic
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
