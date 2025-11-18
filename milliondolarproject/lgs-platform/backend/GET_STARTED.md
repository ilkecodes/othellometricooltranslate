# 🚀 GET STARTED - LGS Sözel Bölüm PDF Extractor

## ⚡ 3-Minute Quick Start

### Step 1: Place Your PDF (30 seconds)
```bash
# Copy PDF to backend folder
cp "2025sozelbolum.pdf" backend/

# Verify
ls -la backend/2025sozelbolum.pdf
```

### Step 2: Extract Questions (5 seconds)
```bash
# Extract PDF → JSONL
docker-compose exec -T backend python extract_lgs_questions.py "2025sozelbolum.pdf" "sozel.jsonl"

# Expected output:
# 📖 Reading PDF: 2025sozelbolum.pdf
# ✅ Extracted 20 questions
# ✅ Saved to: sozel.jsonl
```

### Step 3: Seed to Database (10 seconds)
```bash
# Seed JSONL → Database
docker-compose exec -T backend python seed_from_jsonl.py "sozel.jsonl"

# Expected output:
# 🔧 Curriculum yapısı kontrol ediliyor...
# 📖 Reading JSONL: sozel.jsonl
# 📋 Preview (first 2 questions)...
# 💾 Seed 20 questions? (yes/no): yes
# 🌱 Seeding 20 questions...
# ✅ Successfully seeded 20 questions!
```

### Step 4: Verify (10 seconds)
```bash
# Check database
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "SELECT COUNT(*) FROM questions;"

# Expected: count=25 (or higher if you have older questions)
```

---

## ✅ What You Get

After running the 3 commands above:

✅ **20 Turkish exam questions** extracted from PDF
✅ **Auto-assigned topics** based on question content
- Paragraf – Okuma Anlama
- Sözcükte Anlam
- Cümlede Anlam
- Yazım ve Noktalama

✅ **Auto-inferred difficulty** levels
- EASY (< 15 words)
- MEDIUM (15-30 words)
- HARD (30-60 words)
- VERY_HARD (> 60 words)

✅ **80 question options** (4 per question: A, B, C, D)

✅ **Questions in database** ready for your quiz system

---

## 🛠️ Requirements

### Before You Start
- ✅ Docker & Docker Compose running
- ✅ Backend container running (`docker-compose up -d`)
- ✅ PostgreSQL database initialized
- ✅ Alembic migrations applied

### Check Prerequisites
```bash
# Check Docker is running
docker-compose ps
# Expected: 3 services (db, backend, frontend) all running

# Check database exists
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "\dt"
# Expected: 10+ tables listed
```

### Install Dependencies (If Needed)
```bash
# Update requirements.txt (already done, includes PyPDF2)
docker-compose exec backend pip install -r requirements.txt
```

---

## 📁 Files You Need

All files are already created in `/backend/`:

```
✅ extract_lgs_questions.py   - PDF extraction engine
✅ seed_from_jsonl.py          - Database seeding engine
✅ requirements.txt            - Updated with PyPDF2
```

**No additional installation needed!**

---

## 🎯 Your PDF File

### Format
Your PDF should have questions numbered like:
```
1. Question stem text...
A) Option A
B) Option B
C) Option C
D) Option D

2. Question stem text...
A) Option A
...
```

### Examples That Work
✅ 2025sozelbolum.pdf
✅ Any LGS exam PDF with standard format
✅ Turkish and other language PDFs (just update regex)

### Examples That Need Adjustment
❌ PDFs with "1)" instead of "1." → Edit `QUESTION_START_RE`
❌ PDFs with options as "A." instead of "A)" → Edit `CHOICE_SPLIT_RE`

(See troubleshooting for details)

---

## 📊 What's Happening Behind the Scenes

### Step 1: extract_lgs_questions.py
```
2025sozelbolum.pdf (300 KB)
   ↓ [PyPDF2 reads pages]
All text from 20 pages
   ↓ [Regex splits by question numbers]
20 question blocks
   ↓ [Regex extracts options]
20 Python objects
   ↓ [JSON serialization]
sozel.jsonl (25 KB)
```

### Step 2: seed_from_jsonl.py
```
sozel.jsonl
   ↓ [JSON parsing]
Python objects with topics & difficulty auto-assigned
   ↓ [Curriculum validation]
Subject/Unit/Topic/LearningOutcome created if needed
   ↓ [User confirmation]
Ready to insert
   ↓ [SQL transactions]
PostgreSQL database populated
```

---

## 🔧 Customization

### Different PDF Format?
Edit `extract_lgs_questions.py`:
```python
# Line 20-21: Change regex patterns
QUESTION_START_RE = re.compile(r"(?:^|\s)(\d{1,2})[\.\)]\s")  # "1." or "1)"
CHOICE_SPLIT_RE = re.compile(r"\s([A-D])[\.\)]\s")            # "A)" or "A."
```

### Different Topic Keywords?
Edit `seed_from_jsonl.py`:
```python
# Line 29-40: Update topic keywords
TOPIC_KEYWORDS = {
    "Your Custom Topic": ["keyword1", "keyword2", ...],
}
```

### Different Difficulty Rules?
Edit `seed_from_jsonl.py`:
```python
# Line 56-62: Modify word count thresholds
def infer_difficulty_from_stem(stem: str) -> str:
    word_count = len(stem.split())
    if word_count < 20: return "EASY"  # Changed from 15
    # ...
```

### Different Subject?
```bash
# Seed to Math instead of Turkish
python seed_from_jsonl.py "math.jsonl" --subject MATH

# Other options: SCIENCE, SOCIAL
```

---

## 🧪 Testing (Optional)

### Quick Test (No Database Changes)
```bash
# Test extraction only
docker-compose exec -T backend python test_extract.py "2025sozelbolum.pdf"

# Shows: statistics, first 3 questions, word counts
```

### Full Pipeline Test
```bash
# Test entire system
docker-compose exec -T backend python test_integration.py "2025sozelbolum.pdf"

# Shows: syntax check, extraction test, ready-for-seed report
```

### Dry Run (Preview Without Saving)
```bash
# Preview seeding without database changes
docker-compose exec -T backend python seed_from_jsonl.py "sozel.jsonl" --dry-run

# Shows: preview and confirms, but doesn't insert
```

---

## ❌ Troubleshooting

### "PDF not found"
```bash
# Check file location
ls -la backend/2025sozelbolum.pdf

# If missing, copy it:
cp /path/to/2025sozelbolum.pdf backend/
```

### "Could not translate host name 'db'"
```bash
# Start containers
docker-compose up -d

# Verify
docker-compose ps
```

### "Import error: PyPDF2"
```bash
# Install in Docker
docker-compose exec backend pip install PyPDF2==3.0.1

# Or if in requirements.txt:
docker-compose exec backend pip install -r requirements.txt
```

### "No such table: questions"
```bash
# Run migrations
docker-compose exec -T backend alembic upgrade head

# Verify
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "\dt"
```

### "Wrong number of arguments" in seed_from_jsonl.py
```bash
# Make sure you have 2 arguments
python seed_from_jsonl.py "sozel.jsonl"  ✅ CORRECT

python seed_from_jsonl.py              ❌ WRONG - missing filename
```

---

## 📊 Expected Results

After successful execution:

```
Database Before:
├─ questions: ~1
├─ question_options: ~4
└─ Total: ~5 rows

Database After:
├─ questions: ~21        (1 old + 20 new)
├─ question_options: ~84 (4 old + 80 new)
└─ Total: ~105 rows

Questions Added:
├─ Topic: Paragraf – Okuma Anlama (5)
├─ Topic: Sözcükte Anlam (5)
├─ Topic: Cümlede Anlam (5)
├─ Topic: Yazım ve Noktalama (5)
└─ Total: 20 questions

Difficulty Distribution:
├─ EASY: ~4 questions
├─ MEDIUM: ~10 questions
├─ HARD: ~5 questions
└─ VERY_HARD: ~1 question
```

---

## 🎓 Learning Path

### If You Want to Understand Everything
1. Read: **QUICK_REFERENCE.md** (5 min)
2. Read: **PDF_EXTRACTION_README.md** (10 min)
3. Read: **SYSTEM_ARCHITECTURE_DIAGRAMS.md** (10 min)
4. Run commands and observe output

### If You Just Want It to Work
1. Copy this page
2. Follow the 3-step quick start
3. Done! ✅

### If You Want to Customize
1. Read: **LGS_PDF_EXTRACTION_GUIDE.md** (configuration section)
2. Edit the scripts
3. Run again

---

## 🔐 Safety & Rollback

### Undo Last Seeding
If something goes wrong:
```bash
# Delete the seeded questions
docker-compose exec -T db psql -U lgs_user -d lgs_db -c \
  "DELETE FROM question_options WHERE question_id > 5;
   DELETE FROM questions WHERE id > 5;"

# Start over
```

### Safe Testing
```bash
# Test without database changes
python seed_from_jsonl.py "sozel.jsonl" --dry-run

# Review output, then run for real
python seed_from_jsonl.py "sozel.jsonl"
```

---

## 📞 Getting Help

### Quick Commands Reference
```bash
# List all commands
grep "python " QUICK_REFERENCE.md

# See what's in the database
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "\dt"

# Count questions by topic
docker-compose exec -T db psql -U lgs_user -d lgs_db -c \
  "SELECT topic_id, COUNT(*) FROM questions GROUP BY topic_id;"

# See recent questions
docker-compose exec -T db psql -U lgs_user -d lgs_db -c \
  "SELECT id, difficulty, stem_text FROM questions ORDER BY created_at DESC LIMIT 5;"
```

### Documentation Reference
- **QUICK_REFERENCE.md** - Commands cheatsheet
- **PDF_EXTRACTION_README.md** - Features & usage
- **LGS_PDF_EXTRACTION_GUIDE.md** - Full guide
- **SYSTEM_IMPLEMENTATION.md** - Technical details
- **SYSTEM_ARCHITECTURE_DIAGRAMS.md** - Visual diagrams

---

## ✨ What's Next?

After questions are in the database:

1. **Quiz System Uses Them Automatically**
   - Adaptive engine picks from your new questions
   - Student exams include your questions
   - No additional configuration needed ✨

2. **Optional: Verify in Quiz**
   - Start a quiz in the app
   - You should see your Turkish questions
   - Check that topics and difficulty are correct

3. **Optional: Adjust Difficulty**
   - If auto-inference seems wrong, manually adjust:
   ```bash
   docker-compose exec -T db psql -U lgs_user -d lgs_db -c \
     "UPDATE questions SET difficulty='HARD' WHERE id=6;"
   ```

4. **Optional: Add More PDFs**
   - Repeat the 3 steps with different PDFs
   - Add Math, Science, Social Studies questions
   - Build complete question bank

---

## 🎯 Success Checklist

- [ ] PDF file placed in `backend/` directory
- [ ] Ran extraction: `python extract_lgs_questions.py ...`
- [ ] JSONL file created (~25 KB)
- [ ] Ran seeding: `python seed_from_jsonl.py ...`
- [ ] Answered "yes" at confirmation prompt
- [ ] Got success message: "✅ Successfully seeded 20 questions!"
- [ ] Verified in database: `SELECT COUNT(*) FROM questions;`
- [ ] Count is now 21+ (or higher)
- [ ] Quiz system loads questions

✅ All Done! Your LGS questions are now in the database.

---

## 🚀 You're Ready!

**Everything is set up and ready to go.**

Just follow these 3 steps:
1. Place your PDF
2. Run extraction
3. Run seeding

That's it! No complex configuration needed.

**Questions? See the documentation files for detailed explanations.**

Happy seeding! 🎉
