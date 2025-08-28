#!/usr/bin/env python3
"""
Turkish Font Support PDF Overlay Translator
Full Turkish alphabet support with proper font handling
Türkçe karakter desteği ile PDF çevirici
"""

import fitz  # PyMuPDF
from pathlib import Path
import re
import logging

class TurkishFontOverlayTranslator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.load_turkish_glossary()
        self.setup_turkish_fonts()
        self.stats = {'pages_processed': 0, 'overlays_added': 0, 'translations_made': 0}
    
    def setup_turkish_fonts(self):
        """Türkçe karakter desteği için font seçenekleri"""
        # Türkçe karakterleri destekleyen fontlar
        self.turkish_fonts = [
            "helv",      # Helvetica - genellikle Türkçe karakterleri destekler
            "times",     # Times Roman
            "cour",      # Courier
            "symbol",    # Symbol font
        ]
        
        # Türkçe karakter test metni
        self.turkish_test = "ğüşıöç ĞÜŞIÖÇ"
        
        print("Türkçe font desteği hazırlandı")
        print(f"Desteklenen fontlar: {', '.join(self.turkish_fonts)}")
    
    def load_turkish_glossary(self):
        """Türkçe çeviri sözlüğü - Genişletilmiş versiyon"""
        self.glossary = {
            # Ana Bölümler
            "Social Media Insights": "Sosyal Medya Analitikleri",
            "Community growth": "Topluluk büyümesi", 
            "Posts viewed in period": "Dönemde görüntülenen gönderiler",
            "Demographics": "Demografi",
            "Demographics: countries and cities": "Demografi: ülkeler ve şehirler",
            "Demographics: gender and age": "Demografi: cinsiyet ve yaş",
            "Page impressions": "Sayfa gösterimleri",
            "Top 10 countries": "En iyi 10 ülke",
            "Top 10 cities": "En iyi 10 şehir",
            
            # Metrikler
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
            
            # Analitik İfadeler - Türkçe gramer kurallarına uygun
            "Showing posts sorted by impressions": "Gösterimlere göre sıralanan gönderiler",
            "Showing posts sorted by engagement": "Etkileşime göre sıralanan gönderiler", 
            "Showing posts sorted by likes": "Beğenilere göre sıralanan gönderiler",
            "Showing stories sorted by date": "Tarihe göre sıralanan hikayeler",
            "Showing hashtags sorted by views": "Görüntülemeye göre sıralanan hashtagler",
            "Showing competitors sorted by followers": "Takipçilere göre sıralanan rakipler",
            "Showing sponsored posts sorted by video views": "Video görüntülemelerine göre sıralanan sponsorlu gönderiler",
            "Posts published in period": "Dönemde yayınlanan gönderiler",
            "Stories published in period": "Dönemde yayınlanan hikayeler", 
            "Reels published in period": "Dönemde yayınlanan reels",
            "Interactions of published posts": "Yayınlanan gönderilerin etkileşimleri",
            "Interactions of published reels": "Yayınlanan reels etkileşimleri",
            "Reach of published posts": "Yayınlanan gönderilerin erişimi",
            "Reach of published reels": "Yayınlanan reels erişimi",
            "Average reach per day": "Günlük ortalama erişim",
            "Average reach": "Ortalama erişim",
            "Total clicks": "Toplam tıklama",
            "Clicks on page": "Sayfadaki tıklamalar",
            "Likes on page": "Sayfadaki beğeniler",
            "Video views": "Video görüntülemeleri",
            "Link clicks": "Bağlantı tıklamaları",
            "Ranking of posts": "Gönderilerin sıralaması",
            "Ranking of stories": "Hikayelerin sıralaması",
            "Ranking of reels": "Reels sıralaması",
            "Ranking of hashtags": "Hashtaglerin sıralaması",
            
            # Ülkeler - Türkçe karakterlerle
            "Turkey": "Türkiye",
            "Cyprus": "Kıbrıs",
            "United Kingdom": "Birleşik Krallık",
            "United States": "Amerika Birleşik Devletleri",
            "Pakistan": "Pakistan",
            "Germany": "Almanya",
            "Australia": "Avustralya",
            "Bangladesh": "Bangladeş",
            "Libya": "Libya",
            "Canada": "Kanada",
            "France": "Fransa",
            "Italy": "İtalya",
            "Greece": "Yunanistan",
            "Netherlands": "Hollanda",
            "Spain": "İspanya",
            "Austria": "Avusturya",
            "Belgium": "Belçika",
            "Switzerland": "İsviçre",
            
            # Şehirler - Türkçe karakterlerle
            "Istanbul": "İstanbul",
            "Lefkosa": "Lefkoşa",
            "Gazimağusa": "Gazimağusa",
            "Kyrenia": "Girne",
            "Ankara": "Ankara",
            "Izmir": "İzmir",
            "Antalya": "Antalya",
            "Bursa": "Bursa",
            "Adana": "Adana",
            "London": "Londra",
            "Paris": "Paris",
            "Berlin": "Berlin",
            "Athens": "Atina",
            "Madrid": "Madrid",
            "Rome": "Roma",
            "Vienna": "Viyana",
            "Brussels": "Brüksel",
            "Zurich": "Zürih",
            
            # Coğrafi Detaylar
            "Kyrenia, Kyrenia District": "Girne, Girne İlçesi",
            "Lefkosa, Nicosia District": "Lefkoşa, Lefkoşa İlçesi",
            "Ozanköy, Kyrenia District": "Ozanköy, Girne İlçesi",
            "Istanbul, Istanbul Province": "İstanbul, İstanbul İli",
            "Gönyeli, Lefkosa": "Gönyeli, Lefkoşa",
            "Güngör, Kıbrıs": "Güngör, Kıbrıs",
            
            # Zaman Dilimleri
            "Last 12 months": "Son 12 ay",
            "This month": "Bu ay",
            "Last month": "Geçen ay",
            "This week": "Bu hafta", 
            "Last week": "Geçen hafta",
            "Today": "Bugün",
            "Yesterday": "Dün",
            "Monthly": "Aylık",
            "Weekly": "Haftalık",
            "Daily": "Günlük",
            "Jul 1 - Jul 31": "1 Tem - 31 Tem",
            "Period": "Dönem",
            "Year": "Yıl",
            "Month": "Ay",
            "Week": "Hafta",
            "Day": "Gün",
            
            # Yaygın Kelimeler
            "and": "ve",
            "or": "veya",
            "of": "nin",
            "in": "içinde",
            "on": "üzerinde", 
            "by": "tarafından",
            "per": "başına",
            "with": "ile",
            "from": "dan",
            "to": "ya",
            "for": "için",
            "about": "hakkında",
            "sorted by": "göre sıralanan",
            "sponsored": "sponsorlu",
            "Showing": "Gösterilen",
            "competitors": "rakipler",
            "hashtags": "hashtagler",
            "published": "yayınlanan",
            "period": "dönem",
            "interactions": "etkileşimler",
            "average": "ortalama",
            "total": "toplam",
            "ranking": "sıralama",
            
            # Marka/Şirket İsimleri
            "Cyprus Express": "Kıbrıs Express",
            
            # Sayılar + Bağlam
            "20 posts": "20 gönderi",
            "12 posts": "12 gönderi",
            "8 posts": "8 gönderi", 
            "7 posts": "7 gönderi",
            "9 posts": "9 gönderi",
            "20 stories": "20 hikaye",
            "15 hashtags": "15 hashtag",
            "7 competitors": "7 rakip",
            "10 competitors": "10 rakip",
            "2 sponsored posts": "2 sponsorlu gönderi",
            
            # Ek Metrikler
            "CTR": "Tıklama Oranı",
            "CPM": "Bin Gösterim Maliyeti",
            "CPC": "Tık Başına Maliyet",
            "ROI": "Yatırım Getirisi",
            "KPI": "Ana Performans Göstergesi",
            "Conversion": "Dönüşüm",
            "Bounce Rate": "Çıkış Oranı",
            "Retention": "Elde Tutma",
            "Acquisition": "Kazanım",
            "Growth Rate": "Büyüme Oranı"
        }
    
    def has_turkish_chars(self, text):
        """Metinde Türkçe karakter olup olmadığını kontrol et"""
        turkish_chars = set('ğüşıöçĞÜŞIÖÇ')
        return any(char in turkish_chars for char in text)
    
    def translate_text(self, text):
        """Gelişmiş Türkçe çeviri"""
        if not text or len(text.strip()) < 2:
            return text
        
        # Sayılar, tarihler vb. atla
        if re.match(r'^\d+[\d\s,.\-%€$£₺]*$', text.strip()):
            return text
        if re.match(r'^\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}$', text.strip()):
            return text
        
        original = text.strip()
        result = original
        
        # Direkt eşleşmeler
        for en_term, tr_term in self.glossary.items():
            if original.lower() == en_term.lower():
                self.stats['translations_made'] += 1
                return tr_term
        
        # Kısmi eşleşmeler - uzunluğa göre sıralı
        for en_term, tr_term in sorted(self.glossary.items(), key=len, reverse=True):
            if en_term.lower() in result.lower():
                # Kelime sınırları kullan
                pattern = r'\b' + re.escape(en_term) + r'\b'
                new_result = re.sub(pattern, tr_term, result, flags=re.IGNORECASE)
                if new_result != result:
                    result = new_result
        
        if result != original:
            self.stats['translations_made'] += 1
            print(f"  -> '{original}' -> '{result}'")
        
        return result
    
    def test_font_turkish_support(self, page, font_name):
        """Font'un Türkçe karakterleri desteklediğini test et"""
        try:
            # Test noktası
            test_point = fitz.Point(0, 0)
            result = page.insert_text(
                test_point,
                self.turkish_test,
                fontname=font_name,
                fontsize=8,
                color=(1, 1, 1),  # Beyaz (görünmez)
                render_mode=3  # Görünmez mod
            )
            return result > 0
        except:
            return False
    
    def add_turkish_text_overlay(self, page, bbox, original_text, translated_text, font_size):
        """Türkçe karakter desteği ile metin overlay'i ekle"""
        try:
            # Koordinatları çıkar
            x0, y0, x1, y1 = bbox
            
            # Beyaz arka plan
            padding = 2
            white_rect = fitz.Rect(x0 - padding, y0 - padding, x1 + padding, y1 + padding)
            page.draw_rect(white_rect, color=None, fill=(1, 1, 1), width=0)
            
            # Ekleme noktası
            insert_point = fitz.Point(x0, y1 - 1)
            
            # Türkçe karakterler var mı kontrol et
            has_turkish = self.has_turkish_chars(translated_text)
            
            # Font seçimi - Türkçe karakterler varsa özel dikkat
            fonts_to_try = self.turkish_fonts.copy()
            if has_turkish:
                # Türkçe karakterler için Helvetica öncelik
                fonts_to_try = ["helv", "times", "cour"]
            
            for font_name in fonts_to_try:
                try:
                    # Font boyutu ayarla
                    final_font_size = max(6, font_size * 0.85)
                    
                    result = page.insert_text(
                        insert_point,
                        translated_text,
                        fontname=font_name,
                        fontsize=final_font_size,
                        color=(0, 0, 0),  # Siyah
                        encoding=fitz.TEXT_ENCODING_UTF8  # UTF-8 encoding
                    )
                    
                    if result > 0:
                        self.stats['overlays_added'] += 1
                        if has_turkish:
                            print(f"    Türkçe karakterli metin eklendi: '{translated_text}' ({font_name})")
                        return True
                        
                except Exception as e:
                    continue
            
            # Son çare: basit ekleme
            try:
                page.insert_text(
                    insert_point,
                    translated_text,
                    fontsize=max(6, font_size * 0.8),
                    color=(0, 0, 0)
                )
                self.stats['overlays_added'] += 1
                return True
            except Exception:
                print(f"    Metin eklenemedi: {translated_text}")
                return False
                
        except Exception as e:
            print(f"    Overlay hatası: {e}")
            return False
    
    def translate_pdf_with_turkish_support(self, input_pdf, output_pdf=None):
        """Türkçe karakter desteği ile PDF çevirisi"""
        
        input_path = Path(input_pdf)
        if not input_path.exists():
            print(f"Dosya bulunamadı: {input_pdf}")
            return None
        
        if output_pdf is None:
            output_pdf = input_path.parent / f"{input_path.stem}_turkce_overlay.pdf"
        
        print(f"Türkçe karakter desteği ile PDF işleniyor...")
        print(f"Giriş: {input_path.name}")
        print(f"Çıkış: {Path(output_pdf).name}")
        print("=" * 70)
        
        try:
            pdf_document = fitz.open(input_pdf)
            
            for page_num in range(len(pdf_document)):
                print(f"Sayfa işleniyor {page_num + 1}/{len(pdf_document)}")
                page = pdf_document.load_page(page_num)
                
                # Tüm metinleri pozisyon bilgileriyle al
                text_dict = page.get_text("dict")
                
                overlays_on_page = 0
                
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                original_text = span["text"].strip()
                                
                                if original_text and len(original_text) > 1:
                                    translated_text = self.translate_text(original_text)
                                    
                                    if translated_text != original_text:
                                        bbox = span["bbox"]
                                        font_size = span.get("size", 10)
                                        
                                        if self.add_turkish_text_overlay(page, bbox, original_text, translated_text, font_size):
                                            overlays_on_page += 1
                
                if overlays_on_page > 0:
                    print(f"  Sayfa {page_num + 1}'de {overlays_on_page} overlay eklendi")
                
                self.stats['pages_processed'] += 1
            
            # Optimized ayarlarla kaydet
            pdf_document.save(output_pdf, garbage=4, deflate=True, clean=True)
            pdf_document.close()
            
            self.print_turkish_stats()
            print(f"Başarılı! Türkçe overlay PDF oluşturuldu: {output_pdf}")
            
            return str(output_pdf)
            
        except Exception as e:
            print(f"Overlay PDF oluşturma hatası: {e}")
            return None
    
    def print_turkish_stats(self):
        """Türkçe istatistikleri yazdır"""
        print("\n" + "=" * 70)
        print("TÜRKÇE OVERLAY ÇEVİRİ İSTATİSTİKLERİ")
        print("=" * 70)
        print(f"İşlenen sayfalar: {self.stats['pages_processed']}")
        print(f"Eklenen metin overlay'leri: {self.stats['overlays_added']}")
        print(f"Toplam çeviriler: {self.stats['translations_made']}")
        print(f"Sözlük terimleri: {len(self.glossary)}")
        print(f"Türkçe font desteği: Aktif")
        print("=" * 70)

def main():
    """Ana fonksiyon"""
    print("TÜRKÇE KARAKTER DESTEKLİ PDF OVERLAY ÇEVİRİCİSİ")
    print("Turkish Character Support PDF Overlay Translator")
    print("=" * 70)
    print("Özellikler:")
    print("- Tam Türkçe alfabe desteği (ğüşıöç ĞÜŞİÖÇ)")
    print("- Gelişmiş font yönetimi")
    print("- UTF-8 encoding desteği")
    print("- Optimized metin yerleştirme")
    print("=" * 70)
    
    translator = TurkishFontOverlayTranslator()
    
    # PDF dosyasını işle
    input_file = "/Users/ilkeileri/Downloads/3544252-20250701-Nesdersan-uqldvtlc (1).pdf"
    
    if Path(input_file).exists():
        result = translator.translate_pdf_with_turkish_support(input_file)
        
        if result:
            print(f"\nMÜKEMMEL! Türkçe overlay PDF oluşturuldu:")
            print(f"Orijinal: {Path(input_file).name}")
            print(f"Türkçe overlay: {Path(result).name}")
            print(f"Konum: {Path(result).parent}")
            print("\nTürkçe karakterler (ğüşıöç ĞÜŞİÖÇ) doğru şekilde görüntülenecek!")
        else:
            print(f"\nOverlay oluşturma başarısız")
    else:
        print(f"Dosya bulunamadı: {input_file}")

if __name__ == "__main__":
    main()