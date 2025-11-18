# Turkish PDF Question Parser & Seeder

This directory contains tools to parse Turkish exam PDFs and seed them into the LGS platform database.

## Files

- **`parse_turkish_pdf.py`** - Standalone PDF parser
  - Extracts all 20 Türkçe questions from the exam PDF
  - Cleans stem text and options
  - Applies official answer key from last page
  - Returns structured question dicts

- **`seed_questions_sql.py`** - Raw SQL seeder (no ORM issues)
  - Seeds curriculum structure (subjects, units, topics, learning outcomes)
  - Seeds questions and options in bulk
  - Uses direct psycopg2 connections

- **`seed_turkish_pdf.py`** - Integrated workflow
  - Combines parser + seeder
  - Interactive topic/difficulty mapping
  - Shows parsed questions before seeding
  - Confirms action before writing to database

## Quick Start

### 1. Place PDF in backend directory
```bash
cp /path/to/2025sozelbolum.pdf backend/
```

### 2. Run the integrated seeder
```bash
cd backend
docker-compose exec -T backend python seed_turkish_pdf.py
```

This will:
- Parse the PDF
- Show all 20 questions with correct answers marked
- Map questions to appropriate topics
- Ask for confirmation before seeding

### 3. Verify seeding
```bash
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "SELECT COUNT(*) FROM questions;"
```

## Advanced Usage

### Customize Topic Mapping

Edit `seed_turkish_pdf.py` to adjust `TOPIC_MAPPING`:

```python
TOPIC_MAPPING = {
    1: "Okuma Anlama Konusu 1",  # Q1 → Reading 1
    2: "Okuma Anlama Konusu 1",  # Q2 → Reading 1
    # ...
    15: "Yazın Konusu 1",        # Q15 → Literature 1
}
```

### Customize Difficulty

Edit `DIFFICULTY_MAPPING` in `seed_turkish_pdf.py`:

```python
DIFFICULTY_MAPPING = {
    1: "EASY",
    15: "HARD",
    20: "VERY_HARD",
}
```

### Use Parser Standalone

```python
from parse_turkish_pdf import build_turkish_questions

questions = build_turkish_questions("2025sozelbolum.pdf")

# Modify questions as needed
for q in questions:
    q["topic_name"] = "Custom Topic"
    q["difficulty"] = "HARD"

# Then seed manually
from seed_questions_sql import seed_questions
seed_questions(questions)
```

### Test Parser Without Seeding

```bash
docker-compose exec -T backend python parse_turkish_pdf.py
```

This will:
- Parse the PDF
- Show all 20 questions with correct answers marked (✅)
- NOT modify the database

## Question Schema

Each parsed question has this structure:

```python
{
    "subject_code": "TURKISH",
    "topic_name": "Türkçe Konusu 1",
    "difficulty": "MEDIUM",
    "stem_text": "Full question text with proper cleaning",
    "estimated_time_seconds": 90,
    "options": [
        {
            "label": "A",
            "text": "Option A text",
            "is_correct": True  # From official answer key
        },
        # B, C, D...
    ]
}
```

## Troubleshooting

### PDF Not Found
```
❌ Error: 2025sozelbolum.pdf not found
   Please place the PDF file in the backend directory
```
**Solution:** Copy the PDF to the `backend/` directory

### Answer Key Not Complete
```
ValueError: Expected 20 answers, but only found 15
```
**Solution:** PDF must have answer key on last page with format like:
```
1.  A
2.  B
3.  C
...
```

### Database Connection Error
```
psycopg2.OperationalError: could not translate host name "db" to address
```
**Solution:** Ensure Docker containers are running:
```bash
docker-compose up -d
docker-compose ps
```

### Topic Not Found
```
⚠️  Topic Türkçe Konusu 1 not found, skipping question
```
**Solution:** Verify curriculum was seeded first:
```bash
docker-compose exec -T backend python seed_questions_sql.py
```

Or update `TOPIC_MAPPING` to match existing topics:
```bash
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "SELECT name FROM topics WHERE name LIKE 'Türkçe%';"
```

## Flow Diagram

```
PDF File
   ↓
parse_turkish_pdf.py
   ├─ extract_turkish_block() → clean text
   ├─ find_question_chunks() → 20 questions
   ├─ parse_question_chunk() → Q#, stem, options
   ├─ extract_answer_key() → correct answers
   └─ build_turkish_questions() → structured dicts
   ↓
seed_turkish_pdf.py (interactive)
   ├─ Shows parsed questions
   ├─ Maps to topics/difficulty
   ├─ Asks for confirmation
   └─ Calls seed_questions()
   ↓
seed_questions_sql.py
   ├─ Connects to PostgreSQL
   ├─ Validates relationships
   ├─ Inserts questions + options
   └─ Commits transaction
   ↓
Database
   ├─ questions table (20 rows)
   ├─ question_options table (80 rows)
   └─ linked to curriculum
```

## Notes

- **Q16 Special Case:** If Q16 has no text options (only visuals), parser creates placeholder options (Görsel A/B/C/D)
- **Encoding:** All Turkish characters (ç, ğ, ı, ö, ş, ü, etc.) are properly handled
- **Hyphenation:** Words split across lines (e.g., "yapıl-\nması") are rejoined
- **Page Numbers:** Stray page/line numbers in options are removed
- **Answer Key:** Uses official booklet answer key from last page (not subject to student error)

## Dependencies

- `pdfplumber` - PDF text extraction
- `psycopg2` - PostgreSQL connection
- `pydantic-settings` - Config management (already in requirements.txt)

All are included in `backend/requirements.txt`
