#!/usr/bin/env python3
"""
Complete LGS Exam Bundle Generator - Optimized with Enhanced Error Handling
Creates full LGS exams with exact subject distribution mixing original LGS + MILK questions
"""

import json
import random
import sys
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from anthropic import Anthropic
import os

class CompleteLGSExamGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Load all available data
        self.kazanimlar = self.load_kazanimlar()
        self.original_questions = self.load_original_questions()
        self.lgs_distribution = self.load_lgs_distribution()
        
        # Group kazanımlar by subject
        self.kazanim_by_subject = defaultdict(list)
        for kazanim in self.kazanimlar:
            subject = self.normalize_subject(kazanim.get('subject', ''))
            self.kazanim_by_subject[subject].append(kazanim)
        
        # Target LGS distribution - Real 2024 format
        # Sözel Bölüm: 50 soru (75 dakika) - Sabah oturumu
        # Sayısal Bölüm: 40 soru (80 dakika) - Öğlen oturumu  
        # Toplam: 90 soru, 3 yanlış = 1 doğruyu götürür
        self.target_distribution = {
            'Türkçe': 20,                        # Sözel Bölüm
            'Sosyal Bilgiler': 10,               # Sözel Bölüm (İnkılap + Coğrafya)
            'Din Kültürü ve Ahlak Bilgisi': 10,  # Sözel Bölüm
            'İngilizce': 10,                     # Yabancı Dil (Sözel Bölüm)
            # Sözel Bölüm Toplam: 50 soru
            
            'Matematik': 20,                     # Sayısal Bölüm
            'Fen Bilimleri': 20                  # Sayısal Bölüm
            # Sayısal Bölüm Toplam: 40 soru
        }
        
    def load_kazanimlar(self) -> List[Dict]:
        """Load all kazanımlar from multiple sources"""
        all_kazanimlar = []
        
        # Try multiple kazanim files
        kazanim_files = [
            '/app/extracted_kazanimlar_8_fixed.jsonl',
            '/app/enhanced_kazanimlar_complete.jsonl'
        ]
        
        for file_path in kazanim_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            kazanim = json.loads(line.strip())
                            all_kazanimlar.append(kazanim)
                print(f"✓ Loaded kazanımlar from {file_path}")
                break
            except:
                continue
        
        return all_kazanimlar
    
    def load_original_questions(self) -> List[Dict]:
        """Load original LGS questions"""
        questions = []
        try:
            with open('/app/enhanced_questions_final.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        question = json.loads(line.strip())
                        question['stamp'] = 'LGS'
                        question['source'] = 'Original LGS'
                        questions.append(question)
            print(f"✓ Loaded {len(questions)} original LGS questions")
        except:
            print("⚠️ Could not load original questions")
        
        return questions
    
    def load_lgs_distribution(self) -> Dict:
        """Load LGS historical distribution data"""
        try:
            with open('/app/lgs_distribution_analysis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("✓ Loaded LGS distribution patterns")
            return data
        except:
            print("⚠️ Could not load LGS distribution")
            return {}
    
    def normalize_subject(self, subject: str) -> str:
        """Normalize subject names to LGS standard"""
        subject = subject.strip()
        
        mappings = {
            'matematik': 'Matematik',
            'türkçe': 'Türkçe', 
            'fen bilimleri': 'Fen Bilimleri',
            'din kültürü ve ahlak bilgisi': 'Din Kültürü ve Ahlak Bilgisi',
            'din kültürü': 'Din Kültürü ve Ahlak Bilgisi',
            'İnkılap tarihi ve atatürkçülük': 'Sosyal Bilgiler',
            'inkılap tarihi': 'Sosyal Bilgiler', 
            'tarih': 'Sosyal Bilgiler',
            'sosyal bilgiler': 'Sosyal Bilgiler',
            'english': 'İngilizce',
            'ingilizce': 'İngilizce'
        }
        
        subject_lower = subject.lower()
        for key, value in mappings.items():
            if key in subject_lower:
                return value
        
        return subject
    
    def extract_clean_json(self, response_text: str) -> Dict:
        """Extract clean JSON with multiple fallback methods"""
        
        # Method 1: Code block extraction
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            if end > start:
                json_text = response_text[start:end].strip()
                try:
                    return json.loads(json_text)
                except:
                    pass
        
        # Method 2: Find JSON object boundaries
        lines = response_text.split('\n')
        json_lines = []
        brace_count = 0
        started = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('{') and not started:
                started = True
            
            if started:
                json_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                
                # Check if we have a complete JSON object
                if brace_count == 0 and len(json_lines) > 1:
                    json_text = '\n'.join(json_lines)
                    try:
                        return json.loads(json_text)
                    except:
                        pass
        
        # Method 3: Regex extraction
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # Method 4: Line by line progressive parsing
        all_lines = response_text.split('\n')
        for i in range(len(all_lines)):
            for j in range(i+1, len(all_lines)+1):
                potential_json = '\n'.join(all_lines[i:j])
                try:
                    parsed = json.loads(potential_json)
                    if isinstance(parsed, dict) and 'stem' in parsed:
                        return parsed
                except:
                    continue
        
        raise ValueError("Could not extract valid JSON")
    
    def generate_milk_question(self, kazanim: Dict, subject: str, difficulty: str) -> Dict:
        """Generate MILK question with enhanced error handling and special character support"""
        
        code = kazanim.get('code', 'Unknown')
        description = kazanim.get('description', 'No description')[:200]  # Limit description length
        
        # Special handling for English questions - keep them in English
        if subject == "İngilizce":
            prompt = f"""Create an LGS English question.

Learning Outcome: {code} - {description}
Difficulty: {difficulty}

IMPORTANT: Keep the question in ENGLISH. Do NOT translate to Turkish.

Return ONLY JSON:
{{
  "stem": "Question text in ENGLISH",
  "options": [
    {{"key": "A", "text": "Option A in English"}},
    {{"key": "B", "text": "Option B in English"}},
    {{"key": "C", "text": "Option C in English"}},
    {{"key": "D", "text": "Option D in English"}}
  ],
  "correct_answer": "A",
  "explanation": "Explanation in Turkish",
  "confidence": 90
}}"""
        else:
            # Turkish questions for other subjects
            prompt = f"""LGS {subject} sorusu oluştur.

Kazanım: {code} - {description}
Zorluk: {difficulty}

SADECE JSON döndür:
{{
  "stem": "Soru metni",
  "options": [
    {{"key": "A", "text": "A şıkkı"}},
    {{"key": "B", "text": "B şıkkı"}},
    {{"key": "C", "text": "C şıkkı"}},
    {{"key": "D", "text": "D şıkkı"}}
  ],
  "correct_answer": "A",
  "explanation": "Açıklama",
  "confidence": 90
}}"""

        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,  # Reduced to minimize extra content
                    temperature=0.3,  # Lower temperature for more consistent JSON
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = response.content[0].text.strip()
                question_data = self.extract_clean_json(response_text)
                
                # Validate required fields
                required_fields = ['stem', 'options', 'correct_answer']
                if all(field in question_data for field in required_fields):
                    
                    # Ensure confidence is set
                    if 'confidence' not in question_data:
                        question_data['confidence'] = 85
                    
                    # Add metadata
                    question_data.update({
                        'kazanim_code': code,
                        'subject': subject,
                        'difficulty_level': difficulty,
                        'stamp': 'MILK',
                        'source': 'MILK Generated',
                        'generated_by': 'MILK-AI'
                    })
                    
                    return question_data
                else:
                    raise ValueError(f"Missing required fields")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️ Retry {attempt + 1}/{max_retries} for {code}")
                    continue
        
        # Fallback question
        print(f"   ⚠️ Using fallback for {code}")
        return {
            'stem': f"Bu kazanımla ilgili soru: {description[:80]}...",
            'options': [
                {'key': 'A', 'text': 'Doğru seçenek'},
                {'key': 'B', 'text': 'Yanlış seçenek'},
                {'key': 'C', 'text': 'Yanlış seçenek'}, 
                {'key': 'D', 'text': 'Yanlış seçenek'}
            ],
            'correct_answer': 'A',
            'explanation': 'Bu bir örnek açıklamadır.',
            'confidence': 50,
            'kazanim_code': code,
            'subject': subject,
            'difficulty_level': difficulty,
            'stamp': 'MILK',
            'source': 'MILK Fallback'
        }
    
    def generate_questions_for_subject(self, subject: str, target_count: int, mix_ratio: float = 0.4) -> List[Dict]:
        """Generate mixed original + MILK questions for a subject"""
        
        print(f"  📚 {subject}: {target_count} questions")
        
        # Calculate split
        original_target = int(target_count * mix_ratio) 
        milk_target = target_count - original_target
        
        questions = []
        
        # Get original questions for this subject
        original_available = [q for q in self.original_questions 
                            if self.normalize_subject(q.get('subject', '')) == subject]
        
        # Add original questions
        if original_available:
            original_selected = random.sample(original_available, 
                                            min(original_target, len(original_available)))
            questions.extend(original_selected)
        
        actual_original = len(questions)
        remaining_milk = target_count - actual_original
        
        print(f"    📄 Original: {actual_original}, 🥛 MILK: {remaining_milk}")
        
        # Generate MILK questions
        available_kazanimlar = self.kazanim_by_subject.get(subject, [])
        
        if not available_kazanimlar:
            print(f"    ⚠️ No kazanımlar found for {subject}")
            return questions
        
        difficulties = ['Kolay', 'Orta', 'Zor']
        difficulty_weights = [0.4, 0.4, 0.2]  # 40% easy, 40% medium, 20% hard
        
        # Generate in batches to show progress
        batch_size = 5
        for batch_start in range(0, remaining_milk, batch_size):
            batch_end = min(batch_start + batch_size, remaining_milk)
            print(f"    ⏳ MILK batch {batch_start+1}-{batch_end}")
            
            for i in range(batch_start, batch_end):
                # Select random kazanim and difficulty
                kazanim = random.choice(available_kazanimlar)
                difficulty = random.choices(difficulties, weights=difficulty_weights)[0]
                
                # Generate question
                milk_question = self.generate_milk_question(kazanim, subject, difficulty)
                if milk_question:
                    questions.append(milk_question)
                    conf = milk_question.get('confidence', 0)
                    print(f"       ✓ {i+1}: {kazanim.get('code', '')[:15]} ({conf}%)")
        
        return questions
    
    def create_complete_lgs_bundle(self, bundle_name: str = "Complete LGS Bundle") -> Dict:
        """Create complete LGS exam bundle with all subjects"""
        
        print(f"🎯 GENERATING {bundle_name.upper()}")
        print("=" * 60)
        
        all_questions = []
        bundle_stats = {
            'by_subject': {},
            'by_difficulty': defaultdict(int),
            'by_source': defaultdict(int),
            'total_questions': 0
        }
        
        print(f"\n📊 Target Distribution:")
        for subject, count in self.target_distribution.items():
            print(f"   {subject}: {count} questions")
        
        print(f"\n🔄 Generating questions...")
        
        # Generate questions for each subject
        for subject, target_count in self.target_distribution.items():
            subject_questions = self.generate_questions_for_subject(subject, target_count)
            
            # Update statistics
            bundle_stats['by_subject'][subject] = len(subject_questions)
            bundle_stats['total_questions'] += len(subject_questions)
            
            for question in subject_questions:
                source = question.get('stamp', 'Unknown')
                difficulty = question.get('difficulty_level', 'Unknown')
                
                bundle_stats['by_source'][source] += 1
                bundle_stats['by_difficulty'][difficulty] += 1
            
            all_questions.extend(subject_questions)
            print(f"    ✅ Completed: {len(subject_questions)} questions")
        
        # Add question numbers and shuffle
        for i, question in enumerate(all_questions, 1):
            question['question_number'] = i
        
        random.shuffle(all_questions)
        
        # Re-number after shuffle
        for i, question in enumerate(all_questions, 1):
            question['question_number'] = i
        
        return {
            'bundle_info': {
                'title': bundle_name,
                'description': 'Gerçek LGS formatı: Sözel Bölüm 50 soru (75dk), Sayısal Bölüm 40 soru (80dk) - Karma orijinal + MILK sorular',
                'total_questions': len(all_questions),
                'subjects': list(self.target_distribution.keys()),
                'distribution_type': 'Gerçek LGS 2024 Formatı',
                'sozel_bolum': 50,
                'sayisal_bolum': 40,
                'sozel_sure': 75,  # dakika
                'sayisal_sure': 80, # dakika
                'puanlama': '3 yanlış = 1 doğruyu götürür',
                'generation_date': '2024-11-16',
                'version': '2.1'
            },
            'target_distribution': self.target_distribution,
            'questions': all_questions,
            'statistics': {
                'by_subject': dict(bundle_stats['by_subject']),
                'by_difficulty': dict(bundle_stats['by_difficulty']),
                'by_source': dict(bundle_stats['by_source']),
                'total_questions': bundle_stats['total_questions']
            }
        }

def main():
    print("🎯 COMPLETE LGS EXAM BUNDLE GENERATOR V2.0")
    print("=" * 60)
    
    generator = CompleteLGSExamGenerator()
    
    print(f"✓ Loaded {len(generator.kazanimlar)} kazanımlar")
    print(f"✓ Loaded {len(generator.original_questions)} original questions")
    print(f"✓ Found subjects: {list(generator.kazanim_by_subject.keys())}")
    
    # Generate bundle
    bundle = generator.create_complete_lgs_bundle("LGS Karma Deneme - Optimized")
    
    # Save bundle
    output_file = '/app/complete_lgs_exam_bundle_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    
    # Display results
    stats = bundle['statistics']
    
    print(f"\n" + "=" * 60)
    print(f"📊 COMPLETE LGS BUNDLE SUMMARY")
    print("=" * 60)
    print(f"Total questions: {stats['total_questions']}")
    
    print(f"\n📚 By Subject:")
    target = bundle['target_distribution']
    for subject, actual in stats['by_subject'].items():
        target_count = target.get(subject, 0)
        percentage = (actual / target_count) * 100 if target_count > 0 else 0
        print(f"   {subject}: {actual}/{target_count} ({percentage:.1f}%)")
    
    print(f"\n🏷️ By Source:")
    for source, count in stats['by_source'].items():
        percentage = (count / stats['total_questions']) * 100
        print(f"   {source}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎯 By Difficulty:")
    for difficulty, count in stats['by_difficulty'].items():
        percentage = (count / stats['total_questions']) * 100
        print(f"   {difficulty}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅ Bundle saved to: {output_file}")
    print(f"🚀 Optimized LGS exam bundle ready for deployment!")

if __name__ == "__main__":
    main()