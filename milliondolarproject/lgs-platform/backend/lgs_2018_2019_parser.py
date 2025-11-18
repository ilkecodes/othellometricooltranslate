#!/usr/bin/env python3
"""
2018-2019 LGS PDF Parser - Extract questions from older LGS exams
"""

import json
import os
import re
from typing import Dict, List, Any
from anthropic import Anthropic
import PyPDF2
from pathlib import Path
import time

class LGS2018_2019Parser:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.pdf_directory = Path('/app/lgs_pdfs')
        
    def extract_text_thoroughly(self, pdf_path: Path) -> List[str]:
        """Extract text more thoroughly from older PDFs"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Process ALL pages for older exams
                all_text = ""
                total_pages = len(pdf_reader.pages)
                print(f"   📖 Processing {total_pages} pages...")
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        all_text += f"\n--- PAGE {i+1} ---\n{page_text}"
                
                # Clean and split into meaningful chunks
                all_text = re.sub(r'\s+', ' ', all_text)
                all_text = re.sub(r'LGS.*?SINAVI', '', all_text, flags=re.IGNORECASE)
                all_text = re.sub(r'MEB.*?ÖLÇME', '', all_text, flags=re.IGNORECASE)
                
                # Split by page markers and question patterns
                chunks = []
                
                # Method 1: Split by page markers
                page_sections = all_text.split('--- PAGE')
                for section in page_sections:
                    if len(section.strip()) > 800:
                        chunks.append(section.strip())
                
                # Method 2: Split by question number patterns
                question_pattern = r'(\d+\.\s+[A-Z].*?)(?=\d+\.\s+[A-Z]|$)'
                question_matches = re.findall(question_pattern, all_text, re.DOTALL)
                
                for match in question_matches:
                    if len(match.strip()) > 200:
                        chunks.append(match.strip())
                
                # Remove duplicates and filter
                unique_chunks = []
                seen = set()
                for chunk in chunks:
                    chunk_hash = hash(chunk[:100])  # Hash first 100 chars
                    if chunk_hash not in seen and len(chunk) > 300:
                        seen.add(chunk_hash)
                        unique_chunks.append(chunk)
                
                return unique_chunks
                
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return []
    
    def extract_questions_from_chunk(self, chunk: str, pdf_info: Dict, chunk_num: int) -> List[Dict]:
        """Extract questions with pattern-focused approach"""
        
        year = pdf_info['year']
        exam_type = pdf_info['type']
        
        # Pattern-focused prompt
        prompt = f"""Extract LGS {year} {exam_type.upper()} questions from this text.

FIND ALL questions that have:
- Question number (1, 2, 3...)
- Question stem (ending with ? or clear question)  
- Options A), B), C), D) or similar
- Clear answer choices

For each question found, return JSON:
{{
  "stem": "Full question text",
  "options": [
    {{"key": "A", "text": "Option A text"}},
    {{"key": "B", "text": "Option B text"}},
    {{"key": "C", "text": "Option C text"}},
    {{"key": "D", "text": "Option D text"}}
  ],
  "subject": "Türkçe|Matematik|Fen Bilimleri|Sosyal Bilgiler|Din Kültürü ve Ahlak Bilgisi|İngilizce",
  "year": {year}
}}

Return JSON array of ALL questions found:
[question1, question2, ...]

Text to analyze:
{chunk[:2500]}"""

        try:
            time.sleep(2)  # Rate limiting for older PDFs
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=3500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean response
            response_text = response_text.replace('```json', '').replace('```', '')
            response_text = re.sub(r'^[^[]*', '', response_text)  # Remove text before [
            response_text = re.sub(r'[^]]*$', ']', response_text)  # Ensure ends with ]
            
            # Parse JSON
            try:
                questions = json.loads(response_text)
                
                if isinstance(questions, list):
                    valid_questions = []
                    for q in questions:
                        if self.validate_question(q):
                            q.update({
                                'question_number': len(valid_questions) + 1,
                                'exam_type': exam_type,
                                'stamp': 'LGS',
                                'source': f'Original LGS {year}',
                                'pdf_source': pdf_info.get('filename', ''),
                                'extraction_date': '2024-11-16',
                                'processing_method': f'AI_2018_2019_parser',
                                'confidence': 'high',
                                'chunk_source': chunk_num
                            })
                            valid_questions.append(q)
                    
                    return valid_questions
                    
            except json.JSONDecodeError as e:
                print(f"   ⚠️ JSON error in chunk {chunk_num}: {e}")
                
        except Exception as e:
            print(f"   ⚠️ Chunk {chunk_num} processing error: {str(e)[:100]}")
        
        return []
    
    def validate_question(self, question: Dict) -> bool:
        """Validate if a question object is properly formed"""
        required_fields = ['stem', 'options', 'subject']
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                return False
        
        # Check stem
        if not isinstance(question['stem'], str) or len(question['stem']) < 10:
            return False
        
        # Check options
        options = question.get('options', [])
        if not isinstance(options, list) or len(options) < 3:
            return False
        
        # Check each option
        for opt in options:
            if not isinstance(opt, dict) or 'key' not in opt or 'text' not in opt:
                return False
            if not isinstance(opt['text'], str) or len(opt['text']) < 2:
                return False
        
        return True
    
    def process_old_lgs_pdfs(self) -> Dict:
        """Process 2018 and 2019 LGS PDFs thoroughly"""
        
        target_pdfs = {
            'lgs2018_sozel.pdf': {'year': 2018, 'type': 'sozel', 'filename': 'lgs2018_sozel.pdf'},
            'lgs2018_sayisal.pdf': {'year': 2018, 'type': 'sayisal', 'filename': 'lgs2018_sayisal.pdf'},
            'lgs2019_sozel.pdf': {'year': 2019, 'type': 'sozel', 'filename': 'lgs2019_sozel.pdf'},
            'lgs2019_sayisal.pdf': {'year': 2019, 'type': 'sayisal', 'filename': 'lgs2019_sayisal.pdf'},
        }
        
        print("📚 2018-2019 LGS PDF PARSER")
        print("=" * 50)
        
        all_questions = []
        total_processed = 0
        successful_pdfs = 0
        
        for filename, pdf_info in target_pdfs.items():
            pdf_path = self.pdf_directory / filename
            
            if not pdf_path.exists():
                print(f"⚠️ File not found: {filename}")
                continue
            
            print(f"\n📄 Processing {filename} ({pdf_info['year']} {pdf_info['type'].upper()})")
            total_processed += 1
            
            # Extract text chunks
            chunks = self.extract_text_thoroughly(pdf_path)
            
            if not chunks:
                print(f"   ❌ No text chunks extracted")
                continue
            
            print(f"   📝 Extracted {len(chunks)} text chunks")
            
            pdf_questions = []
            successful_chunks = 0
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                print(f"   🔍 Processing chunk {i+1}/{len(chunks)}...")
                
                chunk_questions = self.extract_questions_from_chunk(chunk, pdf_info, i+1)
                
                if chunk_questions:
                    pdf_questions.extend(chunk_questions)
                    successful_chunks += 1
                    print(f"      ✅ Found {len(chunk_questions)} questions")
                else:
                    print(f"      ❌ No valid questions found")
            
            if pdf_questions:
                all_questions.extend(pdf_questions)
                successful_pdfs += 1
                print(f"   📊 PDF Total: {len(pdf_questions)} questions from {successful_chunks}/{len(chunks)} chunks")
            
            # Wait between PDFs to avoid rate limiting
            if len(target_pdfs) > 1:
                print("   ⏳ Cooling down...")
                time.sleep(8)
        
        return {
            'questions': all_questions,
            'stats': {
                'total_processed': total_processed,
                'successful_pdfs': successful_pdfs,
                'total_questions': len(all_questions)
            }
        }

def main():
    parser = LGS2018_2019Parser()
    
    # Process old LGS PDFs
    results = parser.process_old_lgs_pdfs()
    
    questions = results['questions']
    stats = results['stats']
    
    # Save results
    output_file = '/app/lgs_2018_2019_questions.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    print(f"\n" + "=" * 50)
    print(f"📊 2018-2019 EXTRACTION COMPLETE")
    print("=" * 50)
    print(f"PDFs processed: {stats['successful_pdfs']}/{stats['total_processed']}")
    print(f"Total questions extracted: {stats['total_questions']}")
    
    # Show detailed stats
    if questions:
        by_pdf = {}
        by_subject = {}
        by_year = {}
        
        for q in questions:
            pdf = q.get('pdf_source', 'unknown')
            subject = q.get('subject', 'unknown')
            year = q.get('year', 'unknown')
            
            by_pdf[pdf] = by_pdf.get(pdf, 0) + 1
            by_subject[subject] = by_subject.get(subject, 0) + 1
            by_year[year] = by_year.get(year, 0) + 1
        
        print(f"\n📁 By PDF:")
        for pdf, count in sorted(by_pdf.items()):
            print(f"   {pdf}: {count} questions")
        
        print(f"\n📚 By Subject:")
        for subject, count in sorted(by_subject.items()):
            print(f"   {subject}: {count} questions")
        
        print(f"\n📅 By Year:")
        for year, count in sorted(by_year.items()):
            print(f"   {year}: {count} questions")
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"🎯 {stats['total_questions']} new questions ready for integration!")
    else:
        print("❌ No questions extracted. Check PDF quality or OCR issues.")

if __name__ == "__main__":
    main()