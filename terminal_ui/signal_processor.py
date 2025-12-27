"""
Sinyal İşleme ve Öznitelik Çıkarımı Modülü
Parkinson Hastalığı Analizi için Sensör Verilerini İşleme

Bu modül 3 farklı sensörden gelen ham verileri işleyip klinik metriklere dönüştürür:
- Modül A: Tremor Analizi (FFT ile frekans analizi)
- Modül B: Bradikinezi Analizi (Hız hesaplama ve trend analizi)
- Modül C: Koordinasyon Analizi (Reaksiyon zamanı ve yorgunluk endeksi)
"""

import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')


def analyze_tremor(csv_path):
    """
    Modül A: Tremor Analizi - LDR Sensörü
    
    FFT kullanarak titreşim frekansını tespit eder.
    
    Args:
        csv_path (str): CSV dosya yolu
        
    Returns:
        dict: {
            'dominant_frequency_hz': Baskın frekans (1-15 Hz aralığı),
            'signal_amplitude': Sinyal şiddeti (genlik)
        }
    """
    try:
        # CSV'yi oku
        df = pd.read_csv(csv_path)
        
        # Sütun isimlerini kontrol et
        if len(df.columns) < 2:
            raise ValueError("CSV dosyası en az 2 sütun içermelidir")
        
        # Boş veya çok kısa veri kontrolü
        if len(df) < 10:
            raise ValueError("Yeterli veri yok (en az 10 örnek gerekli)")
        
        # Zaman ve LDR değerlerini al
        time = df.iloc[:, 0].values  # İlk sütun: Zaman (s)
        ldr_values = df.iloc[:, 1].values  # İkinci sütun: LDR Değeri
        
        # NaN değerleri temizle
        valid_mask = ~np.isnan(ldr_values) & ~np.isnan(time)
        time = time[valid_mask]
        ldr_values = ldr_values[valid_mask]
        
        if len(ldr_values) < 10:
            raise ValueError("NaN temizleme sonrası yeterli veri kalmadı")
        
        # ADIM 1: Detrend - sinyalden ortalamayı çıkar
        signal_mean = np.mean(ldr_values)
        detrended_signal = ldr_values - signal_mean
        
        # ADIM 2: FFT uygula
        N = len(detrended_signal)
        
        # Örnekleme frekansını hesapla
        time_diff = np.diff(time)
        avg_time_diff = np.mean(time_diff)
        sampling_rate = 1.0 / avg_time_diff  # Hz
        
        # FFT hesapla
        fft_values = fft(detrended_signal)
        frequencies = fftfreq(N, d=avg_time_diff)
        
        # Sadece pozitif frekansları al
        positive_freq_mask = frequencies > 0
        frequencies = frequencies[positive_freq_mask]
        fft_magnitude = np.abs(fft_values[positive_freq_mask])
        
        # ADIM 3: 1-15 Hz aralığında baskın frekansı bul
        freq_range_mask = (frequencies >= 1.0) & (frequencies <= 15.0)
        
        if not np.any(freq_range_mask):
            # Eğer 1-15 Hz aralığında veri yoksa, 0-15 Hz'e genişlet
            freq_range_mask = (frequencies >= 0.0) & (frequencies <= 15.0)
        
        filtered_frequencies = frequencies[freq_range_mask]
        filtered_magnitudes = fft_magnitude[freq_range_mask]
        
        if len(filtered_magnitudes) == 0:
            raise ValueError("1-15 Hz aralığında frekans bulunamadı")
        
        # En yüksek genliğe sahip frekansı bul
        max_magnitude_index = np.argmax(filtered_magnitudes)
        dominant_frequency = filtered_frequencies[max_magnitude_index]
        signal_amplitude = filtered_magnitudes[max_magnitude_index]
        
        return {
            'dominant_frequency_hz': round(float(dominant_frequency), 2),
            'signal_amplitude': round(float(signal_amplitude), 2),
            'status': 'success'
        }
        
    except FileNotFoundError:
        return {
            'dominant_frequency_hz': None,
            'signal_amplitude': None,
            'status': 'error',
            'error_message': 'Dosya bulunamadı'
        }
    except Exception as e:
        return {
            'dominant_frequency_hz': None,
            'signal_amplitude': None,
            'status': 'error',
            'error_message': str(e)
        }


def analyze_bradykinesia(csv_path):
    """
    Modül B: Bradikinezi Analizi - Ultrasonik Sensör
    
    Mesafe-zaman verisinden hız hesaplar, trend analizi ve frekans analizi yapar.
    
    Args:
        csv_path (str): CSV dosya yolu
        
    Returns:
        dict: {
            'avg_velocity_mm_s': Ortalama hız (mm/s),
            'max_velocity_mm_s': Maksimum hız (mm/s),
            'velocity_slope': Hız değişim eğimi (negatif = yavaşlama)
        }
    """
    try:
        # CSV'yi oku
        df = pd.read_csv(csv_path)
        
        # Sütun kontrolü
        if len(df.columns) < 2:
            raise ValueError("CSV dosyası en az 2 sütun içermelidir")
        
        # Boş veri kontrolü
        if len(df) < 2:
            raise ValueError("Hız hesabı için en az 2 örnek gerekli")
        
        # Zaman ve mesafe değerlerini al
        time = df.iloc[:, 0].values  # İlk sütun: Zaman (s)
        distance = df.iloc[:, 1].values  # İkinci sütun: Mesafe (mm)
        
        # NaN değerleri temizle
        valid_mask = ~np.isnan(distance) & ~np.isnan(time)
        time = time[valid_mask]
        distance = distance[valid_mask]
        
        if len(distance) < 2:
            raise ValueError("NaN temizleme sonrası yeterli veri kalmadı")
        
        # ADIM 1: Hız hesapla (v = Δd / Δt)
        time_diff = np.diff(time)  # Δt
        distance_diff = np.diff(distance)  # Δd
        
        # Sıfıra bölme kontrolü
        time_diff[time_diff == 0] = 1e-6  # Çok küçük bir değer
        
        velocity = distance_diff / time_diff  # mm/s
        
        # Aşırı değerleri filtrele (outlier removal)
        # Mesafe sensöründe ara sıra 0.0 veya çok yüksek değerler olabiliyor
        velocity_abs = np.abs(velocity)
        median_vel = np.median(velocity_abs)
        mad = np.median(np.abs(velocity_abs - median_vel))
        
        # Modified Z-score ile outlier tespiti
        if mad > 0:
            modified_z_scores = 0.6745 * (velocity_abs - median_vel) / mad
            outlier_mask = modified_z_scores < 3.5  # 3.5 sigma
            velocity_filtered = velocity[outlier_mask]
        else:
            velocity_filtered = velocity
        
        if len(velocity_filtered) == 0:
            velocity_filtered = velocity  # Fallback
        
        # ADIM 2: İstatistikler
        avg_velocity = np.mean(np.abs(velocity_filtered))
        max_velocity = np.max(np.abs(velocity_filtered))
        
        # ADIM 3: Linear Regression ile trend analizi
        # Hızın zaman içinde nasıl değiştiğini bul
        velocity_time = time[1:]  # Hız değerleri bir eleman kısa
        
        # Outlier filtrelenmiş indeksleri al
        if mad > 0 and np.any(outlier_mask):
            velocity_time_filtered = velocity_time[outlier_mask]
        else:
            velocity_time_filtered = velocity_time
            
        if len(velocity_time_filtered) < 2:
            velocity_time_filtered = velocity_time
            velocity_filtered = velocity
        
        # Reshape for sklearn
        X = velocity_time_filtered.reshape(-1, 1)
        y = velocity_filtered.reshape(-1, 1)
        
        # Linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        velocity_slope = float(model.coef_[0][0])
        
        # ADIM 4: FFT ile frekans analizi (Modül A'daki gibi)
        # Mesafe sinyalinin frekans içeriğini analiz et
        if len(distance) >= 10:
            # Detrend - sinyalden ortalamayı çıkar
            signal_mean = np.mean(distance)
            detrended_signal = distance - signal_mean
            
            # FFT uygula
            N = len(detrended_signal)
            
            # Örnekleme frekansını hesapla
            time_diff_avg = np.mean(np.diff(time))
            sampling_rate = 1.0 / time_diff_avg  # Hz
            
            # FFT hesapla
            fft_values = fft(detrended_signal)
            frequencies = fftfreq(N, d=time_diff_avg)
            
            # Sadece pozitif frekansları al
            positive_freq_mask = frequencies > 0
            frequencies = frequencies[positive_freq_mask]
            fft_magnitude = np.abs(fft_values[positive_freq_mask])
            
            # 0.1-10 Hz aralığında baskın frekansı bul (hareket frekansları)
            freq_range_mask = (frequencies >= 0.1) & (frequencies <= 10.0)
            
            if np.any(freq_range_mask):
                filtered_frequencies = frequencies[freq_range_mask]
                filtered_magnitudes = fft_magnitude[freq_range_mask]
                
                # En yüksek genliğe sahip frekansı bul
                max_magnitude_index = np.argmax(filtered_magnitudes)
                dominant_frequency = filtered_frequencies[max_magnitude_index]
            else:
                dominant_frequency = 0.0
        else:
            dominant_frequency = 0.0
        
        return {
            'avg_velocity_mm_s': round(float(avg_velocity), 2),
            'max_velocity_mm_s': round(float(max_velocity), 2),
            'velocity_slope': round(velocity_slope, 4),
            'status': 'success'
        }
        
    except FileNotFoundError:
        return {
            'avg_velocity_mm_s': None,
            'max_velocity_mm_s': None,
            'velocity_slope': None,
            'status': 'error',
            'error_message': 'Dosya bulunamadı'
        }
    except Exception as e:
        return {
            'avg_velocity_mm_s': None,
            'max_velocity_mm_s': None,
            'velocity_slope': None,
            'status': 'error',
            'error_message': str(e)
        }


def analyze_coordination(csv_path):
    """
    Modül C: Koordinasyon Analizi - Buton Paneli
    
    Reaksiyon zamanlarını analiz eder ve yorgunluk endeksi hesaplar.
    
    Args:
        csv_path (str): CSV dosya yolu
        
    Returns:
        dict: {
            'avg_reaction_time_ms': Ortalama reaksiyon zamanı (ms),
            'fatigue_index': Yorgunluk endeksi (son 5 / ilk 5)
        }
    """
    try:
        # CSV'yi oku
        df = pd.read_csv(csv_path)
        
        # Sütun kontrolü
        if len(df.columns) < 2:
            raise ValueError("CSV dosyası en az 2 sütun içermelidir")
        
        # Boş veri kontrolü
        if len(df) < 1:
            raise ValueError("Veri bulunamadı")
        
        # Deneme numarası ve reaksiyon zamanı
        trial_num = df.iloc[:, 0].values
        reaction_time = df.iloc[:, 1].values
        
        # NaN değerleri temizle
        valid_mask = ~np.isnan(reaction_time)
        reaction_time = reaction_time[valid_mask]
        
        if len(reaction_time) == 0:
            raise ValueError("Geçerli reaksiyon zamanı verisi bulunamadı")
        
        # ADIM 1: Ortalama reaksiyon zamanı
        avg_reaction_time = np.mean(reaction_time)
        
        # ADIM 2: Yorgunluk endeksi hesapla
        # (Son 5 denemenin ortalaması) / (İlk 5 denemenin ortalaması)
        
        if len(reaction_time) < 10:
            # 10'dan az deneme varsa, yorgunluk endeksi hesaplanamaz
            # Alternatif: ikinci yarı / ilk yarı
            mid_point = len(reaction_time) // 2
            if mid_point > 0:
                first_half = reaction_time[:mid_point]
                second_half = reaction_time[mid_point:]
                
                avg_first = np.mean(first_half)
                avg_second = np.mean(second_half)
                
                if avg_first > 0:
                    fatigue_index = avg_second / avg_first
                else:
                    fatigue_index = 1.0
            else:
                fatigue_index = 1.0
        else:
            # Normal hesaplama: son 5 vs ilk 5
            first_5 = reaction_time[:5]
            last_5 = reaction_time[-5:]
            
            avg_first_5 = np.mean(first_5)
            avg_last_5 = np.mean(last_5)
            
            if avg_first_5 > 0:
                fatigue_index = avg_last_5 / avg_first_5
            else:
                fatigue_index = 1.0
        
        return {
            'avg_reaction_time_ms': round(float(avg_reaction_time), 2),
            'fatigue_index': round(float(fatigue_index), 3),
            'status': 'success'
        }
        
    except FileNotFoundError:
        return {
            'avg_reaction_time_ms': None,
            'fatigue_index': None,
            'status': 'error',
            'error_message': 'Dosya bulunamadı'
        }
    except Exception as e:
        return {
            'avg_reaction_time_ms': None,
            'fatigue_index': None,
            'status': 'error',
            'error_message': str(e)
        }


def process_all_modules(module_a_path, module_b_path, module_c_path):
    """
    Tüm modüllerin verilerini işler ve tek bir sonuç döndürür.
    
    Args:
        module_a_path (str): Modül A CSV dosya yolu
        module_b_path (str): Modül B CSV dosya yolu
        module_c_path (str): Modül C CSV dosya yolu
        
    Returns:
        dict: Tüm modüllerin analiz sonuçlarını içeren dictionary
    """
    results = {}
    
    # Modül A - Tremor
    print("Modül A (Tremor) analiz ediliyor...")
    results['module_a'] = analyze_tremor(module_a_path)
    
    # Modül B - Bradikinezi
    print("Modül B (Bradikinezi) analiz ediliyor...")
    results['module_b'] = analyze_bradykinesia(module_b_path)
    
    # Modül C - Koordinasyon
    print("Modül C (Koordinasyon) analiz ediliyor...")
    results['module_c'] = analyze_coordination(module_c_path)
    
    # Genel durum kontrolü
    all_success = all(
        results[key].get('status') == 'success' 
        for key in ['module_a', 'module_b', 'module_c']
    )
    
    results['overall_status'] = 'success' if all_success else 'partial_success'
    
    return results


def create_prompt_from_results(results):
    """
    JSON analiz sonuçlarından AI prompt metni oluşturur.
    
    Args:
        results (dict): Analiz sonuçları dictionary'si
        
    Returns:
        str: Oluşturulan prompt metni
    """
    # Verileri al
    module_a = results.get('module_a', {})
    module_b = results.get('module_b', {})
    module_c = results.get('module_c', {})
    
    # Veri metni oluştur
    data_text = f"""Modül A (Optik Tremor):
• Baskın Frekans: {module_a.get('dominant_frequency_hz', 'N/A')} Hz
• Sinyal Genliği: {module_a.get('signal_amplitude', 'N/A')}

Modül B (Bradikinezi):
• Ortalama Hız: {module_b.get('avg_velocity_mm_s', 'N/A')} mm/s
• Maksimum Hız: {module_b.get('max_velocity_mm_s', 'N/A')} mm/s
• Hız Eğimi (Velocity Slope): {module_b.get('velocity_slope', 'N/A')}

Modül C (Koordinasyon):
• Ortalama Reaksiyon Süresi: {module_c.get('avg_reaction_time_ms', 'N/A')} ms
• Yorgunluk Endeksi (Fatigue Index): {module_c.get('fatigue_index', 'N/A')}"""
    
    # Prompt şablonu
    prompt_template = f"""GÖREV: Sen bir Kıdemli Biyomedikal Veri Denetçisi ve Hareket Bozuklukları Uzmanısın. Aşağıdaki JSON formatındaki verileri, "Bio-digital Motor Analiz Terminali" prototipinden gelen ham çıktıların rafine edilmiş halleri olarak analiz edeceksin.

ANALİZ PROTOKOLÜ (Sıkı Kurallar):

Önce Teknik Geçerlilik: Veriyi tıbbi olarak yorumlamadan önce, donanım limitlerini (10Hz örnekleme hızı) göz önüne alarak verinin matematiksel olarak mümkün olup olmadığını sorgula. (Örn: Nyquist limitine yakınlık, aliasing riski).

Literatür Çelişkisi: Eğer bir veri (örneğin Velocity Slope) klinik beklentinin (Parkinson'da negatif eğim beklenir) aksine pozitifse, bunu "iyi leşme" olarak değil, "donanım hatası veya hastanın test dışı davranışı" olarak raporla.

Korelasyonel Şüphecilik: Modüller arasındaki tutarsızlıkları (Örn: Titreme var ama reaksiyon hızı normalse) sert bir dille eleştir. JSON verileri şu şekildedir:

{data_text}
"""
    
    return prompt_template


def save_results_to_file(results, output_dir="analysis_results"):
    """
    Analiz sonuçlarını JSON dosyasına kaydeder ve otomatik olarak AI prompt oluşturur.
    
    Args:
        results (dict): Analiz sonuçları
        output_dir (str): Kayıt klasörü
        
    Returns:
        str: Kaydedilen dosyanın yolu
    """
    import json
    from datetime import datetime
    import os
    
    # Klasörü oluştur (yoksa)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Timestamp ile dosya adı oluştur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_result_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Timestamp'i sonuçlara ekle
    results['timestamp'] = timestamp
    results['analysis_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # JSON olarak kaydet
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return filepath


if __name__ == "__main__":
    # Test için örnek kullanım
    import json
    import glob
    import os
    
    # test_data klasöründeki en son dosyaları bul
    test_data_dir = "test_data"
    
    if os.path.exists(test_data_dir):
        module_a_files = sorted(glob.glob(f"{test_data_dir}/module_A_*.csv"))
        module_b_files = sorted(glob.glob(f"{test_data_dir}/module_B_*.csv"))
        module_c_files = sorted(glob.glob(f"{test_data_dir}/module_C_*.csv"))
        
        if module_a_files and module_b_files and module_c_files:
            # En son dosyaları al
            latest_a = module_a_files[-1]
            latest_b = module_b_files[-1]
            latest_c = module_c_files[-1]
            
            print(f"\n{'='*60}")
            print("SİNYAL İŞLEME VE ÖZNİTELİK ÇIKARIMI")
            print(f"{'='*60}")
            print(f"\nModül A: {latest_a}")
            print(f"Modül B: {latest_b}")
            print(f"Modül C: {latest_c}")
            print(f"\n{'='*60}\n")
            
            # Tüm modülleri işle
            results = process_all_modules(latest_a, latest_b, latest_c)
            
            # Sonuçları dosyaya kaydet
            saved_file = save_results_to_file(results)
            print(f"Sonuçlar kaydedildi: {saved_file}\n")
            
            # Sonuçları güzel bir şekilde yazdır
            print("\n" + "="*60)
            print("ANALİZ SONUÇLARI")
            print("="*60 + "\n")
            
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
            print("\n" + "="*60)
            print("KLİNİK YORUM")
            print("="*60)
            
            # Modül A yorumu
            if results['module_a']['status'] == 'success':
                freq = results['module_a']['dominant_frequency_hz']
                print(f"\n[TREMOR ANALİZİ]")
                print(f"   Baskın Frekans: {freq} Hz")
                if 4 <= freq <= 6:
                    print(f"   >> Parkinson tipi tremor aralığında (4-6 Hz)")
                elif freq < 4:
                    print(f"   >> Düşük frekans tremor")
                else:
                    print(f"   >> Yüksek frekans tremor")
            
            # Modül B yorumu
            if results['module_b']['status'] == 'success':
                slope = results['module_b']['velocity_slope']
                freq_b = results['module_b'].get('dominant_frequency_hz', 0)
                print(f"\n[BRADİKİNEZİ ANALİZİ]")
                print(f"   Hız Eğimi: {slope:.4f}")
                if slope < -1:
                    print(f"   >> Belirgin hareket yavaşlaması tespit edildi")
                elif slope < 0:
                    print(f"   >> Hafif hareket yavaşlaması")
                else:
                    print(f"   >> Hız artışı veya stabil")
                
                # Frekans yorumu
                print(f"   Baskın Frekans: {freq_b} Hz")
                if freq_b > 0:
                    if freq_b < 1:
                        print(f"   >> Çok yavaş hareket frekansı")
                    elif 1 <= freq_b < 3:
                        print(f"   >> Normal hareket frekansı aralığı")
                    else:
                        print(f"   >> Hızlı/tekrarlı hareket")
            
            # Modül C yorumu
            if results['module_c']['status'] == 'success':
                fatigue = results['module_c']['fatigue_index']
                print(f"\n[KOORDİNASYON ANALİZİ]")
                print(f"   Yorgunluk Endeksi: {fatigue:.3f}")
                if fatigue > 1.2:
                    print(f"   >> Belirgin performans düşüşü (yorgunluk)")
                elif fatigue > 1.0:
                    print(f"   >> Hafif performans düşüşü")
                else:
                    print(f"   >> Performans korunmuş veya gelişmiş")
            
            print("\n" + "="*60 + "\n")
        else:
            print("Test verileri bulunamadı!")
    else:
        print(f"'{test_data_dir}' klasörü bulunamadı!")
