#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LGS PDF Extraction Pipeline - Integration Tester

Tests the full pipeline:
1. PDF extraction
2. JSONL generation  
3. Database seeding

Usage:
    python test_integration.py "input.pdf"
"""

import sys
import json
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"\n{'='*80}")
    print(f"🔧 {description}")
    print(f"{'='*80}")
    print(f"$ {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def test_extraction_syntax():
    """Test Python scripts for syntax errors."""
    print(f"\n{'='*80}")
    print(f"✅ Checking syntax")
    print(f"{'='*80}\n")
    
    scripts = [
        "extract_lgs_questions.py",
        "seed_from_jsonl.py",
        "test_extract.py"
    ]
    
    for script in scripts:
        if Path(script).exists():
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", script],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✓ {script}")
            else:
                print(f"  ✗ {script}: {result.stderr}")
                return False
        else:
            print(f"  ✗ {script} not found")
            return False
    
    return True


def test_pipeline(pdf_file):
    """Test the full extraction pipeline."""
    
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_file}")
        return False
    
    # Test syntax first
    if not test_extraction_syntax():
        print("\n❌ Syntax errors found")
        return False
    
    print("\n✅ All scripts have valid syntax\n")
    
    # Step 1: Extract questions from PDF
    jsonl_file = pdf_path.stem + "_extracted.jsonl"
    
    print(f"\n{'='*80}")
    print(f"STEP 1: Extract questions from PDF")
    print(f"{'='*80}\n")
    
    extract_cmd = [
        sys.executable,
        "extract_lgs_questions.py",
        str(pdf_path),
        jsonl_file
    ]
    
    if not run_command(extract_cmd, "Running PDF extraction"):
        return False
    
    # Check JSONL was created
    if not Path(jsonl_file).exists():
        print(f"❌ JSONL file not created: {jsonl_file}")
        return False
    
    # Parse JSONL to check format
    print(f"\n{'='*80}")
    print(f"📊 Validating JSONL format")
    print(f"{'='*80}\n")
    
    questions = []
    try:
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    q = json.loads(line)
                    questions.append(q)
                    
                    # Validate structure
                    assert "number" in q, f"Missing 'number' in Q{line_num}"
                    assert "stem" in q, f"Missing 'stem' in Q{line_num}"
                    assert "choices" in q, f"Missing 'choices' in Q{line_num}"
                    assert len(q["choices"]) >= 4, f"Fewer than 4 choices in Q{q['number']}"
                    
                    for choice in q["choices"]:
                        assert "label" in choice, f"Missing 'label' in Q{q['number']}"
                        assert "text" in choice, f"Missing 'text' in Q{q['number']}"
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"❌ JSONL validation error: {e}")
        return False
    
    print(f"✅ Valid JSONL with {len(questions)} questions\n")
    
    # Show preview
    print(f"Preview of first question:")
    if questions:
        q = questions[0]
        print(f"  Q{q['number']}: {q['stem'][:100]}...")
        for choice in q['choices']:
            print(f"    {choice['label']}) {choice['text'][:60]}...")
    
    # Step 2: Show seeding command
    print(f"\n{'='*80}")
    print(f"STEP 2: Ready to seed to database")
    print(f"{'='*80}\n")
    
    seed_cmd = [
        sys.executable,
        "seed_from_jsonl.py",
        jsonl_file,
        "--auto-topic"
    ]
    
    print(f"Run this command to seed to database:")
    print(f"\n  {' '.join(seed_cmd)}")
    print(f"\n  Or in Docker:")
    print(f"  docker-compose exec -T backend {' '.join(seed_cmd)}")
    
    print(f"\n{'='*80}")
    print(f"✅ Pipeline test passed!")
    print(f"{'='*80}\n")
    
    print(f"Summary:")
    print(f"  PDF file: {pdf_file}")
    print(f"  JSONL file: {jsonl_file}")
    print(f"  Questions extracted: {len(questions)}")
    print(f"  Next step: Run seed command above to populate database")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_integration.py <pdf_file>")
        print("\nExample:")
        print("  python test_integration.py '2025sozelbolum.pdf'")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"LGS PDF Extraction Pipeline - Integration Tester")
    print(f"{'='*80}")
    
    success = test_pipeline(pdf_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
