#!/usr/bin/env python3
"""
LGS Statistical Fingerprint Model - Production Implementation
Analyzes authentic LGS questions to create statistical fingerprints for validation and conformance
"""

import json
import re
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
import pickle
from pathlib import Path
import math

@dataclass
class LGSFingerprint:
    """Complete statistical fingerprint of LGS exam characteristics"""
    sentence_length_dist: Dict[str, float]
    option_length_variance: float
    punctuation_patterns: Dict[str, float]
    distractor_patterns: Dict[str, float]
    numeric_distribution: Dict[str, float]
    subject_specific_patterns: Dict[str, Dict[str, float]]
    difficulty_indicators: Dict[str, List[str]]
    vocabulary_frequency: Dict[str, float]
    structural_patterns: Dict[str, float]

class LGSStatisticalFingerprinter:
    """Advanced fingerprinting system for LGS questions"""
    
    def __init__(self, authentic_questions: List[Dict]):
        self.authentic_questions = authentic_questions
        self.fingerprint = self._generate_comprehensive_fingerprint()
        
    def _generate_comprehensive_fingerprint(self) -> LGSFingerprint:
        """Generate complete statistical fingerprint from authentic questions"""
        
        print("🔍 Generating LGS Statistical Fingerprint...")
        print(f"📊 Analyzing {len(self.authentic_questions)} authentic questions")
        
        # Extract all stems and options
        stems = []
        all_options = []
        subject_data = defaultdict(list)
        
        for q in self.authentic_questions:
            stem = q.get('stem', '')
            if stem:
                stems.append(stem)
                subject = q.get('subject', 'unknown')
                subject_data[subject].append(stem)
            
            options = q.get('options', [])
            for opt in options:
                option_text = opt.get('text', '')
                if option_text:
                    all_options.append(option_text)
        
        # Generate each component of the fingerprint
        return LGSFingerprint(
            sentence_length_dist=self._analyze_sentence_lengths(stems),
            option_length_variance=self._analyze_option_variance(self.authentic_questions),
            punctuation_patterns=self._analyze_punctuation_patterns(stems),
            distractor_patterns=self._analyze_distractor_patterns(self.authentic_questions),
            numeric_distribution=self._analyze_numeric_patterns(stems),
            subject_specific_patterns=self._analyze_subject_patterns(subject_data),
            difficulty_indicators=self._extract_difficulty_indicators(self.authentic_questions),
            vocabulary_frequency=self._analyze_vocabulary_frequency(stems),
            structural_patterns=self._analyze_structural_patterns(stems)
        )
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile without numpy"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        index = (percentile / 100.0) * (n - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            if upper_index >= n:
                return sorted_data[lower_index]
            
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _analyze_sentence_lengths(self, stems: List[str]) -> Dict[str, float]:
        """Analyze sentence length distribution patterns"""
        
        word_counts = [len(stem.split()) for stem in stems if stem]
        sentence_counts = [len(re.split(r'[.!?]+', stem)) for stem in stems if stem]
        
        if not word_counts:
            return {}
        
        return {
            'word_count_mean': statistics.mean(word_counts),
            'word_count_median': statistics.median(word_counts),
            'word_count_std': statistics.stdev(word_counts) if len(word_counts) > 1 else 0,
            'word_count_min': min(word_counts),
            'word_count_max': max(word_counts),
            'sentence_count_mean': statistics.mean(sentence_counts),
            'sentence_count_median': statistics.median(sentence_counts),
            # Percentile analysis using basic statistics
            'word_count_p25': self._calculate_percentile(word_counts, 25),
            'word_count_p75': self._calculate_percentile(word_counts, 75),
            'word_count_p90': self._calculate_percentile(word_counts, 90)
        }
    
    def _analyze_option_variance(self, questions: List[Dict]) -> float:
        """Analyze variance in option lengths within questions"""
        
        variances = []
        
        for q in questions:
            options = q.get('options', [])
            if len(options) >= 4:
                option_lengths = [len(opt.get('text', '').split()) for opt in options]
                if len(set(option_lengths)) > 1:  # Only calculate if there's variance
                    variances.append(statistics.variance(option_lengths))
        
        return statistics.mean(variances) if variances else 0.0
    
    def _analyze_punctuation_patterns(self, stems: List[str]) -> Dict[str, float]:
        """Analyze punctuation usage patterns"""
        
        total_stems = len(stems)
        if total_stems == 0:
            return {}
        
        # Count specific punctuation patterns
        patterns = {
            'question_marks': 0,
            'exclamation_marks': 0,
            'commas_per_stem': [],
            'parentheses': 0,
            'quotation_marks': 0,
            'colons': 0,
            'semicolons': 0,
            'dashes': 0
        }
        
        for stem in stems:
            patterns['question_marks'] += stem.count('?')
            patterns['exclamation_marks'] += stem.count('!')
            patterns['commas_per_stem'].append(stem.count(','))
            patterns['parentheses'] += stem.count('(') + stem.count(')')
            patterns['quotation_marks'] += stem.count('"') + stem.count('"') + stem.count('"')
            patterns['colons'] += stem.count(':')
            patterns['semicolons'] += stem.count(';')
            patterns['dashes'] += stem.count('—') + stem.count('-')
        
        # Calculate frequencies
        return {
            'question_mark_frequency': patterns['question_marks'] / total_stems,
            'exclamation_frequency': patterns['exclamation_marks'] / total_stems,
            'comma_frequency': statistics.mean(patterns['commas_per_stem']),
            'parentheses_frequency': patterns['parentheses'] / total_stems,
            'quotation_frequency': patterns['quotation_marks'] / total_stems,
            'colon_frequency': patterns['colons'] / total_stems,
            'semicolon_frequency': patterns['semicolons'] / total_stems,
            'dash_frequency': patterns['dashes'] / total_stems
        }
    
    def _analyze_distractor_patterns(self, questions: List[Dict]) -> Dict[str, float]:
        """Analyze patterns in distractor options"""
        
        distractor_patterns = {
            'length_similarity': [],  # How similar distractor lengths are
            'first_word_patterns': Counter(),
            'ending_patterns': Counter(),
            'numeric_distractors': 0,
            'total_distractors': 0
        }
        
        for q in questions:
            options = q.get('options', [])
            if len(options) >= 4:
                
                # Find distractors (incorrect options)
                distractors = [opt for opt in options if not opt.get('is_correct', False)]
                
                if len(distractors) >= 3:
                    # Analyze length similarity among distractors
                    distractor_lengths = [len(opt.get('text', '').split()) for opt in distractors]
                    if len(distractor_lengths) > 1:
                        length_variance = statistics.variance(distractor_lengths)
                        distractor_patterns['length_similarity'].append(length_variance)
                    
                    # Analyze first words
                    for distractor in distractors:
                        text = distractor.get('text', '').strip()
                        if text:
                            first_word = text.split()[0].lower() if text.split() else ''
                            distractor_patterns['first_word_patterns'][first_word] += 1
                            
                            # Check for numeric content
                            if re.search(r'\d', text):
                                distractor_patterns['numeric_distractors'] += 1
                            
                            distractor_patterns['total_distractors'] += 1
        
        # Calculate metrics
        result = {}
        if distractor_patterns['length_similarity']:
            result['avg_length_variance'] = statistics.mean(distractor_patterns['length_similarity'])
        
        if distractor_patterns['total_distractors'] > 0:
            result['numeric_distractor_rate'] = distractor_patterns['numeric_distractors'] / distractor_patterns['total_distractors']
        
        # Top first word patterns
        top_first_words = distractor_patterns['first_word_patterns'].most_common(5)
        for word, count in top_first_words:
            result[f'first_word_{word}_freq'] = count / distractor_patterns['total_distractors']
        
        return result
    
    def _analyze_numeric_patterns(self, stems: List[str]) -> Dict[str, float]:
        """Analyze usage of numbers and mathematical content"""
        
        total_stems = len(stems)
        if total_stems == 0:
            return {}
        
        numeric_patterns = {
            'contains_numbers': 0,
            'contains_fractions': 0,
            'contains_percentages': 0,
            'contains_equations': 0,
            'number_ranges': []
        }
        
        for stem in stems:
            # Check for numbers
            if re.search(r'\d', stem):
                numeric_patterns['contains_numbers'] += 1
                
                # Extract all numbers
                numbers = re.findall(r'\d+', stem)
                for num_str in numbers:
                    numeric_patterns['number_ranges'].append(int(num_str))
            
            # Check for fractions
            if re.search(r'\d+/\d+', stem):
                numeric_patterns['contains_fractions'] += 1
            
            # Check for percentages
            if '%' in stem:
                numeric_patterns['contains_percentages'] += 1
            
            # Check for equations
            if re.search(r'[=+\-×÷]', stem):
                numeric_patterns['contains_equations'] += 1
        
        result = {
            'number_frequency': numeric_patterns['contains_numbers'] / total_stems,
            'fraction_frequency': numeric_patterns['contains_fractions'] / total_stems,
            'percentage_frequency': numeric_patterns['contains_percentages'] / total_stems,
            'equation_frequency': numeric_patterns['contains_equations'] / total_stems
        }
        
        # Analyze number ranges if we have any
        if numeric_patterns['number_ranges']:
            numbers = numeric_patterns['number_ranges']
            result.update({
                'number_range_mean': statistics.mean(numbers),
                'number_range_median': statistics.median(numbers),
                'number_range_max': max(numbers),
                'small_numbers_rate': sum(1 for n in numbers if n <= 10) / len(numbers)
            })
        
        return result
    
    def _analyze_subject_patterns(self, subject_data: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
        """Analyze subject-specific linguistic patterns"""
        
        subject_patterns = {}
        
        for subject, stems in subject_data.items():
            if len(stems) < 3:  # Skip subjects with too few samples
                continue
            
            # Subject-specific vocabulary
            all_words = []
            for stem in stems:
                words = re.findall(r'\b\w+\b', stem.lower())
                all_words.extend(words)
            
            word_freq = Counter(all_words)
            total_words = len(all_words)
            
            # Calculate subject-specific metrics
            patterns = {
                'avg_stem_length': statistics.mean([len(stem.split()) for stem in stems]),
                'unique_vocabulary_rate': len(set(all_words)) / total_words if total_words > 0 else 0,
                'technical_term_density': self._calculate_technical_density(stems, subject)
            }
            
            # Top vocabulary for this subject
            top_words = word_freq.most_common(5)
            for word, count in top_words:
                patterns[f'top_word_{word}'] = count / total_words
            
            subject_patterns[subject] = patterns
        
        return subject_patterns
    
    def _calculate_technical_density(self, stems: List[str], subject: str) -> float:
        """Calculate density of technical/subject-specific terms"""
        
        # Subject-specific technical term patterns
        technical_patterns = {
            'Matematik': [r'\b(fonksiyon|denklem|köklü|üslü|logaritma|integral)\b'],
            'Türkçe': [r'\b(metafor|benzetme|kişileştirme|anlam|sözcük)\b'],
            'Fen Bilimleri': [r'\b(molekül|atom|enerji|kuvvet|hız)\b'],
            'Sosyal Bilgiler': [r'\b(tarih|coğrafya|nüfus|iklim|kültür)\b']
        }
        
        patterns = technical_patterns.get(subject, [])
        if not patterns:
            return 0.0
        
        total_terms = 0
        total_words = 0
        
        for stem in stems:
            words = stem.split()
            total_words += len(words)
            
            for pattern in patterns:
                total_terms += len(re.findall(pattern, stem.lower()))
        
        return total_terms / total_words if total_words > 0 else 0.0
    
    def _extract_difficulty_indicators(self, questions: List[Dict]) -> Dict[str, List[str]]:
        """Extract linguistic patterns that indicate difficulty levels"""
        
        difficulty_indicators = {
            'KOLAY': [],
            'ORTA': [],
            'ZOR': []
        }
        
        for q in questions:
            difficulty = q.get('difficulty_level', 'ORTA')
            stem = q.get('stem', '')
            
            # Extract key phrases that might indicate difficulty
            phrases = self._extract_key_phrases(stem)
            difficulty_indicators[difficulty].extend(phrases)
        
        # Get most common phrases for each difficulty
        for difficulty in difficulty_indicators:
            phrase_counts = Counter(difficulty_indicators[difficulty])
            difficulty_indicators[difficulty] = [
                phrase for phrase, count in phrase_counts.most_common(10)
            ]
        
        return difficulty_indicators
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple extraction of 2-3 word phrases
        words = re.findall(r'\b\w+\b', text.lower())
        phrases = []
        
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
            if i < len(words) - 2:
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return phrases
    
    def _analyze_vocabulary_frequency(self, stems: List[str]) -> Dict[str, float]:
        """Analyze overall vocabulary frequency patterns"""
        
        all_words = []
        for stem in stems:
            words = re.findall(r'\b\w+\b', stem.lower())
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        total_words = len(all_words)
        
        if total_words == 0:
            return {}
        
        # Calculate frequency metrics
        result = {
            'vocabulary_size': len(set(all_words)),
            'avg_word_frequency': total_words / len(set(all_words)) if all_words else 0,
            'hapax_legomena_rate': sum(1 for count in word_freq.values() if count == 1) / len(word_freq)
        }
        
        # Top 10 most frequent words
        top_words = word_freq.most_common(10)
        for i, (word, count) in enumerate(top_words):
            result[f'top_{i+1}_word'] = word
            result[f'top_{i+1}_freq'] = count / total_words
        
        return result
    
    def _analyze_structural_patterns(self, stems: List[str]) -> Dict[str, float]:
        """Analyze structural patterns in question formation"""
        
        total_stems = len(stems)
        if total_stems == 0:
            return {}
        
        patterns = {
            'starts_with_question': 0,
            'contains_conditional': 0,
            'contains_comparison': 0,
            'contains_enumeration': 0,
            'multiple_sentences': 0
        }
        
        for stem in stems:
            # Check structural patterns
            if re.match(r'^(Ne|Nasıl|Hangi|Kim|Nerede|Neden)', stem):
                patterns['starts_with_question'] += 1
            
            if re.search(r'\b(eğer|ise|olsaydı|durumunda)\b', stem.lower()):
                patterns['contains_conditional'] += 1
            
            if re.search(r'\b(daha|en|göre|karşı|benzer)\b', stem.lower()):
                patterns['contains_comparison'] += 1
            
            if re.search(r'\b(birinci|ikinci|üçüncü|I\.|II\.|III\.)\b', stem):
                patterns['contains_enumeration'] += 1
            
            if len(re.split(r'[.!?]+', stem)) > 2:
                patterns['multiple_sentences'] += 1
        
        return {
            'question_start_rate': patterns['starts_with_question'] / total_stems,
            'conditional_rate': patterns['contains_conditional'] / total_stems,
            'comparison_rate': patterns['contains_comparison'] / total_stems,
            'enumeration_rate': patterns['contains_enumeration'] / total_stems,
            'multi_sentence_rate': patterns['multiple_sentences'] / total_stems
        }
    
    def calculate_conformance_score(self, question: Dict) -> float:
        """Calculate how well a question conforms to LGS fingerprint"""
        
        stem = question.get('stem', '')
        options = question.get('options', [])
        
        conformance_scores = []
        
        # Check sentence length conformance
        word_count = len(stem.split())
        expected_mean = self.fingerprint.sentence_length_dist.get('word_count_mean', 25)
        expected_std = self.fingerprint.sentence_length_dist.get('word_count_std', 10)
        
        # Calculate z-score for word count
        if expected_std > 0:
            z_score = abs(word_count - expected_mean) / expected_std
            length_conformance = max(0, 1 - (z_score / 3))  # 3-sigma rule
        else:
            length_conformance = 1.0
        
        conformance_scores.append(length_conformance)
        
        # Check punctuation conformance
        punct_score = self._check_punctuation_conformance(stem)
        conformance_scores.append(punct_score)
        
        # Check option length variance conformance
        if len(options) >= 4:
            option_lengths = [len(opt.get('text', '').split()) for opt in options]
            actual_variance = statistics.variance(option_lengths) if len(set(option_lengths)) > 1 else 0
            expected_variance = self.fingerprint.option_length_variance
            
            # Variance conformance (closer to expected = higher score)
            if expected_variance > 0:
                variance_ratio = min(actual_variance, expected_variance) / max(actual_variance, expected_variance)
            else:
                variance_ratio = 1.0 if actual_variance == 0 else 0.5
            
            conformance_scores.append(variance_ratio)
        
        # Check subject-specific conformance if available
        subject = question.get('subject', '')
        if subject in self.fingerprint.subject_specific_patterns:
            subject_patterns = self.fingerprint.subject_specific_patterns[subject]
            expected_length = subject_patterns.get('avg_stem_length', 25)
            
            length_diff = abs(word_count - expected_length) / expected_length
            subject_conformance = max(0, 1 - length_diff)
            conformance_scores.append(subject_conformance)
        
        # Return weighted average
        return statistics.mean(conformance_scores)
    
    def _check_punctuation_conformance(self, stem: str) -> float:
        """Check how well punctuation matches LGS patterns"""
        
        expected_patterns = self.fingerprint.punctuation_patterns
        
        actual_patterns = {
            'comma_frequency': stem.count(','),
            'question_mark_frequency': stem.count('?'),
            'parentheses_frequency': stem.count('(') + stem.count(')'),
            'quotation_frequency': stem.count('"')
        }
        
        scores = []
        
        for pattern_name, expected_freq in expected_patterns.items():
            if pattern_name in actual_patterns:
                actual_freq = actual_patterns[pattern_name]
                
                # Calculate conformance (closer to expected = higher score)
                if expected_freq == 0 and actual_freq == 0:
                    scores.append(1.0)
                elif expected_freq == 0:
                    scores.append(0.5)  # Penalty for unexpected punctuation
                else:
                    conformance = 1 - min(1, abs(actual_freq - expected_freq) / expected_freq)
                    scores.append(conformance)
        
        return statistics.mean(scores) if scores else 0.5
    
    def save_fingerprint(self, filepath: str):
        """Save fingerprint to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.fingerprint, f)
        print(f"📁 Fingerprint saved to {filepath}")
    
    @classmethod
    def load_fingerprint(cls, filepath: str) -> 'LGSStatisticalFingerprinter':
        """Load fingerprint from file"""
        with open(filepath, 'rb') as f:
            fingerprint = pickle.load(f)
        
        # Create instance with empty questions (fingerprint already computed)
        instance = cls([])
        instance.fingerprint = fingerprint
        return instance
    
    def generate_report(self) -> str:
        """Generate comprehensive fingerprint report"""
        
        report = []
        report.append("🎯 LGS STATISTICAL FINGERPRINT REPORT")
        report.append("=" * 50)
        
        # Sentence length analysis
        length_stats = self.fingerprint.sentence_length_dist
        report.append(f"\n📏 Sentence Length Distribution:")
        report.append(f"   Mean word count: {length_stats.get('word_count_mean', 0):.1f}")
        report.append(f"   Median word count: {length_stats.get('word_count_median', 0):.1f}")
        report.append(f"   Standard deviation: {length_stats.get('word_count_std', 0):.1f}")
        report.append(f"   Range: {length_stats.get('word_count_min', 0)}-{length_stats.get('word_count_max', 0)} words")
        
        # Option variance
        report.append(f"\n📊 Option Length Variance: {self.fingerprint.option_length_variance:.2f}")
        
        # Punctuation patterns
        punct_patterns = self.fingerprint.punctuation_patterns
        report.append(f"\n🔤 Punctuation Patterns:")
        for pattern, freq in punct_patterns.items():
            report.append(f"   {pattern}: {freq:.3f}")
        
        # Subject patterns
        if self.fingerprint.subject_specific_patterns:
            report.append(f"\n📚 Subject-Specific Patterns:")
            for subject, patterns in self.fingerprint.subject_specific_patterns.items():
                report.append(f"   {subject}:")
                for pattern, value in patterns.items():
                    if isinstance(value, float):
                        report.append(f"      {pattern}: {value:.3f}")
        
        # Vocabulary stats
        vocab_stats = self.fingerprint.vocabulary_frequency
        if vocab_stats:
            report.append(f"\n📖 Vocabulary Analysis:")
            report.append(f"   Total vocabulary size: {vocab_stats.get('vocabulary_size', 0)}")
            report.append(f"   Average word frequency: {vocab_stats.get('avg_word_frequency', 0):.2f}")
            report.append(f"   Hapax legomena rate: {vocab_stats.get('hapax_legomena_rate', 0):.3f}")
        
        return "\n".join(report)

def main():
    """Demo function to generate fingerprint from comprehensive LGS data"""
    
    # Load authentic questions
    questions = []
    jsonl_path = Path('/app/comprehensive_lgs_2018_2025.jsonl')
    
    if jsonl_path.exists():
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line.strip()))
    else:
        print("❌ No authentic questions found, using empty dataset")
    
    # Generate fingerprint
    fingerprinter = LGSStatisticalFingerprinter(questions)
    
    # Generate and print report
    report = fingerprinter.generate_report()
    print(report)
    
    # Save fingerprint
    fingerprinter.save_fingerprint('/app/lgs_fingerprint.pkl')
    
    # Test conformance on a sample question
    if questions:
        sample_question = questions[0]
        conformance_score = fingerprinter.calculate_conformance_score(sample_question)
        print(f"\n🎯 Sample conformance score: {conformance_score:.3f}")

if __name__ == "__main__":
    main()