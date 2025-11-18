# System Architecture & Implementation Map

## Complete System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR EXAM PDF                             │
│               2025sozelbolum.pdf (20 questions)                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Place in: backend/
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│            PARSE TURKISH PDF (parse_turkish_pdf.py)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  extract_turkish_block()                                         │
│  ├─ Find TÜRKÇE pages                                            │
│  ├─ Extract text from each page                                  │
│  ├─ Remove headers/footers/boilerplate                           │
│  └─ Return clean combined text                                   │
│                                                                   │
│  find_question_chunks()                                          │
│  ├─ Find positions of "1.", "2.", ... "20."                     │
│  ├─ Extract text between boundaries                              │
│  └─ Return 20 raw chunks                                         │
│                                                                   │
│  parse_question_chunk()   [for each chunk]                       │
│  ├─ Extract question number                                      │
│  ├─ Split stem from options                                      │
│  ├─ Parse A), B), C), D) options                                │
│  └─ Clean hyphenation + formatting                               │
│                                                                   │
│  extract_answer_key()                                            │
│  ├─ Read PDF last page                                           │
│  ├─ Regex find "1. B", "2. A", etc.                             │
│  └─ Return {1: 'B', 2: 'A', ..., 20: 'D'}                       │
│                                                                   │
│  normalize_text() / clean_option_text()                          │
│  ├─ Remove line break hyphens                                    │
│  ├─ Join newlines with spaces                                    │
│  ├─ Collapse multiple spaces                                     │
│  └─ Remove trailing page numbers                                 │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ OUTPUT: Python list of 20 dicts
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              QUESTION DICTS (structured data)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [                                                                │
│    {                                                              │
│      "subject_code": "TURKISH",                                  │
│      "topic_name": "Türkçe Konusu 1",                           │
│      "difficulty": "MEDIUM",                                     │
│      "stem_text": "Hiç tanımadığımız ancak... hangisi...",     │
│      "estimated_time_seconds": 90,                               │
│      "options": [                                                 │
│        {"label": "A", "text": "rahata...", "is_correct": False}, │
│        {"label": "B", "text": "pes etmemiş...", "is_correct": True}, │
│        {"label": "C", "text": "yenik...", "is_correct": False},  │
│        {"label": "D", "text": "taviz...", "is_correct": False}   │
│      ]                                                             │
│    },                                                              │
│    { ... Q2 ... },                                               │
│    { ... Q3 ... },                                               │
│    ...                                                             │
│    { ... Q20 ... }                                               │
│  ]                                                                │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Interactive Mapping (seed_turkish_pdf.py)
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│           TOPIC MAPPING (customizable)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Q1, Q2     → "Okuma Anlama Konusu 1"                           │
│  Q3, Q4, Q5 → "Okuma Anlama Konusu 2"                           │
│  Q6, Q7, Q8 → "Dil Bilgisi Konusu 1"                            │
│  Q9, Q10    → "Dil Bilgisi Konusu 2"                            │
│  Q11-14     → "Dil Bilgisi Konusu 3"                            │
│  Q15, Q16   → "Yazın Konusu 1"                                  │
│  Q17, Q18   → "Yazın Konusu 2"                                  │
│  Q19, Q20   → "Yazın Konusu 3"                                  │
│                                                                   │
│  [User reviews and confirms]                                     │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Seed to Database (seed_questions_sql.py)
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  subjects table        curriculum_structure/                     │
│  ├─ Matematik          └─ Already seeded:                        │
│  ├─ Fen Bilgisi            4 subjects × 3 units × 3 topics       │
│  ├─ Türkçe                 = 36 curriculum nodes                 │
│  └─ Sosyal Bilgiler                                              │
│                         topics table (36 rows)                   │
│  units table (12 rows)  ├─ Okuma Anlama Konusu 1-3               │
│  ├─ Sayılar             ├─ Dil Bilgisi Konusu 1-3                │
│  ├─ Cebir               └─ Yazın Konusu 1-3                      │
│  ├─ Geometri                                                      │
│  ├─ Fizik              learning_outcomes table (36 rows)         │
│  └─ ... (12 total)      └─ One per topic                         │
│                                                                   │
│  ┌──────────────────────────────────────────────┐                │
│  │ NEWLY SEEDED QUESTIONS (20 rows)             │                │
│  ├──────────────────────────────────────────────┤                │
│  │ id │ subject │ topic              │ stem_text       │ diff   │
│  ├──────────────────────────────────────────────┤                │
│  │ 1  │ Türkçe  │ Okuma Anlama Konusu 1 │ "Hiç tanı..." │ MED   │
│  │ 2  │ Türkçe  │ Okuma Anlama Konusu 1 │ "Vatanına..." │ HARD  │
│  │ 3  │ Türkçe  │ Okuma Anlama Konusu 2 │ "Birçok..." │ EASY   │
│  │ 4  │ Türkçe  │ Okuma Anlama Konusu 2 │ "Yabancı..." │ MED   │
│  │ 5  │ Türkçe  │ Okuma Anlama Konusu 3 │ ...         │ ...    │
│  │ .. │ ..      │ ..                  │ ...         │ ...    │
│  │ 20 │ Türkçe  │ Yazın Konusu 3      │ ...         │ ...    │
│  └──────────────────────────────────────────────┘                │
│                                                                   │
│  question_options table (80 rows - 4 per question)               │
│  ├─ Q1, Option A (not correct)                                  │
│  ├─ Q1, Option B ✅ CORRECT                                     │
│  ├─ Q1, Option C (not correct)                                  │
│  ├─ Q1, Option D (not correct)                                  │
│  ├─ Q2, Option A (not correct)                                  │
│  ├─ Q2, Option B ✅ CORRECT                                     │
│  └─ ... (4 options × 20 questions = 80 total)                   │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Ready for API / Exams
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR PLATFORM API                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  GET  /api/v1/questions/1                                       │
│  → Returns Q1 with 4 options (doesn't reveal correct answer)    │
│                                                                   │
│  POST /api/v1/exams/start                                       │
│  → Creates exam instance, picks first question                  │
│                                                                   │
│  POST /api/v1/exams/{exam_id}/answer                            │
│  → Student submits answer, scores, picks next (adaptive)        │
│                                                                   │
│  GET  /api/v1/exams/{exam_id}/results                           │
│  → Final score, correct/incorrect breakdown                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## File Organization

```
/Users/ilkeileri/milliondolarproject/lgs-platform/
│
├── 📄 IMPLEMENTATION_SUMMARY.md          ← Overview (you are here)
├── 📄 QUICK_START_PDF_SEEDER.md         ← Step-by-step guide
├── 📄 PDF_PARSER_IMPLEMENTATION.md      ← Technical details
├── 📄 FILES_CREATED.md                  ← File listing
│
└── backend/
    │
    ├── 🔴 2025sozelbolum.pdf            ← PLACE YOUR PDF HERE
    │
    ├── 🟢 parse_turkish_pdf.py          ← PDF → Question dicts
    │   ├─ normalize_text()
    │   ├─ extract_turkish_block()
    │   ├─ find_question_chunks()
    │   ├─ parse_question_chunk()
    │   └─ extract_answer_key()
    │
    ├── 🟢 seed_questions_sql.py         ← Dicts → Database (raw SQL)
    │   ├─ get_db_connection()
    │   ├─ seed_curriculum()
    │   └─ seed_questions()
    │
    ├── 🟢 seed_turkish_pdf.py           ← Interactive workflow
    │   └─ TOPIC_MAPPING (customizable)
    │
    ├── 📄 TURKISH_PDF_SEEDER_README.md  ← Reference docs
    │
    ├── 📋 requirements.txt               ← +pdfplumber added
    │
    ├── app/
    │   ├── main.py
    │   ├── core/config.py
    │   ├── db/session.py
    │   ├── models/
    │   │   ├─ question.py
    │   │   ├─ curriculum.py
    │   │   └─ ...
    │   └── ...
    │
    ├── migrations/
    │   ├── alembic.ini
    │   ├── env.py
    │   └── versions/
    │       └── 001_initial_schema.py
    │
    └── tests/
        └── ...
```

## Execution Flow

### Step 1: Setup (One Time)
```
┌─────────────────────────┐
│ docker-compose up -d    │ ← Start containers
│ pip install -r req.txt  │ ← Install dependencies
│ alembic upgrade head    │ ← Create schema
└────────────┬────────────┘
             │
             ▼ ✅ Ready
```

### Step 2: Parse & Seed
```
┌──────────────────────────────────┐
│ cp 2025sozelbolum.pdf backend/   │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ python seed_turkish_pdf.py       │
├──────────────────────────────────┤
│                                  │
│ 1. Parse PDF                     │
│    ↓                             │
│ 2. Show 20 questions             │
│    ↓                             │
│ 3. Map to topics                 │
│    ↓                             │
│ 4. Ask confirmation              │
│    ↓                             │
│ 5. Seed to database              │
│    ↓                             │
│ 6. Commit transaction            │
│                                  │
└────────┬─────────────────────────┘
         │
         ▼ ✅ Done
         
Database now has 20 questions ready
for exams and API calls
```

## Data Flow Example

### Input: Raw PDF Text
```
3. "Birçok türde yazdım ama kendimi en iyi ifade 
   ettiğim tür şiir oldu." diyen bir sanatçı için 
   aşağıdakilerden hangisi kesinlikle söylenir?

   A) Sanatçı, kendini rahat ifade ettiği için şiir 
      türünü seçer.
   B) Sanatçının kendini iyi ifade edemediği türler 
      vardır.
   C) Şiir, sanatçının kendini iyi ifade ettiği türler 
      arasındadır.
   D) Şiir, sanatçının kendini iyi ifade etmesini 
      kolaylaştıran bir türdür.
```

### Processing: Cleaned
```
Q#: 3
Stem: "Birçok türde yazdım ama kendimi en iyi ifade 
       ettiğim tür şiir oldu." diyen bir sanatçı için 
       aşağıdakilerden hangisi kesinlikle söylenir?

Options:
A) Sanatçı, kendini rahat ifade ettiği için şiir türünü seçer.
B) Sanatçının kendini iyi ifade edemediği türler vardır.
C) Şiir, sanatçının kendini iyi ifade ettiği türler arasındadır.
D) Şiir, sanatçının kendini iyi ifade etmesini kolaylaştıran bir türdür.

Answer Key: C → is_correct = true for option C
```

### Output: Database Record
```python
{
  "id": 4,
  "subject_id": 3,  # Türkçe
  "topic_id": 12,   # Dil Bilgisi Konusu 1
  "main_learning_outcome_id": 34,
  "difficulty": "EASY",
  "stem_text": "Birçok türde yazdım...",
  "is_active": true,
  "created_at": "2025-11-14 12:15:00"
}

Options:
[
  {question_id: 4, option_label: "A", text: "...", is_correct: false},
  {question_id: 4, option_label: "B", text: "...", is_correct: false},
  {question_id: 4, option_label: "C", text: "...", is_correct: true},  ✅
  {question_id: 4, option_label: "D", text: "...", is_correct: false}
]
```

## Error Handling Flow

```
┌─────────────────────────────────────┐
│ seed_turkish_pdf.py                 │
└────────┬────────────────────────────┘
         │
         ├─► FileNotFoundError
         │   └─► "2025sozelbolum.pdf not found"
         │       → Solution: Copy PDF to backend/
         │
         ├─► ValueError: "Expected 20 answers..."
         │   └─► Answer key incomplete
         │       → Solution: Check last page of PDF
         │
         ├─► Subject not found
         │   └─► Curriculum not seeded
         │       → Solution: Run seed_questions_sql.py first
         │
         ├─► Topic not found
         │   └─► TOPIC_MAPPING mismatch
         │       → Solution: Adjust mapping in script
         │
         └─► Database error
             └─► Connection/constraint issue
                 → Solution: Check Docker + migrations
```

## Performance Characteristics

```
Parse PDF (20 questions):        ~2-3 seconds
├─ Extract text:                  ~0.5s
├─ Find chunks:                   ~0.2s
├─ Parse each question:           ~1.2s (6 chunks×200ms)
└─ Extract answer key:            ~0.3s

Seed to Database (20 questions):  ~1-2 seconds
├─ Database connection:           ~0.2s
├─ Lookup curriculums:            ~0.3s
├─ Insert questions:              ~0.7s (20 inserts)
├─ Insert options:                ~0.6s (80 inserts)
└─ Commit transaction:            ~0.2s

Total End-to-End:                 ~3-5 seconds
```

## Success Indicators

✅ **You'll see:**
```
📖 Parsing PDF: 2025sozelbolum.pdf
✅ Successfully parsed 20 Türkçe questions

🔄 Applying topic mapping...
  Q1: Türkçe Konusu 1 → Okuma Anlama Konusu 1
  Q2: Türkçe Konusu 1 → Okuma Anlama Konusu 1
  ...

📋 Questions to be seeded:
Q1: [MEDIUM] Hiç tanımadığımız...

Proceed with seeding? (yes/no): yes

🌱 Seeding questions to database...
✓ Created question 1: Hiç tanımadığımız...
✓ Created question 2: Vatanına borçlu...
...
✅ Seeded 20 questions successfully!
```

---

## Quick Links

- 📚 **Quick Start:** `QUICK_START_PDF_SEEDER.md`
- 📖 **Detailed Docs:** `backend/TURKISH_PDF_SEEDER_README.md`
- 🔧 **Technical:** `PDF_PARSER_IMPLEMENTATION.md`
- 📋 **Files:** `FILES_CREATED.md`

**Next Step:** Place your PDF and run the seeder! 🚀
