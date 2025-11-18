# Quick Integration Guide: PDF Parser → Database Seeder

## What Was Built

Three complementary scripts for parsing Turkish exam PDFs and seeding them:

1. **`parse_turkish_pdf.py`** - PDF extraction + cleaning
2. **`seed_questions_sql.py`** - Raw SQL database seeder (no ORM issues)
3. **`seed_turkish_pdf.py`** - Interactive workflow combining both

## Step-by-Step Usage

### Prerequisites
```bash
cd /Users/ilkeileri/milliondolarproject/lgs-platform

# Ensure containers are running
docker-compose up -d

# Verify containers healthy
docker-compose ps
```

### Step 1: Copy Your PDF
```bash
# Place the 2025 Türkçe exam PDF
cp /path/to/2025sozelbolum.pdf backend/
```

### Step 2: Install PDF Dependencies
```bash
docker-compose exec -T backend pip install -q pdfplumber==0.10.3
```

### Step 3: Test the Parser (Optional)
```bash
# See all 20 questions with correct answers marked
docker-compose exec -T backend python parse_turkish_pdf.py
```

Output:
```
✅ Parsed 20 Türkçe questions

Q1: Hiç tanımadığımız ancak görür görmez içimizin ısındığı...
  ✅ A) rahata kavuşmamış - duyarlı
  ✅ B) pes etmemiş - koruyucu        ← Correct answer
     C) yenik düşmemiş - gururlu
     D) taviz vermemiş - baskıcı
...
```

### Step 4: Seed Questions to Database
```bash
docker-compose exec -T backend python seed_turkish_pdf.py
```

The script will:
1. Parse the PDF
2. Display all 20 questions
3. Map them to topics (Okuma Anlama, Yazın, Dil Bilgisi)
4. Ask for confirmation
5. Seed to database

Output:
```
📖 Parsing PDF: 2025sozelbolum.pdf
✅ Successfully parsed 20 questions

🔄 Applying topic mapping...
  Q1: Türkçe Konusu 1 → Okuma Anlama Konusu 1
  Q2: Türkçe Konusu 1 → Okuma Anlama Konusu 1
  ...

📋 Questions to be seeded:

Q1: [MEDIUM] Hiç tanımadığımız ancak görür görmez içimizin ısındığı...
    Topic: Okuma Anlama Konusu 1
    ✅ B) pes etmemiş - koruyucu
    ...
...
Proceed with seeding? (yes/no): yes

🌱 Seeding questions to database...
📝 Seeding questions...
✓ Created question 1: Hiç tanımadığımız ancak...
✓ Created question 2: Vatanına borçlu olarak...
...
✅ Seeded 20 questions successfully!
```

### Step 5: Verify in Database
```bash
# Check total question count
docker-compose exec -T db psql -U lgs_user -d lgs_db \
  -c "SELECT COUNT(*) as total_questions FROM questions;"

# View by topic distribution
docker-compose exec -T db psql -U lgs_user -d lgs_db \
  -c "SELECT topic_name, COUNT(*) FROM questions 
      JOIN topics ON questions.topic_id = topics.id 
      GROUP BY topic_name ORDER BY topic_name;"

# Check answer keys
docker-compose exec -T db psql -U lgs_user -d lgs_db \
  -c "SELECT q.id, q.stem_text, qo.option_label 
      FROM questions q 
      JOIN question_options qo ON q.id = qo.question_id 
      WHERE qo.is_correct = true 
      ORDER BY q.id LIMIT 5;"
```

## Customization

### Change Topic Distribution

Edit `backend/seed_turkish_pdf.py`:

```python
TOPIC_MAPPING = {
    # Q1-5: Reading Comprehension
    1: "Okuma Anlama Konusu 1",
    2: "Okuma Anlama Konusu 1",
    3: "Okuma Anlama Konusu 2",
    4: "Okuma Anlama Konusu 2",
    5: "Okuma Anlama Konusu 3",
    
    # Q6-10: Word Meaning (your preference)
    6: "Sözcükte Anlam Konusu 1",
    7: "Sözcükte Anlam Konusu 1",
    8: "Sözcükte Anlam Konusu 1",
    9: "Sözcükte Anlam Konusu 2",
    10: "Sözcükte Anlam Konusu 2",
    
    # ... rest
}
```

Then re-run:
```bash
docker-compose exec -T backend python seed_turkish_pdf.py
```

### Adjust Difficulty Levels

Edit `DIFFICULTY_MAPPING` in `seed_turkish_pdf.py`:

```python
DIFFICULTY_MAPPING = {
    1: "EASY",      # Q1 is easy
    5: "MEDIUM",    # Q5 is medium
    15: "HARD",     # Q15 is hard
    20: "VERY_HARD" # Q20 is very hard
}
```

### Use Parser Directly in Python

```python
from parse_turkish_pdf import build_turkish_questions
from seed_questions_sql import seed_questions

# Parse PDF
questions = build_turkish_questions("2025sozelbolum.pdf")

# Modify as needed
for q in questions:
    q["difficulty"] = "HARD"
    q["topic_name"] = "Sözel Bölüm"

# Seed to database
seed_questions(questions)
```

## File Locations

All new files are in `backend/`:
```
backend/
├── parse_turkish_pdf.py          ← PDF → Question dicts
├── seed_questions_sql.py         ← Raw SQL seeder
├── seed_turkish_pdf.py           ← Interactive workflow
├── TURKISH_PDF_SEEDER_README.md  ← Detailed docs
├── 2025sozelbolum.pdf            ← Your exam PDF (place here)
└── requirements.txt              ← Updated with pdfplumber
```

## Architecture

```
┌─────────────────────┐
│ 2025sozelbolum.pdf  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  parse_turkish_pdf.py               │
│  • Extract text from TÜRKÇE section │
│  • Parse Q# 1-20 chunks             │
│  • Clean stem + options             │
│  • Read answer key from last page   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Question Dicts (Python objects)    │
│  [                                  │
│    {                                │
│      "subject_code": "TURKISH",     │
│      "topic_name": "Okuma...",      │
│      "stem_text": "...",            │
│      "options": [                   │
│        {"label": "B", ...}  ✅      │
│        {"label": "C", ...}          │
│      ]                              │
│    },                               │
│    ...                              │
│  ]                                  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  seed_turkish_pdf.py (interactive)  │
│  • Show questions preview           │
│  • Map to topics/difficulty         │
│  • Ask for confirmation             │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  seed_questions_sql.py              │
│  • Raw psycopg2 connection          │
│  • Insert questions                 │
│  • Insert options                   │
│  • Validate relationships           │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  PostgreSQL Database                │
│  • questions table (20 rows)        │
│  • question_options table (80 rows) │
│  • Linked to curriculum structure   │
└─────────────────────────────────────┘
```

## Troubleshooting

### Q: PDF Not Found
```
❌ Error: 2025sozelbolum.pdf not found
```
**A:** Copy PDF to `backend/` directory:
```bash
cp /Downloads/2025sozelbolum.pdf backend/
```

### Q: ModuleNotFoundError: No module named 'pdfplumber'
```
ModuleNotFoundError: No module named 'pdfplumber'
```
**A:** Install in container:
```bash
docker-compose exec -T backend pip install pdfplumber
```

### Q: Expected 20 answers, but only found 15
```
ValueError: Expected 20 answers, but only found 15
```
**A:** Answer key is on last page. Make sure PDF has answers like:
```
1.  B
2.  A
...
20. C
```

### Q: Topic not found, skipping question
```
⚠️  Topic Okuma Anlama Konusu 1 not found, skipping question
```
**A:** Check available topics:
```bash
docker-compose exec -T db psql -U lgs_user -d lgs_db \
  -c "SELECT name FROM topics WHERE name LIKE 'Okuma%';"
```

Then update `TOPIC_MAPPING` to match.

### Q: Subject TURKISH not found
```
⚠️  Subject TURKISH not found, skipping question
```
**A:** Seed curriculum first:
```bash
docker-compose exec -T backend python seed_questions_sql.py
```

## What's Next?

After seeding, you can:

1. **Test with API:**
   ```bash
   curl http://localhost:8000/api/v1/questions/1
   ```

2. **Start an exam:**
   ```python
   POST /api/v1/exams/start
   {
     "student_id": 1,
     "type": "PRACTICE"
   }
   ```

3. **Answer a question:**
   ```python
   POST /api/v1/exams/{exam_id}/answer
   {
     "question_id": 1,
     "selected_option": "B"
   }
   ```

4. **View statistics:**
   ```bash
   curl http://localhost:8000/api/v1/questions/stats
   ```

---

**Questions?** Check `TURKISH_PDF_SEEDER_README.md` for detailed docs.
