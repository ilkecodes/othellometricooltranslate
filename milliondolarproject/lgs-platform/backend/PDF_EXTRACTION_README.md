# LGS Sözel Bölüm - PDF to Database Pipeline

## 🎯 Amaç

LGS sınav PDF'lerinden soruları otomatik olarak çıkartıp veritabanına aktarma.

## 📂 Script'ler

### 1. `extract_lgs_questions.py` – PDF → JSONL

PDF dosyasını okuyor ve sorularını JSONL formatında çıkarıyor.

```bash
python extract_lgs_questions.py "input.pdf" "output.jsonl"
```

**Çıktı:** JSONL dosyası (her satır bir soru)

```json
{"number": 1, "stem": "...", "choices": [...]}
{"number": 2, "stem": "...", "choices": [...]}
```

### 2. `seed_from_jsonl.py` – JSONL → Database

JSONL dosyasındaki soruları veritabanına seeder.

```bash
python seed_from_jsonl.py "input.jsonl" --auto-topic
```

**Özellikler:**
- ✅ Otomatik konu atama (anahtar kelime tabanlı)
- ✅ Otomatik zorluk seviyesi (metin uzunluğuna göre)
- ✅ İnteraktif onay
- ✅ Subject (Türkçe, Matematik, vb.) seçimi

### 3. `test_extract.py` – Hızlı Test & Preview

PDF'den soruları hızlıca test et ve preview göster.

```bash
python test_extract.py "input.pdf"
python test_extract.py "input.pdf" --save output.jsonl
```

## 🚀 Hızlı Başlangıç

```bash
# 1. PDF → JSONL çıkart
docker-compose exec -T backend python extract_lgs_questions.py "2025sozelbolum.pdf" "sozel.jsonl"

# 2. JSONL → Database seed et
docker-compose exec -T backend python seed_from_jsonl.py "sozel.jsonl"

# 3. Onayı ver: yes
```

## 🔑 Özellikler

### Otomatik Konu Atama

Soru kökü içindeki anahtar kelimelerden konu belirler:

| Anahtar Kelime | Konu |
|---|---|
| parçada, metinde, paragraf | Paragraf – Okuma Anlama |
| sözcük, kelime, deyim | Sözcükte Anlam |
| cümlede, cümlesiyle | Cümlede Anlam |
| yazım, noktalama, virgül | Yazım ve Noktalama |

### Otomatik Zorluk Seviyesi

Soru kökü uzunluğundan:

- **EASY**: < 15 sözcük
- **MEDIUM**: 15–30 sözcük
- **HARD**: 30–60 sözcük
- **VERY_HARD**: > 60 sözcük

## 📋 Seçenekler

```bash
# Konu atamayı devre dışı bırak
python seed_from_jsonl.py "input.jsonl" --no-auto-topic

# Farklı konu seç (Matematik, Fen, Sosyal)
python seed_from_jsonl.py "input.jsonl" --subject MATH

# Ön izleme (database'ye yazı yazma)
python seed_from_jsonl.py "input.jsonl" --dry-run

# İstatistik göster
python test_extract.py "input.pdf"
```

## 📝 JSONL Formatı

```json
{
  "number": 1,
  "stem": "Aşağıdaki parçada hangi fikir vurgulanmıştır?",
  "choices": [
    {"label": "A", "text": "Birinci seçenek"},
    {"label": "B", "text": "İkinci seçenek"},
    {"label": "C", "text": "Üçüncü seçenek"},
    {"label": "D", "text": "Dördüncü seçenek"}
  ]
}
```

## 🛠️ PDF Yapısı Gereksinimleri

Script şu formatı bekler:

- Sorular: `1. `, `2. `, `3. ` ... `20. `
- Seçenekler: `A) `, `B) `, `C) `, `D) `

Farklı formatsa, script'teki regex'leri güncelleyin:

```python
QUESTION_START_RE = re.compile(r"(?:^|\s)(\d{1,2})[\.\)]\s")  # "1)" veya "1."
CHOICE_SPLIT_RE = re.compile(r"\s([A-D])[\.\)]\s")            # "A)" veya "A."
```

## 🐳 Docker Kullanımı

```bash
# Container içinde çalıştır
docker-compose exec -T backend python extract_lgs_questions.py "input.pdf" "output.jsonl"
docker-compose exec -T backend python seed_from_jsonl.py "output.jsonl"

# Veya container'a gir ve çalıştır
docker-compose exec backend bash
python extract_lgs_questions.py "input.pdf" "output.jsonl"
python seed_from_jsonl.py "output.jsonl"
```

## ❓ Sık Sorulan Sorular

**S: Doğru cevapları nasıl belirler?**
A: Şu an script otomatik olarak "A" seçeneğini doğru işaretliyor. Sonra manuel güncelleyebilirsiniz.

**S: Başka PDF'ler için çalışır mı?**
A: Evet, soru formatı aynıysa. Farklıysa regex'leri güncelleyin.

**S: JSONL dosyası nedir?**
A: JSON Lines formatı - her satır bir JSON nesnesi.

**S: Konu otomatik ataması yanlışsa?**
A: JSONL'yi Excel'de açıp edit edebilirsiniz, ya da seed_from_jsonl.py'deki topic_ids mapping'ini override edin.

## 📚 Detaylı Rehber

Daha fazla bilgi için: `LGS_PDF_EXTRACTION_GUIDE.md`

## 🔗 İlişkili Dosyalar

- `parse_turkish_pdf.py` - Eski Türkçe PDF parser (pdfplumber kullanır)
- `seed_questions_sql.py` - Eski SQL tabanlı seeder
- `seed_from_jsonl.py` - Yeni modern JSONL seeder
