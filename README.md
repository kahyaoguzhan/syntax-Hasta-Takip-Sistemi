# 🏥 Hasta Takip Sistemi (Patient Tracking System)

![Lisans](https://img.shields.io/badge/license-MIT-blue.svg) ![Durum](https://img.shields.io/badge/status-Geliştirme-orange) ![Dil](https://img.shields.io/badge/language-Python%20%7C%20JavaScript-green)

> **Hackathon Projesi** > **Takım Adı:** syntax

---

## 📋 İçindekiler
1. [Proje Özeti](#-proje-özeti)
2. [Problem ve İhtiyaç Analizi](#-problem-ve-ihtiyaç-analizi)
3. [Çözüm Yaklaşımı](#-çözüm-yaklaşımı)
4. [Teknik Mimari](#-teknik-mimari)
5. [Yenilik ve Katma Değer](#-yenilik-ve-katma-değer)
6. [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
7. [Etki ve Fayda](#-etki-ve-fayda)
8. [Yol Haritası](#-yol-haritası)
9. [Takım](#-takım-bilgileri)
10. [Ekran Görüntüleri](#-ekran-görüntüleri)

---

## 💡 Proje Özeti
[cite_start]**Hasta Takip Sistemi**, sağlık personelinin hastaların durumunu uzaktan izlemesini sağlayan, özellikle tremor, bradikinezi ve koordinasyon bozuklukları gibi belirtilerin takibi için geliştirilmiş entegre bir yazılım ve donanım çözümüdür. [cite: 2, 3]

[cite_start]Sistem, sensörlerden alınan verilerin dijital ortamda saklanmasını, anlık olarak görselleştirilmesini ve AI (Yapay Zeka) destekli analizler sunarak doktorların daha doğru teşhis ve tedavi planlaması yapmasına yardımcı olmayı amaçlamaktadır. [cite: 5, 19]

---

## 🎯 Problem ve İhtiyaç Analizi
* [cite_start]**Problem:** Geleneksel yöntemlerde hasta takibi genellikle manuel gözleme ve notlara dayanmakta, bu da veri kaybına, hatalı analizlere ve hastalığın seyrinin hassas bir şekilde izlenmesinde zorluklara yol açmaktadır. [cite: 8]
* [cite_start]**Aciliyet:** Kronik rahatsızlıkları olan hastaların düzenli ve kesintisiz (7/24) veri akışıyla takip edilmesi, olası krizlerin önlenmesi ve tedavinin optimize edilmesi için kritiktir. [cite: 9]
* [cite_start]**İhtiyaç:** Hem doktor hem de hasta tarafından kolayca erişilebilen, sensör verilerini işleyip anlamlı raporlara dönüştüren, kullanıcı dostu ve güvenilir bir dijital platform gereksinimi vardır. [cite: 10]

---

## 🩺 Çözüm Yaklaşımı
[cite_start]Projemiz, hastadan toplanan verileri güvenli bir şekilde işleyerek web tabanlı bir kontrol panelinde görselleştiren uçtan uca bir sistemdir. [cite: 12]

* [cite_start]**Sistem İşleyişi:** Seri port üzerinden bağlanan sensör modülleri (Tremor, Bradikinezi, Koordinasyon) başlatılır ve veri toplamaya başlar. [cite: 13, 20]
* [cite_start]**Etkileşim:** Kullanıcı, web arayüzü üzerinden modülleri kontrol edebilir, anlık sensör grafiklerini izleyebilir ve toplanan veriler üzerinde AI analizi çalıştırarak sonuçları inceleyebilir. [cite: 14]

---

## 🛠 Teknik Mimari

### 4.1 Teknolojik Bileşenler
* [cite_start]**Yazılım Dilleri:** [Python, JavaScript, vb.] [cite: 17]
* **Framework/Kütüphaneler:** [React/Vue.js (Frontend), Flask/Django (Backend), TensorFlow/PyTorch (AI), vb.]
* **Veritabanı:** [PostgreSQL / Firebase / MongoDB]
* [cite_start]**Donanım:** [Arduino/Mikrodenetleyici, LDR Sensörler, İvmeölçer, vb.] [cite: 18]
* [cite_start]**Haberleşme:** Seri Port (COM) bağlantısı. [cite: 19]

### 4.2 Çalışma Mantığı
1.  [cite_start]**Veri Toplama:** Kullanıcı arayüzünden başlatılan modüller (A, B, C), bağlı sensörlerden (örn. LDR) seri port aracılığıyla veri okur. [cite: 21]
2.  **İşleme ve Görselleştirme:** Alınan ham veriler işlenir ve "Tremor Analizi" grafiği gibi anlık grafiklere dönüştürülerek panelde gösterilir.
3.  [cite_start]**AI Analizi:** Toplanan veri setleri tamamlandığında, yapay zeka algoritması devreye girer, analizi gerçekleştirir ve sonuçları kullanıcıya sunar. [cite: 22]

---

## 🚀 Yenilik ve Katma Değer
* [cite_start]**Özgün Yön:** Rakiplerden farklı olarak sistemimiz, sensör tabanlı veri toplama ile yapay zeka destekli analizi tek bir entegre platformda birleştirerek daha kapsamlı bir takip sunmaktadır. [cite: 25, 26]
* [cite_start]**Katma Değer:** Doktorların hasta verilerini analiz etmek için harcadığı süreyi azaltır, nesnel verilere dayalı karar vermeyi destekler ve hastaların kendi durumlarını daha iyi anlamalarını sağlar. [cite: 27]

---

## 💻 Kurulum ve Çalıştırma
[cite_start]Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz. [cite: 29]

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadi/hasta-takip-sistemi.git](https://github.com/kullaniciadi/hasta-takip-sistemi.git)
    cd hasta-takip-sistemi
    ```

2.  **Gereksinimleri Yükleyin:**
    Donanım bağlantıları yapıldıktan sonra gerekli yazılım kütüphanelerini yükleyin.
    ```bash
    pip install -r requirements.txt
    # Frontend bağımlılıkları için (varsa)
    npm install
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    python app.py
    # Frontend sunucusunu başlatmak için (ayrıysa)
    npm start
    ```
4.  **Bağlantı:** Web tarayıcınızdan belirtilen adrese gidin ve seri port bağlantısını (örn. COM3) yapın.

---

## 📊 Etki ve Fayda
* [cite_start]**Toplumsal Etki:** Nörolojik rahatsızlığı olan bireylerin evde takibini kolaylaştırarak yaşam kalitesini artırır ve sağlık hizmetlerine erişimi demokratikleştirir. [cite: 33]
* [cite_start]**Ekonomik Fayda:** Erken teşhis ve düzenli takip sayesinde gereksiz hastane ziyaretleri azalır, uzun vadeli tedavi maliyetleri düşer. [cite: 35]

---

## ⚠️ Riskler ve Kısıtlar
* **Teknik Riskler:** Seri port bağlantısında kopmalar veya sensör verilerinde gürültü oluşabilir. [cite_start]AI modelinin doğruluğu veri setinin kalitesine bağlıdır. [cite: 37]
* [cite_start]**Kısıtlar:** Sistem şu an için belirli sensör donanımlarına ve kablolu bağlantıya ihtiyaç duymaktadır. [cite: 39]

---

## 🗺 Gelecek Yol Haritası
- [x] Temel sensör veri okuma ve web arayüzü (MVP)
- [x] Modül bazlı kontrol ve anlık grafik gösterimi
- [x] Seri port bağlantı entegrasyonu
- [ ] AI modelinin eğitilmesi ve entegrasyonunun tamamlanması
- [ ] Hasta kayıt ve geçmiş veri inceleme modülü
- [ ] Kablosuz veri iletimi (Bluetooth/Wi-Fi) desteği
- [ ] [cite_start]Mobil uygulama geliştirme [cite: 40, 41, 42]

---

## 👥 Takım Bilgileri
[cite_start]**Takım Adı:** syntax [cite: 45]

| İsim | Rol | GitHub |
|------|-----|--------|
| **Oğuzhan KAHYA** | [Rol] | [@GitHubKullanıcıAdı](https://github.com) |
| **Huzeyfe Ahmet DÜNDAR** | [Rol] | [@GitHubKullanıcıAdı](https://github.com) |
| **Emir** | [Rol] | [@GitHubKullanıcıAdı](https://github.com) |
| **Berat** | [Rol] | [@GitHubKullanıcıAdı](https://github.com) |
[cite_start][cite: 46]

---

## 📸 Ekran Görüntüleri
### Ana Kontrol Paneli
[cite_start]Aşağıdaki ekran görüntüsü, Hasta Takip Sistemi'nin web tabanlı ana kontrol panelini göstermektedir. [cite: 48]

* **Sol Panel:** Seri port bağlantı ayarları, Tremor, Bradikinezi ve Koordinasyon modüllerini başlatma/durdurma kontrolleri ve LDR sensöründen gelen anlık sinyal grafiği yer almaktadır.
* **Sağ Panel:** AI analizlerini çalıştırma ve geçmiş analizleri inceleme seçenekleri ile analiz sonuçlarının gösterileceği alan bulunmaktadır.

![Hasta Takip Sistemi Kontrol Paneli](image_0.png)
