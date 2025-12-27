"""
Geçmiş analizler için toplu prompt oluşturma
"""
import json


# Kullanıcı tarafından tanımlanan geçmiş analiz promptu
HISTORICAL_ANALYSIS_PROMPT = """
GÖREV: Sen, hareket bozuklukları (özellikle Parkinson) üzerine uzmanlaşmış bir Kıdemli Nörolog ve Klinik Danışmansın. Sana sunulan veriler, "Biyodijital Motor Analiz Terminali" üzerinden farklı seanslarda (oturumlarda) alınmış özet metriklerdir. Görevin; bu seanslar arasındaki verileri kıyaslayarak hastanın klinik tablosundaki değişimi analiz etmek ve profesyonel bir tıbbi geri bildirim raporu oluşturmaktır.

ANALİZ ODAĞI:

Sistemin teknik işleyişini veya hatalarını eleştirme.

Tamamen verilerin işaret ettiği semptom seyrine (iyileşme, kötüleşme veya stabilite) odaklan.

Farklı seanslar arasındaki korelasyonları "hasta performansı" perspektifinden yorumla.

GİRDİ VERİ SETLERİ (JSON):

{data}

1. SEMPTOM KARARLILIĞI VE TREMOR ANALİZİ (Modül A):

Seanslar boyunca titreme (tremor) frekansındaki ve şiddetindeki değişimler nelerdir? (Stabil mi kalıyor yoksa dalgalanma mı mevcut?)

Tespit edilen Hz değerlerinin (4-6 Hz aralığı baz alınarak) hastanın motor kontrolü üzerindeki etkisini yorumla.

2. KİNEMATİK PERFORMANS VE BRADİKİNEZİ SEYRİ (Modül B):

Hastanın hareket hızı ve hızlanma/yavaşlama trendleri seanslar arasında nasıl bir gelişim gösteriyor?

Hareket akıcılığındaki değişimleri bradikinezi literatürüyle ilişkilendirerek hastanın motor kapasitesini değerlendir.

3. NÖROMÜSKÜLER YORGUNLUK VE KOORDİNASYON (Modül C):

Tepki süreleri (ms) ve Yorgunluk Endeksi seanslar arasında nasıl farklılaşıyor?

Hastanın bilişsel-motor dayanıklılığı ve testler sırasındaki nöral iletim hızı hakkında ne söylenebilir?

4. GENEL KLİNİK SENTEZ VE SONUÇ:

Tüm seanslar birleştirildiğinde hastanın genel motor durumu nasıl bir seyir izlemektedir (Progresif ilerleme, plato evresi veya dönemsel dalgalanma)?

Hastanın günlük yaşam aktivitelerindeki potansiyel motor beceri seviyesi hakkında rasyonel bir öngörüde bulun.

ÖNEMLİ NOT: Bu rapor tamamen klinik verilere dayalı bir geri bildirim niteliğindedir. Teşhis koyma iddiası taşımaz, sadece objektif verilerin tıbbi literatürle sentezidir.

"""


def format_analysis_data(results_list):
    """
    Birden fazla analiz sonucunu metin formatına dönüştürür
    
    Args:
        results_list: Analiz sonuçları listesi (her biri bir dict)
        
    Returns:
        str: Formatlanmış analiz verileri
    """
    if not results_list:
        return ""
    
    # Her analizi formatla
    analysis_sections = []
    for idx, results in enumerate(results_list, 1):
        module_a = results.get('module_a', {})
        module_b = results.get('module_b', {})
        module_c = results.get('module_c', {})
        timestamp = results.get('analysis_datetime', results.get('timestamp', 'Bilinmiyor'))
        
        section = f"""ANALİZ {idx} (Tarih: {timestamp}):
• Tremor Frekans: {module_a.get('dominant_frequency_hz', 'N/A')} Hz
• Tremor Genlik: {module_a.get('signal_amplitude', 'N/A')}
• Ortalama Hız: {module_b.get('avg_velocity_mm_s', 'N/A')} mm/s
• Maksimum Hız: {module_b.get('max_velocity_mm_s', 'N/A')} mm/s
• Hız Eğimi: {module_b.get('velocity_slope', 'N/A')}
• Reaksiyon Süresi: {module_c.get('avg_reaction_time_ms', 'N/A')} ms
• Yorgunluk Endeksi: {module_c.get('fatigue_index', 'N/A')}"""
        
        analysis_sections.append(section)
    
    # Tüm analizleri birleştir
    return "\n\n".join(analysis_sections)


def create_historical_analysis_prompt(results_list):
    """
    Kullanıcı tanımlı prompt şablonuna analiz verilerini ekler
    
    Args:
        results_list: Analiz sonuçları listesi (her biri bir dict)
        
    Returns:
        str: Oluşturulan toplu analiz prompt metni
    """
    if not results_list:
        return None
    
    # Veriyi formatla
    data_text = format_analysis_data(results_list)
    
    # Kullanıcı tanımlı prompt'a veriyi ekle
    prompt = HISTORICAL_ANALYSIS_PROMPT.format(data=data_text)
    
    return prompt


def create_prompt_from_files(json_filepaths):
    """
    Birden fazla JSON dosyasından toplu prompt oluşturur
    
    Args:
        json_filepaths: JSON dosya yolları listesi
        
    Returns:
        str: Oluşturulan prompt metni veya None
    """
    try:
        results_list = []
        
        for filepath in json_filepaths:
            with open(filepath, 'r', encoding='utf-8') as f:
                results = json.load(f)
                results_list.append(results)
        
        return create_historical_analysis_prompt(results_list)
        
    except Exception as e:
        print(f"Toplu prompt oluşturma hatası: {e}")
        return None
