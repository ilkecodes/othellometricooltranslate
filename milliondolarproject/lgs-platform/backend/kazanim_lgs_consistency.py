#!/usr/bin/env python3
"""
Kazanım-LGS Consistency Analysis
Maps curriculum learning outcomes against historical LGS exam question distribution patterns
"""

import json
import sys
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from pathlib import Path

def load_kazanimlar(kazanim_file: str) -> List[Dict[str, Any]]:
    """Load kazanımlar from JSONL file"""
    kazanimlar = []
    
    with open(kazanim_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            kazanimlar.append(data)
    
    return kazanimlar

def load_lgs_distribution(lgs_file: str) -> Dict[str, Any]:
    """Load LGS distribution analysis"""
    with open(lgs_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def map_subjects(kazanim_subject: str, lgs_subject: str) -> bool:
    """Check if kazanım subject maps to LGS subject"""
    
    # Subject mapping rules
    subject_mappings = {
        'Türkçe': ['Türkçe'],
        'Matematik': ['Matematik'],
        'Fen Bilimleri': ['Fen Bilimleri'],
        'Din Kültürü ve Ahlak Bilgisi': ['Din Kültürü ve Ahlak Bilgisi'],
        'İnkılap Tarihi ve Atatürkçülük': ['İnkılap Tarihi'],
        'English': ['İngilizce'],
        'İngilizce': ['İngilizce'],
        'Tarih': ['İnkılap Tarihi'],  # Some history topics may appear in İnkılap Tarihi
    }
    
    mapped_subjects = subject_mappings.get(kazanim_subject, [])
    return lgs_subject in mapped_subjects

def calculate_topic_frequency(topic_data: Dict[str, Any]) -> Tuple[float, int, int]:
    """Calculate frequency statistics for a topic"""
    years_data = topic_data.get('years_data', {})
    
    if not years_data:
        return 0.0, 0, 0
    
    total_questions = 0
    total_percentage = 0.0
    years_count = len(years_data)
    
    for year, stats in years_data.items():
        questions = stats.get('questions', 0)
        percentage = stats.get('percentage', 0.0)
        
        if isinstance(questions, (int, float)):
            total_questions += questions
        if isinstance(percentage, (int, float)):
            total_percentage += percentage
    
    avg_questions_per_year = total_questions / years_count if years_count > 0 else 0
    avg_percentage = total_percentage / years_count if years_count > 0 else 0
    
    return avg_percentage, int(total_questions), years_count

def analyze_kazanim_lgs_consistency(kazanimlar: List[Dict], lgs_data: Dict) -> Dict[str, Any]:
    """Analyze consistency between kazanımlar and LGS distribution"""
    
    analysis = {
        'total_kazanimlar': len(kazanimlar),
        'subjects_analysis': {},
        'coverage_summary': {
            'covered_kazanimlar': 0,
            'uncovered_kazanimlar': 0,
            'high_frequency_topics': [],
            'low_frequency_topics': [],
            'missing_topics': []
        }
    }
    
    # Group kazanımlar by subject
    kazanim_by_subject = defaultdict(list)
    for kazanim in kazanimlar:
        subject = kazanim.get('subject', 'Unknown')
        kazanim_by_subject[subject].append(kazanim)
    
    lgs_subjects = lgs_data.get('subjects', {})
    
    # Analyze each subject
    for kazanim_subject, kazanim_list in kazanim_by_subject.items():
        subject_analysis = {
            'kazanim_count': len(kazanim_list),
            'lgs_mapped': False,
            'lgs_subject': None,
            'topic_coverage': {},
            'frequency_analysis': {
                'high_frequency': [],  # >15% average
                'medium_frequency': [],  # 5-15% average
                'low_frequency': [],   # <5% average
                'unmapped': []
            }
        }
        
        # Find matching LGS subject
        for lgs_subject in lgs_subjects.keys():
            if map_subjects(kazanim_subject, lgs_subject):
                subject_analysis['lgs_mapped'] = True
                subject_analysis['lgs_subject'] = lgs_subject
                
                # Analyze topic coverage
                lgs_topics = lgs_subjects[lgs_subject]['topics']
                
                for topic in lgs_topics:
                    topic_name = topic['name']
                    avg_percentage, total_questions, years_count = calculate_topic_frequency(topic)
                    
                    topic_info = {
                        'name': topic_name,
                        'avg_percentage': round(avg_percentage, 1),
                        'total_questions': total_questions,
                        'years_covered': years_count,
                        'kazanim_codes': topic.get('kazanim_codes', [])
                    }
                    
                    subject_analysis['topic_coverage'][topic_name] = topic_info
                    
                    # Categorize by frequency
                    if avg_percentage >= 15:
                        subject_analysis['frequency_analysis']['high_frequency'].append(topic_info)
                        analysis['coverage_summary']['high_frequency_topics'].append({
                            'subject': lgs_subject,
                            **topic_info
                        })
                    elif avg_percentage >= 5:
                        subject_analysis['frequency_analysis']['medium_frequency'].append(topic_info)
                    else:
                        subject_analysis['frequency_analysis']['low_frequency'].append(topic_info)
                        analysis['coverage_summary']['low_frequency_topics'].append({
                            'subject': lgs_subject,
                            **topic_info
                        })
                
                break
        
        if not subject_analysis['lgs_mapped']:
            # Count unmapped kazanımlar
            for kazanim in kazanim_list:
                subject_analysis['frequency_analysis']['unmapped'].append({
                    'code': kazanim.get('code', 'Unknown'),
                    'description': kazanim.get('description', 'No description')[:100] + '...'
                })
            analysis['coverage_summary']['uncovered_kazanimlar'] += len(kazanim_list)
        else:
            analysis['coverage_summary']['covered_kazanimlar'] += len(kazanim_list)
        
        analysis['subjects_analysis'][kazanim_subject] = subject_analysis
    
    # Calculate coverage percentages
    total = analysis['total_kazanimlar']
    if total > 0:
        analysis['coverage_summary']['coverage_percentage'] = round(
            (analysis['coverage_summary']['covered_kazanimlar'] / total) * 100, 1
        )
    
    return analysis

def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on consistency analysis"""
    recommendations = []
    
    coverage_pct = analysis['coverage_summary'].get('coverage_percentage', 0)
    
    if coverage_pct < 70:
        recommendations.append(
            f"⚠️ Low curriculum-exam alignment ({coverage_pct}%). Consider reviewing subject mappings."
        )
    
    high_freq_topics = analysis['coverage_summary']['high_frequency_topics']
    if high_freq_topics:
        recommendations.append(
            f"🎯 Focus on high-frequency topics: {len(high_freq_topics)} topics appear ≥15% on exams."
        )
        
        # List top 3 high frequency topics
        sorted_topics = sorted(high_freq_topics, key=lambda x: x['avg_percentage'], reverse=True)
        top_topics = sorted_topics[:3]
        for topic in top_topics:
            recommendations.append(
                f"   • {topic['subject']}: {topic['name']} ({topic['avg_percentage']}% avg)"
            )
    
    low_freq_topics = analysis['coverage_summary']['low_frequency_topics']
    if len(low_freq_topics) > 10:
        recommendations.append(
            f"📉 {len(low_freq_topics)} topics have low exam frequency (<5%). Review curriculum emphasis."
        )
    
    # Subject-specific recommendations
    for subject, data in analysis['subjects_analysis'].items():
        if not data['lgs_mapped']:
            recommendations.append(f"❓ {subject}: No LGS mapping found - may need subject alignment review")
        else:
            high_freq = len(data['frequency_analysis']['high_frequency'])
            if high_freq == 0:
                recommendations.append(f"📚 {subject}: No high-frequency topics - focus on medium-frequency areas")
    
    return recommendations

def main():
    if len(sys.argv) != 4:
        print("Usage: python kazanim_lgs_consistency.py <kazanim_jsonl> <lgs_distribution_json> <output_json>")
        sys.exit(1)
    
    kazanim_file = sys.argv[1]
    lgs_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("🔍 KAZANIM-LGS CONSISTENCY ANALYSIS")
    print("=" * 50)
    
    # Load data
    print("\n1️⃣ Loading data...")
    try:
        kazanimlar = load_kazanimlar(kazanim_file)
        print(f"✓ Loaded {len(kazanimlar)} kazanımlar")
        
        lgs_data = load_lgs_distribution(lgs_file)
        subjects_count = len(lgs_data.get('subjects', {}))
        print(f"✓ Loaded LGS data for {subjects_count} subjects")
        
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)
    
    # Perform analysis
    print("\n2️⃣ Analyzing consistency...")
    analysis = analyze_kazanim_lgs_consistency(kazanimlar, lgs_data)
    
    # Generate recommendations
    print("\n3️⃣ Generating recommendations...")
    recommendations = generate_recommendations(analysis)
    analysis['recommendations'] = recommendations
    
    # Save results
    print("\n4️⃣ Saving analysis...")
    analysis['metadata'] = {
        'kazanim_file': kazanim_file,
        'lgs_file': lgs_file,
        'analysis_date': '2024-11-14'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 CONSISTENCY ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total kazanımlar analyzed: {analysis['total_kazanimlar']}")
    print(f"Coverage percentage: {analysis['coverage_summary'].get('coverage_percentage', 0)}%")
    print(f"Covered kazanımlar: {analysis['coverage_summary']['covered_kazanimlar']}")
    print(f"Uncovered kazanımlar: {analysis['coverage_summary']['uncovered_kazanimlar']}")
    
    print(f"\n🎯 High-frequency topics (≥15%): {len(analysis['coverage_summary']['high_frequency_topics'])}")
    print(f"📉 Low-frequency topics (<5%): {len(analysis['coverage_summary']['low_frequency_topics'])}")
    
    print(f"\n📋 Recommendations:")
    for rec in recommendations[:5]:  # Show top 5 recommendations
        print(f"   {rec}")
    
    print(f"\nOutput saved to: {output_file}")
    print("\n✅ Consistency analysis completed!")

if __name__ == "__main__":
    main()