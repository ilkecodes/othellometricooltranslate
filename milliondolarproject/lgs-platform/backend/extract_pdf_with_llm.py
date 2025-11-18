#!/usr/bin/env python3
"""
Hybrid PDF Parser: pdfplumber + Claude LLM

Extracts text from PDFs using pdfplumber, then uses Claude to:
1. Classify text as questions, answers, or metadata
2. Identify subjects and topics
3. Structure questions with options
4. Validate and clean data
"""

import json
import os
import sys
import re
from pathlib import Path
import pdfplumber
import anthropic

def clean_text_for_json(text: str) -> str:
    """Clean text to prevent JSON parsing errors."""
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extract text from PDF using pdfplumber with position info."""
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
                # Clean the text to prevent JSON parsing errors
                if page_text:
                    page_text = clean_text_for_json(page_text)
                    
                page_data = {
                    "page_num": page_num,
                    "text": page_text,
                    "tables": [],
                    "lines": []
                }
                
                # Try to extract tables
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
                extracted_data["raw_text"] += f"\n--- Page {page_num} ---\n{page_text}"
        
        print(f"✓ Extracted text from {extracted_data['total_pages']} pages")
        return extracted_data
        
    except Exception as e:
        print(f"✗ Error extracting PDF: {e}")
        sys.exit(1)

def classify_with_llm(pdf_text: str, page_num: int = None) -> list:
    """Use Claude to classify and structure questions from raw text."""
    
    context = f"Page {page_num}" if page_num else "PDF content"
    
    # Clean the input text
    cleaned_text = clean_text_for_json(pdf_text)
    
    prompt = f"""You are an expert at parsing LGS (Turkish standardized test) exam papers.

Your task is to analyze the following text and extract structured questions with answers.

TEXT TO ANALYZE:
{cleaned_text}

INSTRUCTIONS:
1. Identify all questions (numbered or bulleted items asking for answers)
2. For each question, extract:
   - The question stem (the actual question text)
   - All 4 answer options (A, B, C, D)
   - Which option is correct
   - The subject (Türkçe, Matematik, Fen, Sosyal, Din, İngilizce)
   - The topic/unit

3. IGNORE:
   - Answer keys (lines starting with "Cevap" or "Answer Key")
   - Instructions (lines like "Bu testte X soru vardır")
   - Headers and footers
   - Blank lines or page numbers
   - Lines that are obviously not questions

4. RETURN FORMAT:
   Return a JSON array with this structure:
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
         "subject": "Türkçe",
         "topic": "Okuma Anlama"
       }}
     ],
     "confidence": 0.95,
     "notes": "Any notes about parsing quality"
   }}

5. CONFIDENCE SCORING:
   - 1.0 = Perfect extraction, clear structure
   - 0.8+ = Good extraction, minor issues
   - 0.6-0.8 = Moderate extraction, some uncertainty
   - <0.6 = Poor extraction, many issues

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
            # First try direct JSON parsing
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Raw response: {response_text[:300]}...")
            
            # Try to extract just the JSON part
            try:
                # Look for JSON blocks between ```json and ```
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return result
                    
                # Look for any JSON object
                json_match = re.search(r'\{[^{}]*"questions"[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                    
                # If nothing works, return empty result
                print(f"✗ Could not extract valid JSON from Claude response")
                return {"questions": [], "confidence": 0}
                
            except json.JSONDecodeError as e2:
                print(f"✗ JSON extraction also failed: {e2}")
                return {"questions": [], "confidence": 0}
                
    except Exception as e:
        print(f"✗ Error calling Claude API: {e}")
        sys.exit(1)

def process_pdf_smart(pdf_path: str, output_file: str = "extracted_questions.jsonl") -> int:
    """
    Process PDF: extract text -> classify with LLM -> save to JSONL
    """
    print(f"\n📄 Processing PDF: {pdf_path}")
    print("=" * 60)
    
    # Step 1: Extract text
    print("\n1️⃣ Extracting text from PDF...")
    extracted_data = extract_text_from_pdf(pdf_path)
    
    # Step 2: Process with Claude
    print("\n2️⃣ Classifying questions with Claude LLM...")
    all_questions = []
    total_confidence = 0
    pages_processed = 0
    
    for page in extracted_data["pages"]:
        page_num = page["page_num"]
        page_text = page["text"]
        
        # Skip mostly empty pages
        if len(page_text.strip()) < 100:
            print(f"   ⊘ Page {page_num}: Too short, skipping")
            continue
        
        print(f"   ⏳ Processing page {page_num}...")
        result = classify_with_llm(page_text, page_num)
        
        if result.get("questions"):
            questions = result["questions"]
            confidence = result.get("confidence", 0)
            all_questions.extend(questions)
            total_confidence += confidence
            pages_processed += 1
            print(f"   ✓ Found {len(questions)} questions (confidence: {confidence:.1%})")
    
    # Step 3: Save to JSONL
    print(f"\n3️⃣ Saving extracted questions...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for q in all_questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total pages: {extracted_data['total_pages']}")
    print(f"Pages processed: {pages_processed}")
    print(f"Questions found: {len(all_questions)}")
    avg_confidence = (total_confidence / pages_processed * 100) if pages_processed > 0 else 0
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Output file: {output_file}")
    
    if len(all_questions) > 0:
        print(f"\n✓ Sample question:")
        q = all_questions[0]
        print(f"  Stem: {q.get('stem', 'N/A')[:80]}...")
        print(f"  Subject: {q.get('subject', 'N/A')}")
        print(f"  Options: {len(q.get('options', []))} / 4")
    
    return len(all_questions)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_with_llm.py <pdf_path> [output_file]")
        print("\nExample:")
        print("  python extract_pdf_with_llm.py sozel.pdf extracted_questions.jsonl")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "extracted_questions.jsonl"
    
    if not os.path.exists(pdf_path):
        print(f"✗ PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("✗ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    question_count = process_pdf_smart(pdf_path, output_file)
    
    if question_count == 0:
        print("\n⚠️  No questions extracted. Check PDF format and content.")
        sys.exit(1)
    
    print(f"\n✅ Successfully extracted {question_count} questions!")
