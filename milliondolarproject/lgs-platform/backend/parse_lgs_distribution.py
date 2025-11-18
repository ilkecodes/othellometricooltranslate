#!/usr/bin/env python3
"""
LGS Topic Distribution Parser
Analyzes historical LGS exam question distribution by subjects and topics
"""

import sys
import json
import pdfplumber
from pathlib import Path
from typing import Dict, List, Any
from anthropic import Anthropic
import os

def extract_text_from_pdf(pdf_path: str) -> Dict[int, str]:
    """Extract text from PDF pages"""
    pages_text = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📄 Processing PDF: {pdf_path}")
        print(f"📊 Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                text = page.extract_text()
                if text and len(text.strip()) > 50:  # Only meaningful pages
                    pages_text[page_num] = text.strip()
                    print(f"✓ Page {page_num}: {len(text)} characters")
                else:
                    print(f"⊘ Page {page_num}: Too short, skipping")
            except Exception as e:
                print(f"✗ Error on page {page_num}: {e}")
                
    return pages_text

def analyze_distribution_with_llm(page_text: str, page_num: int) -> Dict[str, Any]:
    """Analyze LGS distribution data using Claude"""
    
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = f"""Analyze this LGS (Liselere Geçiş Sınavı) topic distribution page and extract structured data.

This document contains historical data about which topics appear on LGS exams and how frequently.

Please extract:
1. Subject areas (Türkçe, Matematik, Fen Bilimleri, etc.)
2. Topics/units within each subject
3. Question counts or percentages for different years
4. Any patterns or trends mentioned
5. Learning outcome codes (kazanım kodları) if present

Page Text:
{page_text}

Return a JSON response with this structure:
{{
  "page_number": {page_num},
  "subjects": [
    {{
      "name": "subject_name",
      "topics": [
        {{
          "name": "topic_name",
          "years_data": {{
            "2018": {{"questions": 3, "percentage": 15}},
            "2019": {{"questions": 2, "percentage": 10}}
          }},
          "kazanim_codes": ["T.8.1.1", "T.8.1.2"],
          "trends": "description of trends"
        }}
      ]
    }}
  ],
  "summary": "overall insights about distribution patterns",
  "confidence": 85
}}

Focus on extracting numerical data and clear patterns. If the page doesn't contain distribution data, return confidence: 0."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Clean up response
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        return json.loads(response_text)
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing failed on page {page_num}: {e}")
        return {"page_number": page_num, "confidence": 0, "error": str(e)}
    except Exception as e:
        print(f"✗ LLM analysis failed on page {page_num}: {e}")
        return {"page_number": page_num, "confidence": 0, "error": str(e)}

def main():
    if len(sys.argv) != 3:
        print("Usage: python parse_lgs_distribution.py <input_pdf> <output_json>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not Path(pdf_path).exists():
        print(f"✗ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 LGS TOPIC DISTRIBUTION ANALYSIS")
    print("=" * 50)
    
    # Step 1: Extract text from PDF
    print("\n1️⃣ Extracting text from PDF...")
    pages_text = extract_text_from_pdf(pdf_path)
    
    if not pages_text:
        print("✗ No readable content found in PDF")
        sys.exit(1)
    
    print(f"✓ Extracted text from {len(pages_text)} pages")
    
    # Step 2: Analyze each page for distribution data
    print("\n2️⃣ Analyzing distribution patterns...")
    all_analysis = []
    successful_pages = 0
    total_confidence = 0
    
    for page_num, text in pages_text.items():
        print(f"   ⏳ Analyzing page {page_num}...")
        
        analysis = analyze_distribution_with_llm(text, page_num)
        confidence = analysis.get('confidence', 0)
        
        if confidence > 50:
            print(f"   ✓ Page {page_num}: {confidence}% confidence")
            successful_pages += 1
            total_confidence += confidence
            all_analysis.append(analysis)
        else:
            print(f"   ⊘ Page {page_num}: Low confidence ({confidence}%), skipping")
    
    # Step 3: Compile results
    print("\n3️⃣ Compiling distribution analysis...")
    
    if successful_pages == 0:
        print("✗ No distribution data found")
        sys.exit(1)
    
    avg_confidence = total_confidence / successful_pages if successful_pages > 0 else 0
    
    # Aggregate subjects and topics
    compiled_data = {
        "source": pdf_path,
        "analysis_date": "2024-11-14",
        "pages_analyzed": len(pages_text),
        "successful_pages": successful_pages,
        "average_confidence": round(avg_confidence, 1),
        "subjects": {},
        "raw_analysis": all_analysis
    }
    
    # Merge subject data from all pages
    for analysis in all_analysis:
        for subject in analysis.get('subjects', []):
            subject_name = subject['name']
            if subject_name not in compiled_data['subjects']:
                compiled_data['subjects'][subject_name] = {
                    "topics": [],
                    "total_topics": 0,
                    "years_covered": set()
                }
            
            for topic in subject.get('topics', []):
                compiled_data['subjects'][subject_name]['topics'].append(topic)
                compiled_data['subjects'][subject_name]['total_topics'] += 1
                
                # Track years with data
                years_data = topic.get('years_data', {})
                compiled_data['subjects'][subject_name]['years_covered'].update(years_data.keys())
    
    # Convert sets to lists for JSON serialization
    for subject_data in compiled_data['subjects'].values():
        subject_data['years_covered'] = sorted(list(subject_data['years_covered']))
    
    # Step 4: Save results
    print("\n4️⃣ Saving analysis results...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(compiled_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("📊 LGS DISTRIBUTION ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Source PDF: {pdf_path}")
    print(f"Pages processed: {len(pages_text)}")
    print(f"Successful extractions: {successful_pages}")
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Subjects found: {len(compiled_data['subjects'])}")
    
    for subject, data in compiled_data['subjects'].items():
        print(f"  {subject}: {data['total_topics']} topics")
    
    print(f"Output file: {output_path}")
    print("\n✅ LGS distribution analysis completed successfully!")

if __name__ == "__main__":
    main()