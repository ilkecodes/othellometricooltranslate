# 🚀 LGS Sözel Bölüm - Hızlı Referans

## Komutlar

### Adım 1: PDF'den Soruları Çıkart
```bash
docker-compose exec -T backend python extract_lgs_questions.py "2025sozelbolum.pdf" "sozel.jsonl"
```

**Veya lokal olarak:**
```bash
python extract_lgs_questions.py "2025sozelbolum.pdf" "sozel.jsonl"
```

### Adım 2: Soruları Veritabanına Seed Et
```bash
docker-compose exec -T backend python seed_from_jsonl.py "sozel.jsonl"
```

**Onay sorulacak:** `Seed 20 questions? (yes/no): yes`

### Adım 3: Doğrula
```bash
docker-compose exec -T db psql -U lgs_user -d lgs_db -c "SELECT COUNT(*) FROM questions;"
```

---

## Seçenekler

```bash
# Konu atamayı devre dışı bırak
python seed_from_jsonl.py "sozel.jsonl" --no-auto-topic

# Farklı subject (Matematik, Fen, Sosyal)
python seed_from_jsonl.py "sozel.jsonl" --subject MATH

# Ön izleme (database yazı yazmadan)
python seed_from_jsonl.py "sozel.jsonl" --dry-run

# Test et (extraction test)
python test_extract.py "2025sozelbolum.pdf"

# Tam entegrasyon testi
python test_integration.py "2025sozelbolum.pdf"
```

---

## Dosyalar

| Script | Amaç |
|--------|------|
| `extract_lgs_questions.py` | PDF → JSONL |
| `seed_from_jsonl.py` | JSONL → Database |
| `test_extract.py` | Hızlı test & preview |
| `test_integration.py` | Tam pipeline test |
| `PDF_EXTRACTION_README.md` | Detaylı rehber |
| `LGS_PDF_EXTRACTION_GUIDE.md` | Kapsamlı dokümantasyon |

---

## PDF Yapısı

```
1. Soru kökü burada...
A) Seçenek A
B) Seçenek B
C) Seçenek C
D) Seçenek D

2. Soru kökü burada...
...
```

---

## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| PDF not found | PDF'i backend/ klasörüne koy |
| Database error | `docker-compose up` ile containers başlat |
| Import error | `pip install PyPDF2 psycopg2-binary` |
| Konu yanlış atanıyor | Seed komutundan sonra manuel düzelt |

---

## Otomatik Konu Atama

| Soruda geçiyorsa | Atanan Konu |
|--|--|
| parçada, metinde, paragraf | Paragraf – Okuma Anlama |
| sözcük, kelime, deyim | Sözcükte Anlam |
| cümlede, cümleleriyle | Cümlede Anlam |
| yazım, noktalama | Yazım ve Noktalama |

---

## Otomatik Zorluk

| Sözcük Sayısı | Zorluk |
|--|--|
| < 15 | EASY |
| 15-30 | MEDIUM |
| 30-60 | HARD |
| > 60 | VERY_HARD |

---

## Docker Cheatsheet

```bash
# Containers başlat
docker-compose up -d

# Container'a gir
docker-compose exec backend bash

# Container loglarını gör
docker-compose logs -f backend

# Database'ye sor (PSql)
docker-compose exec db psql -U lgs_user -d lgs_db -c "SELECT ..."

# Containers durdur
docker-compose down
```
