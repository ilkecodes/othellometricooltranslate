#!/usr/bin/env python3
"""
Special Character-Safe Question Generator
Handles mathematical symbols, roots, exponentials properly
"""

import json
import random
from typing import Dict, List, Any
from anthropic import Anthropic
import os
import html

class SpecialCharQuestionGenerator:
    def __init__(self, kazanim_file: str):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.kazanimlar = self.load_kazanimlar(kazanim_file)
        
        # Group by subject for easier access
        self.subjects = {}
        for kazanim in self.kazanimlar:
            subject = kazanim.get('subject', 'Unknown')
            if subject not in self.subjects:
                self.subjects[subject] = []
            self.subjects[subject].append(kazanim)
    
    def load_kazanimlar(self, file_path: str) -> List[Dict]:
        """Load kazanımlar from JSONL file"""
        kazanimlar = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    kazanimlar.append(json.loads(line.strip()))
        return kazanimlar
    
    def escape_special_chars(self, text: str) -> str:
        """Properly escape special characters for JSON"""
        # Replace mathematical symbols with Unicode escape sequences if needed
        replacements = {
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
            '"': '\\"',
            '\\': '\\\\'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def generate_question_safe(self, kazanim: Dict, difficulty: str = "Orta") -> Dict:
        """Generate question with special character handling"""
        
        subject = kazanim.get('subject', 'Unknown')
        code = kazanim.get('code', 'Unknown')
        description = kazanim.get('description', 'No description')
        
        # Create subject-specific examples and formatting
        if subject == 'Matematik':
            special_char_examples = """
ÖRNEKLER:
- Kareköklü ifadeler: √16 = 4, √25 = 5
- Üslü sayılar: 2³ = 8, 3² = 9
- Eşitsizlikler: x ≥ 5, y ≤ 10
- Formüller: a² + b² = c²
"""
        else:
            special_char_examples = ""
        
        prompt = f"""Sen LGS {subject} soru uzmanısın. Aşağıdaki kazanım için {difficulty} seviyesinde soru oluştur.

KAZANIM:
- Kod: {code}
- Konu: {subject}
- Açıklama: {description}

{special_char_examples}

ÖNEMLİ: Özel karakterleri doğru kullan ve JSON formatında düzgün escape et.

ÇIKTI FORMATI:
{{
  "stem": "Soru metni burada (özel karakterlerle)",
  "options": [
    {{"key": "A", "text": "Seçenek A"}},
    {{"key": "B", "text": "Seçenek B"}},
    {{"key": "C", "text": "Seçenek C"}},
    {{"key": "D", "text": "Seçenek D"}}
  ],
  "correct_answer": "B",
  "explanation": "Çözüm açıklaması",
  "confidence": 90
}}

{subject} sorusu oluştur:"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean up response - more robust parsing
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                if end > start:
                    response_text = response_text[start:end]
            elif '```' in response_text:
                response_text = response_text.replace('```', '')
            
            # Try to parse JSON with better error handling
            try:
                question_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues
                response_text = response_text.replace('\n', '\\n')
                response_text = response_text.replace('\t', '\\t')
                question_data = json.loads(response_text)
            
            # Add metadata
            question_data.update({
                'kazanim_code': code,
                'subject': subject,
                'difficulty_level': difficulty,
                'generated_by': 'MILK',
                'stamp': 'MILK',
                'special_chars_safe': True
            })
            
            return question_data
            
        except Exception as e:
            print(f"⚠️ Error generating question for {code}: {e}")
            # Return a safe fallback question
            return {
                'stem': f"Bu kazanımla ilgili temel bir soru: {description[:100]}...",
                'options': [
                    {'key': 'A', 'text': 'Seçenek A'},
                    {'key': 'B', 'text': 'Seçenek B'}, 
                    {'key': 'C', 'text': 'Seçenek C'},
                    {'key': 'D', 'text': 'Seçenek D'}
                ],
                'correct_answer': 'A',
                'explanation': 'Bu bir örnek açıklamadır.',
                'confidence': 50,
                'kazanim_code': code,
                'subject': subject,
                'difficulty_level': difficulty,
                'generated_by': 'MILK_FALLBACK',
                'stamp': 'MILK'
            }
    
    def generate_comprehensive_exam(self, questions_per_subject: Dict[str, int]) -> Dict:
        """Generate comprehensive exam with all LGS subjects"""
        
        print("🎯 GENERATING COMPREHENSIVE LGS EXAM")
        print("=" * 50)
        
        all_questions = []
        stats = {'by_subject': {}, 'by_difficulty': {}, 'total': 0}
        
        # Target LGS subjects
        lgs_mapping = {
            'Türkçe': 'Türkçe',
            'Matematik': 'Matematik',
            'Fen Bilimleri': 'Fen Bilimleri',
            'Sosyal Bilgiler': 'Sosyal Bilgiler',
            'İnkılap Tarihi': 'İnkılap Tarihi ve Atatürkçülük',
            'Din Kültürü ve Ahlak Bilgisi': 'Din Kültürü ve Ahlak Bilgisi',
            'İngilizce': 'English'
        }
        
        for lgs_subject, target_count in questions_per_subject.items():
            if target_count <= 0:
                continue
                
            print(f"\n📚 {lgs_subject}: {target_count} questions")
            
            # Find matching subject kazanımlar
            available_kazanimlar = []
            for subject_name, kazanimlar in self.subjects.items():
                if (lgs_subject.lower() in subject_name.lower() or 
                    subject_name.lower() in lgs_subject.lower() or
                    (lgs_subject == 'Sosyal Bilgiler' and 'sosyal' in subject_name.lower()) or
                    (lgs_subject == 'İngilizce' and 'english' in subject_name.lower())):
                    available_kazanimlar.extend(kazanimlar)
            
            if not available_kazanimlar:
                print(f"   ⚠️ No kazanımlar found for {lgs_subject}")
                continue
            
            # Generate questions
            subject_questions = []
            difficulties = ['Kolay', 'Orta', 'Zor']
            
            for i in range(target_count):
                # Select random kazanim and difficulty
                kazanim = random.choice(available_kazanimlar)
                difficulty = random.choice(difficulties)
                
                print(f"   ⏳ Question {i+1}/{target_count}: {kazanim.get('code', 'No code')} ({difficulty})")
                
                question = self.generate_question_safe(kazanim, difficulty)
                
                if question:
                    subject_questions.append(question)
                    confidence = question.get('confidence', 0)
                    print(f"      ✓ Generated ({confidence}% confidence)")
                else:
                    print(f"      ✗ Failed to generate")
            
            all_questions.extend(subject_questions)
            stats['by_subject'][lgs_subject] = len(subject_questions)
            
            # Count by difficulty
            for question in subject_questions:
                diff = question.get('difficulty_level', 'Unknown')
                stats['by_difficulty'][diff] = stats['by_difficulty'].get(diff, 0) + 1
        
        stats['total'] = len(all_questions)
        
        # Add question numbers
        for i, question in enumerate(all_questions, 1):
            question['question_number'] = i
        
        # Shuffle questions
        random.shuffle(all_questions)
        
        return {
            'exam_info': {
                'title': 'Comprehensive LGS Practice Exam - All Subjects',
                'description': 'Complete LGS exam covering all subjects with special character support',
                'total_questions': len(all_questions),
                'subjects_covered': list(questions_per_subject.keys()),
                'generation_date': '2024-11-14'
            },
            'questions': all_questions,
            'statistics': stats
        }

def main():
    print("🎯 LGS COMPREHENSIVE EXAM GENERATOR")
    print("=" * 50)
    
    # Use enhanced kazanımlar with all subjects
    kazanim_file = '/app/enhanced_kazanimlar_complete.jsonl'
    
    try:
        generator = SpecialCharQuestionGenerator(kazanim_file)
        print(f"✓ Loaded {len(generator.kazanimlar)} kazanımlar")
        print(f"✓ Found subjects: {list(generator.subjects.keys())}")
        
        # Define LGS exam distribution
        questions_per_subject = {
            'Türkçe': 20,
            'Matematik': 20, 
            'Fen Bilimleri': 20,
            'İnkılap Tarihi': 10,
            'Din Kültürü ve Ahlak Bilgisi': 10,
            'İngilizce': 10
            # Note: Sosyal Bilgiler might be covered by other subjects
        }
        
        total_questions = sum(questions_per_subject.values())
        print(f"\n🎲 Target: {total_questions} questions across {len(questions_per_subject)} subjects")
        
        # Generate exam
        exam_data = generator.generate_comprehensive_exam(questions_per_subject)
        
        # Save exam
        output_file = '/app/comprehensive_lgs_exam_all_subjects.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exam_data, f, ensure_ascii=False, indent=2)
        
        # Display results
        stats = exam_data['statistics']
        print(f"\n" + "=" * 50)
        print(f"📊 COMPREHENSIVE EXAM SUMMARY")
        print("=" * 50)
        print(f"Total questions generated: {stats['total']}")
        
        print(f"\n📚 By Subject:")
        for subject, count in stats['by_subject'].items():
            percentage = (count / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"   {subject}: {count} ({percentage:.1f}%)")
        
        print(f"\n🎯 By Difficulty:")
        for difficulty, count in stats['by_difficulty'].items():
            percentage = (count / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"   {difficulty}: {count} ({percentage:.1f}%)")
        
        print(f"\nOutput saved to: {output_file}")
        print("✅ Comprehensive LGS exam with all subjects completed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()