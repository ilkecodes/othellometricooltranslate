#!/usr/bin/env python3
"""
Gerçek LGS formatında sorular oluşturucu
"""

import requests
import json

# LGS formatında örnek sorular
LGS_QUESTIONS = [
    {
        "id": "lgs-turkce-1",
        "stem": """
Aşağıdaki cümlelerden hangisinde özne yoktur?

A) Sabah erkenden kalktı.
B) Dışarıda yağmur yağıyor.  
C) Kitabını masaya bıraktı.
D) Burada sigara içilmez.
        """.strip(),
        "options": [
            "Sabah erkenden kalktı.",
            "Dışarıda yağmur yağıyor.",
            "Kitabını masaya bıraktı.",
            "Burada sigara içilmez."
        ],
        "correct_answer": 3,  # D şıkkı (öznesiz cümle)
        "subject": "Türkçe",
        "source": "LGS",
        "difficulty": "medium"
    },
    {
        "id": "lgs-matematik-1",
        "stem": """
Bir sayının 3 katının 5 fazlası 23'tür.
Bu sayı kaçtır?

A) 4
B) 5  
C) 6
D) 7
        """.strip(),
        "options": ["4", "5", "6", "7"],
        "correct_answer": 2,  # C şıkkı (6): 3×6+5=23
        "subject": "Matematik",
        "source": "LGS",
        "difficulty": "medium"
    },
    {
        "id": "lgs-fen-1",
        "stem": """
Aşağıdaki maddelerden hangisi element değildir?

A) Demir
B) Su
C) Altın  
D) Karbon
        """.strip(),
        "options": ["Demir", "Su", "Altın", "Karbon"],
        "correct_answer": 1,  # B şıkkı (su bileşiktir)
        "subject": "Fen Bilimleri",
        "source": "LGS", 
        "difficulty": "easy"
    },
    {
        "id": "lgs-sosyal-1",
        "stem": """
Aşağıdakilerden hangisi Osmanlı Devleti'nin kuruluş dönemi beyliklerinden değildir?

A) Karamanoğulları
B) Aydınoğulları
C) Danişmendliler
D) Germiyanoğulları  
        """.strip(),
        "options": ["Karamanoğulları", "Aydınoğulları", "Danişmendliler", "Germiyanoğulları"],
        "correct_answer": 2,  # C şıkkı (daha önceki dönem)
        "subject": "Sosyal Bilgiler",
        "source": "LGS",
        "difficulty": "medium"
    },
    {
        "id": "lgs-ingilizce-1",
        "stem": """
Choose the correct option to complete the sentence:

"I _____ to school every day."

A) go
B) goes
C) going
D) went
        """.strip(),
        "options": ["go", "goes", "going", "went"],
        "correct_answer": 0,  # A şıkkı (Simple Present)
        "subject": "İngilizce",
        "source": "LGS",
        "difficulty": "easy"
    },
    {
        "id": "lgs-turkce-2", 
        "stem": """
"Öğretmen, öğrencilerin başarısından mutlu oldu."
cümlesinde kaç tane isim vardır?

A) 2
B) 3
C) 4
D) 5
        """.strip(),
        "options": ["2", "3", "4", "5"],
        "correct_answer": 1,  # B şıkkı: öğretmen, öğrencilerin, başarısından
        "subject": "Türkçe",
        "source": "LGS",
        "difficulty": "medium"
    },
    {
        "id": "lgs-matematik-2",
        "stem": """
2x + 5 = 13 denkleminin çözüm kümesi aşağıdakilerden hangisidir?

A) {2}
B) {3}  
C) {4}
D) {5}
        """.strip(),
        "options": ["{2}", "{3}", "{4}", "{5}"],
        "correct_answer": 2,  # C şıkkı: x=4
        "subject": "Matematik", 
        "source": "LGS",
        "difficulty": "easy"
    },
    {
        "id": "lgs-fen-2",
        "stem": """
Besinlerin sindirimi ile ilgili aşağıdakilerden hangisi yanlıştır?

A) Karbonhidratların sindirimi ağızda başlar.
B) Proteinlerin sindirimi midede başlar.
C) Yağların sindirimi midede başlar.
D) Sindirimin tamamlanması ince bağırsakta olur.
        """.strip(),
        "options": [
            "Karbonhidratların sindirimi ağızda başlar.",
            "Proteinlerin sindirimi midede başlar.", 
            "Yağların sindirimi midede başlar.",
            "Sindirimin tamamlanması ince bağırsakta olur."
        ],
        "correct_answer": 2,  # C şıkkı (yağların sindirimi ince bağırsakta başlar)
        "subject": "Fen Bilimleri",
        "source": "LGS",
        "difficulty": "medium"
    }
]

def create_bundle_with_proper_questions():
    """Doğru LGS sorularıyla bundle oluştur"""
    
    # Yeni bundle oluştur
    bundle_data = {
        "bundle_id": "lgs-gerçek-sorular",
        "name": "LGS Gerçek Format Sorular", 
        "description": "LGS formatında gerçek Türkçe sorular - doğru format ve içerik",
        "subject_distribution": {
            "Türkçe": 2,
            "Matematik": 2, 
            "Fen Bilimleri": 2,
            "Sosyal Bilgiler": 1,
            "İngilizce": 1
        },
        "difficulty_distribution": {
            "easy": 3,
            "medium": 5
        },
        "total_questions": 8
    }
    
    # Bundle oluştur
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/exams/bundles/",
            json=bundle_data,
            headers={"Authorization": "Bearer test_token", "Content-Type": "application/json"}
        )
        print(f"Bundle creation response: {response.status_code}")
        if response.status_code == 200:
            print("Bundle created successfully!")
        else:
            print(f"Bundle creation failed: {response.text}")
            return
    except Exception as e:
        print(f"Error creating bundle: {e}")
        return
    
    # Soruları ekle
    for question in LGS_QUESTIONS:
        question_data = {
            "bundle_id": "lgs-gerçek-sorular",
            **question
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/questions/",
                json=question_data, 
                headers={"Authorization": "Bearer test_token", "Content-Type": "application/json"}
            )
            print(f"Question {question['id']}: {response.status_code}")
            if response.status_code != 200:
                print(f"Failed to add question: {response.text}")
        except Exception as e:
            print(f"Error adding question {question['id']}: {e}")
    
    print("\n✅ LGS formatında doğru sorularla bundle oluşturuldu!")
    print("Bundle ID: lgs-gerçek-sorular")

if __name__ == "__main__":
    create_bundle_with_proper_questions()