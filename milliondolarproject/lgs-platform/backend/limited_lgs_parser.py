#!/usr/bin/env python3
"""
Limited LGS PDF Parser - Test with specific PDFs only
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
import time

class LimitedLGSPDFParser:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.pdf_directory = Path('/app/lgs_pdfs')
        self.output_file = '/app/lgs_historical_questions_limited.jsonl'
        
        # Process only specific PDFs that worked
        self.pdf_mapping = {
            'lgs2019_sozel.pdf': {'year': 2019, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']},
            'lgs2019_sayisal.pdf': {'year': 2019, 'type': 'sayisal', 'subjects': ['Matematik', 'Fen Bilimleri']},
            'lgs2025_sozel.pdf': {'year': 2025, 'type': 'sozel', 'subjects': ['Türkçe', 'Sosyal Bilgiler', 'Din Kültürü ve Ahlak Bilgisi', 'İngilizce']}
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                # Extract from first few pages only
                max_pages = min(10, len(pdf_reader.pages))
                for i in range(max_pages):
                    text += pdf_reader.pages[i].extract_text()
                return text
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'LGS.*?SINAVI.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'MEB.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'ÖLÇME.*?DEĞERLENDIRME.*?\n', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def parse_questions_with_ai(self, text: str, pdf_info: Dict) -> List[Dict]:
        """Use AI to parse questions with improved stability"""
        
        year = pdf_info['year']
        exam_type = pdf_info['type']
        
        # Simple focused prompt
        prompt = f"""Extract exactly 3-5 LGS {year} questions from this text.
Return clean JSON array only.

[
  {{
    "stem": "Question text here",
    "options": [
      {{"key": "A", "text": "Option A"}},
      {{"key": "B", "text": "Option B"}},
      {{"key": "C", "text": "Option C"}},
      {{"key": "D", "text": "Option D"}}
    ],
    "subject": "Subject name",
    "year": {year}
  }}
]

Text: {text[:2000]}"""

        try:
            # Wait to avoid rate limiting
            time.sleep(3)
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '')
            
            # Extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx + 1]
                questions = json.loads(json_text)
                
                if isinstance(questions, list):
                    # Add metadata
                    for i, q in enumerate(questions):
                        q.update({
                            'question_number': i + 1,
                            'exam_type': exam_type,
                            'stamp': 'LGS',
                            'source': f'Original LGS {year}',
                            'pdf_source': pdf_info.get('filename', ''),
                            'extraction_date': '2024-11-16',
                            'processing_method': 'AI_claude_limited',
                            'confidence': 'high'
                        })
                    
                    return questions
                    
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        return []
    
    def process_limited_pdfs(self) -> Dict[str, Any]:
        """Process only selected PDFs"""
        print("🎯 LIMITED LGS PDF PARSER")
        print("=" * 40)
        
        all_questions = []
        stats = {'total_pdfs': 0, 'successful_pdfs': 0, 'total_questions': 0}
        
        for filename, pdf_info in self.pdf_mapping.items():
            pdf_path = self.pdf_directory / filename
            
            if not pdf_path.exists():
                print(f"⚠️ File not found: {filename}")
                continue
            
            stats['total_pdfs'] += 1
            pdf_info['filename'] = filename
            
            print(f"\n📄 Processing {filename}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                continue
                
            text = self.clean_text(text)
            print(f"   📝 Extracted {len(text)} characters")
            
            # Parse with AI
            questions = self.parse_questions_with_ai(text, pdf_info)
            
            if questions:
                all_questions.extend(questions)
                stats['successful_pdfs'] += 1
                stats['total_questions'] += len(questions)
                print(f"   ✅ Extracted {len(questions)} questions")
            else:
                print(f"   ❌ No questions extracted")
        
        return {
            'questions': all_questions,
            'stats': stats
        }
    
    def save_results(self, results: Dict):
        """Save results"""
        questions = results['questions']
        
        # Save to JSONL
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for question in questions:
                f.write(json.dumps(question, ensure_ascii=False) + '\n')
        
        stats = results['stats']
        print(f"\n" + "=" * 40)
        print(f"📊 EXTRACTION COMPLETE")
        print("=" * 40)
        print(f"PDFs processed: {stats['successful_pdfs']}/{stats['total_pdfs']}")
        print(f"Total questions: {stats['total_questions']}")
        print(f"✅ Saved to: {self.output_file}")

def main():
    parser = LimitedLGSPDFParser()
    results = parser.process_limited_pdfs()
    parser.save_results(results)

if __name__ == "__main__":
    main()