"""
Veri Kaydedici - CSV Format
Her modülün verilerini ayrı dosyalara kaydeder
"""

import csv
import os
from datetime import datetime


class DataLogger:
    """Modül verilerini CSV'ye kaydeder"""
    
    def __init__(self, save_dir="test_data"):
        self.save_dir = save_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Klasör oluştur
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Dosya yolları
        self.file_mod_a = os.path.join(save_dir, f"module_A_{self.session_id}.csv")
        self.file_mod_b = os.path.join(save_dir, f"module_B_{self.session_id}.csv")
        self.file_mod_c = os.path.join(save_dir, f"module_C_{self.session_id}.csv")
        
        # CSV dosyalarını başlat
        self._init_csv_files()
        
    def _init_csv_files(self):
        """CSV başlıklarını yaz"""
        # Modül A - Tremor (sadece Zaman ve LDR)
        with open(self.file_mod_a, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Zaman (s)', 'LDR Değeri'])
        
        # Modül B - Mesafe
        with open(self.file_mod_b, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Zaman (s)', 'Mesafe (mm)'])
        
        # Modül C - Reaksiyon
        with open(self.file_mod_c, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Deneme #', 'Reaksiyon Zamanı (ms)'])
    
    def log_module_a(self, time_s, ldr_value):
        """Modül A verisini kaydet (sadece LDR)"""
        with open(self.file_mod_a, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([f"{time_s:.3f}", ldr_value])
    
    def log_module_b(self, time_s, distance_mm):
        """Modül B verisini kaydet"""
        with open(self.file_mod_b, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([f"{time_s:.3f}", f"{distance_mm:.1f}"])
    
    def log_module_c(self, trial_num, reaction_time_ms):
        """Modül C verisini kaydet"""
        with open(self.file_mod_c, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([trial_num, f"{reaction_time_ms:.1f}"])
    
    def get_files(self):
        """Kaydedilen dosyaların yollarını döndür"""
        return {
            'A': self.file_mod_a,
            'B': self.file_mod_b,
            'C': self.file_mod_c
        }
