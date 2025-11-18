#!/usr/bin/env python3
"""
Comprehensive LGS Parser for 2018-2025
Combines Turkish PDF parsing with aggressive extraction for all subjects
Handles both Sözel and Sayısal sections across all available years
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
import pdfplumber
import PyPDF2
from anthropic import Anthropic


class ComprehensiveLGSParser:
    def __init__(self):
        """Initialize parser with all available LGS years and types"""
        # Try to initialize Anthropic client, but make it optional
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
                self.ai_available = True
                print("✅ Anthropic API client initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize Anthropic client: {e}")
                self.client = None
                self.ai_available = False
        else:
            print("ℹ️ No Anthropic API key found - AI extraction disabled")
            self.client = None
            self.ai_available = False
        
        # Available PDF files from directory listing
        self.available_pdfs = {
            # 2018 files
            'lgs2018_sozel.pdf': {'year': 2018, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            'lgs2018_sayisal.pdf': {'year': 2018, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            
            # 2019 files  
            'lgs2019_sozel.pdf': {'year': 2019, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            'lgs2019_sayisal.pdf': {'year': 2019, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            
            # 2020 files
            'lgs2020_sayisal.pdf': {'year': 2020, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            
            # 2021 files
            'lgs2021_sozel.pdf': {'year': 2021, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            'lgs2021_sayisal.pdf': {'year': 2021, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            
            # 2022 files
            'lgs2022_sozel.pdf': {'year': 2022, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            'lgs2022_sayisal.pdf': {'year': 2022, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            
            # 2023 files
            'lgs2023_sozel.pdf': {'year': 2023, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            
            # 2025 files
            'lgs2025_sozel.pdf': {'year': 2025, 'type': 'sozel', 'subjects': ['TURKISH', 'SOCIAL_STUDIES', 'RELIGION']},
            'lgs2025_sayisal.pdf': {'year': 2025, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
            'lgs2025_sayisal_v2.pdf': {'year': 2025, 'type': 'sayisal', 'subjects': ['MATH', 'SCIENCE', 'ENGLISH']},
        }
        
        # Check both locations for PDFs (container paths)
        self.pdf_directories = [
            Path('/app/lgs_pdfs'),
            Path('/app/lgs_pdfs/lgs_pdfs'),
        ]

    def find_pdf_file(self, filename: str) -> Optional[Path]:
        """Find PDF file in available directories"""
        for directory in self.pdf_directories:
            pdf_path = directory / filename
            if pdf_path.exists():
                return pdf_path
        return None

    def normalize_text(self, s: str) -> str:
        """Clean and normalize text: remove hyphens, newlines, collapse spaces."""
        if not s:
            return ""
        # remove hyphen-only line breaks: "yapıl -\nması" → "yapılması"
        s = re.sub(r"-\s*\n\s*", "", s)
        # normal newlines → spaces
        s = re.sub(r"\s*\n\s*", " ", s)
        # collapse spaces
        s = re.sub(r"\s{2,}", " ", s)
        return s.strip()

    def clean_option_text(self, text: str) -> str:
        """Clean option text, removing trailing page numbers."""
        text = self.normalize_text(text)
        # remove stray trailing page/line numbers like "... 10"
        text = re.sub(r"\s+\d{1,2}$", "", text)
        return text

    def parse_turkish_questions_detailed(self, pdf_path: Path, year: int) -> List[Dict]:
        """Parse Turkish questions using the proven detailed method"""
        print(f"   🇹🇷 Parsing Turkish questions with detailed method for {year}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract Turkish section
                turkce_text = self.extract_subject_block(pdf, "TÜRKÇE")
                if not turkce_text:
                    return []
                
                # Find question chunks
                chunks = self.find_question_chunks(turkce_text, 1, 20)  # Turkish has 20 questions
                
                # Extract answer key
                answer_key = self.extract_answer_key(pdf, 1, 20)
                
                questions = []
                for i, chunk in enumerate(chunks, 1):
                    question = self.parse_single_turkish_question(chunk, i, answer_key, year)
                    if question:
                        questions.append(question)
                
                return questions
                
        except Exception as e:
            print(f"   ❌ Turkish parsing error: {e}")
            return []

    def extract_subject_block(self, pdf: pdfplumber.PDF, subject: str) -> str:
        """Extract text block for a specific subject"""
        subject_page_indices = []
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if subject in text:
                subject_page_indices.append(i)
        
        # Filter out cover and answer key pages
        subject_page_indices = [i for i in subject_page_indices if 0 < i < len(pdf.pages) - 1]
        
        if not subject_page_indices:
            return ""
        
        start = min(subject_page_indices)
        end = max(subject_page_indices)
        
        combined = ""
        for i in range(start, end + 1):
            combined += "\n\n===PAGE %d===\n" % (i + 1)
            combined += pdf.pages[i].extract_text() or ""
        
        return self.clean_subject_text(combined, subject)

    def clean_subject_text(self, text: str, subject: str) -> str:
        """Clean subject-specific text"""
        clean = text
        
        # Common patterns to remove
        patterns = [
            r"SINAVLA ÖĞRENCİ ALACAK ORTAÖĞRETİM KURUMLARINA İLİŞKİN MERKEZÎ SINAV",
            r"A \(ÖDSGM\)\d{4}-\d{4} EĞİTİM - ÖĞRETİM YILI",
            r"Diğer sayfaya geçiniz\.",
            r"A\d+\.\s*Bu\s*testte\s*\d+\s*soru\s*vardır\.",
            r"\d+\.\s*Cevaplarınızı,\s*cevap\s*kâğıdına\s*işaretleyiniz\.",
            rf"A\s*\(ÖDSGM\){subject}",
            rf"A\(ÖDSGM\){subject}",
            r"===PAGE \d+===\n",
        ]
        
        for p in patterns:
            clean = re.sub(p, "", clean)
        
        # Fix "A3.", "A5." etc → "3.", "5."
        clean = re.sub(r"A(\d{1,2})\.", r"\1.", clean)
        
        # Clean up whitespace
        clean = clean.replace("\t", " ")
        clean = re.sub(r"[ ]{2,}", " ", clean)
        
        return clean.strip()

    def find_question_chunks(self, text: str, start_q: int, end_q: int) -> List[str]:
        """Find question chunks for a range of question numbers"""
        positions = []
        for n in range(start_q, end_q + 1):
            s = f"{n}."
            idx = text.find(s)
            if idx != -1:
                positions.append((n, idx))
        
        chunks = []
        for i, (q_num, start_pos) in enumerate(positions):
            if i + 1 < len(positions):
                end_pos = positions[i + 1][1]
            else:
                end_pos = len(text)
            
            chunk = text[start_pos:end_pos].strip()
            chunks.append(chunk)
        
        return chunks

    def extract_answer_key(self, pdf: pdfplumber.PDF, start_q: int, end_q: int) -> Dict[int, str]:
        """Extract answer key from last page"""
        try:
            last_page = pdf.pages[-1]
            text = last_page.extract_text() or ""
            
            pairs = re.findall(r"(\d{1,2})\.\s*([A-D])", text)
            answers = {}
            for num_str, letter in pairs:
                num = int(num_str)
                if start_q <= num <= end_q:
                    answers[num] = letter
            
            return answers
        except:
            return {}

    def parse_single_turkish_question(self, chunk: str, q_num: int, answer_key: Dict, year: int) -> Optional[Dict]:
        """Parse a single Turkish question chunk"""
        try:
            # Extract question number and content
            m = re.match(r"(\d{1,2})\.\s*(.*)", chunk, flags=re.S)
            if not m:
                return None
            
            rest = m.group(2).strip()
            
            # Find first option
            first_opt = re.search(r"[A-D]\)", rest)
            if not first_opt:
                stem = rest.strip()
                opts = []
            else:
                stem = rest[:first_opt.start()].strip()
                opt_str = rest[first_opt.start():]
                
                # Parse options
                opt_matches = list(re.finditer(
                    r"([A-D])\)\s*(.*?)(?=(?:[A-D]\)\s)|$)",
                    opt_str,
                    flags=re.S
                ))
                opts = [(m.group(1), m.group(2).strip()) for m in opt_matches]
            
            # Build options with correct answers
            options = []
            correct_answer = answer_key.get(q_num)
            
            if opts:
                for label, text in opts:
                    options.append({
                        "key": label,
                        "text": self.clean_option_text(text),
                        "is_correct": (label == correct_answer)
                    })
            else:
                # Handle visual questions
                for label in ['A', 'B', 'C', 'D']:
                    options.append({
                        "key": label,
                        "text": f"Görsel {label}",
                        "is_correct": (label == correct_answer)
                    })
            
            # Infer topic and difficulty
            topic_name, difficulty = self.infer_turkish_topic_and_difficulty(stem)
            
            return {
                "question_number": q_num,
                "stem": self.normalize_text(stem),
                "options": options,
                "subject": "TURKISH",
                "topic_name": topic_name,
                "difficulty": difficulty,
                "year": year,
                "exam_type": "sozel",
                "stamp": "LGS",
                "source": f"Original LGS {year}",
                "extraction_date": "2024-11-16",
                "processing_method": "detailed_turkish",
                "confidence": "high",
                "estimated_time_seconds": 90
            }
            
        except Exception as e:
            print(f"   ⚠️ Error parsing Turkish Q{q_num}: {e}")
            return None

    def infer_turkish_topic_and_difficulty(self, stem_text: str) -> tuple:
        """Infer Turkish topic and difficulty from question stem"""
        stem_lower = stem_text.lower()
        
        # Topic inference
        if any(word in stem_lower for word in ["parçada", "bu parça", "parçanın", "paragrafta", "metinde"]):
            topic = "Paragraf – Okuma Anlama"
        elif any(word in stem_lower for word in ["sözcük", "sözcüğü", "kelime", "deyim", "atasözü", "anlamı"]):
            topic = "Sözcükte Anlam"
        elif any(word in stem_lower for word in ["cümlede", "cümlelerin", "cümlesinde"]):
            topic = "Cümlede Anlam"
        elif any(word in stem_lower for word in ["yazım", "yazılışı", "noktalama", "virgül", "nokta"]):
            topic = "Yazım ve Noktalama"
        else:
            topic = "Türkçe – Diğer"
        
        # Difficulty inference
        words = stem_lower.split()
        if len(words) < 15:
            difficulty = "EASY"
        elif len(words) < 30:
            difficulty = "MEDIUM"
        else:
            difficulty = "HARD"
        
        return topic, difficulty

    def extract_with_ai_aggressive(self, pdf_path: Path, pdf_info: Dict) -> List[Dict]:
        """Extract questions using AI with aggressive chunking"""
        if not self.ai_available:
            print(f"   ⚠️ AI extraction skipped - no API key available")
            return []
            
        print(f"   🤖 AI aggressive extraction for {pdf_info['year']} {pdf_info['type']}")
        
        try:
            # Extract text chunks
            chunks = self.extract_text_chunks_pdf(pdf_path, chunk_size=3000)
            if not chunks:
                return []
            
            print(f"   📝 Processing {len(chunks)} chunks")
            
            all_questions = []
            for i, chunk in enumerate(chunks):
                questions = self.parse_chunk_with_ai(chunk, pdf_info, i + 1)
                if questions:
                    all_questions.extend(questions)
                    print(f"      ✅ Chunk {i+1}: {len(questions)} questions")
                
                # Rate limiting
                if i < len(chunks) - 1:
                    time.sleep(1)
            
            return all_questions
            
        except Exception as e:
            print(f"   ❌ AI extraction error: {e}")
            return []

    def extract_text_chunks_pdf(self, pdf_path: Path, chunk_size: int = 3000) -> List[str]:
        """Extract text in chunks from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                # Extract from meaningful pages
                max_pages = min(15, len(pdf_reader.pages))
                for i in range(1, max_pages - 1):  # Skip cover and answer key
                    page_text = pdf_reader.pages[i].extract_text()
                    full_text += page_text + "\n"
                
                # Clean text
                full_text = re.sub(r'\s+', ' ', full_text)
                full_text = re.sub(r'LGS.*?SINAVI.*?\n', '', full_text, flags=re.IGNORECASE)
                
                # Split into chunks
                chunks = []
                for i in range(0, len(full_text), chunk_size):
                    chunk = full_text[i:i + chunk_size]
                    if len(chunk.strip()) > 500:
                        chunks.append(chunk.strip())
                
                return chunks
                
        except Exception as e:
            return []

    def parse_chunk_with_ai(self, chunk: str, pdf_info: Dict, chunk_num: int) -> List[Dict]:
        """Parse chunk using AI"""
        year = pdf_info['year']
        exam_type = pdf_info['type']
        
        # Enhanced prompt for better extraction
        prompt = f"""Extract ALL complete LGS {year} questions from this text. Find questions with:
- Question numbers (1-90)
- Question text/stem
- Multiple choice options A, B, C, D
- Complete readable content

For each question found, return JSON:
[
  {{
    "question_number": <number>,
    "stem": "Complete question text",
    "options": [
      {{"key": "A", "text": "Option A text"}},
      {{"key": "B", "text": "Option B text"}},
      {{"key": "C", "text": "Option C text"}},
      {{"key": "D", "text": "Option D text"}}
    ],
    "subject": "TURKISH|MATH|SCIENCE|SOCIAL_STUDIES|RELIGION|ENGLISH"
  }}
]

Text:
{chunk}"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=3000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '')
            
            # Find JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx + 1]
                questions = json.loads(json_text)
                
                if isinstance(questions, list):
                    valid_questions = []
                    for q in questions:
                        if self.validate_question(q):
                            q.update({
                                'year': year,
                                'exam_type': exam_type,
                                'stamp': 'LGS',
                                'source': f'Original LGS {year}',
                                'extraction_date': '2024-11-16',
                                'processing_method': 'AI_aggressive',
                                'confidence': 'medium',
                                'source_chunk': chunk_num
                            })
                            valid_questions.append(q)
                    
                    return valid_questions
            
            return []
                    
        except Exception as e:
            return []

    def validate_question(self, question: Dict) -> bool:
        """Validate if extracted question is complete"""
        return (
            isinstance(question, dict) and
            'stem' in question and
            'options' in question and
            isinstance(question['options'], list) and
            len(question['options']) >= 3 and
            'subject' in question and
            len(str(question.get('stem', '')).strip()) > 20
        )

    def process_single_pdf(self, filename: str, pdf_info: Dict) -> List[Dict]:
        """Process a single PDF file using appropriate method"""
        pdf_path = self.find_pdf_file(filename)
        if not pdf_path:
            print(f"   ❌ File not found: {filename}")
            return []
        
        print(f"\n📄 Processing {filename} ({pdf_info['year']} {pdf_info['type']})")
        
        questions = []
        
        # Use detailed parsing for Turkish if it's a sözel exam
        if pdf_info['type'] == 'sozel' and 'TURKISH' in pdf_info['subjects']:
            turkish_questions = self.parse_turkish_questions_detailed(pdf_path, pdf_info['year'])
            if turkish_questions:
                questions.extend(turkish_questions)
                print(f"   ✅ Detailed Turkish: {len(turkish_questions)} questions")
        
        # Use aggressive AI extraction for all subjects (if available)
        ai_questions = self.extract_with_ai_aggressive(pdf_path, pdf_info)
        if ai_questions:
            questions.extend(ai_questions)
            print(f"   ✅ AI extraction: {len(ai_questions)} questions")
        elif self.ai_available:
            print(f"   ❌ AI extraction: 0 questions")
        
        # Remove duplicates based on question stem
        unique_questions = []
        seen_stems = set()
        for q in questions:
            stem_key = str(q.get('stem', ''))[:100].lower().strip()
            if stem_key not in seen_stems and len(stem_key) > 20:
                seen_stems.add(stem_key)
                unique_questions.append(q)
        
        if len(unique_questions) != len(questions):
            print(f"   🔄 Removed {len(questions) - len(unique_questions)} duplicates")
        
        return unique_questions

    def process_all_available_pdfs(self) -> Dict:
        """Process all available PDF files"""
        print("🚀 COMPREHENSIVE LGS PARSER 2018-2025")
        print("=" * 60)
        print(f"Found {len(self.available_pdfs)} PDF files to process")
        
        all_questions = []
        stats = {
            'total_pdfs': len(self.available_pdfs),
            'processed_pdfs': 0,
            'successful_pdfs': 0,
            'by_year': {},
            'by_subject': {},
            'by_method': {},
        }
        
        for filename, pdf_info in self.available_pdfs.items():
            try:
                questions = self.process_single_pdf(filename, pdf_info)
                
                stats['processed_pdfs'] += 1
                if questions:
                    stats['successful_pdfs'] += 1
                    all_questions.extend(questions)
                    
                    # Update stats
                    year = pdf_info['year']
                    stats['by_year'][year] = stats['by_year'].get(year, 0) + len(questions)
                    
                    for q in questions:
                        subject = q.get('subject', 'unknown')
                        method = q.get('processing_method', 'unknown')
                        stats['by_subject'][subject] = stats['by_subject'].get(subject, 0) + 1
                        stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
                
                # Rate limiting between PDFs
                if stats['processed_pdfs'] < stats['total_pdfs']:
                    time.sleep(3)
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
        
        stats['total_questions'] = len(all_questions)
        return {'questions': all_questions, 'stats': stats}

    def save_results(self, results: Dict, output_file: str):
        """Save extraction results to JSONL file"""
        questions = results['questions']
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for question in questions:
                f.write(json.dumps(question, ensure_ascii=False) + '\n')
        
        return len(questions)

    def print_summary(self, results: Dict):
        """Print comprehensive extraction summary"""
        questions = results['questions']
        stats = results['stats']
        
        print(f"\n" + "=" * 60)
        print(f"📊 COMPREHENSIVE EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"PDFs processed: {stats['successful_pdfs']}/{stats['processed_pdfs']}")
        print(f"Total questions: {stats['total_questions']}")
        
        print(f"\n📅 Questions by Year:")
        for year, count in sorted(stats['by_year'].items()):
            print(f"   {year}: {count} questions")
        
        print(f"\n📚 Questions by Subject:")
        for subject, count in sorted(stats['by_subject'].items()):
            print(f"   {subject}: {count} questions")
        
        print(f"\n🔬 Questions by Method:")
        for method, count in sorted(stats['by_method'].items()):
            print(f"   {method}: {count} questions")


def main():
    """Main execution function"""
    parser = ComprehensiveLGSParser()
    
    # Process all PDFs - AI extraction optional
    print("Starting comprehensive LGS extraction...")
    if not parser.ai_available:
        print("📌 Note: Running in Turkish-only mode (detailed parsing)")
        print("   For full extraction of all subjects, set ANTHROPIC_API_KEY")
    
    results = parser.process_all_available_pdfs()
    
    # Save results
    output_file = '/app/comprehensive_lgs_2018_2025.jsonl'
    question_count = parser.save_results(results, output_file)
    
    # Print summary
    parser.print_summary(results)
    
    print(f"\n✅ Saved {question_count} questions to:")
    print(f"   {output_file}")
    
    if question_count > 0:
        print(f"\n🎯 Ready to add {question_count} authentic LGS questions to database!")
        print("   Next steps:")
        print("   1. Review extracted questions")
        print("   2. Merge with existing question database") 
        print("   3. Generate new LGS bundle with expanded authentic content")
    else:
        print("⚠️ No questions extracted. Check PDF files and API configuration.")


if __name__ == "__main__":
    main()