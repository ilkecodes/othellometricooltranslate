#!/usr/bin/env python3
"""
Enhanced Hybrid PDF Parser: Questions + Kazanım Mapping

Combines:
1. pdfplumber text extraction
2. Claude LLM question classification  
3. Kazanım-based learning outcome mapping
"""

import json
import os
import sys
import re
from pathlib import Path
import pdfplumber
import anthropic

def load_kazanimlar(kazanim_file: str) -> dict:
    """Load extracted kazanımlar for mapping."""
    kazanimlar = {}
    subjects = set()
    
    if not os.path.exists(kazanim_file):
        print(f"⚠️  Kazanım file not found: {kazanim_file}")
        return {"kazanimlar": {}, "subjects": set(), "by_subject": {}}
    
    try:
        with open(kazanim_file, 'r', encoding='utf-8') as f:
            for line in f:
                kazanim = json.loads(line)
                code = kazanim.get('code')
                subject = kazanim.get('subject')
                
                if code and subject:  # Only include if both code and subject exist
                    kazanimlar[code] = kazanim
                    subjects.add(subject)
        
        # Group by subject for easier lookup
        by_subject = {}
        for code, kazanim in kazanimlar.items():
            subject = kazanim.get('subject', 'Unknown')
            if subject not in by_subject:
                by_subject[subject] = []
            by_subject[subject].append(kazanim)
        
        print(f"✓ Loaded {len(kazanimlar)} kazanımlar from {len(subjects)} subjects")
        return {
            "kazanimlar": kazanimlar,
            "subjects": subjects, 
            "by_subject": by_subject
        }
        
    except Exception as e:
        print(f"✗ Error loading kazanımlar: {e}")
        return {"kazanimlar": {}, "subjects": set(), "by_subject": {}}

def clean_text_for_json(text: str) -> str:
    """Clean text to prevent JSON parsing errors."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extract text from PDF using pdfplumber."""
    
    print(f"📄 Processing PDF: {pdf_path}")
    print("=" * 60)
    
    extracted_data = {
        "pages": [],
        "raw_text": "",
        "total_pages": 0
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_data["total_pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    page_text = clean_text_for_json(page_text)
                    
                page_data = {
                    "page_num": page_num,
                    "text": page_text,
                    "tables": [],
                    "lines": []
                }
                
                try:
                    tables = page.extract_tables()
                    if tables:
                        page_data["tables"] = [
                            {"rows": table, "page": page_num} 
                            for table in tables
                        ]
                except Exception as e:
                    print(f"Warning: Could not extract tables from page {page_num}: {e}")
                
                extracted_data["pages"].append(page_data)
                extracted_data["raw_text"] += f"\\n--- Page {page_num} ---\\n{page_text}"
        
        print(f"✓ Extracted text from {extracted_data['total_pages']} pages")
        return extracted_data
        
    except Exception as e:
        print(f"✗ Error extracting PDF: {e}")
        sys.exit(1)

def classify_with_enhanced_llm(pdf_text: str, kazanim_data: dict, page_num: int = None) -> dict:
    """Enhanced classification with kazanım mapping."""
    
    context = f"Page {page_num}" if page_num else "PDF content"
    cleaned_text = clean_text_for_json(pdf_text)
    
    # Prepare kazanım context for Claude
    available_subjects = [s for s in kazanim_data["subjects"] if s and s != "Unknown"]
    kazanim_examples = []
    
    for subject in available_subjects:
        if subject in kazanim_data["by_subject"]:
            # Take first 3 kazanımlar as examples
            examples = kazanim_data["by_subject"][subject][:3]
            for ex in examples:
                kazanim_examples.append(f"  - {ex.get('code', 'N/A')}: {ex.get('description', 'N/A')[:100]}...")
    
    kazanim_context = "\\n".join(kazanim_examples[:15])  # Limit to prevent token overflow
    
    prompt = f"""You are an expert at parsing LGS (Turkish standardized test) exam papers and mapping questions to curriculum learning outcomes (kazanımlar).

AVAILABLE SUBJECTS: {', '.join(available_subjects)}

SAMPLE LEARNING OUTCOMES (KAZANIMLAR):
{kazanim_context}

TEXT TO ANALYZE:
{cleaned_text}

INSTRUCTIONS:
1. Identify all questions (numbered or bulleted items asking for answers)
2. For each question, extract:
   - The question stem (the actual question text)
   - All 4 answer options (A, B, C, D)
   - The subject (from available subjects list)
   - The topic/unit
   - Match to the most appropriate kazanım code if possible

3. IGNORE:
   - Answer keys (lines starting with "Cevap" or "Answer Key")
   - Instructions (lines like "Bu testte X soru vardır")
   - Headers and footers
   - Blank lines or page numbers

4. RETURN FORMAT:
   {{
     "questions": [
       {{
         "number": 1,
         "stem": "Question text here...",
         "options": [
           {{"label": "A", "text": "Option A text"}},
           {{"label": "B", "text": "Option B text"}},
           {{"label": "C", "text": "Option C text"}},
           {{"label": "D", "text": "Option D text"}}
         ],
         "correct_answer": "B",
         "subject": "Matematik",
         "topic": "Çokgenler",
         "kazanim_code": "M.8.3.1.1",
         "confidence": 0.95
       }}
     ],
     "confidence": 0.95,
     "notes": "Any notes about parsing quality"
   }}

5. CONFIDENCE SCORING:
   - 1.0 = Perfect extraction, clear structure, definite kazanım match
   - 0.8+ = Good extraction, likely kazanım match
   - 0.6-0.8 = Moderate extraction, uncertain kazanım match
   - <0.6 = Poor extraction, no clear kazanım match

CRITICAL: Return ONLY valid JSON, no markdown formatting, no code blocks, no extra text.
Your response must start with {{ and end with }}."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text
        
        # Parse JSON response with better error handling
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Raw response: {response_text[:300]}...")
            
            try:
                json_match = re.search(r'```json\\s*(\\{.*?\\})\\s*```', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return result
                    
                json_match = re.search(r'\\{[^{}]*"questions"[^{}]*\\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                    
                print(f"✗ Could not extract valid JSON from Claude response")
                return {"questions": [], "confidence": 0}
                
            except json.JSONDecodeError as e2:
                print(f"✗ JSON extraction also failed: {e2}")
                return {"questions": [], "confidence": 0}
                
    except Exception as e:
        print(f"✗ Error calling Claude API: {e}")
        return {"questions": [], "confidence": 0}

def main():
    """Main function to parse PDF with kazanım mapping."""
    
    if len(sys.argv) != 4:
        print("Usage: python extract_pdf_with_kazanim.py <input_pdf> <kazanim_jsonl> <output_jsonl>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    kazanim_file = sys.argv[2] 
    output_jsonl = sys.argv[3]
    
    # Check if API key is available
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("✗ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Load kazanımlar
    print("1️⃣ Loading kazanımlar...")
    kazanim_data = load_kazanimlar(kazanim_file)
    
    # Extract text from PDF
    print("2️⃣ Extracting text from PDF...")
    extracted_data = extract_text_from_pdf(input_pdf)
    
    # Process each page with enhanced Claude
    print("3️⃣ Classifying questions with kazanım mapping...")
    all_questions = []
    total_confidence = 0
    processed_pages = 0
    
    for page_data in extracted_data["pages"]:
        page_num = page_data["page_num"]
        page_text = page_data["text"]
        
        if not page_text or len(page_text.strip()) < 50:
            print(f"   ⊘ Page {page_num}: Too short, skipping")
            continue
            
        print(f"   ⏳ Processing page {page_num}...")
        
        result = classify_with_enhanced_llm(page_text, kazanim_data, page_num)
        
        if result and result.get("questions"):
            questions = result["questions"]
            confidence = result.get("confidence", 0)
            
            print(f"   ✓ Found {len(questions)} questions (confidence: {confidence * 100}%)")
            
            # Add page number to each question
            for q in questions:
                q["page"] = page_num
            
            all_questions.extend(questions)
            total_confidence += confidence
            processed_pages += 1
        else:
            print(f"   ⊘ Page {page_num}: No questions found")
    
    # Save extracted questions
    print("4️⃣ Saving enhanced questions...")
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for question in all_questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    # Print summary
    avg_confidence = total_confidence / max(processed_pages, 1) * 100
    kazanim_mapped = sum(1 for q in all_questions if q.get('kazanim_code'))
    
    print("\n" + "=" * 60)
    print("📊 ENHANCED EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total pages: {extracted_data['total_pages']}")
    print(f"Pages processed: {processed_pages}")
    print(f"Questions found: {len(all_questions)}")
    print(f"Kazanım mapped: {kazanim_mapped}/{len(all_questions)} ({kazanim_mapped/max(len(all_questions),1)*100:.1f}%)")
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Output file: {output_jsonl}")
    
    if all_questions:
        sample = all_questions[0]
        print(f"\n✓ Sample question:")
        print(f"  Stem: {sample.get('stem', 'N/A')[:100]}...")
        print(f"  Subject: {sample.get('subject', 'N/A')}")
        print(f"  Kazanım: {sample.get('kazanim_code', 'Not mapped')}")
        print(f"  Options: {len(sample.get('options', []))} / 4")
        
        print(f"\n✅ Successfully extracted {len(all_questions)} questions with kazanım mapping!")
    else:
        print(f"\n⚠️  No questions were extracted. Check the PDF content and try again.")

if __name__ == "__main__":
    main()