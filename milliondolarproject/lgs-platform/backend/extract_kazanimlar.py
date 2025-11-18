#!/usr/bin/env python3
"""
Kazanım Parser: Extract Turkish curriculum learning outcomes from PDF

Extracts learning outcomes with:
- Kazanım codes (M.8.1.1.1, etc.)
- Grade levels
- Subjects
- Descriptions
- Keywords/terms
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
    """Extract text from kazanım PDF using pdfplumber."""
    
    print(f"📄 Processing kazanım PDF: {pdf_path}")
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

def parse_kazanimlar_with_llm(pdf_text: str, page_num: int = None) -> list:
    """Use Claude to extract structured learning outcomes from raw text."""
    
    context = f"Page {page_num}" if page_num else "PDF content"
    
    # Clean the input text
    cleaned_text = clean_text_for_json(pdf_text)
    
    prompt = f"""You are an expert at parsing Turkish educational curriculum documents (kazanımlar).

Your task is to analyze the following text and extract structured learning outcomes.

TEXT TO ANALYZE:
{cleaned_text}

INSTRUCTIONS:
1. Identify all learning outcomes (kazanımlar) with codes like M.8.1.1.1, T.8.2.3.4, etc.
2. For each kazanım, extract:
   - The kazanım code (e.g., M.8.1.1.1)
   - Subject (Matematik, Türkçe, Fen Bilimleri, etc.)
   - Grade level (usually 7 or 8)
   - Main topic/unit title
   - Full description text
   - Any keywords or terms listed

3. IGNORE:
   - Page headers/footers
   - Table of contents entries
   - General explanatory text
   - Blank lines

4. RETURN FORMAT:
   Return a JSON array with this structure:
   {{
     "kazanimlar": [
       {{
         "code": "M.8.1.1.1",
         "subject": "Matematik", 
         "grade": 8,
         "topic": "Çarpanlar ve Katlar",
         "description": "Verilen pozitif tam sayıların pozitif tam sayı çarpanlarını bulur...",
         "terms": ["çarpan", "bölen", "pozitif tam sayı"],
         "page": {page_num}
       }}
     ],
     "confidence": 0.95,
     "notes": "Any notes about parsing quality"
   }}

5. CONFIDENCE SCORING:
   - 1.0 = Perfect extraction, all kazanımlar found
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
                json_match = re.search(r'\{[^{}]*"kazanimlar"[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                    
                # If nothing works, return empty result
                print(f"✗ Could not extract valid JSON from Claude response")
                return {"kazanimlar": [], "confidence": 0}
                
            except json.JSONDecodeError as e2:
                print(f"✗ JSON extraction also failed: {e2}")
                return {"kazanimlar": [], "confidence": 0}
                
    except Exception as e:
        print(f"✗ Error calling Claude API: {e}")
        return {"kazanimlar": [], "confidence": 0}

def main():
    """Main function to parse kazanım document."""
    
    if len(sys.argv) != 3:
        print("Usage: python extract_kazanimlar.py <input_pdf> <output_jsonl>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_jsonl = sys.argv[2]
    
    # Check if API key is available
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("✗ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Extract text from PDF
    print("1️⃣ Extracting text from kazanım PDF...")
    extracted_data = extract_text_from_pdf(input_pdf)
    
    # Process each page with Claude
    print("2️⃣ Extracting kazanımlar with Claude LLM...")
    all_kazanimlar = []
    total_confidence = 0
    processed_pages = 0
    
    for page_data in extracted_data["pages"]:
        page_num = page_data["page_num"]
        page_text = page_data["text"]
        
        if not page_text or len(page_text.strip()) < 50:
            print(f"   ⊘ Page {page_num}: Too short, skipping")
            continue
            
        print(f"   ⏳ Processing page {page_num}...")
        
        result = parse_kazanimlar_with_llm(page_text, page_num)
        
        if result and result.get("kazanimlar"):
            kazanimlar = result["kazanimlar"]
            confidence = result.get("confidence", 0)
            
            print(f"   ✓ Found {len(kazanimlar)} kazanımlar (confidence: {confidence * 100}%)")
            
            all_kazanimlar.extend(kazanimlar)
            total_confidence += confidence
            processed_pages += 1
        else:
            print(f"   ⊘ Page {page_num}: No kazanımlar found")
    
    # Save extracted kazanımlar
    print("3️⃣ Saving extracted kazanımlar...")
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for kazanim in all_kazanimlar:
            f.write(json.dumps(kazanim, ensure_ascii=False) + '\n')
    
    # Print summary
    avg_confidence = total_confidence / max(processed_pages, 1) * 100
    
    print("\n" + "=" * 60)
    print("📊 KAZANIM EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total pages: {extracted_data['total_pages']}")
    print(f"Pages processed: {processed_pages}")
    print(f"Kazanımlar found: {len(all_kazanimlar)}")
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Output file: {output_jsonl}")
    
    if all_kazanimlar:
        sample = all_kazanimlar[0]
        print(f"\n✓ Sample kazanım:")
        print(f"  Code: {sample.get('code', 'N/A')}")
        print(f"  Subject: {sample.get('subject', 'N/A')}")
        print(f"  Description: {sample.get('description', 'N/A')[:100]}...")
        
        print(f"\n✅ Successfully extracted {len(all_kazanimlar)} kazanımlar!")
    else:
        print(f"\n⚠️  No kazanımlar were extracted. Check the PDF content and try again.")

if __name__ == "__main__":
    main()