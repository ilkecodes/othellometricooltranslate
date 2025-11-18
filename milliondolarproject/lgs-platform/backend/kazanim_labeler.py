#!/usr/bin/env python3
"""
Kazanım Labeler: Tool for analyzing and labeling unknown kazanımlar

This tool helps identify unknown learning outcomes and provides
an interface for manual subject classification.
"""

import json
import sys
from collections import defaultdict

def analyze_unknown_kazanimlar(jsonl_file: str):
    """Analyze unknown kazanımlar and group them for easier labeling."""
    
    unknown_kazanimlar = []
    subject_stats = defaultdict(int)
    
    print("📖 Loading kazanımlar...")
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                kazanim = json.loads(line)
                subject = kazanim.get('subject')
                
                if subject:
                    subject_stats[subject] += 1
                else:
                    unknown_kazanimlar.append({
                        'line': line_num,
                        'code': kazanim.get('code', 'N/A'),
                        'description': kazanim.get('description', 'N/A'),
                        'topic': kazanim.get('topic', 'N/A'),
                        'terms': kazanim.get('terms', []),
                        'page': kazanim.get('page', 'N/A'),
                        'grade': kazanim.get('grade', 'N/A')
                    })
            except Exception as e:
                print(f'⚠️  Error on line {line_num}: {e}')
    
    # Analyze patterns in unknown kazanımlar
    code_patterns = defaultdict(list)
    topic_patterns = defaultdict(list)
    
    for kazanim in unknown_kazanimlar:
        code = kazanim['code']
        topic = kazanim['topic']
        
        # Group by code prefix
        if code and code != 'N/A':
            prefix = code.split('.')[0] if '.' in code else code[:2]
            code_patterns[prefix].append(kazanim)
        
        # Group by topic
        if topic and topic != 'N/A' and topic != 'None':
            topic_patterns[topic].append(kazanim)
    
    # Display analysis
    print("\\n" + "=" * 80)
    print("📊 KAZANIM ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total kazanımlar: {sum(subject_stats.values()) + len(unknown_kazanimlar)}")
    print(f"Classified: {sum(subject_stats.values())}")
    print(f"Unknown: {len(unknown_kazanimlar)}")
    
    print("\\n🏷️  Known subjects:")
    for subject, count in sorted(subject_stats.items()):
        print(f"  • {subject}: {count} kazanımlar")
    
    print("\\n🔍 Unknown kazanımlar by CODE PREFIX:")
    for prefix, kazanimlar in sorted(code_patterns.items()):
        print(f"  • {prefix}: {len(kazanimlar)} kazanımlar")
        if len(kazanimlar) <= 3:
            for k in kazanimlar:
                print(f"    - {k['code']}: {k['description'][:60]}...")
    
    print("\\n🔍 Unknown kazanımlar by TOPIC:")
    for topic, kazanimlar in sorted(topic_patterns.items()):
        print(f"  • {topic}: {len(kazanimlar)} kazanımlar")
        if len(kazanimlar) <= 3:
            for k in kazanimlar:
                print(f"    - {k['code']}: {k['description'][:60]}...")
    
    return unknown_kazanimlar, code_patterns, topic_patterns

def suggest_subjects(unknown_kazanimlar):
    """Suggest possible subjects based on content analysis."""
    
    suggestions = []
    
    for kazanim in unknown_kazanimlar:
        code = kazanim['code']
        description = kazanim['description'].lower()
        topic = kazanim['topic']
        
        suggested_subject = "Unknown"
        confidence = "Low"
        reasoning = ""
        
        # English language indicators
        if any(word in description for word in ['student', 'teacher', 'lesson', 'vocabulary', 'grammar', 'speaking', 'listening', 'reading', 'writing']):
            suggested_subject = "English"
            confidence = "High"
            reasoning = "English teaching methodology terms"
        elif any(word in description for word in ['warm-up', 'icebreaker', 'class', 'activity']):
            suggested_subject = "English"
            confidence = "Medium"
            reasoning = "Teaching activity descriptions"
        elif code and (code.startswith('D') or code.startswith('V') or code.startswith('LS') or code.startswith('CS')):
            suggested_subject = "English"
            confidence = "Medium"
            reasoning = "English curriculum code pattern"
        
        # Turkish language indicators
        elif any(word in description for word in ['türkçe', 'dil', 'metin', 'yazma', 'okuma']):
            suggested_subject = "Türkçe"
            confidence = "High"
            reasoning = "Turkish language terms"
        
        # Math indicators
        elif any(word in description for word in ['matematik', 'sayı', 'geometri', 'hesap']):
            suggested_subject = "Matematik"
            confidence = "High"
            reasoning = "Mathematical terms"
        
        suggestions.append({
            'code': code,
            'suggested_subject': suggested_subject,
            'confidence': confidence,
            'reasoning': reasoning,
            'original': kazanim
        })
    
    return suggestions

def main():
    """Main function for kazanım analysis."""
    
    if len(sys.argv) != 2:
        print("Usage: python kazanim_labeler.py <kazanim_jsonl_file>")
        sys.exit(1)
    
    jsonl_file = sys.argv[1]
    
    try:
        unknown_kazanimlar, code_patterns, topic_patterns = analyze_unknown_kazanimlar(jsonl_file)
        
        if not unknown_kazanimlar:
            print("\\n✅ No unknown kazanımlar found! All are properly classified.")
            return
        
        print("\\n" + "=" * 80)
        print("🤖 AI SUBJECT SUGGESTIONS")
        print("=" * 80)
        
        suggestions = suggest_subjects(unknown_kazanimlar)
        
        # Group suggestions by suggested subject
        by_subject = defaultdict(list)
        for suggestion in suggestions:
            by_subject[suggestion['suggested_subject']].append(suggestion)
        
        for subject, subject_suggestions in sorted(by_subject.items()):
            print(f"\\n📚 Suggested subject: {subject} ({len(subject_suggestions)} kazanımlar)")
            print("-" * 60)
            
            for suggestion in subject_suggestions[:10]:  # Show first 10 per subject
                print(f"  Code: {suggestion['code']}")
                print(f"  Confidence: {suggestion['confidence']}")
                print(f"  Reasoning: {suggestion['reasoning']}")
                print(f"  Description: {suggestion['original']['description'][:100]}...")
                print()
            
            if len(subject_suggestions) > 10:
                print(f"  ... and {len(subject_suggestions) - 10} more")
        
        print("\\n" + "=" * 80)
        print("📝 NEXT STEPS FOR MANUAL LABELING")
        print("=" * 80)
        print("1. Review the AI suggestions above")
        print("2. Most unknown kazanımlar appear to be English curriculum")
        print("3. Update the kazanım parser to better recognize English patterns")
        print("4. Or manually create a mapping file for these codes")
        
    except FileNotFoundError:
        print(f"❌ File not found: {jsonl_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()