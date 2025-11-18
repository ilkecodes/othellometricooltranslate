#!/usr/bin/env python3
"""
Enhanced Question Generation Engine - Production Ready
Real-time, stateless, self-validating question generation with LGS fingerprinting
"""

import json
import re
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import statistics
from anthropic import Anthropic
import os
from pathlib import Path

class DifficultyLevel(str, Enum):
    EASY = "KOLAY"
    MEDIUM = "ORTA"
    HARD = "ZOR"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

@dataclass
class GenerationRequest:
    """Structured generation request"""
    subject: str
    topic: str
    learning_outcome: str
    difficulty: DifficultyLevel
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    user_id: Optional[str] = None
    style_preference: Optional[str] = "lgs_standard"

@dataclass
class ValidationResult:
    """Validation result with detailed feedback"""
    is_valid: bool
    confidence_score: float
    validation_errors: List[str]
    quality_metrics: Dict[str, float]
    similarity_score: float

class StyleConditioner:
    """Extract and apply LGS linguistic fingerprints"""
    
    def __init__(self, authentic_questions: List[Dict]):
        self.fingerprints = self._extract_style_fingerprints(authentic_questions)
        
    def _extract_style_fingerprints(self, questions: List[Dict]) -> Dict[str, Any]:
        """Extract statistical fingerprint from authentic LGS questions"""
        patterns = {
            'common_phrases': [],
            'sentence_patterns': [],
            'punctuation_style': {},
            'option_cadence': {},
            'stem_length_stats': {},
            'vocab_frequency': {}
        }
        
        # Extract common phrases and patterns
        stems = [q.get('stem', '') for q in questions]
        
        # Common LGS phrases
        lgs_phrases = [
            'Buna göre', 'Aşağıdakilerden hangisi', 'Bu durumda',
            'Metne göre', 'Yukarıdaki bilgilere göre', 'Bu bilgilere göre'
        ]
        
        for phrase in lgs_phrases:
            count = sum(1 for stem in stems if phrase in stem)
            if count > 0:
                patterns['common_phrases'].append({
                    'phrase': phrase,
                    'frequency': count / len(stems),
                    'usage_rate': count
                })
        
        # Sentence length statistics
        stem_lengths = [len(stem.split()) for stem in stems if stem]
        if stem_lengths:
            patterns['stem_length_stats'] = {
                'mean': statistics.mean(stem_lengths),
                'median': statistics.median(stem_lengths),
                'std_dev': statistics.stdev(stem_lengths) if len(stem_lengths) > 1 else 0,
                'min': min(stem_lengths),
                'max': max(stem_lengths)
            }
        
        return patterns
    
    def condition_prompt(self, base_prompt: str, subject: str) -> str:
        """Add style conditioning to generation prompt"""
        style_instructions = f"""
STYLE GUIDELINES - Follow LGS Exam Style:
- Use formal Turkish academic language
- Include common LGS phrases: {', '.join([p['phrase'] for p in self.fingerprints['common_phrases'][:3]])}
- Target stem length: {self.fingerprints['stem_length_stats'].get('mean', 25):.0f} words
- Use clear, unambiguous language
- Follow standard LGS question format
- Ensure options are similar in length and structure
"""
        return base_prompt + "\n" + style_instructions

class QuestionValidator:
    """Multi-stage validation system with four independent validators"""
    
    def __init__(self, authentic_questions: List[Dict]):
        self.authentic_questions = authentic_questions
        self.similarity_threshold = 0.35
    
    async def validate_question(self, question: Dict) -> ValidationResult:
        """Run all validation stages"""
        errors = []
        metrics = {}
        
        # Stage 1: Technical validation
        tech_valid, tech_errors = self._validate_technical(question)
        errors.extend(tech_errors)
        
        # Stage 2: Ambiguity validation  
        ambig_score, ambig_errors = self._validate_ambiguity(question)
        errors.extend(ambig_errors)
        metrics['ambiguity_score'] = ambig_score
        
        # Stage 3: Similarity validation
        similarity_score = self._validate_similarity(question)
        if similarity_score > self.similarity_threshold:
            errors.append(f"Too similar to existing question (score: {similarity_score:.3f})")
        metrics['similarity_score'] = similarity_score
        
        # Stage 4: Difficulty validation
        diff_score, diff_errors = self._validate_difficulty(question)
        errors.extend(diff_errors)
        metrics['difficulty_score'] = diff_score
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(metrics, len(errors))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            confidence_score=confidence,
            validation_errors=errors,
            quality_metrics=metrics,
            similarity_score=similarity_score
        )
    
    def _validate_technical(self, question: Dict) -> Tuple[bool, List[str]]:
        """Validate technical correctness"""
        errors = []
        
        # Check required fields
        required_fields = ['stem', 'options', 'correct_answer', 'explanation']
        for field in required_fields:
            if not question.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate options
        options = question.get('options', [])
        if len(options) != 4:
            errors.append(f"Must have exactly 4 options, found {len(options)}")
        
        # Check exactly one correct answer
        correct_count = sum(1 for opt in options if opt.get('is_correct', False))
        if correct_count != 1:
            errors.append(f"Must have exactly 1 correct option, found {correct_count}")
        
        return len(errors) == 0, errors
    
    def _validate_ambiguity(self, question: Dict) -> Tuple[float, List[str]]:
        """Detect ambiguity in question and options"""
        errors = []
        ambiguity_score = 0.0
        
        stem = question.get('stem', '')
        
        # Check for ambiguous phrases
        ambiguous_phrases = [
            'bazen', 'genellikle', 'çoğunlukla', 'belki', 
            'muhtemelen', 'sanırım', 'büyük ihtimalle'
        ]
        
        for phrase in ambiguous_phrases:
            if phrase in stem.lower():
                ambiguity_score += 0.2
                errors.append(f"Potentially ambiguous phrase: '{phrase}'")
        
        # Check option clarity
        options = question.get('options', [])
        option_texts = [opt.get('text', '') for opt in options]
        
        # Check for overlapping meanings
        for i, opt1 in enumerate(option_texts):
            for j, opt2 in enumerate(option_texts[i+1:], i+1):
                if self._calculate_text_similarity(opt1, opt2) > 0.7:
                    ambiguity_score += 0.3
                    errors.append(f"Options {i+1} and {j+1} are too similar")
        
        return ambiguity_score, errors
    
    def _validate_similarity(self, question: Dict) -> float:
        """Check similarity to existing questions"""
        stem = question.get('stem', '')
        max_similarity = 0.0
        
        for existing in self.authentic_questions:
            existing_stem = existing.get('stem', '')
            if existing_stem:
                similarity = self._calculate_text_similarity(stem, existing_stem)
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _validate_difficulty(self, question: Dict) -> Tuple[float, List[str]]:
        """Validate difficulty appropriateness"""
        errors = []
        
        target_difficulty = question.get('difficulty_level', 'ORTA')
        stem = question.get('stem', '')
        
        # Simple heuristics for difficulty
        word_count = len(stem.split())
        complexity_score = 0.0
        
        # Length-based complexity
        if word_count < 15:
            complexity_score = 0.3  # Easy
        elif word_count < 30:
            complexity_score = 0.6  # Medium  
        else:
            complexity_score = 0.9  # Hard
        
        # Check alignment
        if target_difficulty == 'KOLAY' and complexity_score > 0.7:
            errors.append("Question seems too complex for EASY difficulty")
        elif target_difficulty == 'ZOR' and complexity_score < 0.4:
            errors.append("Question seems too simple for HARD difficulty")
        
        return complexity_score, errors
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_confidence(self, metrics: Dict, error_count: int) -> float:
        """Calculate overall confidence score"""
        base_confidence = 1.0 - (error_count * 0.2)  # -20% per error
        
        # Adjust for quality metrics
        ambiguity_penalty = metrics.get('ambiguity_score', 0) * 0.1
        similarity_penalty = max(0, metrics.get('similarity_score', 0) - 0.2) * 0.3
        
        confidence = base_confidence - ambiguity_penalty - similarity_penalty
        return max(0.0, min(1.0, confidence))

class MutationEngine:
    """Self-correcting mutation system"""
    
    def __init__(self, client: Anthropic):
        self.client = client
    
    async def mutate_for_difficulty(self, question: Dict, target_difficulty: str) -> Dict:
        """Mutate question to match target difficulty"""
        
        prompt = f"""
MUTATION TASK: Adjust question difficulty to {target_difficulty}

Original Question:
{question.get('stem', '')}

Current Options:
{json.dumps(question.get('options', []), ensure_ascii=False, indent=2)}

INSTRUCTIONS:
- Keep the core learning outcome the same
- Adjust complexity to match {target_difficulty} level:
  - KOLAY: Simple, direct, basic concepts
  - ORTA: Moderate complexity, some analysis required  
  - ZOR: Complex reasoning, multi-step solutions
- Maintain LGS style and format
- Ensure exactly 4 options with 1 correct answer

Return JSON:
{{
  "stem": "Adjusted question text",
  "options": [
    {{"key": "A", "text": "Option A", "is_correct": false}},
    {{"key": "B", "text": "Option B", "is_correct": true}},
    {{"key": "C", "text": "Option C", "is_correct": false}},
    {{"key": "D", "text": "Option D", "is_correct": false}}
  ],
  "explanation": "Updated explanation",
  "difficulty_level": "{target_difficulty}"
}}
"""
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=800,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            return self._extract_json_from_response(response_text)
            
        except Exception as e:
            print(f"Mutation failed: {e}")
            return question  # Return original if mutation fails
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            # Find JSON block
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
        
        return {}

class EnhancedQuestionGenerator:
    """Production-ready question generator with full validation pipeline"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.authentic_questions = self._load_authentic_questions()
        self.style_conditioner = StyleConditioner(self.authentic_questions)
        self.validator = QuestionValidator(self.authentic_questions)
        self.mutator = MutationEngine(self.client)
        self.generation_cache = {}
        
    def _load_authentic_questions(self) -> List[Dict]:
        """Load authentic LGS questions for fingerprinting"""
        try:
            questions = []
            jsonl_path = Path('/app/comprehensive_lgs_2018_2025.jsonl')
            if jsonl_path.exists():
                with open(jsonl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            questions.append(json.loads(line.strip()))
            return questions[:100]  # Use subset for performance
        except Exception as e:
            print(f"Warning: Could not load authentic questions: {e}")
            return []
    
    async def generate_question(self, request: GenerationRequest) -> Dict:
        """Main generation method with full validation pipeline"""
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        if cache_key in self.generation_cache:
            return self.generation_cache[cache_key]
        
        max_iterations = 3
        best_question = None
        best_confidence = 0.0
        
        for iteration in range(max_iterations):
            print(f"Generation attempt {iteration + 1}/{max_iterations}")
            
            # Generate question
            question = await self._generate_base_question(request)
            if not question:
                continue
            
            # Validate
            validation = await self.validator.validate_question(question)
            
            if validation.is_valid:
                # Cache successful generation
                self.generation_cache[cache_key] = question
                return question
            
            # Track best attempt
            if validation.confidence_score > best_confidence:
                best_question = question
                best_confidence = validation.confidence_score
            
            # Try mutation if validation failed
            if iteration < max_iterations - 1:
                print(f"Validation failed, attempting mutation...")
                print(f"Errors: {validation.validation_errors}")
                
                # Mutate for most critical error
                if any("difficulty" in error.lower() for error in validation.validation_errors):
                    question = await self.mutator.mutate_for_difficulty(
                        question, request.difficulty.value
                    )
        
        # Return best attempt if all iterations failed
        print(f"Warning: All validation attempts failed, returning best attempt (confidence: {best_confidence:.3f})")
        return best_question or {'error': 'Generation failed'}
    
    async def _generate_base_question(self, request: GenerationRequest) -> Dict:
        """Generate base question with style conditioning"""
        
        base_prompt = f"""
Generate a high-quality {request.question_type.value} question for LGS exam.

REQUIREMENTS:
- Subject: {request.subject}
- Topic: {request.topic}  
- Learning Outcome: {request.learning_outcome}
- Difficulty: {request.difficulty.value}
- Must follow official LGS format and standards
- Exactly 4 multiple choice options (A, B, C, D)
- Exactly 1 correct answer
- Clear, unambiguous question stem
- Realistic, plausible distractors

Return valid JSON only:
{{
  "stem": "Question text here",
  "options": [
    {{"key": "A", "text": "Option A text", "is_correct": false}},
    {{"key": "B", "text": "Option B text", "is_correct": true}},
    {{"key": "C", "text": "Option C text", "is_correct": false}},
    {{"key": "D", "text": "Option D text", "is_correct": false}}
  ],
  "correct_answer": "B",
  "explanation": "Detailed solution explanation",
  "subject": "{request.subject}",
  "difficulty_level": "{request.difficulty.value}",
  "confidence": 85
}}
"""
        
        # Apply style conditioning
        conditioned_prompt = self.style_conditioner.condition_prompt(base_prompt, request.subject)
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=1200,
                temperature=0.4,
                messages=[{"role": "user", "content": conditioned_prompt}]
            )
            
            response_text = response.content[0].text.strip()
            question = self._extract_json_from_response(response_text)
            
            # Add metadata
            question.update({
                'topic': request.topic,
                'learning_outcome': request.learning_outcome,
                'generated_at': time.time(),
                'generation_method': 'enhanced_pipeline_v2',
                'user_id': request.user_id
            })
            
            return question
            
        except Exception as e:
            print(f"Base generation failed: {e}")
            return None
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Enhanced JSON extraction with multiple fallback methods"""
        
        # Method 1: Find JSON block
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Method 2: Try removing markdown formatting
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
        
        # Method 3: Extract between curly braces more aggressively
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(response_text[start:end+1])
            except json.JSONDecodeError:
                pass
        
        return {}
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.subject}_{request.topic}_{request.learning_outcome}_{request.difficulty}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def generate_question_batch(self, requests: List[GenerationRequest]) -> List[Dict]:
        """Generate multiple questions efficiently"""
        tasks = [self.generate_question(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    def get_cache_stats(self) -> Dict:
        """Get generation cache statistics"""
        return {
            'cache_size': len(self.generation_cache),
            'cache_keys': list(self.generation_cache.keys())[:10],  # Sample
            'hit_rate': 0.0  # TODO: Implement hit tracking
        }