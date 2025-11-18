#!/usr/bin/env python3
"""
Bulk LGS PDF Parser - Extract questions from all historical LGS PDFs
This script processes all LGS PDFs to extract questions and build comprehensive original question database
"""

import json
import os
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from anthropic import Anthropic
import PyPDF2
from pathlib import Path
import sys

class BulkLGSPDFParser:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.pdf_directory = Path('/app/lgs_pdfs')
        self.output_file = '/app/lgs_historical_questions_bulk.jsonl'
        
        # Year and type mapping
        self.pdf_mapping = {
            'lgs2025_sozel.pdf': {'year': 2025, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2025_sayisal.pdf': {'year': 2025, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2023_sozel.pdf': {'year': 2023, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2022_sozel.pdf': {'year': 2022, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2022_sayisal.pdf': {'year': 2022, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2021_sozel.pdf': {'year': 2021, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2021_sayisal.pdf': {'year': 2021, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2020_sayisal.pdf': {'year': 2020, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2019_sozel.pdf': {'year': 2019, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2019_sayisal.pdf': {'year': 2019, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2018_sozel.pdf': {'year': 2018, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2018_sayisal.pdf': {'year': 2018, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']}
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page headers/footers
        text = re.sub(r'LGS.*?SINAVI.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'MEB.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'ÖLÇME.*?DEĞERLENDIRME.*?\n', '', text, flags=re.IGNORECASE)
        # Remove exam instructions
        text = re.sub(r'Bu test.*?süreniz.*?\n', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def parse_questions_with_ai(self, text: str, pdf_info: Dict, max_retries: int = 3) -> List[Dict]:
        """Use AI to parse questions from text with improved error handling"""
        
        year = pdf_info['year']
        exam_type = pdf_info['type']
        subjects = ', '.join(pdf_info['subjects'])
        
        # Shorter, more focused prompts to avoid overload
        if exam_type == 'sozel':
            prompt = f"""Parse {year} LGS Sözel questions. Extract max 5-8 questions.
Keep English questions in English.

Return ONLY clean JSON array:
[
  {{
    "stem": "Question text",
    "options": [
      {{"key": "A", "text": "Choice A"}},
      {{"key": "B", "text": "Choice B"}},
      {{"key": "C", "text": "Choice C"}},
      {{"key": "D", "text": "Choice D"}}
    ],
    "subject": "Türkçe|Sosyal Bilgiler|Din Kültürü ve Ahlak Bilgisi|İngilizce",
    "year": {year}
  }}
]

Text: {text[:3000]}"""
        else:
            prompt = f"""Parse {year} LGS Sayısal questions. Extract max 5-8 questions.

Return ONLY clean JSON array:
[
  {{
    "stem": "Question text",
    "options": [
      {{"key": "A", "text": "Choice A"}},
      {{"key": "B", "text": "Choice B"}},
      {{"key": "C", "text": "Choice C"}},
      {{"key": "D", "text": "Choice D"}}
    ],
    "subject": "Matematik|Fen Bilimleri",
    "year": {year}
  }}
]

Text: {text[:3000]}"""

        for attempt in range(max_retries):
            try:
                # Wait between retries to avoid rate limiting
                if attempt > 0:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,  # Reduced tokens
                    temperature=0.0,  # More deterministic
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = response.content[0].text.strip()
                
                # Clean response text
                response_text = response_text.replace('```json', '').replace('```', '')
                
                # Extract JSON array more carefully
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    
                    try:
                        questions = json.loads(json_text)
                        
                        if isinstance(questions, list) and questions:
                            # Validate and clean questions
                            valid_questions = []
                            for q in questions:
                                if (isinstance(q, dict) and 
                                    'stem' in q and 
                                    'options' in q and 
                                    isinstance(q['options'], list) and 
                                    len(q['options']) >= 4):
                                    
                                    # Add missing fields
                                    q.update({
                                        'question_number': len(valid_questions) + 1,
                                        'exam_type': exam_type,
                                        'stamp': 'LGS',
                                        'source': f'Original LGS {year}'
                                    })
                                    valid_questions.append(q)
                            
                            return valid_questions
                    
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️ JSON parse error: {e}")
                        continue
                
                print(f"   ⚠️ No valid JSON array found in response")
                continue
                
            except Exception as e:
                error_msg = str(e)
                if "overloaded" in error_msg.lower() or "529" in error_msg:
                    print(f"   ⚠️ API overloaded, waiting...")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(5 + attempt * 3)  # Longer wait for overload
                        continue
                else:
                    print(f"   ⚠️ Attempt {attempt + 1}/{max_retries}: {error_msg}")
        
        return []
    
    def process_single_pdf(self, pdf_path: Path) -> List[Dict]:
        """Process a single PDF file"""
        filename = pdf_path.name
        
        if filename not in self.pdf_mapping:
            print(f"⚠️ Unknown PDF: {filename}")
            return []
        
        pdf_info = self.pdf_mapping[filename]
        print(f"\n📄 Processing {filename} ({pdf_info['year']} {pdf_info['type'].upper()})")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"   ❌ No text extracted")
            return []
        
        # Clean text
        clean_text = self.clean_text(text)
        print(f"   📝 Extracted {len(clean_text)} characters")
        
        # Parse with AI
        questions = self.parse_questions_with_ai(clean_text, pdf_info)
        
        if questions:
            print(f"   ✅ Extracted {len(questions)} questions")
            
            # Add metadata to each question
            for q in questions:
                q.update({
                    'pdf_source': filename,
                    'extraction_date': '2024-11-16',
                    'processing_method': 'AI_claude',
                    'confidence': 'high'
                })
        else:
            print(f"   ❌ No questions extracted")
        
        return questions
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """Process all PDFs in the directory"""
        print("🚀 BULK LGS PDF PARSER STARTING")
        print("=" * 60)
        
        all_questions = []
        processing_stats = {
            'total_pdfs': 0,
            'successful_pdfs': 0,
            'total_questions': 0,
            'by_year': defaultdict(int),
            'by_subject': defaultdict(int),
            'by_type': defaultdict(int)
        }
        
        # Process each PDF
        pdf_files = list(self.pdf_directory.glob('*.pdf'))
        processing_stats['total_pdfs'] = len(pdf_files)
        
        for pdf_path in sorted(pdf_files):
            try:
                questions = self.process_single_pdf(pdf_path)
                
                if questions:
                    all_questions.extend(questions)
                    processing_stats['successful_pdfs'] += 1
                    processing_stats['total_questions'] += len(questions)
                    
                    # Update stats
                    for q in questions:
                        processing_stats['by_year'][q.get('year', 'unknown')] += 1
                        processing_stats['by_subject'][q.get('subject', 'unknown')] += 1
                        processing_stats['by_type'][q.get('exam_type', 'unknown')] += 1
                
            except Exception as e:
                print(f"❌ Error processing {pdf_path}: {e}")
        
        return {
            'questions': all_questions,
            'stats': dict(processing_stats),
            'processing_summary': {
                'total_pdfs_found': processing_stats['total_pdfs'],
                'successfully_processed': processing_stats['successful_pdfs'],
                'total_questions_extracted': processing_stats['total_questions'],
                'by_year': dict(processing_stats['by_year']),
                'by_subject': dict(processing_stats['by_subject']),
                'by_type': dict(processing_stats['by_type'])
            }
        }
    
    def save_results(self, results: Dict[str, Any]):
        """Save extraction results"""
        questions = results['questions']
        
        # Save questions to JSONL
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for question in questions:
                f.write(json.dumps(question, ensure_ascii=False) + '\n')
        
        # Save summary
        summary_file = '/app/lgs_historical_extraction_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results['processing_summary'], f, ensure_ascii=False, indent=2)
        
        print(f"\n" + "=" * 60)
        print(f"📊 BULK EXTRACTION COMPLETE")
        print("=" * 60)
        
        stats = results['processing_summary']
        print(f"📄 PDFs processed: {stats['successfully_processed']}/{stats['total_pdfs_found']}")
        print(f"📝 Total questions: {stats['total_questions_extracted']}")
        
        print(f"\n📅 By Year:")
        for year, count in sorted(stats['by_year'].items()):
            print(f"   {year}: {count} questions")
        
        print(f"\n📚 By Subject:")
        for subject, count in stats['by_subject'].items():
            print(f"   {subject}: {count} questions")
        
        print(f"\n🎯 By Type:")
        for exam_type, count in stats['by_type'].items():
            print(f"   {exam_type}: {count} questions")
        
        print(f"\n✅ Results saved to:")
        print(f"   Questions: {self.output_file}")
        print(f"   Summary: {summary_file}")
        print(f"\n🎉 Historical LGS question database ready for integration!")

def main():
    parser = BulkLGSPDFParser()
    
    # Check if PDFs exist
    if not parser.pdf_directory.exists():
        print(f"❌ PDF directory not found: {parser.pdf_directory}")
        sys.exit(1)
    
    pdf_files = list(parser.pdf_directory.glob('*.pdf'))
    if not pdf_files:
        print(f"❌ No PDF files found in {parser.pdf_directory}")
        sys.exit(1)
    
    print(f"📁 Found {len(pdf_files)} PDF files to process")
    
    # Process all PDFs
    results = parser.process_all_pdfs()
    
    # Save results
    parser.save_results(results)

if __name__ == "__main__":
    main()