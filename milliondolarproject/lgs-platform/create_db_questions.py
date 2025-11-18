#!/usr/bin/env python3
"""
Gerçek LGS formatında sorular oluşturucu - Veritabanına doğrudan ekleme
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Gerçek LGS formatında örnek sorular
LGS_QUESTIONS = [
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "Aşağıdaki cümlelerden hangisinde özne yoktur?\n\nA) Sabah erkenden kalktı.\nB) Dışarıda yağmur yağıyor.\nC) Kitabını masaya bıraktı.\nD) Burada sigara içilmez.",
        "options": ["Sabah erkenden kalktı.", "Dışarıda yağmur yağıyor.", "Kitabını masaya bıraktı.", "Burada sigara içilmez."],
        "correct_answer": 3,
        "subject": "Türkçe",
        "source": "LGS",
        "difficulty": "medium",
        "stamp": "lgs-turkce-ozne"
    },
    {
        "bundle_id": "lgs-gercek-format", 
        "stem": "Bir sayının 3 katının 5 fazlası 23'tür.\nBu sayı kaçtır?\n\nA) 4\nB) 5\nC) 6\nD) 7",
        "options": ["4", "5", "6", "7"],
        "correct_answer": 2,
        "subject": "Matematik",
        "source": "LGS", 
        "difficulty": "medium",
        "stamp": "lgs-matematik-denklem"
    },
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "Aşağıdaki maddelerden hangisi element değildir?\n\nA) Demir\nB) Su\nC) Altın\nD) Karbon", 
        "options": ["Demir", "Su", "Altın", "Karbon"],
        "correct_answer": 1,
        "subject": "Fen Bilimleri",
        "source": "LGS",
        "difficulty": "easy",
        "stamp": "lgs-fen-element"
    },
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "Aşağıdakilerden hangisi Osmanlı Devleti'nin kuruluş dönemi beyliklerinden değildir?\n\nA) Karamanoğulları\nB) Aydınoğulları\nC) Danişmendliler\nD) Germiyanoğulları",
        "options": ["Karamanoğulları", "Aydınoğulları", "Danişmendliler", "Germiyanoğulları"],
        "correct_answer": 2,
        "subject": "Sosyal Bilgiler",
        "source": "LGS",
        "difficulty": "medium", 
        "stamp": "lgs-sosyal-beylikliker"
    },
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "Choose the correct option to complete the sentence:\n\n\"I _____ to school every day.\"\n\nA) go\nB) goes\nC) going\nD) went",
        "options": ["go", "goes", "going", "went"],
        "correct_answer": 0,
        "subject": "İngilizce",
        "source": "LGS", 
        "difficulty": "easy",
        "stamp": "lgs-ingilizce-simple-present"
    },
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "\"Öğretmen, öğrencilerin başarısından mutlu oldu.\"\ncümlesinde kaç tane isim vardır?\n\nA) 2\nB) 3\nC) 4\nD) 5",
        "options": ["2", "3", "4", "5"],
        "correct_answer": 1,
        "subject": "Türkçe",
        "source": "LGS",
        "difficulty": "medium",
        "stamp": "lgs-turkce-isim-sayma"
    },
    {
        "bundle_id": "lgs-gercek-format", 
        "stem": "2x + 5 = 13 denkleminin çözüm kümesi aşağıdakilerden hangisidir?\n\nA) {2}\nB) {3}\nC) {4}\nD) {5}",
        "options": ["{2}", "{3}", "{4}", "{5}"],
        "correct_answer": 2,
        "subject": "Matematik",
        "source": "LGS",
        "difficulty": "easy",
        "stamp": "lgs-matematik-denklem-cozum"
    },
    {
        "bundle_id": "lgs-gercek-format",
        "stem": "Besinlerin sindirimi ile ilgili aşağıdakilerden hangisi yanlıştır?\n\nA) Karbonhidratların sindirimi ağızda başlar.\nB) Proteinlerin sindirimi midede başlar.\nC) Yağların sindirimi midede başlar.\nD) Sindirimin tamamlanması ince bağırsakta olur.",
        "options": [
            "Karbonhidratların sindirimi ağızda başlar.",
            "Proteinlerin sindirimi midede başlar.",
            "Yağların sindirimi midede başlar.", 
            "Sindirimin tamamlanması ince bağırsakta olur."
        ],
        "correct_answer": 2,
        "subject": "Fen Bilimleri",
        "source": "LGS",
        "difficulty": "medium",
        "stamp": "lgs-fen-sindirim"
    }
]

def create_bundle_and_questions():
    """Gerçek LGS formatında bundle ve sorular oluştur"""
    
    # Veritabanı bağlantısı
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="lgs_platform",
            user="lgs_user",
            password="lgs_password"
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Veritabanına bağlandı")
        
        # Önce bundle'ı oluştur
        bundle_query = """
        INSERT INTO exam_bundles (id, name, description, total_questions, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET 
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        total_questions = EXCLUDED.total_questions,
        updated_at = NOW()
        """
        
        cursor.execute(bundle_query, (
            "lgs-gercek-format",
            "LGS Gerçek Format Sorular",
            "Gerçek LGS formatında Türkçe sorular - doğru içerik ve format",
            len(LGS_QUESTIONS)
        ))
        
        print("✅ Bundle oluşturuldu/güncellendi")
        
        # Mevcut soruları sil
        delete_query = "DELETE FROM questions WHERE bundle_id = %s"
        cursor.execute(delete_query, ("lgs-gercek-format",))
        print(f"🗑️ Eski sorular silindi")
        
        # Yeni soruları ekle
        question_query = """
        INSERT INTO questions (id, bundle_id, stem, options, correct_answer, subject, source, difficulty, stamp, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        for i, question in enumerate(LGS_QUESTIONS):
            question_id = f"lgs-gercek-format-{i+1}"
            
            cursor.execute(question_query, (
                question_id,
                question["bundle_id"],
                question["stem"],
                json.dumps(question["options"]),
                question["correct_answer"],
                question["subject"],
                question["source"],
                question["difficulty"],
                question["stamp"]
            ))
            
            print(f"✅ Soru eklendi: {question['subject']} - {question['stamp']}")
        
        # Değişiklikleri kaydet
        conn.commit()
        print("🎉 Tüm sorular başarıyla eklendi!")
        
        # Sonuçları kontrol et
        cursor.execute("SELECT COUNT(*) as count FROM questions WHERE bundle_id = %s", ("lgs-gercek-format",))
        result = cursor.fetchone()
        print(f"📊 Toplam soru sayısı: {result['count']}")
        
        # Konu dağılımını kontrol et
        cursor.execute("""
            SELECT subject, COUNT(*) as count 
            FROM questions 
            WHERE bundle_id = %s 
            GROUP BY subject 
            ORDER BY subject
        """, ("lgs-gercek-format",))
        
        subjects = cursor.fetchall()
        print("\n📚 Konu dağılımı:")
        for subject in subjects:
            print(f"   {subject['subject']}: {subject['count']} soru")
            
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
    create_bundle_and_questions()