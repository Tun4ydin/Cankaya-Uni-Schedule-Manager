# 🎓 Çankaya Üniversitesi Ders Programı Yöneticisi (Web Versiyonu)

Bu proje, masaüstü PySide6 uygulamasının modern **React 18 + Vite + Tailwind CSS** frontend ve **FastAPI** backend mimarisine dönüştürülmüş halidir.

---

## 🚀 Mimari ve Teknolojiler

- **Frontend (`WEB/frontend`)**:
  - **React 18** (React 18.3.1)
  - **Vite** (Hızlı HMR ve yapılandırma)
  - **Tailwind CSS** (Çankaya Lacivert `#002855` & Altın `#d49a17` kurumsal renkleri, tam karanlık tema ve cam morfizim efektleri)
  - **Lucide React** (Modern simgeler)
  - **html2canvas** (Ders programını tek tıkla PNG olarak indirme)
- **Backend (`WEB/backend`)**:
  - **FastAPI** & **Uvicorn** (Yüksek performanslı Python REST API)
  - **Pydantic v2** (Veri doğrulama ve modelleme)
  - Python tabanlı çakışma çözme motoru (`SchedulerEngine`), ön koşul denetleyicisi (`PrerequisiteManager`), transkript ayrıştırıcı (`TranscriptParser`) ve veri yöneticisi (`DataManager`).

---

## 📦 Kurulum ve Çalıştırma

### 🐳 Yöntem 1: Docker Compose (Tek Komut - Önerilen)

Her seferinde 2 ayrı terminal açmak yerine tek bir komutla hem backend hem frontend'i ayağa kaldırabilirsiniz:

```bash
docker compose up --build
```
*(Arka planda çalıştırmak isterseniz: `docker compose up -d --build`)*

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Durdurmak için**: `docker compose down`

---

### 💻 Yöntem 2: Manuel Çalıştırma (2 Ayrı Terminal)

#### 1. Backend'i Başlatma (Terminal 1)
```bash
cd WEB/backend
python3 -m uvicorn main:app --reload --port 8000
```

#### 2. Frontend'i Başlatma (Terminal 2)
```bash
cd WEB/frontend
npm run dev
```

---

## ✨ Özellikler

1. **⚡ Gerçek Zamanlı Ders Arama & Filtreleme**:
   - 580+ ders arasında anında arama (ders kodu, ders adı, hoca adı).
   - Bölüm bazlı filtreleme (CENG, SENG, EE, IE, ME, MECE, vb.).
   - Ders türü filtreleri: `📌 Zorunlu`, `🟣 ÇAP Zorunlu`, `🔵 Yandal Zorunlu`, `🔹 Seçmeli`.
2. **🔄 Çakışmasız Program Kombinasyonları**:
   - Sepete eklenen derslerin tüm şubelerini tarayarak haftalık çakışmasız alternatif programları üretir.
   - Tercih filtreleri: `Cuma Boş`, `Pazartesi Boş`, `Sabah Dersi Yok (<10:00)`.
   - İstenilen ders için belirli bir şubeyi kilitleme veya otomatik seçimde bırakma.
3. **📅 İnteraktif Haftalık Takvim**:
   - Pazartesi - Cumartesi arası 08:40 - 20:50 saat dilimleri.
   - Her ders için özel ayırt edici renk kartı, hoca adı ve derslik bilgisi (örn. `LA-01`, `B-102`).
   - Boş kutulara tıklayarak `🍔 Yemek Arası`, `☕ Mola`, `📚 Ders Çalışma`, `🏋️ Spor` gibi özel etkinlik blokları ekleme/düzenleme.
4. **📖 Ders Detayları & İzlence**:
   - Takvimdeki veya aramadaki bir derse tıklandığında dersin kredisi, AKTS'si, tanımı, ön koşul kontrolü ve resmi Çankaya bağlantıları.
5. **📄 Transkript Yükleme & Müfredat Takibi**:
   - PDF transkript yükleme veya metin yapıştırma desteği.
   - Öğrenci numarası, ana bölüm, yandal/ÇAP tespiti ve geçilen derslerin harf notlarıyla birlikte taranması.
   - Zorunlu, teknik seçmeli ve sosyal seçmeli ders tamamlama yüzdesi ve kalan zorunlu dersler listesi.
6. **💾 Dışa Aktarma**:
   - Oluşturulan haftalık programı yüksek çözünürlüklü PNG görseli veya JSON olarak bilgisayara indirme.
7. **🌙 Çift Tema**:
   - Çankaya Üniversitesi açık kurumsal teması ve göz yormayan karanlık tema.
