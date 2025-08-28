import streamlit as st
import fitz  # PyMuPDF
import io
import re
from pathlib import Path

# ====== Özel Font ve CSS ======
DEJAVU_FONT_PATH = "fonts/DejaVuSans.ttf"  # fonts klasörüne indirdiğin .ttf dosyasını koy

st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'DejaVuSans';
        src: url('{DEJAVU_FONT_PATH}');
    }}
    html, body, [class*="css"] {{
        font-family: 'DejaVuSans', sans-serif;
    }}
    /* Sidebar'ı gizle */
    .css-1d391kg {{display: none;}}
    .css-1v3fvcr {{padding: 0;}}
    </style>
""", unsafe_allow_html=True)

# ====== PDF Çeviri Sınıfı ======
class FullStreamlitTurkishTranslator:
    def __init__(self):
        self.load_complete_glossary()
        self.stats = {'pages_processed': 0, 'overlays_added': 0, 'translations_made': 0}

    def load_complete_glossary(self):
        """Tam Türkçe çeviri sözlüğü - rapordaki tüm terimler dahil"""
        self.glossary = {
            # Ana Başlıklar ve Bölümler
            "Social Media Insights": "Sosyal Medya Analitikleri",
            "Community growth": "Topluluk büyümesi",
            "Posts viewed in period": "Dönemde görüntülenen gönderiler",
            "Demographics": "Demografi",
            "Demographics: countries and cities": "Demografi: ülkeler ve şehirler",
            "Demographics: gender and age": "Demografi: cinsiyet ve yaş",
            "Page impressions": "Sayfa gösterimleri",
            "Top 10 countries": "İlke 10 ülke",
            "Top 10 cities": "İlk 10 şehir",
            "Clicks on page": "Sayfadaki tıklamalar",
            "Posts published in period": "Dönemde yayınlanan gönderiler",
            "Stories published in period": "Dönemde yayınlanan hikayeler",
            "Reels published in period": "Dönemde yayınlanan reels",
            "Interactions of published posts": "Yayınlanan gönderilerin etkileşimleri",
            "Interactions of published reels": "Yayınlanan reels etkileşimleri",
            "Interactions of published stories": "Yayınlanan hikayelerin etkileşimleri",
            "Reach of published posts": "Yayınlanan gönderilerin erişimi",
            "Reach of published reels": "Yayınlanan reels erişimi",
            "Average reach per day": "Günlük ortalama erişim",
            "Promoted reels": "Sponsorlu reels",
            "Competitors": "Rakipler",
            
            # Sıralama ve Gösterim İfadeleri
            "Ranking of posts": "Gönderilerin sıralaması",
            "Ranking of stories": "Hikayelerin sıralaması",
            "Ranking of reels": "Reels sıralaması",
            "Ranking of hashtags": "Hashtaglerin sıralaması",
            "Showing posts sorted by impressions": "Gösterimlere göre sıralanan gönderiler",
            "Showing posts sorted by engagement": "Etkileşime göre sıralanan gönderiler",
            "Showing posts sorted by likes": "Beğenilere göre sıralanan gönderiler",
            "Showing stories sorted by date": "Tarihe göre sıralanan hikayeler",
            "Showing hashtags sorted by views": "Görüntülemeye göre sıralanan hashtagler",
            "Showing competitors sorted by followers": "Takipçilere göre sıralanan rakipler",
            "Showing sponsored posts sorted by video views": "Video görüntülemelerine göre sıralanan sponsorlu gönderiler",
            # Metrikler ve KPI'lar
            "Followers": "Takipçiler",
            "Following": "Takip Edilen",
            "Total content": "Toplam içerik",
            "Acquired likes": "Kazanılan beğeniler",
            "Lost likes": "Kaybedilen beğeniler",
            "Impressions": "Gösterimler",
            "Reactions": "Tepkiler",
            "Comments": "Yorumlar",
            "Shares": "Paylaşımlar",
            "Engagement": "Etkileşim",
            "Reach": "Erişim",
            "Views": "Görüntülemeler",
            "Clicks": "Tıklamalar",
            "Likes": "Beğeniler",
            "Posts": "Gönderiler",
            "Stories": "Hikayeler",
            "Reels": "Reels",
            "Published": "Yayınlandı",
            "Text": "Metin",
            "Image": "Görsel",
            "Video": "Video",
            "Link": "Bağlantı",
            "Photo": "Fotoğraf",
            "Type": "Tür",
            "Interactions": "Etkileşimler",
            "Video views": "Video görüntülemeleri",
            "Link clicks": "Bağlantı tıklamaları",
            "Actions": "Eylemler",
            "Saved": "Kaydedilen",
            "Replies": "Yanıtlar",
            "Tap back": "Geri dokunma",
            "Tap forward": "İleri dokunma",
            "Exits": "Çıkışlar",
            "Page visits": "Sayfa ziyaretleri",
            "Total clicks": "Toplam tıklamalar",
            "Followers balance": "Takipçi dengesi",
            "Gender": "Cinsiyet",
            "Ages": "Yaşlar",
            "Time watched": "İzleme süresi",
            "Avg. time watched": "Ort. izleme süresi",
            "Spent": "Harcanan",
            # Ortalama ve Hesaplamalar
            "Average reach": "Ortalama erişim",
            "per day": "günlük",
            "Avg reach per post": "Gönderi başına ort. erişim",
            "Avg reach per reel": "Reels başına ort. erişim",
            "Avg reach per story": "Hikaye başına ort. erişim",
            # Ülkeler ve şehirler örnek
            "Turkey": "Türkiye",
            "Cyprus": "Kıbrıs",
            "United Kingdom": "Birleşik Krallık",
            "United States": "Amerika Birleşik Devletleri",
            "Istanbul": "İstanbul",
            "Kyrenia": "Girne",
            # (Listeyi kendi sözlüğüne göre devam ettir)
        }

    def translate_text(self, text):
        """Tam sözlük ile çeviri, Türkçe karakter desteği ile"""
        if not text or len(text.strip()) < 2:
            return text

        skip_patterns = [
            r'^\d+[\d\s,.\-%€$£₺KkMm]*$', r'^\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}$',
            r'^\d{4}[./\-]\d{1,2}[./\-]\d{1,2}$', r'^[+\-]\d+[\d\s,.\-%€$£₺KkMm]*$', 
            r'^#\w+$', r'^@\w+$', r'^https?://', r'^\w+@\w+\.\w+$',
            r'^\d+h\s+\d+m\s+\d+s$', r'^\d+[sm]$'
        ]
        for pattern in skip_patterns:
            if re.match(pattern, text.strip()):
                return text

        result = text.strip()

        # 🔹 Tam eşleşme
        for en, tr in self.glossary.items():
            if result.lower() == en.lower():
                self.stats['translations_made'] += 1
                return tr

        # 🔹 Kısmi eşleşmeler, uzun ifadeler önce
        for en, tr in sorted(self.glossary.items(), key=len, reverse=True):
            if len(en) > 3:
                pattern = r'(?<!\w)' + re.escape(en) + r'(?!\w)'
                new_result = re.sub(pattern, tr, result, flags=re.IGNORECASE | re.UNICODE)
                if new_result != result:
                    result = new_result
                    self.stats['translations_made'] += 1

        return result

    def add_text_overlay(self, page, bbox, translated_text, font_size):
        try:
            x0, y0, x1, y1 = bbox
            padding = 3
            page.draw_rect(fitz.Rect(x0-padding, y0-padding, x1+padding, y1+padding), color=None, fill=(1,1,1), width=0)
            insert_point = fitz.Point(x0, y1-1)
            fonts = ["helv", "times", "cour"]
            for font_name in fonts:
                try:
                    result = page.insert_text(insert_point, translated_text, fontname=font_name, fontsize=max(6,font_size*0.85), color=(0,0,0), encoding=fitz.TEXT_ENCODING_UTF8)
                    if result>0:
                        self.stats['overlays_added'] +=1
                        return True
                except: continue
            page.insert_text(insert_point, translated_text, fontsize=max(6,font_size*0.8), color=(0,0,0))
            self.stats['overlays_added'] +=1
            return True
        except:
            return False

    def translate_pdf_bytes(self, pdf_bytes, progress_callback=None):
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(pdf_document)
            for page_num in range(total_pages):
                if progress_callback: progress_callback(page_num+1,total_pages)
                page = pdf_document.load_page(page_num)
                text_dict = page.get_text("dict")
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                original_text = span["text"].strip()
                                if original_text and len(original_text)>1:
                                    translated_text = self.translate_text(original_text)
                                    if translated_text != original_text:
                                        bbox = span["bbox"]
                                        font_size = span.get("size",10)
                                        self.add_text_overlay(page,bbox,translated_text,font_size)
                self.stats['pages_processed'] +=1
            output_buffer = io.BytesIO()
            pdf_document.save(output_buffer, garbage=4, deflate=True, clean=True)
            pdf_document.close()
            return output_buffer.getvalue()
        except Exception as e:
            st.error(f"PDF işleme hatası: {str(e)}")
            return None

# ====== Streamlit Ana Sayfa ======
st.set_page_config(page_title="Türkçe PDF Çevirici", page_icon="📄", layout="wide")
st.title("📄 Türkçe PDF Çevirici")
st.markdown("**Sosyal medya analitik raporlarını tam Türkçe'ye çevirin**")

uploaded_file = st.file_uploader("PDF dosyanızı buraya sürükleyin", type=['pdf'])

if uploaded_file:
    st.success(f"✅ {uploaded_file.name} yüklendi")
    if st.button("🚀 Türkçe'ye Çevir"):
        translator = FullStreamlitTurkishTranslator()
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current_page,total_pages):
            progress_bar.progress(current_page/total_pages)
            status_text.text(f"📄 Sayfa {current_page}/{total_pages} çeviriliyor...")

        with st.spinner("PDF çeviriliyor..."):
            translated_pdf = translator.translate_pdf_bytes(uploaded_file.getvalue(), progress_callback=update_progress)

        if translated_pdf:
            st.success("🎉 Çeviri tamamlandı!")
            st.download_button(
                label="📥 Türkçe PDF'yi İndir",
                data=translated_pdf,
                file_name=f"{Path(uploaded_file.name).stem}_TURKCE.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.balloons()
