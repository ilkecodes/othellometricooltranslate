#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quick Test: Extract LGS Questions from PDF and Preview as JSON

This script:
1. Extracts questions from a PDF
2. Shows preview in JSON format
3. Optionally saves to JSONL file

Usage (offline):
    python test_extract.py "2025sozelbolum.pdf"
    
With Docker:
    docker-compose exec -T backend python test_extract.py "2025sozelbolum.pdf"
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any

from PyPDF2 import PdfReader


def read_pdf_text(pdf_path: Path) -> str:
    """PDF'in tüm sayfalarından metni alır."""
    reader = PdfReader(str(pdf_path))
    chunks = []
    for i, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        # Whitespace normalizasyonu
        txt = re.sub(r"\s+", " ", txt)
        chunks.append(txt.strip())
        print(f"  ✓ Sayfa {i+1} okundu ({len(txt)} karakter)")
    
    full_text = " ".join(chunks)
    print(f"  ✓ Toplam: {len(full_text)} karakter\n")
    return full_text


def split_into_question_blocks(full_text: str) -> List[Dict[str, Any]]:
    """Soruları bölüklere ayırır."""
    QUESTION_START_RE = re.compile(r"(?:^|\s)(\d{1,2})\.\s")
    blocks = []
    matches = list(QUESTION_START_RE.finditer(full_text))
    
    print(f"📌 {len(matches)} soru başlangıcı bulundu\n")

    for i, m in enumerate(matches):
        q_number = int(m.group(1))
        start = m.start(1)
        end = matches[i + 1].start(1) if i + 1 < len(matches) else len(full_text)
        
        block_text = full_text[start:end].strip()
        blocks.append({"number": q_number, "raw": block_text})

    return blocks


def parse_choices(block_text: str) -> Dict[str, Any]:
    """Soru kökü ve seçenekleri çıkarır."""
    CHOICE_SPLIT_RE = re.compile(r"\s([A-D])\)\s")
    
    block_text = block_text.lstrip()
    block_text = re.sub(r"^\d{1,2}\.\s*", "", block_text, count=1)

    parts = CHOICE_SPLIT_RE.split(block_text)

    if len(parts) < 3:
        return {"stem": block_text.strip(), "choices": []}

    stem = parts[0].strip()
    choices = []

    for label, text in zip(parts[1::2], parts[2::2]):
        choices.append({"label": label, "text": text.strip()})

    return {"stem": stem, "choices": choices}


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_extract.py <pdf_file> [--save output.jsonl]")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    save_output = "--save" in sys.argv

    if not pdf_path.exists():
        print(f"❌ PDF bulunamadı: {pdf_path}")
        sys.exit(1)

    print(f"📖 PDF okunuyor: {pdf_path}\n")
    full_text = read_pdf_text(pdf_path)

    print("🔍 Sorular ayrıştırılıyor...")
    blocks = split_into_question_blocks(full_text)

    print("📝 Soruların yapısı analiz ediliyor...\n")
    questions = []
    for b in blocks:
        parsed = parse_choices(b["raw"])
        q = {
            "number": b["number"],
            "stem": parsed["stem"],
            "choices": parsed["choices"]
        }
        questions.append(q)

    questions.sort(key=lambda x: x["number"])

    # Show summary
    print(f"✅ {len(questions)} soru başarıyla çıkarıldı!\n")

    print("=" * 80)
    print("📋 SORU ÖNİZLEMESİ")
    print("=" * 80 + "\n")

    # Show first 3 as full, rest as summary
    for i, q in enumerate(questions):
        if i < 3:
            print(f"Q{q['number']} ({len(q['stem'].split())} sözcük):")
            print(f"  {q['stem'][:100]}{'...' if len(q['stem']) > 100 else ''}\n")
            for choice in q["choices"]:
                print(f"  {choice['label']}) {choice['text'][:70]}{'...' if len(choice['text']) > 70 else ''}")
            print()
        else:
            if i == 3:
                print(f"Q{q['number']} Q{questions[-1]['number']}: (toplam {len(questions)} soru)\n")

    # Statistics
    print("\n" + "=" * 80)
    print("📊 İSTATİSTİKLER")
    print("=" * 80)

    total_words = sum(len(q["stem"].split()) for q in questions)
    avg_stem_length = total_words // len(questions) if questions else 0

    print(f"  Toplam soru: {len(questions)}")
    print(f"  Ortalama soru kökü: {avg_stem_length} sözcük")
    print(f"  Toplam seçenek: {sum(len(q['choices']) for q in questions)}")

    # Check for complete questions
    complete = sum(1 for q in questions if len(q["choices"]) >= 4)
    print(f"  Tam 4 seçenekli sorular: {complete}/{len(questions)}")

    if save_output:
        output_file = "extracted_questions.jsonl"
        if "--save" in sys.argv:
            idx = sys.argv.index("--save")
            if idx + 1 < len(sys.argv):
                output_file = sys.argv[idx + 1]

        with open(output_file, "w", encoding="utf-8") as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")

        print(f"\n✅ Kaydedildi: {output_file}")
    
    else:
        print(f"\n💡 JSONL olarak kaydetmek için:")
        print(f"   python test_extract.py '{pdf_path}' --save questions.jsonl")


if __name__ == "__main__":
    main()
