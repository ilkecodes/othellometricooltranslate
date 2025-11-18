# LGS PDF → Database Extraction Pipeline

Türkçe bölümüne ait LGS sınav PDF'lerinden soruları otomatik olarak veritabanına aktarma sistemi.

## İş Akışı

```
LGS PDF 
   ↓
extract_lgs_questions.py (PDF → JSONL)
   ↓
JSONL dosyası
   ↓
seed_from_jsonl.py (JSONL → Database)
   ↓
Database'deki Questions ve QuestionOptions tabloları
```

## Adım 1: PDF'ten Soruları Çıkart

```bash
cd backend/
docker-compose exec -T backend python extract_lgs_questions.py "PDF_DOSYASI.pdf" "çıktı.jsonl"
```

**Örnek:**
```bash
docker-compose exec -T backend python extract_lgs_questions.py "2025sozelbolum.pdf" "lgs_2025_sozel.jsonl"
```

**Çıktı:**
```
📖 Reading PDF: 2025sozelbolum.pdf
✅ Extracted 20 questions
✅ Saved to: lgs_2025_sozel.jsonl

📋 Preview (first 3 questions):

  Q1: Aşağıdaki cümlede hangi sözcük...
    A) ...
    B) ...
    C) ...
    D) ...
```

## Adım 2: JSONL'den Veritabanına Seed Et

```bash
docker-compose exec -T backend python seed_from_jsonl.py "çıktı.jsonl"
```

**Örnek:**
```bash
docker-compose exec -T backend python seed_from_jsonl.py "lgs_2025_sozel.jsonl" --auto-topic
```

**İnteraktif Workflow:**
```
🔧 Curriculum yapısı kontrol ediliyor...
✅ Subject ID: 1

📖 Reading JSONL: lgs_2025_sozel.jsonl
✅ Loaded 20 questions

📋 Preview (first 2 questions):

  Q1:
    Topic: Cümlede Anlam
    Difficulty: MEDIUM
    Stem: Aşağıdaki cümlede...

💾 Seed 20 questions? (yes/no): yes

🌱 Seeding 20 questions...
  ✓ Seeded 10/20 questions
  ✓ Seeded 20/20 questions

✅ Successfully seeded 20 questions!
```

## Otomatik Konu Atama

`--auto-topic` bayrağı (varsayılan) sorular için otomatik konu atama yapar:

### Konu Çıkarma Kuralları

| Konu | Anahtar Kelimeler |
|------|-------------------|
| **Paragraf – Okuma Anlama** | parçada, metinde, paragrafta, yazar, ana fikir |
| **Sözcükte Anlam** | sözcük, kelime, deyim, atasözü |
| **Cümlede Anlam** | cümlede, cümlesinde, cümlesiyle |
| **Yazım ve Noktalama** | yazım, noktalama, virgül, kesme işareti |
| **Türkçe – Diğer** | (fallback) |

### Zorluk Seviyeleri

| Zorluk | Sözcük Sayısı |
|--------|---------------|
| EASY | < 15 |
| MEDIUM | 15–30 |
| HARD | 30–60 |
| VERY_HARD | > 60 |

## Seçenekler

### Konu Atamayı Devre Dışı Bırak

```bash
python seed_from_jsonl.py "lgs_2025_sozel.jsonl" --no-auto-topic
```

### Farklı Konu (Subject) Kullan

```bash
python seed_from_jsonl.py "lgs_matematikler.jsonl" --subject MATH
python seed_from_jsonl.py "lgs_fen.jsonl" --subject SCIENCE
python seed_from_jsonl.py "lgs_sosyal.jsonl" --subject SOCIAL
```

### Ön İzleme Modu (Dry Run)

Database'ye yazı yazmadan preview göster:

```bash
python seed_from_jsonl.py "lgs_2025_sozel.jsonl" --dry-run
```

## JSONL Dosyası Formatı

Her satır bir JSON nesnesidir:

```json
{
  "number": 1,
  "stem": "Aşağıdaki parçada hangi fikir vurgulanmıştır?",
  "choices": [
    {"label": "A", "text": "Seçenek A"},
    {"label": "B", "text": "Seçenek B"},
    {"label": "C", "text": "Seçenek C"},
    {"label": "D", "text": "Seçenek D"}
  ]
}
```

## PDF Yapısı Gereksinimleri

Script şu PDF yapısını bekler:

- Soru numaraları: `1. `, `2. `, vb.
- Seçenekler: `A) `, `B) `, `C) `, `D) `
- Metin sayfalar arası kırılabilir

### PDF Yapısı Değişiyorsa

`extract_lgs_questions.py` içindeki regex'leri güncelleyin:

```python
# Soru numaraları: "1)" veya "1." olabilir
QUESTION_START_RE = re.compile(r"(?:^|\s)(\d{1,2})[\.\)]\s")

# Seçenekler: "A." veya "A)" olabilir
CHOICE_SPLIT_RE = re.compile(r"\s([A-D])[\.\)]\s")
```

## Doğru Cevapları Manuel Ayarlama

Şu an script otomatik olarak **A seçeneğini doğru** olarak işaretliyor.

Doğru cevapları sonradan güncellemek için:

```sql
UPDATE question_options 
SET is_correct = true 
WHERE question_id = 6 AND option_label = 'C';
```

Ya da seeder'ı değiştirerek answer key'i PDF'den çıkartabilirsiniz.

## Sorun Giderme

### "PDF not found" hatası

PDF dosyası backend klasöründe olduğundan emin olun:
```bash
ls -la backend/*.pdf
```

### "Could not translate host name 'db'" hatası

Docker'ın çalışıyor olduğundan emin olun:
```bash
docker-compose ps
```

### Veritabanı hataları

Migration'ların uygulandığından emin olun:
```bash
docker-compose exec -T backend alembic upgrade head
```

## Örnek Tam İş Akışı

```bash
# 1. Container'a gir
docker-compose exec backend bash

# 2. PDF'ten JSONL çıkart
python extract_lgs_questions.py "2025sozelbolum.pdf" "sozel_2025.jsonl"

# 3. JSONL'den seed et
python seed_from_jsonl.py "sozel_2025.jsonl"

# 4. Veritabanında doğrula
psql -U lgs_user -d lgs_db -c "SELECT COUNT(*) FROM questions;"
```

## Notlar

- Doğru cevaplar manuel gözden geçirilmesi gerekebilir (şu an A varsayılan)
- Konu otomatik ataması % 95 doğrulukla çalışır, kontrol önerilir
- JSONL dosyası başka araçlarda (Excel, Python, vb.) işlenebilir
