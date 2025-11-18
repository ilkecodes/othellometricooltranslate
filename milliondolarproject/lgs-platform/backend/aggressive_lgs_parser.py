#!/usr/bin/env python3
"""
Aggressive LGS PDF Parser - Extract many more questions using multiple strategies
"""

import json
import os
import re
from typing import Dict, List, Any
from anthropic import Anthropic
import PyPDF2
from pathlib import Path
import time

class AggressiveLGSPDFParser:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.pdf_directory = Path('/app/lgs_pdfs')
        
    def extract_text_chunks(self, pdf_path: Path, chunk_size: int = 3000) -> List[str]:
        """Extract text in chunks for better processing"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                # Extract from more pages
                max_pages = min(15, len(pdf_reader.pages))
                for i in range(max_pages):
                    page_text = pdf_reader.pages[i].extract_text()
                    full_text += page_text + "\n"
                
                # Clean text
                full_text = re.sub(r'\s+', ' ', full_text)
                full_text = re.sub(r'LGS.*?SINAVI.*?\n', '', full_text, flags=re.IGNORECASE)
                
                # Split into chunks
                chunks = []
                for i in range(0, len(full_text), chunk_size):
                    chunk = full_text[i:i + chunk_size]
                    if len(chunk.strip()) > 500:  # Only process meaningful chunks
                        chunks.append(chunk.strip())
                
                return chunks
                
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return []
    
    def parse_chunk_aggressively(self, chunk: str, pdf_info: Dict, chunk_num: int) -> List[Dict]:
        """Parse a text chunk more aggressively"""
        
        year = pdf_info['year']
        exam_type = pdf_info['type']
        
        # More specific prompt to find questions
        prompt = f"""Extract ALL LGS {year} questions from this text chunk. Look for:
- Question numbers (1, 2, 3... or A), B), C)...)
- Multiple choice options (A, B, C, D)
- Question stems ending with question marks
- Answer choices

Return JSON array with ALL questions found:
[
  {{
    "stem": "Complete question text",
    "options": [
      {{"key": "A", "text": "Option A"}},
      {{"key": "B", "text": "Option B"}}, 
      {{"key": "C", "text": "Option C"}},
      {{"key": "D", "text": "Option D"}}
    ],
    "subject": "Best guess: Türkçe|Matematik|Fen Bilimleri|Sosyal Bilgiler|Din Kültürü ve Ahlak Bilgisi|İngilizce",
    "year": {year},
    "source_chunk": {chunk_num}
  }}
]

Text chunk:
{chunk}"""

        try:
            time.sleep(1)  # Rate limiting
            
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
                    for i, q in enumerate(questions):
                        if (isinstance(q, dict) and 
                            'stem' in q and 
                            'options' in q and
                            isinstance(q['options'], list) and
                            len(q['options']) >= 3):  # At least 3 options
                            
                            q.update({
                                'question_number': i + 1,
                                'exam_type': exam_type,
                                'stamp': 'LGS',
                                'source': f'Original LGS {year}',
                                'pdf_source': pdf_info.get('filename', ''),
                                'extraction_date': '2024-11-16',
                                'processing_method': 'AI_aggressive',
                                'confidence': 'medium'
                            })
                            valid_questions.append(q)
                    
                    return valid_questions
                    
        except Exception as e:
            print(f"   ⚠️ Chunk {chunk_num} error: {str(e)[:100]}")
        
        return []
    
    def process_pdf_aggressively(self, pdf_path: Path, pdf_info: Dict) -> List[Dict]:
        """Process a single PDF more thoroughly"""
        filename = pdf_path.name
        print(f"\n📄 Processing {filename} AGGRESSIVELY")
        
        # Extract text in chunks
        chunks = self.extract_text_chunks(pdf_path)
        if not chunks:
            print(f"   ❌ No text chunks extracted")
            return []
        
        print(f"   📝 Extracted {len(chunks)} text chunks")
        
        all_questions = []
        successful_chunks = 0
        
        for i, chunk in enumerate(chunks):
            print(f"   🔍 Processing chunk {i+1}/{len(chunks)}...")
            
            questions = self.parse_chunk_aggressively(chunk, pdf_info, i+1)
            
            if questions:
                all_questions.extend(questions)
                successful_chunks += 1
                print(f"      ✅ Found {len(questions)} questions")
            else:
                print(f"      ❌ No questions found")
        
        print(f"   📊 Total: {len(all_questions)} questions from {successful_chunks}/{len(chunks)} chunks")
        return all_questions
    
    def process_specific_pdfs(self) -> Dict:
        """Process specific high-yield PDFs"""
        
        # Process 2018-2019 LGS PDFs using same successful method
        target_pdfs = {
            'lgs2018_sozel.pdf': {'year': 2018, 'type': 'sozel', 'filename': 'lgs2018_sozel.pdf'},
            'lgs2018_sayisal.pdf': {'year': 2018, 'type': 'sayisal', 'filename': 'lgs2018_sayisal.pdf'},
            'lgs2019_sozel.pdf': {'year': 2019, 'type': 'sozel', 'filename': 'lgs2019_sozel.pdf'},
            'lgs2019_sayisal.pdf': {'year': 2019, 'type': 'sayisal', 'filename': 'lgs2019_sayisal.pdf'},
        }
        
        print("🚀 AGGRESSIVE LGS PDF PARSER - 2018-2019 EDITION")
        print("=" * 50)
        
        all_questions = []
        total_processed = 0
        successful_pdfs = 0
        
        for filename, pdf_info in target_pdfs.items():
            pdf_path = self.pdf_directory / filename
            
            if not pdf_path.exists():
                print(f"⚠️ File not found: {filename}")
                continue
            
            total_processed += 1
            
            questions = self.process_pdf_aggressively(pdf_path, pdf_info)
            
            if questions:
                all_questions.extend(questions)
                successful_pdfs += 1
            
            # Avoid rate limiting
            if len(target_pdfs) > 1:
                print("   ⏳ Waiting to avoid rate limits...")
                time.sleep(5)
        
        return {
            'questions': all_questions,
            'stats': {
                'total_processed': total_processed,
                'successful_pdfs': successful_pdfs,
                'total_questions': len(all_questions)
            }
        }

def main():
    parser = AggressiveLGSPDFParser()
    
    # Process PDFs aggressively
    results = parser.process_specific_pdfs()
    
    questions = results['questions']
    stats = results['stats']
    
    # Save results
    output_file = '/app/lgs_2018_2019_questions.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    print(f"\n" + "=" * 50)
    print(f"📊 AGGRESSIVE EXTRACTION COMPLETE")
    print("=" * 50)
    print(f"PDFs processed: {stats['successful_pdfs']}/{stats['total_processed']}")
    print(f"Total questions: {stats['total_questions']}")
    
    # Show distribution
    by_pdf = {}
    by_subject = {}
    for q in questions:
        pdf = q.get('pdf_source', 'unknown')
        subject = q.get('subject', 'unknown')
        by_pdf[pdf] = by_pdf.get(pdf, 0) + 1
        by_subject[subject] = by_subject.get(subject, 0) + 1
    
    print(f"\n📁 By PDF:")
    for pdf, count in by_pdf.items():
        print(f"   {pdf}: {count} questions")
    
    print(f"\n📚 By Subject:")
    for subject, count in by_subject.items():
        print(f"   {subject}: {count} questions")
    
    print(f"\n✅ Saved to: {output_file}")
    
    if stats['total_questions'] > 0:
        print(f"🎯 Ready to add {stats['total_questions']} more questions to database!")
    else:
        print("⚠️ No questions extracted. PDF OCR quality might be poor.")

if __name__ == "__main__":
    main()