# 🎓 Çankaya Üniversitesi Ders Programı Oluşturucu (Schedule Manager)

Çankaya Üniversitesi öğrenci işleri web sitesinden açılan dersleri ve saatlerini otomatik çeken, haftalık çakışmasız ders programı kombinasyonları üreten, kredi/AKTS takibi ve özel etkinlik planlaması sunan modern masaüstü uygulaması.

---

## 🚀 Özellikler

- **⚡ Otomatik Ders & Program Çekme**: Çankaya Üniversitesi web sitesinden tüm bölümlerin açılan derslerini, şubelerini, saatlerini, öğretim elemanlarını ve dersliklerini çeker.
- **🔄 Çakışmasız Program Kombinasyonları**: Seçilen derslerin tüm şube ihtimallerini değerlendirir ve haftalık çakışmasız alternatif programları üretir.
- **🎨 Çift Tema Desteği**:
  - **☀️ Açık Tema (Çankaya)**: Üniversitenin resmi kurumsal renkleri (Lacivert `#002855` & Altın Sarısı `#d49a17`).
  - **🌙 Karanlık Tema**: Gözü yormayan modern koyu tema.
- **🎓 Yandal & ÇAP Müfredat Desteği**: Ana bölüm ve ikinci bölüm (Yandal veya Çift Anadal) kombinasyonuna göre ortak ders muafiyetlerini hesaplar ve dersleri `📌 Zorunlu`, `🟣 ÇAP Zorunlu`, `🔵 Yandal Zorunlu` veya `🔹 Seçmeli` olarak sınıflandırır.
- **💳 Kredi ve AKTS Takibi**: Sepetteki derslerin toplam yerel kredi, AKTS ve haftalık ders saatini canlı olarak hesaplar.
- **📍 Sınıf / Derslik Bilgisi**: Okul sitesinde belirtilmişse dersin işleneceği sınıfı (örn. `LA-01`, `B-102`) takvimde ve detay kartlarında gösterir.
- **📖 Ders Bilgisi & Web Sayfası**: Takvimdeki veya aramadaki bir derse tıklandığında dersin tanımı, konuları ve resmi ders web sitesine (`http://{kod}.cankaya.edu.tr`) doğrudan bağlantı sağlar.
- **✏️ Özel Etkinlik & Mola Ekleme**: Boş kutulara tıklayarak `🍔 Yemek Arası`, `☕ Mola`, `📚 Ders Çalışma`, `🏋️ Spor` gibi özel bloklar eklenebilir.
- **💾 Dışa Aktarma**: Oluşturulan haftalık ders programını PNG görseli veya JSON olarak kaydetme imkanı.

---

## 📦 Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın veya İndirin
```bash
git clone https://github.com/Tun4ydin/Cankaya-Uni-Schedule-Manager.git
cd Cankaya-Uni-Schedule-Manager
```

### 2. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatın
```bash
python3 main.py
# veya Windows için:
python main.py
```

> **Not**: Uygulama içerisinde güncel 587 derslik önbellek (`cankaya_courses.json`) hazır geldiği için ilk açılışta internetten veri çekmenize gerek kalmadan doğrudan program oluşturmaya başlayabilirsiniz.
