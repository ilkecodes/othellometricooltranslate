#!/usr/bin/env python3
"""
Enhanced Kazanım Extractor with Special Character Support
Re-extracts kazanımlar with better Unicode and special character handling
"""

import sys
import json
import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Any
from anthropic import Anthropic
import os

def extract_text_with_special_chars(pdf_path: str) -> Dict[int, str]:
    """Extract text from PDF with better Unicode handling"""
    pages_text = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📄 Re-processing PDF with special char support: {pdf_path}")
        print(f"📊 Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                # Extract with different methods to catch special chars
                text = page.extract_text()
                
                # Try to extract tables as well for structured data
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row:
                                text += "\n" + " ".join([cell for cell in row if cell])
                
                if text and len(text.strip()) > 50:
                    # Clean and normalize Unicode
                    text = text.strip()
                    # Preserve mathematical symbols
                    text = text.replace('', '√')  # Square root if corrupted
                    text = text.replace('²', '²')  # Superscript 2
                    text = text.replace('³', '³')  # Superscript 3
                    text = text.replace('≥', '≥')  # Greater than or equal
                    text = text.replace('≤', '≤')  # Less than or equal
                    text = text.replace('±', '±')  # Plus minus
                    
                    pages_text[page_num] = text
                    print(f"✓ Page {page_num}: {len(text)} characters (special chars preserved)")
                else:
                    print(f"⊘ Page {page_num}: Too short, skipping")
            except Exception as e:
                print(f"✗ Error on page {page_num}: {e}")
                
    return pages_text

def enhanced_kazanim_extraction(page_text: str, page_num: int) -> Dict[str, Any]:
    """Enhanced kazanım extraction with better subject detection"""
    
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = f"""Bu sayfa 8. sınıf kazanımları içeriyor. BÜTÜN KONULARI ve kazanımları dikkatli şekilde çıkar.

ÖZEL DİKKAT:
1. TÜM LGS KONULARINI ara: Türkçe, Matematik, Fen Bilimleri, Sosyal Bilgiler, İnkılap Tarihi, Din Kültürü, İngilizce
2. Özel karakterleri koru: √, ², ³, ±, ≥, ≤ gibi matematik sembolleri
3. Her kazanımın tam kodunu çıkar (M.8.1.1.1 formatında)
4. Konu başlıklarını ve alt başlıkları yakala

Sayfa İçeriği:
{page_text}

JSON formatında çıkar:
{{
  "page_number": {page_num},
  "subjects_found": ["Matematik", "Fen Bilimleri", "vb..."],
  "kazanimlar": [
    {{
      "subject": "Matematik",
      "unit": "Sayılar ve İşlemler", 
      "topic": "Çarpanlar ve Katlar",
      "code": "M.8.1.1.1",
      "description": "Verilen pozitif tam sayıların pozitif tam sayı çarpanlarını bulur, pozitif tam sayıların pozitif tam sayı çarpanlarını üslü ifadelerin çarpımı şeklinde yazar.",
      "grade": "8",
      "notes": "Bir pozitif tam sayının asal çarpanlarını bulmaya yönelik çalışmalara da yer verilir."
    }}
  ],
  "confidence": 90
}}

MUTLAKA TÜM KONULARI VE ÖZEL KARAKTERLERİ ÇIKAR!"""

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
        print("Usage: python enhanced_kazanim_extractor.py <input_pdf> <output_jsonl>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not Path(pdf_path).exists():
        print(f"✗ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("📚 ENHANCED KAZANIM EXTRACTION WITH SPECIAL CHARACTERS")
    print("=" * 70)
    
    # Step 1: Extract text with special character support
    print("\n1️⃣ Extracting text with Unicode support...")
    pages_text = extract_text_with_special_chars(pdf_path)
    
    if not pages_text:
        print("✗ No readable content found in PDF")
        sys.exit(1)
    
    print(f"✓ Extracted text from {len(pages_text)} pages with special characters")
    
    # Step 2: Enhanced kazanım extraction
    print("\n2️⃣ Enhanced kazanım extraction...")
    all_kazanimlar = []
    all_subjects = set()
    successful_pages = 0
    total_confidence = 0
    
    for page_num, text in pages_text.items():
        print(f"   ⏳ Processing page {page_num}...")
        
        extraction = enhanced_kazanim_extraction(text, page_num)
        confidence = extraction.get('confidence', 0)
        
        if confidence > 50:
            print(f"   ✓ Page {page_num}: {confidence}% confidence")
            successful_pages += 1
            total_confidence += confidence
            
            # Extract kazanımlar
            kazanimlar = extraction.get('kazanimlar', [])
            all_kazanimlar.extend(kazanimlar)
            
            # Track subjects
            subjects_found = extraction.get('subjects_found', [])
            all_subjects.update(subjects_found)
            
            print(f"      📚 Found {len(kazanimlar)} kazanımlar, subjects: {subjects_found}")
        else:
            print(f"   ⊘ Page {page_num}: Low confidence ({confidence}%), skipping")
    
    # Step 3: Save enhanced results
    print("\n3️⃣ Saving enhanced kazanımlar...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for kazanim in all_kazanimlar:
            json.dump(kazanim, f, ensure_ascii=False)
            f.write('\n')
    
    avg_confidence = total_confidence / successful_pages if successful_pages > 0 else 0
    
    # Display summary
    print("\n" + "=" * 70)
    print("📊 ENHANCED EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Source PDF: {pdf_path}")
    print(f"Pages processed: {len(pages_text)}")
    print(f"Successful extractions: {successful_pages}")
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Total kazanımlar extracted: {len(all_kazanimlar)}")
    print(f"Subjects found: {len(all_subjects)}")
    
    # Subject breakdown
    subject_counts = {}
    for kazanim in all_kazanimlar:
        subject = kazanim.get('subject', 'Unknown')
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    print(f"\n📚 Subject Distribution:")
    for subject, count in sorted(subject_counts.items()):
        print(f"   {subject}: {count} kazanımlar")
    
    # Check for LGS subjects
    lgs_subjects = {'Türkçe', 'Matematik', 'Fen Bilimleri', 'Sosyal Bilgiler', 'İnkılap Tarihi', 'Din Kültürü', 'İngilizce'}
    found_lgs = set(all_subjects) & lgs_subjects
    missing_lgs = lgs_subjects - set(all_subjects)
    
    print(f"\n🎯 LGS Subject Coverage:")
    print(f"   Found: {sorted(found_lgs)}")
    if missing_lgs:
        print(f"   Missing: {sorted(missing_lgs)}")
    else:
        print(f"   ✅ All LGS subjects covered!")
    
    print(f"\nOutput file: {output_path}")
    print("✅ Enhanced extraction completed successfully!")

if __name__ == "__main__":
    main()