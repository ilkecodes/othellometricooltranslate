#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LGS PDF -> Questions JSONL Extractor

Extracts questions from LGS exam PDFs and outputs them as JSONL format.

Usage:
    python extract_lgs_questions.py input.pdf output.jsonl
    
Example:
    python extract_lgs_questions.py "2025sozelbolum.pdf" "lgs_2025_sozel.jsonl"

Output format (JSONL - one JSON object per line):
{
  "number": 1,
  "stem": "Question text...",
  "choices": [
    {"label": "A", "text": "Option A text"},
    {"label": "B", "text": "Option B text"},
    {"label": "C", "text": "Option C text"},
    {"label": "D", "text": "Option D text"}
  ]
}
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any

from PyPDF2 import PdfReader


QUESTION_START_RE = re.compile(r"(?:^|\s)(\d{1,2})\.\s")  # " 1. " , "10. " vb.
CHOICE_SPLIT_RE = re.compile(r"\s([A-D])\)\s")            # " A) ", " B) " vb.


def read_pdf_text(pdf_path: Path) -> str:
    """PDF'in tüm sayfalarından metni alıp tek bir stringe bağlar."""
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        # whitespace normalizasyonu
        txt = re.sub(r"\s+", " ", txt)
        chunks.append(txt.strip())
    full_text = " ".join(chunks)
    return full_text


def split_into_question_blocks(full_text: str) -> List[Dict[str, Any]]:
    """
    Tüm metin içinden '1.', '2.' gibi soru başlangıçlarını bulup
    her biri için bir blok oluşturur.
    """
    blocks = []
    matches = list(QUESTION_START_RE.finditer(full_text))

    for i, m in enumerate(matches):
        q_number = int(m.group(1))
        start = m.start(1)

        if i + 1 < len(matches):
            end = matches[i + 1].start(1)
        else:
            end = len(full_text)

        block_text = full_text[start:end].strip()
        blocks.append({"number": q_number, "raw": block_text})

    return blocks


def parse_choices_from_block(block_text: str) -> Dict[str, Any]:
    """
    Bir soru bloğu içinden:
      - soru kökü
      - A/B/C/D şıkları
    çıkarır.

    Beklenen form: "1. ... A) ... B) ... C) ... D) ..."
    """
    # "1. " kısmını at
    block_text = block_text.lstrip()
    block_text = re.sub(r"^\d{1,2}\.\s*", "", block_text, count=1)

    # Şıklar için split
    parts = CHOICE_SPLIT_RE.split(block_text)

    # parts şöyle bir yapı olur:
    # [ "soru kökü ...", "A", "A şıkkı metni ...", "B", "B şıkkı metni ...", ... ]

    if len(parts) < 3:
        # Şık bulunamazsa, soru kökü olarak bırak
        return {
            "stem": block_text.strip(),
            "choices": []
        }

    stem = parts[0].strip()
    choices = []

    label_text_pairs = list(zip(parts[1::2], parts[2::2]))  # ("A", "metin"), ("B", "metin"), ...

    for label, text in label_text_pairs:
        choices.append({
            "label": label,
            "text": text.strip()
        })

    return {
        "stem": stem,
        "choices": choices
    }


def extract_questions(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    PDF'ten soru objeleri listesi çıkarır:
    {
      "number": 1,
      "stem": "...",
      "choices": [
        {"label": "A", "text": "..."},
        ...
      ]
    }
    """
    full_text = read_pdf_text(pdf_path)
    blocks = split_into_question_blocks(full_text)

    questions = []
    for b in blocks:
        parsed = parse_choices_from_block(b["raw"])
        q = {
            "number": b["number"],
            "stem": parsed["stem"],
            "choices": parsed["choices"]
        }
        questions.append(q)

    # Soru numarasına göre sırala
    questions.sort(key=lambda x: x["number"])
    return questions


def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_lgs_questions.py input.pdf output.jsonl")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"📖 Reading PDF: {pdf_path}")
    questions = extract_questions(pdf_path)

    print(f"✅ Extracted {len(questions)} questions")
    
    with out_path.open("w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"✅ Saved to: {out_path}")
    
    # Preview first 3 questions
    print("\n📋 Preview (first 3 questions):")
    for q in questions[:3]:
        print(f"\n  Q{q['number']}: {q['stem'][:80]}...")
        for choice in q['choices']:
            print(f"    {choice['label']}) {choice['text'][:70]}...")


if __name__ == "__main__":
    main()
