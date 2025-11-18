#!/usr/bin/env python3
"""
Mixed Question Set Builder
Combines original LGS questions (stamped 'LGS') with MILK-generated questions (stamped 'MILK')
"""

import json
import random
import sys
from typing import Dict, List, Any
from collections import defaultdict

def load_original_questions(file_path: str) -> List[Dict]:
    """Load original questions from enhanced extraction"""
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            # Add LGS stamp to original questions
            data['stamp'] = 'LGS'
            data['source'] = 'Original LGS Exam'
            questions.append(data)
    return questions

def load_generated_questions(file_path: str) -> List[Dict]:
    """Load MILK-generated questions"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('questions', [])

def categorize_questions_by_subject_and_difficulty(questions: List[Dict]) -> Dict:
    """Categorize questions by subject and difficulty for balanced mixing"""
    categorized = defaultdict(lambda: defaultdict(list))
    
    for question in questions:
        subject = question.get('subject') or question.get('kazanim_subject', 'Unknown')
        
        # Determine difficulty for original questions (if not present)
        if 'difficulty_level' not in question:
            # Basic heuristic for original questions
            stem = question.get('stem', '').lower()
            if any(word in stem for word in ['basit', 'temel', 'hangi']):
                difficulty = 'Kolay'
            elif any(word in stem for word in ['analiz', 'karşılaştır', 'değerlendir']):
                difficulty = 'Zor'  
            else:
                difficulty = 'Orta'
            question['difficulty_level'] = difficulty
        
        difficulty = question.get('difficulty_level', 'Orta')
        categorized[subject][difficulty].append(question)
    
    return categorized

def create_balanced_mix(original_questions: List[Dict], generated_questions: List[Dict], 
                       target_count: int, mix_ratio: float = 0.6) -> List[Dict]:
    """Create a balanced mix of original and generated questions
    
    Args:
        mix_ratio: Ratio of original questions (0.6 = 60% original, 40% generated)
    """
    
    # Categorize both sets
    original_categorized = categorize_questions_by_subject_and_difficulty(original_questions)
    generated_categorized = categorize_questions_by_subject_and_difficulty(generated_questions)
    
    # Calculate target counts
    original_target = int(target_count * mix_ratio)
    generated_target = target_count - original_target
    
    mixed_questions = []
    used_original = set()
    used_generated = set()
    
    # Get all subjects from both sets
    all_subjects = set(original_categorized.keys()) | set(generated_categorized.keys())
    
    # Distribute questions proportionally across subjects
    subject_weights = {}
    total_available = 0
    
    for subject in all_subjects:
        orig_count = sum(len(diff_questions) for diff_questions in original_categorized[subject].values())
        gen_count = sum(len(diff_questions) for diff_questions in generated_categorized[subject].values())
        subject_weights[subject] = orig_count + gen_count
        total_available += subject_weights[subject]
    
    # Select questions for each subject proportionally
    for subject in all_subjects:
        if total_available == 0:
            continue
            
        # Calculate proportion for this subject
        subject_proportion = subject_weights[subject] / total_available
        subject_original_target = int(original_target * subject_proportion)
        subject_generated_target = int(generated_target * subject_proportion)
        
        # Select original questions for this subject
        subject_original_selected = []
        for difficulty in ['Kolay', 'Orta', 'Zor']:
            available = original_categorized[subject][difficulty]
            available_unused = [q for q in available if id(q) not in used_original]
            
            difficulty_target = max(1, subject_original_target // 3)
            selected = random.sample(available_unused, min(difficulty_target, len(available_unused)))
            
            for q in selected:
                used_original.add(id(q))
                subject_original_selected.append(q)
        
        # Select generated questions for this subject  
        subject_generated_selected = []
        for difficulty in ['Kolay', 'Orta', 'Zor']:
            available = generated_categorized[subject][difficulty]
            available_unused = [q for q in available if id(q) not in used_generated]
            
            difficulty_target = max(1, subject_generated_target // 3)
            selected = random.sample(available_unused, min(difficulty_target, len(available_unused)))
            
            for q in selected:
                used_generated.add(id(q))
                subject_generated_selected.append(q)
        
        mixed_questions.extend(subject_original_selected[:subject_original_target])
        mixed_questions.extend(subject_generated_selected[:subject_generated_target])
    
    # Fill remaining slots if needed
    while len(mixed_questions) < target_count:
        # Add remaining original questions
        remaining_original = [q for q in original_questions if id(q) not in used_original]
        if remaining_original and len(mixed_questions) < target_count:
            q = random.choice(remaining_original)
            mixed_questions.append(q)
            used_original.add(id(q))
            continue
        
        # Add remaining generated questions
        remaining_generated = [q for q in generated_questions if id(q) not in used_generated]
        if remaining_generated and len(mixed_questions) < target_count:
            q = random.choice(remaining_generated)
            mixed_questions.append(q)
            used_generated.add(id(q))
            continue
        
        break
    
    # Shuffle the final mix
    random.shuffle(mixed_questions)
    
    return mixed_questions[:target_count]

def add_question_numbers(questions: List[Dict]) -> List[Dict]:
    """Add sequential question numbers"""
    for i, question in enumerate(questions, 1):
        question['question_number'] = i
    return questions

def generate_mix_statistics(questions: List[Dict]) -> Dict:
    """Generate statistics about the mixed question set"""
    
    stats = {
        'total_questions': len(questions),
        'by_source': {'LGS': 0, 'MILK': 0},
        'by_subject': defaultdict(int),
        'by_difficulty': defaultdict(int),
        'by_subject_and_source': defaultdict(lambda: {'LGS': 0, 'MILK': 0})
    }
    
    for question in questions:
        # Source statistics
        stamp = question.get('stamp', 'Unknown')
        if stamp in stats['by_source']:
            stats['by_source'][stamp] += 1
        
        # Subject statistics
        subject = question.get('subject') or question.get('kazanim_subject', 'Unknown')
        stats['by_subject'][subject] += 1
        stats['by_subject_and_source'][subject][stamp] += 1
        
        # Difficulty statistics
        difficulty = question.get('difficulty_level', 'Unknown')
        stats['by_difficulty'][difficulty] += 1
    
    # Convert defaultdicts to regular dicts for JSON serialization
    stats['by_subject'] = dict(stats['by_subject'])
    stats['by_difficulty'] = dict(stats['by_difficulty'])
    stats['by_subject_and_source'] = {k: dict(v) for k, v in stats['by_subject_and_source'].items()}
    
    return stats

def main():
    if len(sys.argv) != 4:
        print("Usage: python mix_questions.py <original_questions_jsonl> <generated_questions_json> <output_json>")
        sys.exit(1)
    
    original_file = sys.argv[1]
    generated_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("🔄 MIXING ORIGINAL LGS + MILK QUESTIONS")
    print("=" * 50)
    
    # Load questions
    print("\n1️⃣ Loading question sets...")
    try:
        original_questions = load_original_questions(original_file)
        print(f"✓ Loaded {len(original_questions)} original LGS questions")
        
        generated_questions = load_generated_questions(generated_file)
        print(f"✓ Loaded {len(generated_questions)} MILK-generated questions")
        
    except Exception as e:
        print(f"✗ Error loading questions: {e}")
        sys.exit(1)
    
    # Create balanced mix
    print(f"\n2️⃣ Creating balanced question mix...")
    target_count = 50  # Target exam length
    mix_ratio = 0.6    # 60% original, 40% generated
    
    print(f"   Target: {target_count} questions")
    print(f"   Mix ratio: {int(mix_ratio*100)}% LGS, {int((1-mix_ratio)*100)}% MILK")
    
    mixed_questions = create_balanced_mix(original_questions, generated_questions, target_count, mix_ratio)
    
    # Add question numbers
    mixed_questions = add_question_numbers(mixed_questions)
    
    # Generate statistics
    print(f"\n3️⃣ Generating mix statistics...")
    stats = generate_mix_statistics(mixed_questions)
    
    # Create output data
    output_data = {
        'exam_info': {
            'title': 'LGS Karma Deneme Sınavı',
            'description': 'Original LGS questions mixed with MILK-generated questions',
            'question_count': len(mixed_questions),
            'mix_ratio': mix_ratio,
            'creation_date': '2024-11-14'
        },
        'questions': mixed_questions,
        'statistics': stats
    }
    
    # Save mixed question set
    print(f"\n4️⃣ Saving mixed question set...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Display summary
    print(f"\n" + "=" * 50)
    print(f"📊 MIXED QUESTION SET SUMMARY")
    print("=" * 50)
    print(f"Total questions: {stats['total_questions']}")
    
    print(f"\n🏷️ By Source:")
    for source, count in stats['by_source'].items():
        percentage = (count / stats['total_questions']) * 100
        print(f"   {source}: {count} ({percentage:.1f}%)")
    
    print(f"\n📚 By Subject:")
    for subject, count in stats['by_subject'].items():
        percentage = (count / stats['total_questions']) * 100
        print(f"   {subject}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎯 By Difficulty:")
    for difficulty, count in stats['by_difficulty'].items():
        percentage = (count / stats['total_questions']) * 100
        print(f"   {difficulty}: {count} ({percentage:.1f}%)")
    
    print(f"\n📋 Subject-Source Breakdown:")
    for subject, sources in stats['by_subject_and_source'].items():
        lgs_count = sources.get('LGS', 0)
        milk_count = sources.get('MILK', 0)
        print(f"   {subject}: {lgs_count} LGS + {milk_count} MILK")
    
    print(f"\nOutput saved to: {output_file}")
    print("✅ Mixed question set created successfully!")

if __name__ == "__main__":
    main()