#!/usr/bin/env python3
"""
Gerçek LGS formatında sorular - Bölümlere ayrılmış
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Gerçek LGS formatında sorular - bölümlere ayrılmış
LGS_QUESTIONS = {
    "sözel": [
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Aşağıdaki cümlelerden hangisinde özne yoktur?\n\nA) Sabah erkenden kalktı.\nB) Dışarıda yağmur yağıyor.\nC) Kitabını masaya bıraktı.\nD) Burada sigara içilmez.",
            "options": ["Sabah erkenden kalktı.", "Dışarıda yağmur yağıyor.", "Kitabını masaya bıraktı.", "Burada sigara içilmez."],
            "correct_answer": 3,
            "subject": "Türkçe",
            "section": "sözel",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-turkce-ozne"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "\"Öğretmen, öğrencilerin başarısından mutlu oldu.\" cümlesinde kaç tane isim vardır?\n\nA) 2\nB) 3\nC) 4\nD) 5",
            "options": ["2", "3", "4", "5"],
            "correct_answer": 1,  # öğretmen, öğrencilerin, başarısından
            "subject": "Türkçe",
            "section": "sözel",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-turkce-isim-sayma"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Aşağıdakilerden hangisi Osmanlı Devleti'nin kuruluş dönemi beyliklerinden değildir?\n\nA) Karamanoğulları\nB) Aydınoğulları\nC) Danişmendliler\nD) Germiyanoğulları",
            "options": ["Karamanoğulları", "Aydınoğulları", "Danişmendliler", "Germiyanoğulları"],
            "correct_answer": 2,  # Danişmendliler daha önceki dönem
            "subject": "İnkılap Tarihi ve Atatürkçülük",
            "section": "sözel",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-tarih-beylikliker"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "İslam dininde hangi ibadet farz kılınmıştır?\n\nA) Hac\nB) Umre\nC) Namaz\nD) Kurban",
            "options": ["Hac", "Umre", "Namaz", "Kurban"],
            "correct_answer": 2,  # Namaz farz
            "subject": "Din Kültürü ve Ahlak Bilgisi",
            "section": "sözel",
            "source": "LGS",
            "difficulty": "easy",
            "stamp": "lgs-din-farz-ibadet"
        }
    ],
    "sayısal": [
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Bir sayının 3 katının 5 fazlası 23'tür.\nBu sayı kaçtır?\n\nA) 4\nB) 5\nC) 6\nD) 7",
            "options": ["4", "5", "6", "7"],
            "correct_answer": 2,  # 3x + 5 = 23 → x = 6
            "subject": "Matematik",
            "section": "sayısal",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-matematik-denklem"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "2x + 5 = 13 denkleminin çözüm kümesi aşağıdakilerden hangisidir?\n\nA) {2}\nB) {3}\nC) {4}\nD) {5}",
            "options": ["{2}", "{3}", "{4}", "{5}"],
            "correct_answer": 2,  # x = 4
            "subject": "Matematik",
            "section": "sayısal",
            "source": "LGS",
            "difficulty": "easy",
            "stamp": "lgs-matematik-denklem-cozum"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Aşağıdaki maddelerden hangisi element değildir?\n\nA) Demir\nB) Su\nC) Altın\nD) Karbon",
            "options": ["Demir", "Su", "Altın", "Karbon"],
            "correct_answer": 1,  # Su bileşiktir (H2O)
            "subject": "Fen Bilimleri",
            "section": "sayısal",
            "source": "LGS",
            "difficulty": "easy",
            "stamp": "lgs-fen-element"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Besinlerin sindirimi ile ilgili aşağıdakilerden hangisi yanlıştır?\n\nA) Karbonhidratların sindirimi ağızda başlar.\nB) Proteinlerin sindirimi midede başlar.\nC) Yağların sindirimi midede başlar.\nD) Sindirimin tamamlanması ince bağırsakta olur.",
            "options": [
                "Karbonhidratların sindirimi ağızda başlar.",
                "Proteinlerin sindirimi midede başlar.",
                "Yağların sindirimi midede başlar.",
                "Sindirimin tamamlanması ince bağırsakta olur."
            ],
            "correct_answer": 2,  # Yağların sindirimi ince bağırsakta başlar
            "subject": "Fen Bilimleri",
            "section": "sayısal",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-fen-sindirim"
        }
    ],
    "yabancı_dil": [
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Choose the correct option to complete the sentence:\n\n\"I _____ to school every day.\"\n\nA) go\nB) goes\nC) going\nD) went",
            "options": ["go", "goes", "going", "went"],
            "correct_answer": 0,  # Simple Present: I go
            "subject": "İngilizce",
            "section": "yabancı_dil",
            "source": "LGS",
            "difficulty": "easy",
            "stamp": "lgs-english-simple-present"
        },
        {
            "bundle_id": "lgs-dogru-format",
            "stem": "Which sentence is grammatically correct?\n\nA) She don't like apples.\nB) She doesn't likes apples.\nC) She doesn't like apples.\nD) She not like apples.",
            "options": ["She don't like apples.", "She doesn't likes apples.", "She doesn't like apples.", "She not like apples."],
            "correct_answer": 2,  # Doğru: She doesn't like apples
            "subject": "İngilizce", 
            "section": "yabancı_dil",
            "source": "LGS",
            "difficulty": "medium",
            "stamp": "lgs-english-negative"
        }
    ]
}

def create_lgs_bundle_with_sections():
    """LGS formatında bölümlü sorular oluştur"""
    
    try:
        conn = psycopg2.connect(
            host="db",
            port="5432",
            database="lgs_db",  # docker-compose'den
            user="lgs_user",
            password="lgs_pass"  # docker-compose'den
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Veritabanına bağlandı")
        
        # Önce exam_bundles tablosuna section field'i ekleyelim (varsa skip eder)
        try:
            cursor.execute("ALTER TABLE exam_bundles ADD COLUMN section_info JSONB;")
            print("✅ Section info sütunu eklendi")
        except:
            print("ℹ️ Section info sütunu zaten mevcut")
        
        # Questions tablosuna section field'i ekleyelim
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN section VARCHAR(50);")
            print("✅ Section sütunu eklendi")
        except:
            print("ℹ️ Section sütunu zaten mevcut")
        
        conn.commit()
        
        # Bundle'ı oluştur
        all_questions = []
        for section, questions in LGS_QUESTIONS.items():
            all_questions.extend(questions)
        
        section_info = {
            "sözel": {"count": len(LGS_QUESTIONS["sözel"]), "subjects": ["Türkçe", "İnkılap Tarihi ve Atatürkçülük", "Din Kültürü ve Ahlak Bilgisi"]},
            "sayısal": {"count": len(LGS_QUESTIONS["sayısal"]), "subjects": ["Matematik", "Fen Bilimleri"]},
            "yabancı_dil": {"count": len(LGS_QUESTIONS["yabancı_dil"]), "subjects": ["İngilizce"]}
        }
        
        bundle_query = """
        INSERT INTO exam_bundles (id, name, description, total_questions, section_info, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET 
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        total_questions = EXCLUDED.total_questions,
        section_info = EXCLUDED.section_info,
        updated_at = NOW()
        """
        
        cursor.execute(bundle_query, (
            "lgs-dogru-format",
            "LGS Doğru Format - Bölümlü",
            "Gerçek LGS formatında bölümlere ayrılmış sorular (Sözel/Sayısal/Yabancı Dil)",
            len(all_questions),
            json.dumps(section_info)
        ))
        
        print("✅ Bundle oluşturuldu")
        
        # Mevcut soruları sil
        cursor.execute("DELETE FROM questions WHERE bundle_id = %s", ("lgs-dogru-format",))
        print("🗑️ Eski sorular silindi")
        
        # Yeni soruları ekle
        question_query = """
        INSERT INTO questions (id, bundle_id, stem, options, correct_answer, subject, section, source, difficulty, stamp, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        question_counter = 1
        for section_name, questions in LGS_QUESTIONS.items():
            print(f"\n📚 {section_name.upper()} bölümü soruları ekleniyor...")
            
            for question in questions:
                question_id = f"lgs-dogru-format-{question_counter}"
                
                cursor.execute(question_query, (
                    question_id,
                    question["bundle_id"],
                    question["stem"],
                    json.dumps(question["options"]),
                    question["correct_answer"],
                    question["subject"],
                    question["section"],
                    question["source"],
                    question["difficulty"],
                    question["stamp"]
                ))
                
                print(f"   ✅ {question['subject']}: {question['stamp']}")
                question_counter += 1
        
        conn.commit()
        print("\n🎉 Tüm sorular başarıyla eklendi!")
        
        # Sonuçları kontrol et
        cursor.execute("""
            SELECT section, subject, COUNT(*) as count 
            FROM questions 
            WHERE bundle_id = %s 
            GROUP BY section, subject 
            ORDER BY section, subject
        """, ("lgs-dogru-format",))
        
        results = cursor.fetchall()
        print("\n📊 Bölüm ve ders dağılımı:")
        
        current_section = None
        for result in results:
            if result['section'] != current_section:
                current_section = result['section']
                print(f"\n🔹 {current_section.upper()}:")
            print(f"     {result['subject']}: {result['count']} soru")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_lgs_bundle_with_sections()