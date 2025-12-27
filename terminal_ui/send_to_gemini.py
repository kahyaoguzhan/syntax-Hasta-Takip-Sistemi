import os
import google.generativeai as genai

def main():
    # API Key kontrolü
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Hata: GEMINI_API_KEY çevre değişkeni bulunamadı.")
        print("Lütfen API anahtarınızı ayarlayın. Örnek (Windows):")
        print("set GEMINI_API_KEY=API_ANAHTARINIZ")
        print("$env:GEMINI_API_KEY='API_ANAHTARINIZ' (PowerShell)")
        return

    # Gemini API konfigürasyonu
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Konfigürasyon hatası: {e}")
        return

    # Model ayarları - Daha uzun ve detaylı yanıtlar için
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,  # Çok daha uzun yanıtlar için artırıldı
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

    try:
        # Gemini 2.5 Flash modelini kullan
        model_name = "gemini-2.5-flash"
        print(f"Model: {model_name}")

        model = genai.GenerativeModel(
            model_name=model_name, 
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # ai_prompt dosyasını oku
        prompt_file = "analysis_results/ai_prompt_20251227_123013.txt"
        
        if not os.path.exists(prompt_file):
            print(f"Hata: {prompt_file} dosyası bulunamadı.")
            return
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        print(f"Dosya okundu: {prompt_file}")
        print(f"Prompt uzunluğu: {len(prompt_content)} karakter")
        print("-" * 50)
        print("Gemini'ye gönderiliyor...")
        print("-" * 50)
        
        # Streaming ile cevap alma
        print("\nGemini Yanıtı:\n")
        full_response = ""
        chunk_count = 0
        
        response = model.generate_content(prompt_content, stream=True)
        
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                full_response += chunk.text
                chunk_count += 1
        
        print("\n" + "-" * 50)
        print(f"İşlem tamamlandı!")
        print(f"Toplam {chunk_count} chunk alındı")
        print(f"Toplam yanıt uzunluğu: {len(full_response)} karakter")
        
        # Yanıt çok kısaysa uyarı ver
        if len(full_response) < 500:
            print("\n⚠️ UYARI: Yanıt beklenenden çok kısa!")
            print("Prompt safety filter'a takılmış olabilir.")
            if hasattr(response, 'prompt_feedback'):
                print(f"Prompt Feedback: {response.prompt_feedback}")

    except FileNotFoundError as e:
        print(f"\nDosya bulunamadı: {e}")
    except Exception as e:
        print(f"\nBir hata oluştu: {e}")

if __name__ == "__main__":
    main()
