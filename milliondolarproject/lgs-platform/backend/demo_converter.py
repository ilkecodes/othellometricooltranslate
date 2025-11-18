#!/usr/bin/env python3
"""
Convert the structured exam data to JSONL format for seeding.
This demonstrates what the hybrid parser would output.
"""

import json

# Your structured exam data
exam_data = {
    "title": "2025 Sınavla Öğrenci Alacak Ortaöğretim Kurumlarına İlişkin Merkezi Sınav - Sözel Bölüm",
    "date": "15 Haziran 2025",
    "duration": "75 dakika",
    "totalQuestions": 50,
    "subjects": [
        {
            "name": "TÜRKÇE",
            "questionCount": 20,
            "questions": [
                {
                    "number": 1,
                    "topic": "Sözcük Anlamı ve Bağlam",
                    "question": "Hiç tanımadığımız ancak görür görmez içimizin ısındığı, şöyle bir kucaklayıp da sarmalamak istediğimiz insanlar vardır. Onların gülüşlerinde duygularının yıpranmış, çok acı çekmiş olduklarını görürsünz. Fakat bu kişiler yine de - - - -, yaşama direncini ve umudunu yitirmemiş insanlardır...",
                    "answer": "B) pes etmemiş - koruyucu",
                    "explanation": "Metinde yaşam direnci ve umut vurgusu yapılıyor. 'Pes etmemiş' ve 'koruyucu' sözcükleri bu anlama en uygun seçenekler."
                },
                {
                    "number": 2,
                    "topic": "Anlam ve İfade Yorumlama",
                    "question": "Vatanına borçlu olarak ölmek istemez Fazıl Hüsnü Dağlarca. O ki şairdir, nefesiyle dalgalandırmalıdır bayrağını. Bu metindeki altı çizili ifadeyle anlatılmak istenen nedir?",
                    "answer": "A) Bağımsızlık mücadelesine şiirleriyle katılmak",
                    "explanation": "Şairin 'nefesiyle bayrağı dalgalandırması' ifadesi şiirleriyle vatan savunmasına katılma metaforudur."
                },
                {
                    "number": 3,
                    "topic": "Mantıksal Çıkarım",
                    "question": "'Birçok türde yazdım ama kendimi en iyi ifade ettiğim tür şiir oldu.' diyen bir sanatçı için aşağıdakilerden hangisi kesinlikle söylenir?",
                    "answer": "C) Şiir, sanatçının kendini iyi ifade ettiği türler arasındadır",
                    "explanation": "Mantıksal olarak 'en iyi' ifade ettiği tür şiirse, şiir iyi ifade ettiği türler arasında yer alır."
                },
                {
                    "number": 4,
                    "topic": "Ana Düşünce Bulma",
                    "question": "Yabancı kültür unsurlarını bire bir kopyalamak yerine bunları millî değerlerimizle yorumlayarak yeni tasarımlar ortaya koymamız gerekir. Bu cümlede anlatılmak istenen nedir?",
                    "answer": "D) Farklı kültürlere ait ögeler milletimize özgü bir bakış açısıyla işlenerek özgün eserler verilmelidir",
                    "explanation": "Yabancı unsurların millî değerlerle yorumlanması vurgulanıyor."
                },
                {
                    "number": 5,
                    "topic": "Cümle Yapısı ve Anlatım Bozuklukları",
                    "question": "Aşağıdaki cümlelerin hangisinde nesne eksikliğinden kaynaklanan anlatım bozukluğu yoktur?",
                    "answer": "C) Dilimizi doğru bir şekilde konuşmalı, gerekli özeni göstermeliyiz",
                    "explanation": "Bu cümlede 'dilimizi konuşmalı' ve 'özeni göstermeliyiz' şeklinde nesneler tam."
                }
            ]
        },
        {
            "name": "T.C. İNKILAP TARİHİ VE ATATÜRKÇÜLÜK", 
            "questionCount": 10,
            "questions": [
                {
                    "number": 1,
                    "topic": "Atatürk İlkeleri",
                    "question": "Mustafa Kemal Atatürk 'Artık duramayız, mutlaka ileri gideceğiz çünkü mecburuz! Medeni dünya çok ileridedir...' sözleriyle hangi ilkenin önemini vurgulamıştır?",
                    "answer": "C) İnkılapçılık",
                    "explanation": "Sürekli ilerleme ve yenileşme vurgusu inkılapçılık ilkesine işaret eder."
                }
            ]
        },
        {
            "name": "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ",
            "questionCount": 10, 
            "questions": [
                {
                    "number": 1,
                    "topic": "İyilik ve Niyet",
                    "question": "Yardımseverin 'kendimi aşçının elindeki kepçe gibi kabul ediyorum' sözüyle asıl mesaj nedir?",
                    "answer": "C) İyilik, her şeyin sahibinin Allah olduğu bilinciyle yapılmalıdır",
                    "explanation": "Kepçe metaforu, kişinin sadece aracı olduğunu, asıl verenin Allah olduğunu anlatıyor."
                }
            ]
        },
        {
            "name": "YABANCI DİL (İNGİLİZCE)",
            "questionCount": 10,
            "questions": [
                {
                    "number": 1,
                    "topic": "Reading Comprehension - Opinions", 
                    "question": "Who says something positive about his/her friend?",
                    "answer": "A) Alex",
                    "explanation": "Alex says Tim organizes birthday parties, which is positive. Others express negative opinions."
                }
            ]
        }
    ]
}

def parse_answer_options(answer_text):
    """
    Parse answer text to extract options.
    Format: "B) pes etmemiş - koruyucu"
    """
    # For this demo, create mock options since we only have the correct answer
    correct_letter = answer_text[0]  # Extract A, B, C, or D
    correct_text = answer_text[3:]   # Extract text after ") "
    
    # Generate mock options (in real LLM extraction, we'd get all 4)
    mock_options = [
        {"label": "A", "text": "Option A text"},
        {"label": "B", "text": "Option B text"}, 
        {"label": "C", "text": "Option C text"},
        {"label": "D", "text": "Option D text"}
    ]
    
    # Set the correct option text
    for opt in mock_options:
        if opt["label"] == correct_letter:
            opt["text"] = correct_text
            
    return mock_options, correct_letter

def convert_to_jsonl_format():
    """Convert structured data to JSONL format expected by seed_from_llm.py"""
    
    subject_mapping = {
        "TÜRKÇE": "Türkçe",
        "T.C. İNKILAP TARİHİ VE ATATÜRKÇÜLÜK": "Sosyal Bilgiler", 
        "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ": "Din Kültürü ve Ahlak Bilgisi",
        "YABANCI DİL (İNGİLİZCE)": "İngilizce"
    }
    
    questions = []
    
    for subject in exam_data["subjects"]:
        subject_name = subject_mapping.get(subject["name"], subject["name"])
        
        for q in subject["questions"]:
            options, correct_answer = parse_answer_options(q["answer"])
            
            question_data = {
                "number": q["number"],
                "stem": q["question"],
                "options": options,
                "correct_answer": correct_answer,
                "subject": subject_name,
                "topic": q["topic"],
                "confidence": 1.0,  # Perfect since this is structured data
                "explanation": q.get("explanation", "")
            }
            
            questions.append(question_data)
    
    return questions

def save_to_jsonl(filename="demo_extracted_questions.jsonl"):
    """Save questions to JSONL format"""
    questions = convert_to_jsonl_format()
    
    with open(filename, 'w', encoding='utf-8') as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    
    print(f"✓ Converted {len(questions)} questions to {filename}")
    print(f"\nSubject breakdown:")
    
    subjects = {}
    for q in questions:
        subj = q["subject"]
        subjects[subj] = subjects.get(subj, 0) + 1
    
    for subj, count in subjects.items():
        print(f"  {subj}: {count} questions")
    
    return len(questions)

if __name__ == "__main__":
    count = save_to_jsonl()
    print(f"\n✅ Demo extraction complete! Ready for seeding.")
    print(f"\nNext step:")
    print(f"  docker-compose exec -T backend python /app/seed_from_llm.py /app/demo_extracted_questions.jsonl")