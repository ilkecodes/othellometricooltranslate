#!/usr/bin/env python3
"""
Intelligent Question Generator for LGS Platform
Generates questions following kazanım guidelines and LGS distribution patterns
"""

import json
import sys
import random
from typing import Dict, List, Any, Tuple
from anthropic import Anthropic
import os
from pathlib import Path

class QuestionGenerator:
    def __init__(self, kazanim_file: str, lgs_analysis_file: str):
        """Initialize the question generator with curriculum and distribution data"""
        self.kazanimlar = self.load_kazanimlar(kazanim_file)
        self.lgs_analysis = self.load_lgs_analysis(lgs_analysis_file)
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Create subject-kazanım mapping
        self.kazanim_by_subject = {}
        for kazanim in self.kazanimlar:
            subject = kazanim.get('subject', 'Unknown')
            if subject not in self.kazanim_by_subject:
                self.kazanim_by_subject[subject] = []
            self.kazanim_by_subject[subject].append(kazanim)
        
        # Create distribution mapping
        self.distribution_weights = self.calculate_distribution_weights()
        
    def load_kazanimlar(self, file_path: str) -> List[Dict]:
        """Load kazanımlar from JSONL file"""
        kazanimlar = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                kazanimlar.append(json.loads(line.strip()))
        return kazanimlar
    
    def load_lgs_analysis(self, file_path: str) -> Dict:
        """Load LGS distribution analysis"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_distribution_weights(self) -> Dict[str, Dict[str, float]]:
        """Calculate topic weights based on LGS historical distribution"""
        weights = {}
        
        consistency = self.lgs_analysis.get('consistency', {})
        subjects_analysis = consistency.get('subjects_analysis', {})
        
        for subject, analysis in subjects_analysis.items():
            if not analysis.get('lgs_mapped'):
                continue
                
            weights[subject] = {
                'high_frequency': [],  # >15% - weight 3
                'medium_frequency': [],  # 5-15% - weight 2  
                'low_frequency': []  # <5% - weight 1
            }
            
            freq_analysis = analysis.get('frequency_analysis', {})
            
            # Categorize topics by frequency
            for category, topics in freq_analysis.items():
                if category in weights[subject]:
                    for topic in topics:
                        topic_name = topic.get('name', 'Unknown')
                        avg_percentage = topic.get('avg_percentage', 0)
                        
                        weights[subject][category].append({
                            'name': topic_name,
                            'percentage': avg_percentage,
                            'kazanim_codes': topic.get('kazanim_codes', [])
                        })
        
        return weights
    
    def select_kazanim_by_distribution(self, subject: str, count: int) -> List[Dict]:
        """Select kazanımlar following LGS distribution patterns"""
        if subject not in self.distribution_weights:
            # If no distribution data, select randomly
            available = self.kazanim_by_subject.get(subject, [])
            return random.sample(available, min(count, len(available)))
        
        selected = []
        weights = self.distribution_weights[subject]
        
        # Distribution strategy: 60% high-freq, 30% medium-freq, 10% low-freq
        high_count = int(count * 0.6)
        medium_count = int(count * 0.3)
        low_count = count - high_count - medium_count
        
        # Select from each frequency category
        for category, target_count, weight in [
            ('high_frequency', high_count, 3),
            ('medium_frequency', medium_count, 2),
            ('low_frequency', low_count, 1)
        ]:
            category_kazanimlar = []
            category_topics = weights.get(category, [])
            
            for topic in category_topics:
                # Find kazanımlar related to this topic
                topic_codes = topic.get('kazanim_codes', [])
                for kazanim in self.kazanim_by_subject.get(subject, []):
                    kazanim_code = kazanim.get('code', '')
                    if any(code in kazanim_code for code in topic_codes):
                        category_kazanimlar.append(kazanim)
            
            # Remove duplicates and select
            unique_kazanimlar = list({k['code']: k for k in category_kazanimlar}.values())
            selected.extend(random.sample(unique_kazanimlar, min(target_count, len(unique_kazanimlar))))
        
        # Fill remaining with random selection if needed
        if len(selected) < count:
            all_subject_kazanimlar = self.kazanim_by_subject.get(subject, [])
            used_codes = {k['code'] for k in selected}
            remaining = [k for k in all_subject_kazanimlar if k['code'] not in used_codes]
            
            additional_needed = count - len(selected)
            selected.extend(random.sample(remaining, min(additional_needed, len(remaining))))
        
        return selected[:count]
    
    def determine_difficulty_level(self, kazanim: Dict, topic_frequency: float) -> Tuple[str, str]:
        """Determine difficulty level based on kazanım complexity and topic frequency"""
        
        description = kazanim.get('description', '').lower()
        
        # Difficulty indicators
        easy_indicators = ['tanır', 'listeler', 'sayar', 'hatırlar', 'bilir', 'tanımlar']
        medium_indicators = ['açıklar', 'karşılaştırır', 'analiz eder', 'uygular', 'gösterir']
        hard_indicators = ['değerlendirir', 'sentezler', 'yaratır', 'eleştirir', 'tasarlar', 'oluşturur']
        
        # Base difficulty from content analysis
        easy_count = sum(1 for indicator in easy_indicators if indicator in description)
        medium_count = sum(1 for indicator in medium_indicators if indicator in description)
        hard_count = sum(1 for indicator in hard_indicators if indicator in description)
        
        # Adjust based on topic frequency (high frequency = easier conceptually)
        if topic_frequency >= 15:  # High frequency
            if hard_count > 0:
                difficulty = "Orta"
                level = "medium"
            elif medium_count > 0:
                difficulty = "Kolay" 
                level = "easy"
            else:
                difficulty = "Kolay"
                level = "easy"
        elif topic_frequency >= 5:  # Medium frequency
            if hard_count > medium_count:
                difficulty = "Zor"
                level = "hard"
            elif medium_count > 0:
                difficulty = "Orta"
                level = "medium"
            else:
                difficulty = "Kolay"
                level = "easy"
        else:  # Low frequency
            if hard_count > 0 or medium_count > easy_count:
                difficulty = "Zor"
                level = "hard"
            else:
                difficulty = "Orta"
                level = "medium"
        
        return difficulty, level
    
    def generate_question_with_llm(self, kazanim: Dict, difficulty: str, topic_frequency: float) -> Dict:
        """Generate a question using Claude based on kazanım and difficulty"""
        
        prompt = f"""Sen LGS (Liselere Geçiş Sınavı) soru uzmanısın. Aşağıdaki kazanım için {difficulty} seviyesinde bir soru oluştur.

KAZANIM BİLGİLERİ:
- Kod: {kazanim.get('code', 'Bilinmiyor')}
- Konu: {kazanim.get('subject', 'Bilinmiyor')}
- Açıklama: {kazanim.get('description', 'Açıklama yok')}

ZORLUK SEVİYESİ: {difficulty}
- Kolay: Temel bilgi, tanıma, hatırlama
- Orta: Anlama, uygulama, analiz
- Zor: Sentez, değerlendirme, yaratıcılık

SORU GEREKSİNİMLERİ:
1. LGS formatında çoktan seçmeli (A, B, C, D seçenekli)
2. 8. sınıf seviyesine uygun
3. Türkçe dilbilgisi ve yazım kurallarına uygun
4. Net ve anlaşılır
5. Kazanımı ölçecek şekilde tasarlanmış
6. Gereksiz detaylardan arınmış

ÇIKTI FORMATI (JSON):
{{
  "stem": "soru metni...",
  "options": [
    {{"key": "A", "text": "seçenek metni"}},
    {{"key": "B", "text": "seçenek metni"}},
    {{"key": "C", "text": "seçenek metni"}},
    {{"key": "D", "text": "seçenek metni"}}
  ],
  "correct_answer": "doğru seçenek harfi",
  "explanation": "çözüm açıklaması",
  "confidence": 85
}}

LGS tarzında kaliteli bir soru oluştur:"""

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
                'kazanim_code': kazanim.get('code'),
                'kazanim_subject': kazanim.get('subject'),
                'difficulty_level': difficulty,
                'topic_frequency': topic_frequency,
                'generated_by': 'MILK',
                'stamp': 'MILK'
            })
            
            return question_data
            
        except Exception as e:
            print(f"⚠️ Error generating question for {kazanim.get('code', 'Unknown')}: {e}")
            return None
    
    def generate_questions_for_subject(self, subject: str, count: int) -> List[Dict]:
        """Generate questions for a specific subject following distribution patterns"""
        
        print(f"   🎯 Generating {count} questions for {subject}...")
        
        # Select kazanımlar based on LGS distribution
        selected_kazanimlar = self.select_kazanim_by_distribution(subject, count)
        
        if not selected_kazanimlar:
            print(f"   ⚠️ No kazanımlar found for {subject}")
            return []
        
        questions = []
        
        for i, kazanim in enumerate(selected_kazanimlar, 1):
            print(f"      ⏳ Question {i}/{count}: {kazanim.get('code', 'Unknown')}")
            
            # Find topic frequency for this kazanım
            topic_frequency = self.get_kazanim_frequency(subject, kazanim)
            
            # Determine difficulty
            difficulty, level = self.determine_difficulty_level(kazanim, topic_frequency)
            
            # Generate question
            question = self.generate_question_with_llm(kazanim, difficulty, topic_frequency)
            
            if question:
                questions.append(question)
                confidence = question.get('confidence', 0)
                print(f"      ✓ Generated ({difficulty}, {confidence}% confidence)")
            else:
                print(f"      ✗ Failed to generate question")
        
        return questions
    
    def get_kazanim_frequency(self, subject: str, kazanim: Dict) -> float:
        """Get frequency percentage for a kazanım based on LGS analysis"""
        
        if subject not in self.distribution_weights:
            return 5.0  # Default medium frequency
        
        kazanim_code = kazanim.get('code', '')
        weights = self.distribution_weights[subject]
        
        # Check each frequency category
        for category, topics in weights.items():
            for topic in topics:
                topic_codes = topic.get('kazanim_codes', [])
                if any(code in kazanim_code for code in topic_codes):
                    return topic.get('percentage', 5.0)
        
        return 5.0  # Default if not found
    
    def generate_mixed_question_set(self, total_questions: int, subject_distribution: Dict[str, int]) -> Dict:
        """Generate a mixed set of questions following LGS distribution patterns"""
        
        print(f"🤖 GENERATING {total_questions} QUESTIONS WITH MILK AI")
        print("=" * 50)
        
        all_questions = []
        generation_stats = {
            'total_requested': total_questions,
            'generated_count': 0,
            'by_subject': {},
            'by_difficulty': {'Kolay': 0, 'Orta': 0, 'Zor': 0},
            'by_frequency': {'high': 0, 'medium': 0, 'low': 0},
            'average_confidence': 0
        }
        
        total_confidence = 0
        
        for subject, count in subject_distribution.items():
            if count > 0:
                print(f"\n📚 {subject} - {count} questions")
                subject_questions = self.generate_questions_for_subject(subject, count)
                
                generation_stats['by_subject'][subject] = len(subject_questions)
                generation_stats['generated_count'] += len(subject_questions)
                
                # Update statistics
                for question in subject_questions:
                    difficulty = question.get('difficulty_level', 'Orta')
                    generation_stats['by_difficulty'][difficulty] += 1
                    
                    frequency = question.get('topic_frequency', 5)
                    if frequency >= 15:
                        generation_stats['by_frequency']['high'] += 1
                    elif frequency >= 5:
                        generation_stats['by_frequency']['medium'] += 1
                    else:
                        generation_stats['by_frequency']['low'] += 1
                    
                    confidence = question.get('confidence', 0)
                    total_confidence += confidence
                
                all_questions.extend(subject_questions)
        
        # Calculate average confidence
        if generation_stats['generated_count'] > 0:
            generation_stats['average_confidence'] = round(
                total_confidence / generation_stats['generated_count'], 1
            )
        
        return {
            'questions': all_questions,
            'statistics': generation_stats,
            'generation_date': '2024-11-14',
            'generator_version': 'MILK-1.0'
        }

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_questions.py <kazanim_file> <lgs_analysis_file> <output_file>")
        sys.exit(1)
    
    kazanim_file = sys.argv[1]
    lgs_analysis_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Initialize generator
    print("🚀 INITIALIZING QUESTION GENERATOR")
    print("=" * 50)
    generator = QuestionGenerator(kazanim_file, lgs_analysis_file)
    
    print(f"✓ Loaded {len(generator.kazanimlar)} kazanımlar")
    print(f"✓ Loaded LGS analysis data")
    print(f"✓ Calculated distribution weights for {len(generator.distribution_weights)} subjects")
    
    # Define question distribution (based on typical LGS)
    # Total 90 questions following LGS subject distribution
    subject_distribution = {
        'Türkçe': 20,  # Literature and language
        'Matematik': 20,  # Mathematics  
        'Fen Bilimleri': 20,  # Science
        'İnkılap Tarihi ve Atatürkçülük': 10,  # History
        'Din Kültürü ve Ahlak Bilgisi': 10,  # Religion and ethics
        'English': 10  # English
    }
    
    total_questions = sum(subject_distribution.values())
    
    # Generate questions
    print(f"\n🎲 TARGET DISTRIBUTION:")
    for subject, count in subject_distribution.items():
        percentage = (count / total_questions) * 100
        print(f"   {subject}: {count} questions ({percentage:.1f}%)")
    
    result = generator.generate_mixed_question_set(total_questions, subject_distribution)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Display summary
    stats = result['statistics']
    print(f"\n" + "=" * 50)
    print(f"📊 GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total generated: {stats['generated_count']}/{stats['total_requested']}")
    print(f"Average confidence: {stats['average_confidence']}%")
    
    print(f"\n📚 By Subject:")
    for subject, count in stats['by_subject'].items():
        print(f"   {subject}: {count} questions")
    
    print(f"\n🎯 By Difficulty:")
    for difficulty, count in stats['by_difficulty'].items():
        print(f"   {difficulty}: {count} questions")
    
    print(f"\n📈 By Frequency:")
    freq_map = {'high': 'Yüksek (≥15%)', 'medium': 'Orta (5-15%)', 'low': 'Düşük (<5%)'}
    for freq, count in stats['by_frequency'].items():
        print(f"   {freq_map[freq]}: {count} questions")
    
    print(f"\nOutput saved to: {output_file}")
    print("✅ MILK Question Generator completed successfully!")

if __name__ == "__main__":
    main()