"""
Integrated seeder script that:
1. Parses the 2025 Türkçe PDF exam
2. Adjusts topic mappings as needed
3. Seeds all 20 questions to the database

Usage:
    python seed_turkish_pdf.py [--pdf path/to/pdf] [--remap-topics]
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parse_turkish_pdf import build_turkish_questions
from seed_questions_sql import seed_questions


# Topic mapping: question numbers to topic names
# Adjust these to match your curriculum structure
TOPIC_MAPPING = {
    # Okuma Anlama (Reading Comprehension)
    1: "Okuma Anlama Konusu 1",
    2: "Okuma Anlama Konusu 1",
    3: "Okuma Anlama Konusu 2",
    4: "Okuma Anlama Konusu 2",
    5: "Okuma Anlama Konusu 3",
    
    # Sözcükte Anlam (Vocabulary/Word Meaning)
    6: "Dil Bilgisi Konusu 1",
    7: "Dil Bilgisi Konusu 1",
    8: "Dil Bilgisi Konusu 1",
    9: "Dil Bilgisi Konusu 2",
    10: "Dil Bilgisi Konusu 2",
    
    # Cümlede Anlam (Sentence Meaning)
    11: "Dil Bilgisi Konusu 2",
    12: "Dil Bilgisi Konusu 3",
    13: "Dil Bilgisi Konusu 3",
    14: "Dil Bilgisi Konusu 3",
    
    # Yazın (Literature)
    15: "Yazın Konusu 1",
    16: "Yazın Konusu 2",
    17: "Yazın Konusu 2",
    18: "Yazın Konusu 3",
    19: "Yazın Konusu 3",
    20: "Yazın Konusu 3",
}

# Optional: Difficulty adjustments by question
DIFFICULTY_MAPPING = {
    # Map question numbers to difficulty if needed
    # e.g., 1: "EASY", 20: "HARD"
}


def seed_turkish_pdf(pdf_path: str = "2025sozelbolum.pdf", remap_topics: bool = True):
    """
    Parse Turkish PDF and seed all 20 questions.
    
    Args:
        pdf_path: Path to the PDF file
        remap_topics: If True, apply TOPIC_MAPPING to distribute questions across topics
    """
    print(f"📖 Parsing PDF: {pdf_path}")
    
    try:
        # Parse the PDF
        questions = build_turkish_questions(pdf_path)
        print(f"✅ Successfully parsed {len(questions)} questions\n")
        
        if remap_topics:
            print("🔄 Applying topic mapping...")
            for i, q in enumerate(questions, start=1):
                if i in TOPIC_MAPPING:
                    old_topic = q["topic_name"]
                    q["topic_name"] = TOPIC_MAPPING[i]
                    print(f"  Q{i}: {old_topic} → {q['topic_name']}")
                
                if i in DIFFICULTY_MAPPING:
                    q["difficulty"] = DIFFICULTY_MAPPING[i]
            print()
        
        # Display parsed questions
        print("📋 Questions to be seeded:\n")
        for i, q in enumerate(questions, start=1):
            print(f"Q{i}: [{q['difficulty']}] {q['stem_text'][:80]}...")
            print(f"    Topic: {q['topic_name']}")
            for opt in q["options"]:
                flag = "✅" if opt["is_correct"] else "  "
                print(f"    {flag} {opt['label']}) {opt['text'][:70]}...")
            print()
        
        # Confirm before seeding
        response = input("Proceed with seeding? (yes/no): ").strip().lower()
        if response != "yes":
            print("❌ Seeding cancelled")
            return
        
        # Seed the questions
        print("\n🌱 Seeding questions to database...")
        seed_questions(questions)
        
        print("\n✅ All Turkish questions seeded successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: {pdf_path} not found")
        print("   Please place the PDF file in the backend directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    pdf_path = "2025sozelbolum.pdf"
    remap = True
    
    # Parse command line args
    if "--pdf" in sys.argv:
        idx = sys.argv.index("--pdf")
        if idx + 1 < len(sys.argv):
            pdf_path = sys.argv[idx + 1]
    
    if "--no-remap" in sys.argv:
        remap = False
    
    seed_turkish_pdf(pdf_path, remap_topics=remap)
