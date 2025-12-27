# 🧠 Biyodijital Motor Analiz Terminali (Bio-digital Motor Analysis Terminal)

![Proje Arayüzü](image_55b363.jpg)

> **Takım:** SYNTAX  
> **Kurum:** Bursa Teknik Üniversitesi [cite: 52]  
> **Durum:** Prototip Geliştirme Aşamasında (Aralık 2025) [cite: 53]

---

## 📋 İçindekiler
1. [Proje Tanımı ve Amacı](#-proje-tanımı-ve-amacı)
2. [Hedeflenen Problemler](#-hedeflenen-problemler)
3. [Sistem Mimarisi ve Modüller](#-sistem-mimarisi-ve-modüller)
4. [Teknik Donanım ve Mekanik](#-teknik-donanım-ve-mekanik)
5. [Yazılım ve AI Analizi](#-yazılım-ve-ai-analizi)
6. [Kurulum](#-kurulum)
7. [Takım](#-takım)

---

## 💡 Proje Tanımı ve Amacı
**Biyodijital Motor Analiz Terminali**, Parkinson ve benzeri nörolojik hastalıklarda görülen motor beceri kayıplarını sensörler aracılığıyla ölçmeyi ve nicel veriye dökmeyi amaçlayan entegre bir sistemdir[cite: 56].

Projenin temel hedefleri:
* **Dijital Parmak İzi:** Hastadan toplanan hareket verilerini işleyerek hastaya özgü bir profil oluşturmak[cite: 57].
* **Objektif Takip:** Verileri analiz edip görselleştirerek doktor ve hasta arasında sürdürülebilir bir takip mekanizması kurmak[cite: 58].
* **Bilimsel Temel:** Espay ve ark. (2016) ve Maetzler (2013) gibi literatür çalışmalarına dayanarak klinik geçerliliği olan veriler sunmak[cite: 67, 68].

---

## 🎯 Hedeflenen Problemler
Proje, Parkinson hastalığının üç temel belirtisinin takibine odaklanmaktadır[cite: 59]:

1.  **Tremor (Titreme):** İstirahat halindeki veya hareket sırasındaki titremeler[cite: 60].
2.  **Bradikinezi:** Hareketlerin yavaşlaması ve başlatma güçlüğü[cite: 61, 62].
3.  **Rijidite:** Kas sertliği ve hareket zorluğu[cite: 65].

---

## ⚙️ Sistem Mimarisi ve Modüller
Terminal, üç ana test modülü üzerinden veri toplar ve analiz eder[cite: 80, 81, 82]:

### 🔹 Modül A: Tremor Analizi
* **Sensör:** LDR (Işık Bağımlı Direnç) ve Optik sensörler[cite: 83].
* **İşlev:** Hastanın el titremelerinin frekansını (Hz) ve sinyal genliğini ölçer.
* **Çıktı:** Zaman serisi grafiği üzerinden titreme analizi.

### 🔹 Modül B: Bradikinezi Analizi
* **Sensör:** Mesafe Sensörleri (Ultrasonik/Lazer)[cite: 88].
* **İşlev:** Belirli bir mesafedeki hareketin hızı ve akıcılığını test eder.
* **Çıktı:** Hareketin genliği ve hız grafikleri.

### 🔹 Modül C: Koordinasyon Testi
* **Sensör:** Butonlar ve Joystick mekanizması.
* **İşlev:** Reaksiyon zamanını ve el-göz koordinasyonunu ölçer[cite: 94].

---

## 🛠 Teknik Donanım ve Mekanik

### Elektronik Bileşenler
Sistem, mikrodenetleyici tabanlı bir mimariye sahiptir[cite: 70, 72]:
* **Mikrodenetleyici:** Arduino UNO[cite: 72].
* **Görüntüleme:** LCM 1602 IIC LCD Ekran[cite: 73].
* **Sensörler:** HC-SR04 Ultrasonik Sensör, LDR Sensörler, Buton modülleri.
* **Devre:** Breadboard üzerinde prototiplenmiş özel devre tasarımı.

### Mekanik Tasarım
* Özel tasarlanmış 3D baskı gövde[cite: 134].
* Joystick ve butonlar için ergonomik yerleşim.
* Tremor ölçümü için izole edilmiş sensör yuvası.

---

## 💻 Yazılım ve AI Analizi
Yazılım arayüzü, donanımdan gelen verileri Seri Port (COM) üzerinden okur ve işler[cite: 77].

### Arayüz Özellikleri
* **Canlı Grafik:** LDR ve Mesafe sensörlerinden gelen verilerin anlık çizimi[cite: 113, 115].
* **Modül Kontrolü:** Modül A, B ve C'nin bağımsız olarak başlatılıp durdurulması[cite: 79].
* **AI Raporlama:** "Kıdemli Biyomedikal Veri Denetçisi" personasına sahip bir AI modeli, toplanan verileri yorumlar[cite: 112].
    * *Örnek Analiz:* 10 Hz örnekleme hızının limitleri ve Nyquist frekansı değerlendirmesi[cite: 120, 130].

---

## 🚀 Kurulum

1.  **Donanım Bağlantısı:**
    * Arduino'yu USB kablosu ile bilgisayara bağlayın.
    * Sensörlerin devre şemasına uygun bağlandığından emin olun[cite: 70].

2.  **Yazılımı Çalıştırma:**
    ```bash
    # Repoyu klonlayın
    git clone [https://github.com/kahyaoguzhan/Hasta-Takip-Sistemi.git](https://github.com/kahyaoguzhan/Hasta-Takip-Sistemi.git)
    
    # Gerekli kütüphaneleri yükleyin
    pip install -r requirements.txt
    
    # Uygulamayı başlatın
    python main.py
    ```

3.  **Arayüz Kullanımı:**
    * Doğru **COM Port**'u seçin ve "Bağlan" butonuna tıklayın[cite: 77].
    * Test etmek istediğiniz modülü (Tremor, Bradikinezi veya Koordinasyon) "Başlat" butonu ile aktif edin.
    * Veri toplama bittiğinde "Son Analizi Çalıştır" diyerek AI yorumunu alın[cite: 97].

---

## 👥 Takım: SYNTAX

Bu proje **Bursa Teknik Üniversitesi** öğrencileri tarafından geliştirilmiştir.

| İsim | Rol |
|------|-----|
| **Oğuzhan KAHYA** | [Rol] |
| **Huzeyfe Ahmet DÜNDAR** | [Rol] |
| **Emir** | [Rol] |
| **Berat** | [Rol] |

---

> *Bu proje akademik araştırma ve prototip geliştirme amaçlıdır; tıbbi tanı cihazı değildir.*
> 
