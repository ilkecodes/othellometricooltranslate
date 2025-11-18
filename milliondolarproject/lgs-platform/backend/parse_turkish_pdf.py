"""
Parser script for 2025 Türkçe PDF exam.

Extracts all 20 Türkçe questions, cleans them, and uses the official answer key
to mark correct answers. Outputs a list of dicts compatible with seed_questions().

Usage:
    from parse_turkish_pdf import build_turkish_questions
    questions = build_turkish_questions("2025sozelbolum.pdf")
    # Optionally adjust topic_name for each question
    seed_questions(questions)
"""
import re
import pdfplumber


def normalize_text(s: str) -> str:
    """Clean and normalize text: remove hyphens, newlines, collapse spaces."""
    if not s:
        return ""
    # remove hyphen-only line breaks: "yapıl -\nması" → "yapılması"
    s = re.sub(r"-\s*\n\s*", "", s)
    # normal newlines → spaces
    s = re.sub(r"\s*\n\s*", " ", s)
    # collapse spaces
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


def clean_option_text(text: str) -> str:
    """Clean option text, removing trailing page numbers."""
    text = normalize_text(text)
    # remove stray trailing page/line numbers like "... 10"
    text = re.sub(r"\s+\d{1,2}$", "", text)
    return text


def parse_question_chunk(chunk: str):
    """
    Parse a single question chunk.

    Expected format:
        1. "Birçok türde yazdım ama ... hangisi kesinlikle söylenir?
        A) rahata kavuşmamış - duyarlı
        B) pes etmemiş - koruyucu
        ...
    
    Returns: (q_no, stem, [(label, text), ...]) or None if parse fails
    """
    m = re.match(r"(\d{1,2})\.\s*(.*)", chunk, flags=re.S)
    if not m:
        return None

    q_no = int(m.group(1))
    rest = m.group(2).strip()

    # split into stem + option block (find first A) occurrence)
    first_opt = re.search(r"[A-D]\)", rest)
    if not first_opt:
        stem = rest.strip()
        opts = []
    else:
        stem = rest[:first_opt.start()].strip()
        opt_str = rest[first_opt.start():]

        # options can be on separate lines OR in a single line like: "A) I B) II C) III D) IV"
        opt_matches = list(re.finditer(
            r"([A-D])\)\s*(.*?)(?=(?:[A-D]\)\s)|$)",
            opt_str,
            flags=re.S
        ))
        opts = [(m.group(1), m.group(2).strip()) for m in opt_matches]

    return q_no, stem, opts


def extract_turkish_block(pdf: pdfplumber.PDF) -> str:
    """Concatenate only the TÜRKÇE pages into one text blob."""
    turkce_page_indices = []

    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if "TÜRKÇE" in text:
            turkce_page_indices.append(i)

    # for this booklet, cover and answer key also contain "TÜRKÇE"; ignore first & last
    turkce_page_indices = [i for i in turkce_page_indices if 0 < i < len(pdf.pages) - 1]

    if not turkce_page_indices:
        raise ValueError("No TÜRKÇE pages found in PDF")

    start = min(turkce_page_indices)
    end = max(turkce_page_indices)

    combined = ""
    for i in range(start, end + 1):
        combined += "\n\n===PAGE %d===\n" % (i + 1)
        combined += pdf.pages[i].extract_text() or ""

    # --- cleaning headers / footers / boilerplate ---
    clean = combined

    patterns = [
        r"SINAVLA ÖĞRENCİ ALACAK ORTAÖĞRETİM KURUMLARINA İLİŞKİN MERKEZÎ SINAV",
        r"A \(ÖDSGM\)2024-2025 EĞİTİM - ÖĞRETİM YILI",
        r"Diğer sayfaya geçiniz\.",
        r"A31\.\s*Bu\s*testte\s*20\s*soru\s*vardır\.",
        r"2\.\s*Cevaplarınızı,\s*cevap\s*kâğıdına\s*ișaretleyiniz\.",
        r"A\s*\(ÖDSGM\)TÜRKÇE",
        r"A\(ÖDSGM\)TÜRKÇE",
    ]
    for p in patterns:
        clean = re.sub(p, "", clean)

    # remove our page markers (if any)
    clean = re.sub(r"===PAGE \d+===\n", "", clean)

    # fix "A3.", "A5." etc → "3.", "5."
    clean = re.sub(r"A(\d{1,2})\.", r"\1.", clean)

    # tabs → space, compress spaces
    clean = clean.replace("\t", " ")
    clean = re.sub(r"[ ]{2,}", " ", clean)

    return clean.strip()


def find_question_chunks(clean_text: str):
    """Return raw chunks for 1–20 using the positions of '1.', '2.', ... '20.'."""
    positions = []
    for n in range(1, 21):
        s = f"{n}."
        idx = clean_text.find(s)
        if idx == -1:
            raise ValueError(f"Question number {n} not found in text.")
        positions.append(idx)

    chunks = []
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(clean_text)
        chunk = clean_text[start:end].strip()
        chunks.append(chunk)

    return chunks


def extract_answer_key(pdf: pdfplumber.PDF):
    """
    Reads last page (answer key) and returns a dict:
    {1: 'B', 2: 'A', ..., 20: 'D'}
    """
    last_page = pdf.pages[-1]
    t = last_page.extract_text() or ""

    # Pattern: '1.   B' etc. (may have variable whitespace)
    pairs = re.findall(r"(\d{1,2})\.\s*([A-D])", t)
    answers = {}
    for num_str, letter in pairs:
        num = int(num_str)
        if 1 <= num <= 20:  # Türkçe has 20 questions
            answers[num] = letter
    
    if len(answers) != 20:
        raise ValueError(f"Expected 20 answers, but only found {len(answers)}")
    
    return answers


def infer_topic_and_difficulty(stem_text: str) -> tuple:
    """
    Infer topic name and difficulty from question stem using keyword matching.
    
    Returns: (topic_name, difficulty)
    """
    stem_lower = stem_text.lower()
    
    # Topic inference based on keywords
    # Paragraf / Okuma Anlama
    if any(word in stem_lower for word in ["parçada", "bu parça", "parçanın", 
                                             "paragrafta", "paragrafın", "parçanın ana düşüncesi",
                                             "metinde", "metinle"]):
        topic = "Paragraf – Okuma Anlama"
    
    # Sözcükte Anlam
    elif any(word in stem_lower for word in ["sözcük", "sözcüğü", "sözcüğün", 
                                              "kelime", "deyim", "atasözü", "anlamı",
                                              "sözcüklerin", "kelimesi"]):
        topic = "Sözcükte Anlam"
    
    # Cümlede Anlam
    elif any(word in stem_lower for word in ["cümlede", "cümlelerin", "cümlelerden",
                                              "cümlesinde", "cümlesiyle", "cümlesinden",
                                              "bu cümlede"]):
        topic = "Cümlede Anlam"
    
    # Yazım ve Noktalama
    elif any(word in stem_lower for word in ["yazım", "yazılışı", "bitişik mi ayrı mı",
                                              "noktalama", "virgül", "nokta", 
                                              "kesme işareti", "büyük harf"]):
        topic = "Yazım ve Noktalama"
    
    # Fallback
    else:
        topic = "Türkçe – Diğer"
    
    # Difficulty inference based on stem length and complexity
    # Simple heuristic: longer stems with more complex structures → harder
    words = stem_lower.split()
    if len(words) < 15:
        difficulty = "EASY"
    elif len(words) < 30:
        difficulty = "MEDIUM"
    else:
        difficulty = "HARD"
    
    return topic, difficulty


def build_turkish_questions(pdf_path: str, auto_assign_topic: bool = True):
    """
    Parse PDF and extract all 20 Türkçe questions.
    
    Args:
        pdf_path: Path to the PDF file
        auto_assign_topic: If True, infer topic_name from question stem.
                          If False, use default "Türkçe Konusu 1"
    
    Returns:
        List of question dicts with keys: subject_code, topic_name, difficulty, 
        stem_text, estimated_time_seconds, options
    """
    with pdfplumber.open(pdf_path) as pdf:
        clean_text = extract_turkish_block(pdf)
        chunks = find_question_chunks(clean_text)
        answer_key = extract_answer_key(pdf)

    questions = []
    for raw in chunks:
        q_parsed = parse_question_chunk(raw)
        if q_parsed is None:
            continue
        
        q_no, stem_raw, opts_raw = q_parsed
        stem_clean = normalize_text(stem_raw)

        # Infer topic and difficulty if enabled
        if auto_assign_topic:
            topic_name, difficulty = infer_topic_and_difficulty(stem_clean)
        else:
            topic_name = "Türkçe Konusu 1"
            difficulty = "MEDIUM"

        # handle Q16 (only visuals) specially: create placeholder option texts
        if q_no == 16 and len(opts_raw) == 0:
            opts = [
                {"label": "A", "text": "Görsel A"},
                {"label": "B", "text": "Görsel B"},
                {"label": "C", "text": "Görsel C"},
                {"label": "D", "text": "Görsel D"},
            ]
        else:
            opts = [
                {"label": label, "text": clean_option_text(text)}
                for label, text in opts_raw
            ]

        # plug answer key
        correct = answer_key.get(q_no)
        for o in opts:
            o["is_correct"] = (o["label"] == correct)

        question = {
            "subject_code": "TURKISH",
            "topic_name": topic_name,
            "difficulty": difficulty,
            "stem_text": stem_clean,
            "estimated_time_seconds": 90,
            "options": opts,
        }
        questions.append(question)

    return questions


if __name__ == "__main__":
    # Test the parser
    try:
        # Parse with auto topic assignment (default)
        questions = build_turkish_questions("2025sozelbolum.pdf", auto_assign_topic=True)
        
        # quick sanity check
        print(f"✅ Parsed {len(questions)} Türkçe questions\n")
        
        # Group by topic
        topics = {}
        for q in questions:
            topic = q["topic_name"]
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(q)
        
        print("📊 Questions by Topic:")
        for topic, qs in sorted(topics.items()):
            print(f"  {topic}: {len(qs)} questions")
        
        print("\n📋 Questions with auto-assigned topics:\n")
        for i, q in enumerate(questions, start=1):
            print(f"Q{i}: [{q['difficulty']}] [{q['topic_name']}]")
            print(f"    {q['stem_text'][:100]}...")
            for opt in q["options"]:
                flag = "✅" if opt["is_correct"] else "  "
                print(f"    {flag} {opt['label']}) {opt['text'][:70]}...")
            print()
    except FileNotFoundError:
        print("❌ Error: 2025sozelbolum.pdf not found")
        print("   Please place the PDF file in the same directory as this script")
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
