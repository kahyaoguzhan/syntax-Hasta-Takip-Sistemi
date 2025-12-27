# 🧠 Nöro-Motor Takip Sistemi

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
**Biyodijital Motor Analiz Terminali**, Parkinson ve benzeri nörolojik hastalıklarda görülen motor beceri kayıplarını sensörler aracılığıyla ölçmeyi ve nicel veriye dökmeyi amaçlayan entegre bir sistemdir.
Projenin temel hedefleri:
* **Dijital Parmak İzi:** Hastadan toplanan hareket verilerini işleyerek hastaya özgü bir profil oluşturmak.
* **Objektif Takip:** Verileri analiz edip görselleştirerek doktor ve hasta arasında sürdürülebilir bir takip mekanizması kurmak.
* **Bilimsel Temel:** Espay ve ark. (2016) ve Maetzler (2013) gibi literatür çalışmalarına dayanarak klinik geçerliliği olan veriler sunmak.

---

## 🎯 Hedeflenen Problemler
Proje, Parkinson hastalığının üç temel belirtisinin takibine odaklanmaktadır:

1.  **Tremor (Titreme):** İstirahat halindeki veya hareket sırasındaki titremeler.
2.  **Bradikinezi:** Hareketlerin yavaşlaması ve başlatma güçlüğü.
3.  **Rijidite:** Kas sertliği ve hareket zorluğu.

---

## ⚙️ Sistem Mimarisi ve Modüller
Terminal, üç ana test modülü üzerinden veri toplar ve analiz eder:

### 🔹 Modül A: Tremor Analizi
* **Sensör:** LDR (Işık Bağımlı Direnç) ve Optik sensörler.
* **İşlev:** Hastanın el titremelerinin frekansını (Hz) ve sinyal genliğini ölçer.
* **Çıktı:** Zaman serisi grafiği üzerinden titreme analizi.

### 🔹 Modül B: Bradikinezi Analizi
* **Sensör:** Mesafe Sensörleri (Ultrasonik/Lazer).
* **İşlev:** Belirli bir mesafedeki hareketin hızı ve akıcılığını test eder.
* **Çıktı:** Hareketin genliği ve hız grafikleri.

### 🔹 Modül C: Koordinasyon Testi
* **Sensör:** Butonlar ve Joystick mekanizması.
* **İşlev:** Reaksiyon zamanını ve el-göz koordinasyonunu ölçer.

---

## 🛠 Teknik Donanım ve Mekanik

### Elektronik Bileşenler
Sistem, mikrodenetleyici tabanlı bir mimariye sahiptir]:
* **Mikrodenetleyici:** Arduino UNO.
* **Görüntüleme:** LCM 1602 IIC LCD Ekran.
* **Sensörler:** HC-SR04 Ultrasonik Sensör, LDR Sensörler, Buton modülleri.
* **Devre:** Breadboard üzerinde prototiplenmiş özel devre tasarımı.

### Mekanik Tasarım
* Özel tasarlanmış 3D baskı gövde.
* Joystick ve butonlar için ergonomik yerleşim.
* Tremor ölçümü için izole edilmiş sensör yuvası.

---

## 💻 Yazılım ve AI Analizi
Yazılım arayüzü, donanımdan gelen verileri Seri Port (COM) üzerinden okur ve işler.

### Arayüz Özellikleri
* **Canlı Grafik:** LDR ve Mesafe sensörlerinden gelen verilerin anlık çizimi.
* **Modül Kontrolü:** Modül A, B ve C'nin bağımsız olarak başlatılıp durdurulması.
* **AI Raporlama:** "Kıdemli Biyomedikal Veri Denetçisi" personasına sahip bir AI modeli, toplanan verileri yorumlar.
    * *Örnek Analiz:* 10 Hz örnekleme hızının limitleri ve Nyquist frekansı değerlendirmesi.

---

## 🚀 Kurulum

1.  **Donanım Bağlantısı:**
    * Arduino'yu USB kablosu ile bilgisayara bağlayın.
    * Sensörlerin devre şemasına uygun bağlandığından emin olun.


2.  **Arayüz Kullanımı:**
    * Doğru **COM Port**'u seçin ve "Bağlan" butonuna tıklayın.
    * Test etmek istediğiniz modülü (Tremor, Bradikinezi veya Koordinasyon) "Başlat" butonu ile aktif edin.
    * Veri toplama bittiğinde "Son Analizi Çalıştır" diyerek AI yorumunu alın.

---

## 👥 Takım: SYNTAX

Bu proje **Bursa Teknik Üniversitesi** öğrencileri tarafından geliştirilmiştir.

| İsim | Rol |
|------|-----|
| **Oğuzhan KAHYA** | [Takım Kaptanı ve Elektronik] |
| **Huzeyfe Ahmet DÜNDAR** | [Mekanik Tasarım ve Sunum Hazırlığı] |
| **Emir Erdem DAYANÇ** | [Proje Araştırması ve Literatür Taraması] |
| **Berat BOZTEPE** | [Yazılım Geliştirmesi ve Yapay Zeka] |

---

> *Bu proje akademik araştırma ve prototip geliştirme amaçlıdır; tıbbi tanı cihazı değildir.*
> 
