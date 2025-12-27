"""
Gemini API Handler
En yeni prompt dosyasını bulup Gemini API'ye gönderen modül
"""

import os
import glob
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
import google.generativeai as genai


def get_latest_analysis_json(directory="analysis_results"):
    """
    En yeni analysis_result_*.json dosyasını bulur
    
    Args:
        directory: JSON dosyalarının bulunduğu klasör
        
    Returns:
        str: En yeni dosyanın yolu veya None
    """
    try:
        # analysis_result_*.json dosyalarını bul
        pattern = os.path.join(directory, "analysis_result_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return None
        
        # En yeni dosyayı bul (modification time'a göre)
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
        
    except Exception as e:
        print(f"JSON dosyası bulma hatası: {e}")
        return None


def create_prompt_from_json(json_filepath):
    """
    JSON dosyasından prompt metni oluşturur
    
    Args:
        json_filepath: JSON dosyasının yolu
        
    Returns:
        str: Oluşturulan prompt metni veya None
    """
    try:
        import json
        from signal_processor import create_prompt_from_results
        
        # JSON dosyasını oku
        with open(json_filepath, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Prompt oluştur
        prompt = create_prompt_from_results(results)
        return prompt
        
    except Exception as e:
        print(f"Prompt oluşturma hatası: {e}")
        return None


def get_all_analysis_json_files(directory="analysis_results"):
    """
    Tüm analysis_result_*.json dosyalarını bulur ve tarihe göre sıralar
    
    Args:
        directory: JSON dosyalarının bulunduğu klasör
        
    Returns:
        list: Sıralanmış dosya yolları listesi (en eskiden en yeniye)
    """
    try:
        # analysis_result_*.json dosyalarını bul
        pattern = os.path.join(directory, "analysis_result_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return []
        
        # Tarihe göre sırala (modification time - en eskiden en yeniye)
        files_sorted = sorted(files, key=os.path.getmtime)
        return files_sorted
        
    except Exception as e:
        print(f"JSON dosyaları bulma hatası: {e}")
        return []


class GeminiWorker(QThread):
    """
    Gemini API çağrısını arka planda yapan worker thread
    """
    # Signaller
    status_update = pyqtSignal(str)  # Durum güncellemesi
    chunk_received = pyqtSignal(str)  # Yanıt chunk'ı geldi
    completed = pyqtSignal()  # İşlem tamamlandı
    error_occurred = pyqtSignal(str)  # Hata oluştu
    
    def __init__(self, prompt_text):
        super().__init__()
        self.prompt_text = prompt_text
        self.should_stop = False
        
    def run(self):
        """Thread ana fonksiyonu"""
        try:
            # API Key kontrolü
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.error_occurred.emit(
                    "HATA: GEMINI_API_KEY çevre değişkeni bulunamadı.\n"
                    "Lütfen API anahtarınızı ayarlayın:\n"
                    "$env:GEMINI_API_KEY='API_ANAHTARINIZ' (PowerShell)"
                )
                return
            
            # Gemini API konfigürasyonu
            self.status_update.emit("API konfigürasyonu yapılıyor...")
            genai.configure(api_key=api_key)
            
            # Model ayarları - Daha uzun ve detaylı yanıtlar için
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            # Güvenlik ayarları - Tıbbi içerik için
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
            
            # Model oluştur
            self.status_update.emit("Model yükleniyor...")
            model_name = "gemini-2.5-flash"
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Prompt'u terminale yazdır
            print("-" * 80)
            print("📤 GEMINI'YE GÖNDERİLEN PROMPT:")
            print("-" * 80)
            print(self.prompt_text)
            print("-" * 80)
            print("\n")
            
            # Streaming ile yanıt al
            self.status_update.emit("Gemini'den yanıt bekleniyor...")
            print("📥 GEMINI'DEN GELEN YANIT:")
            print("-" * 80)
            response = model.generate_content(self.prompt_text, stream=True)
            
            full_response = ""
            chunk_count = 0
            
            for chunk in response:
                if self.should_stop:
                    break
                    
                if chunk.text:
                    # UI'a gönder
                    self.chunk_received.emit(chunk.text)
                    # Terminale yazdır
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text
                    chunk_count += 1
            
            # Tamamlandı
            print("\n" + "-" * 80)
            if not self.should_stop:
                print(f"✅ Tamamlandı! {chunk_count} chunk, {len(full_response)} karakter")
                self.status_update.emit(
                    f"Tamamlandı! {chunk_count} chunk, {len(full_response)} karakter"
                )
                self.completed.emit()
            
            # Yanıt çok kısaysa uyarı
            if len(full_response) < 500:
                self.error_occurred.emit(
                    "⚠️ UYARI: Yanıt beklenenden çok kısa! "
                    "Prompt safety filter'a takılmış olabilir."
                )
                
        except Exception as e:
            self.error_occurred.emit(f"Hata oluştu: {str(e)}")
    
    def stop(self):
        """Worker'ı durdur"""
        self.should_stop = True
