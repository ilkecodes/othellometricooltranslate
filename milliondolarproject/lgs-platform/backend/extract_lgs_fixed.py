#!/usr/bin/env python3
"""
Fixed LGS question extraction with proper subject detection.
This script extracts 50 real questions from the PDF:
- 20 Turkish (Türkçe)
- 10 Social Studies (Sosyal - T.C. İnkılap Tarihi ve Atatürkçülük)
- 10 Religion (Din - Din Kültürü ve Ahlak Bilgisi)
- 10 English (İngilizce - Yabancı Dil)
"""

import re
import json
from pathlib import Path
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def detect_subject(text_before_question):
    """Detect which subject a question belongs to based on headers."""
    text_upper = text_before_question.upper()
    
    # Check for subject headers in the text
    if "YABANCI DİL" in text_upper or "İNGİLİZCE" in text_upper:
        return "İngilizce"
    elif "DİN KÜLTÜRÜ" in text_upper or "DİN" in text_upper:
        return "Din"
    elif "T.C. İNKILAP" in text_upper or "TARİHİ" in text_upper or "ATATÜRK" in text_upper:
        return "Sosyal"
    elif "TÜRKÇE" in text_upper:
        return "Türkçe"
    return "Unknown"

def extract_questions(pdf_path, max_questions=50):
    """
    Extract questions from PDF with proper parsing.
    Returns a list of question dicts with subject classification.
    """
    text = extract_text_from_pdf(pdf_path)
    
    # Split by question numbers (1., 2., 3., etc.)
    # This is tricky because questions can span multiple lines
    # Strategy: find "Number. " patterns and extract until next question or section header
    
    questions = []
    current_subject = "Türkçe"  # Default subject
    
    # Split into potential question blocks
    lines = text.split('\n')
    current_q = None
    buffer = []
    
    for line in lines:
        # Detect subject changes from headers
        if any(s in line for s in ["TÜRKÇE", "İNKILAP TARİHİ", "DİN KÜLTÜRÜ", "YABANCI DİL", "İNGİLİZCE"]):
            current_subject = detect_subject(line)
            if buffer and current_q:
                # Save previous question
                current_q['stem'] = '\n'.join(buffer).strip()
                buffer = []
            continue
        
        # Look for question starts (number followed by dot and space)
        match = re.match(r'^(\d+)\.\s+(.+)', line)
        if match:
            # Save previous question if exists
            if current_q and buffer:
                current_q['stem'] = '\n'.join(buffer).strip()
                if len(current_q['choices']) == 4:
                    current_q['subject'] = current_subject
                    questions.append(current_q)
            
            # Start new question
            q_num = int(match.group(1))
            q_text = match.group(2)
            current_q = {
                'number': q_num,
                'stem': '',
                'choices': [],
                'subject': current_subject
            }
            buffer = [q_text]
        
        # Look for answer options (A), (B), (C), (D) or A. B. C. D.
        elif re.match(r'^\s*[A-D]\s*[.\)]\s*(.+)', line):
            if current_q:
                match = re.match(r'^\s*([A-D])\s*[.\)]\s*(.+)', line)
                if match:
                    label = match.group(1)
                    text_content = match.group(2).strip()
                    current_q['choices'].append({
                        'label': label,
                        'text': text_content
                    })
                    buffer = []  # Don't add option lines to stem
        
        # Regular line, add to buffer if we're in a question
        elif current_q and line.strip() and not re.match(r'^[A-D]\s*$', line):
            buffer.append(line)
    
    # Don't forget the last question
    if current_q and buffer:
        current_q['stem'] = '\n'.join(buffer).strip()
        if len(current_q['choices']) == 4:
            current_q['subject'] = current_subject
            questions.append(current_q)
    
    return questions[:max_questions]

def main():
    pdf_path = Path(__file__).parent / "2025sozelbolum.pdf"
    
    print(f"Extracting questions from {pdf_path}...")
    questions = extract_questions(str(pdf_path), max_questions=50)
    
    # Count by subject
    subject_counts = {}
    for q in questions:
        subj = q['subject']
        subject_counts[subj] = subject_counts.get(subj, 0) + 1
    
    print(f"\nExtracted {len(questions)} questions:")
    for subj, count in sorted(subject_counts.items()):
        print(f"  {subj}: {count}")
    
    # Save as JSONL
    output_path = Path(__file__).parent / "sozel_fixed.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for q in questions:
            record = {
                'number': q['number'],
                'stem': q['stem'],
                'choices': q['choices'],
                'subject': q['subject']
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"\nSaved to {output_path}")
    
    # Show first question
    if questions:
        print(f"\nFirst question example:")
        print(f"  Number: {questions[0]['number']}")
        print(f"  Subject: {questions[0]['subject']}")
        print(f"  Stem: {questions[0]['stem'][:100]}...")
        print(f"  Choices: {len(questions[0]['choices'])}")

if __name__ == "__main__":
    main()
