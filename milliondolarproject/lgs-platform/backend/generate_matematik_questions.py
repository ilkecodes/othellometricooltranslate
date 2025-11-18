#!/usr/bin/env python3
"""
Matematik-Focused Question Generator
Specifically generates questions for the matematik curriculum topics you provided
"""

import json
import random
from typing import Dict, List, Any
from anthropic import Anthropic
import os

class MatematikQuestionGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Detailed matematik curriculum based on your provided content
        self.matematik_topics = {
            "M.8.1. SAYILAR VE İŞLEMLER": {
                "M.8.1.1. Çarpanlar ve Katlar": [
                    "M.8.1.1.1. Verilen pozitif tam sayıların pozitif tam sayı çarpanlarını bulur",
                    "M.8.1.1.2. İki doğal sayının EBOB ve EKOK'unu hesaplar", 
                    "M.8.1.1.3. İki doğal sayının aralarında asal olup olmadığını belirler"
                ],
                "M.8.1.2. Üslü İfadeler": [
                    "M.8.1.2.1. Tam sayıların, tam sayı kuvvetlerini hesaplar",
                    "M.8.1.2.2. Üslü ifadelerle ilgili temel kuralları anlar",
                    "M.8.1.2.3. Sayıların ondalık gösterimlerini 10'un kuvvetleriyle çözümler",
                    "M.8.1.2.4. Verilen sayıyı 10'un farklı kuvvetleriyle ifade eder",
                    "M.8.1.2.5. Çok büyük ve küçük sayıları bilimsel gösterimle ifade eder"
                ],
                "M.8.1.3. Kareköklü İfadeler": [
                    "M.8.1.3.1. Tam kare pozitif tam sayılarla karekökü arasındaki ilişkiyi belirler",
                    "M.8.1.3.2. Tam kare olmayan kareköklü sayının hangi iki doğal sayı arasında olduğunu belirler",
                    "M.8.1.3.3. Kareköklü ifadeyi a√b şeklinde yazar",
                    "M.8.1.3.4. Kareköklü ifadelerde çarpma ve bölme işlemlerini yapar",
                    "M.8.1.3.5. Kareköklü ifadelerde toplama ve çıkarma işlemlerini yapar"
                ]
            },
            "M.8.2. CEBİR": {
                "M.8.2.1. Cebirsel İfadeler ve Özdeşlikler": [
                    "M.8.2.1.1. Basit cebirsel ifadeleri anlar ve farklı biçimlerde yazar",
                    "M.8.2.1.2. Cebirsel ifadelerin çarpımını yapar",
                    "M.8.2.1.3. Özdeşlikleri modellerle açıklar",
                    "M.8.2.1.4. Cebirsel ifadeleri çarpanlara ayırır"
                ],
                "M.8.2.2. Doğrusal Denklemler": [
                    "M.8.2.2.1. Birinci dereceden bir bilinmeyenli denklemleri çözer",
                    "M.8.2.2.2. Koordinat sistemini özellikleriyle tanır",
                    "M.8.2.2.3. Doğrusal ilişki bulunan değişkenleri tablo ve denklem ile ifade eder",
                    "M.8.2.2.4. Doğrusal denklemlerin grafiğini çizer",
                    "M.8.2.2.6. Doğrunun eğimini modellerle açıklar"
                ],
                "M.8.2.3. Eşitsizlikler": [
                    "M.8.2.3.1. Eşitsizlik içeren günlük hayat durumlarına uygun matematik cümleleri yazar",
                    "M.8.2.3.2. Birinci dereceden eşitsizlikleri sayı doğrusunda gösterir",
                    "M.8.2.3.3. Birinci dereceden eşitsizlikleri çözer"
                ]
            },
            "M.8.3. GEOMETRİ VE ÖLÇME": {
                "M.8.3.1. Üçgenler": [
                    "M.8.3.1.1. Üçgende kenarortay, açıortay ve yüksekliği inşa eder",
                    "M.8.3.1.2. Üçgen eşitsizliği - iki kenar toplamı üçüncü kenarla ilişki",
                    "M.8.3.1.3. Üçgenin kenar uzunlukları ile açıların ölçülerini ilişkilendirir",
                    "M.8.3.1.5. Pisagor bağıntısını oluşturur, problemleri çözer"
                ],
                "M.8.3.2. Dönüşüm Geometrisi": [
                    "M.8.3.2.1. Öteleme sonucundaki görüntüleri çizer",
                    "M.8.3.2.2. Yansıma sonucu oluşan görüntüleri oluşturur"
                ],
                "M.8.3.4. Geometrik Cisimler": [
                    "M.8.3.4.3. Dik dairesel silindirin yüzey alanı bağıntısını oluşturur",
                    "M.8.3.4.4. Dik dairesel silindirin hacim bağıntısını oluşturur"
                ]
            }
        }
    
    def generate_matematik_question(self, unit: str, topic: str, kazanim: str, difficulty: str = "Orta") -> Dict:
        """Generate a specific matematik question"""
        
        # Create detailed prompts for different matematik topics
        topic_examples = {
            "Çarpanlar ve Katlar": "EBOB, EKOK, asal çarpanlar, ortak bölen kavramları",
            "Üslü İfadeler": "üslü sayılar, bilimsel gösterim, kuvvet kuralları",
            "Kareköklü İfadeler": "karekök, irrasyonel sayılar, kök içine alma/dışına çıkarma",
            "Cebirsel İfadeler": "değişken, katsayı, çarpanlara ayırma, özdeşlikler",
            "Doğrusal Denklemler": "denklem çözme, koordinat sistemi, eğim, grafik",
            "Eşitsizlikler": "eşitsizlik çözme, sayı doğrusu gösterimi",
            "Üçgenler": "kenarortay, açıortay, Pisagor teoremi, üçgen eşitsizliği",
            "Dönüşüm Geometrisi": "öteleme, yansıma, simetri",
            "Geometrik Cisimler": "silindir, prizma, yüzey alanı, hacim"
        }
        
        topic_key = topic.split(". ")[1] if ". " in topic else topic
        examples = topic_examples.get(topic_key, "temel matematik kavramları")
        
        prompt = f"""Sen LGS matematik soru uzmanısın. Aşağıdaki kazanım için {difficulty} seviyesinde bir matematik sorusu oluştur.

KAZANIM BİLGİLERİ:
- Ünite: {unit}
- Konu: {topic}
- Kazanım: {kazanim}
- Zorluk: {difficulty}

KONU ÖRNEKLERİ: {examples}

SORU GEREKSİNİMLERİ:
1. LGS formatında çoktan seçmeli (A, B, C, D)
2. 8. sınıf matematik seviyesine uygun
3. Sayısal hesaplamalar içermeli
4. Net ve anlaşılır matematik dili
5. Kazanımı tam olarak ölçmeli
6. Günlük hayat bağlantısı olabilir

ZORLUK SEVİYESİ DETAYI:
- Kolay: Temel tanımlar, basit hesaplamalar
- Orta: Çok adımlı hesaplar, kavram uygulaması  
- Zor: Problem çözme, analiz, sentez

ÇIKTI FORMATI (JSON):
{{
  "stem": "matematik soru metni (sayılar, formüller, şekil açıklaması dahil)",
  "options": [
    {{"key": "A", "text": "seçenek A"}},
    {{"key": "B", "text": "seçenek B"}},
    {{"key": "C", "text": "seçenek C"}},
    {{"key": "D", "text": "seçenek D"}}
  ],
  "correct_answer": "doğru seçenek harfi",
  "explanation": "adım adım çözüm",
  "confidence": 90
}}

Matematik LGS sorusu oluştur:"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            question_data = json.loads(response_text)
            
            # Add metadata
            question_data.update({
                'unit': unit,
                'topic': topic, 
                'kazanim_description': kazanim,
                'subject': 'Matematik',
                'difficulty_level': difficulty,
                'generated_by': 'MILK',
                'stamp': 'MILK',
                'grade': 8
            })
            
            return question_data
            
        except Exception as e:
            print(f"⚠️ Error generating question for {kazanim}: {e}")
            return None
    
    def generate_comprehensive_matematik_set(self, questions_per_topic: int = 2) -> List[Dict]:
        """Generate a comprehensive matematik question set covering all topics"""
        
        print("🧮 GENERATING COMPREHENSIVE MATEMATIK QUESTION SET")
        print("=" * 60)
        
        all_questions = []
        
        for unit, topics in self.matematik_topics.items():
            print(f"\n📘 {unit}")
            
            for topic, kazanimlar in topics.items():
                print(f"  📚 {topic}")
                
                for i, kazanim in enumerate(kazanimlar):
                    # Vary difficulty
                    difficulties = ['Kolay', 'Orta', 'Zor']
                    difficulty = random.choice(difficulties)
                    
                    print(f"    ⏳ Question {i+1}: {difficulty}")
                    
                    question = self.generate_matematik_question(unit, topic, kazanim, difficulty)
                    
                    if question:
                        all_questions.append(question)
                        confidence = question.get('confidence', 0)
                        print(f"    ✓ Generated ({confidence}% confidence)")
                    else:
                        print(f"    ✗ Failed")
        
        return all_questions

def main():
    print("🧮 MATEMATIK CURRICULUM QUESTION GENERATOR")
    print("=" * 60)
    
    generator = MatematikQuestionGenerator()
    
    # Generate comprehensive matematik questions
    matematik_questions = generator.generate_comprehensive_matematik_set()
    
    # Create output data
    output_data = {
        'title': 'Comprehensive Matematik Question Set - 8th Grade',
        'description': 'Questions covering all matematik curriculum topics based on official MEB program',
        'grade': 8,
        'subject': 'Matematik',
        'total_questions': len(matematik_questions),
        'questions': matematik_questions,
        'curriculum_coverage': {
            'units': len(generator.matematik_topics),
            'topics': sum(len(topics) for topics in generator.matematik_topics.values()),
            'kazanimlar': sum(len(kazanimlar) for topics in generator.matematik_topics.values() for kazanimlar in topics.values())
        },
        'generation_date': '2024-11-14',
        'generator': 'MILK-Matematik-v1.0'
    }
    
    # Save results
    output_file = '/app/comprehensive_matematik_questions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Display summary
    print(f"\n" + "=" * 60)
    print(f"📊 MATEMATIK QUESTION GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total questions generated: {len(matematik_questions)}")
    
    # Count by difficulty
    difficulties = {}
    for q in matematik_questions:
        diff = q.get('difficulty_level', 'Unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\n🎯 By Difficulty:")
    for diff, count in difficulties.items():
        print(f"   {diff}: {count} questions")
    
    # Count by unit
    units = {}
    for q in matematik_questions:
        unit = q.get('unit', 'Unknown')
        units[unit] = units.get(unit, 0) + 1
    
    print(f"\n📘 By Unit:")
    for unit, count in units.items():
        unit_short = unit.split(". ")[1] if ". " in unit else unit
        print(f"   {unit_short}: {count} questions")
    
    print(f"\nOutput saved to: {output_file}")
    print("✅ Comprehensive matematik question set completed!")

if __name__ == "__main__":
    main()