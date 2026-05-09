# Lumos - Smart Investment Assistant — TODO 

> **~18 hafta · 6 faz · $0 başlangıç maliyeti**
> Başlangıç: 2026-05-09

---

## 📁 Proje Klasör Yapısı

```
lumos/                          ← proje kökü
│
├── backend/                    ← FastAPI uygulaması (Python)
│   ├── __init__.py
│   ├── main.py                 ← FastAPI app, middleware kayıtları, lifespan
│   ├── requirements.txt        ← Python bağımlılıkları ✅
│   ├── .env.example            ← ortam değişkenleri şablonu ✅
│   │
│   ├── routers/                ← [CONTROLLER] HTTP endpoint tanımları
│   │   ├── __init__.py
│   │   ├── chat.py             ← POST /chat
│   │   ├── profile.py          ← POST /profile
│   │   ├── recommend.py        ← POST /recommend
│   │   ├── users.py            ← GET|PATCH /users
│   │   └── health.py           ← GET /health
│   │
│   ├── services/               ← [SERVICE] İş mantığı katmanı
│   │   ├── __init__.py
│   │   ├── ai_service.py       ← Claude API istemcisi
│   │   ├── risk_engine.py      ← Risk skoru hesaplama (1-10)
│   │   ├── market_data.py      ← yfinance veri çekme
│   │   ├── tefas_service.py    ← TEFAS fon verisi
│   │   ├── portfolio_engine.py ← Volatilite ağırlıklı portföy
│   │   ├── volatility.py       ← Standart sapma / numpy hesapları
│   │   ├── hybrid_basket.py    ← REIT hibrit sepet mantığı
│   │   ├── explainer.py        ← Claude ile portföy açıklaması
│   │   └── cache.py            ← Günlük diskcache katmanı
│   │
│   ├── models/                 ← [MODEL] Pydantic şemaları & SQLAlchemy ORM
│   │   ├── __init__.py
│   │   ├── user.py             ← User ORM modeli
│   │   ├── user_profile.py     ← Risk profil şeması
│   │   ├── risk_score.py       ← Risk skoru şeması
│   │   └── portfolio.py        ← Portföy şeması
│   │
│   ├── middleware/             ← Auth & global hata yakalama
│   │   ├── __init__.py
│   │   ├── verify_clerk.py     ← Clerk JWT doğrulama
│   │   └── error_handler.py    ← Global exception handler
│   │
│   ├── db/                     ← Veritabanı bağlantısı & session
│   │   ├── __init__.py
│   │   └── database.py         ← SQLAlchemy engine, AsyncSession
│   │
│   ├── prompts/                ← Claude sistem promptları (düz metin)
│   │   ├── system_prompt.txt
│   │   └── reit_explain_prompt.txt
│   │
│   ├── data/                   ← Statik JSON veri dosyaları
│   │   ├── fund_list.json      ← TEFAS fon listesi
│   │   └── asset_universe.json ← Tüm varlıklar (hisse, ETF, REIT)
│   │
│   └── tests/                  ← Backend birim testleri
│       ├── __init__.py
│       ├── test_risk_engine.py
│       └── test_chat.py
│
├── frontend/                   ← React 18 + Vite uygulaması
│   ├── src/
│   │   ├── App.jsx             ← Root bileşen, router tanımı
│   │   ├── main.jsx            ← ClerkProvider sarmalı
│   │   │
│   │   ├── components/         ← Yeniden kullanılabilir UI bileşenleri
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── RiskGauge.jsx
│   │   │   ├── PortfolioChart.jsx
│   │   │   ├── AssetCard.jsx
│   │   │   ├── PerformanceChart.jsx
│   │   │   ├── ReitCard.jsx
│   │   │   ├── AssetExplainer.jsx
│   │   │   └── DisclaimerModal.jsx
│   │   │
│   │   ├── pages/              ← Sayfa düzeyinde bileşenler (route başına 1)
│   │   │   ├── OnboardingPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   ├── RecommendPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   │
│   │   ├── hooks/              ← Custom React hook'ları
│   │   │   ├── useChat.js
│   │   │   └── usePortfolio.js
│   │   │
│   │   └── utils/              ← Yardımcı fonksiyonlar & hata sınırı
│   │       └── errorBoundary.jsx
│   │
│   ├── .env                    ← (commit'leme!)
│   └── .env.production
│
├── tests/
│   └── e2e/                    ← Playwright uçtan uca testler
│       ├── test_full_flow.py
│       └── scenarios.json
│
├── docs/                       ← Mimari ve API dokümantasyonu
│   ├── architecture.md
│   ├── api_reference.md
│   └── case_study.md
│
├── demo/
│   └── demo_script.md
│
├── venv/                       ← Python sanal ortamı ✅ (git'e girmiyor)
├── .gitignore                  ✅
├── .env.example                ✅
├── render.yaml                 ← Render.com deployment config
├── Dockerfile                  ← Backend Docker imajı
├── vercel.json                 ← Vercel deployment config
├── README.md
└── todo.md                     ← Bu dosya
```

---

## Phase 1 — Setup, Scaffolding & Auth

**Süre:** Hafta 1–2  
**Stack:** Python 3.11+, FastAPI, React 18, Vite, Git, **Clerk Auth** 🆕

### Backend

- [x] Python sanal ortamı (venv) oluştur
- [x] FastAPI ve temel bağımlılıkları yükle
- [x] Klasör yapısını oluştur: `/backend`, `/frontend`, `/docs`
- [x] `backend/main.py` — FastAPI app başlangıcı
- [x] `backend/requirements.txt` — tüm bağımlılıkları listele
- [x] `backend/routers/` — boş router klasörü, `__init__.py` ekle
- [x] `backend/.env` — ortam değişkenleri dosyası (commit'leme!)

### Frontend

- [x] Vite ile React 18 projesi oluştur
- [x] React Router kurulumu ve base sayfa yapısını kur
- [x] `frontend/src/App.jsx` — ana uygulama bileşeni + ErrorBoundary + BottomNav
- [x] `frontend/src/components/` — bileşen klasörü oluştur
- [x] `frontend/.env.example` — frontend ortam değişkenleri şablonu

### Auth — Clerk Entegrasyonu 🆕

- [ ] Clerk hesabı oluştur, uygulama kaydet (free tier — 10.000 MAU)
- [ ] Clerk SDK'yı frontend'e kur (`@clerk/clerk-react`)
- [ ] `frontend/src/main.jsx` → `<ClerkProvider>` ile uygulamayı sar
- [ ] `frontend/src/middleware/auth.js` → korunan route'lar için middleware yaz
  - Kimlik doğrulanmamış kullanıcılar portföy ve chat sayfalarına erişememeli
- [x] `backend/middleware/verify_clerk.py` → Clerk JWT token doğrulama middleware'i
- [ ] Clerk publishable key ve secret key'i `.env`'e ekle

### Auth — Kullanıcı Profili Kalıcılığı 🆕

- [x] `backend/models/user.py` — kullanıcı veri modeli
- [x] `backend/routers/users.py` — kullanıcı endpoint'leri
- [x] `backend/db/database.py` — DB bağlantısı (SQLite başlangıç, Postgres üretime geçişte)
- [x] Risk profili sonuçlarını Clerk user ID'ye bağlı DB'ye kaydet
- [x] Geri dönen kullanıcı kendi portföyünü görüntüleyebilmeli

### Config & DevOps

- [ ] Anthropic API anahtarını al ve `.env`'e ekle
- [ ] Clerk publishable + secret key'leri `.env`'e ekle
- [x] `.env.example` → tüm değişken isimlerini içeren örnek dosya oluştur
- [x] `.gitignore` → `.env`, `__pycache__`, `node_modules`, `venv/` ekle
- [ ] Git repo başlat: `main / dev / feature/*` branch modeli
- [ ] İlk commit'i yap
- [ ] GitHub'da `main` branch'ini koru (branch protection rule)
- [ ] `README.md` — temel proje açıklaması (başlangıç versiyonu)

> 💡 Clerk ücretsiz tier 10.000 aylık aktif kullanıcıya kadar ücretsizdir.

---

## Phase 2 — NLP Engine & Risk Profile Module

**Süre:** Hafta 3–5  
**Stack:** Claude API (claude-sonnet-4), FastAPI, Pydantic, Python, SQLite / Postgres

### AI — Claude API Bağlantısı

- [x] Anthropic Python SDK'yı kur (`pip install anthropic`)
- [x] `backend/services/ai_service.py` → Claude API istemcisi ve temel chat fonksiyonu
- [x] `backend/prompts/system_prompt.txt` → Finansal danışman sistem prompt'u yaz
  - **ZORUNLU:** Şu uyarıyı ekle: *"This app does not provide investment advice. It is for educational purposes only. Consult a licensed financial advisor."*
- [x] `backend/routers/chat.py` → `/chat` endpoint'ini aç

### AI — Risk Profili Çıkarma Akışı

- [x] 5 soruluk konuşma akışını tasarla:
  1. Bütçe
  2. Zaman ufku
  3. Kayıp toleransı
  4. Yatırım hedefi
  5. Deneyim seviyesi
- [x] `backend/services/risk_engine.py` → cevaplardan 1-10 arasında risk skoru üret
- [x] `backend/models/user_profile.py` → kullanıcı profil veri modeli (Pydantic)

### API — Profil Kaydetme

- [x] `backend/routers/profile.py` → `POST /profile` endpoint'i
  - Girdi: 5 soru cevabı → risk skoru hesapla → Clerk user ID'ye bağlı DB'ye kaydet
- [x] `backend/models/risk_score.py` → risk skoru veri modeli

### Testing

- [x] `backend/tests/test_risk_engine.py` → pytest ile risk motoru birim testleri (10/10 ✅)
- [ ] `backend/tests/test_chat.py` → chat endpoint testleri
- [ ] Prompt testleri: farklı girdilerle sistem prompt davranışını doğrula

---

## Phase 3 — Market Data & Portfolio Engine 🔄 UPDATED

**Süre:** Hafta 5–8  
**Stack:** yfinance, pandas, numpy, TEFAS API, ExchangeRate API

### Data — Yahoo Finance Entegrasyonu

- [x] `yfinance`, `pandas`, `numpy` kur
- [x] `backend/services/market_data.py` → varlık fiyatı çekme servisi
  - BIST hisseleri (XU100)
  - US ETF'leri (SPY, QQQ)
  - Altın (GLD)
- [x] `backend/services/cache.py` → günlük önbellekleme katmanı (rate limit'ten kaçınmak için)

### Data — TEFAS Fon Verisi

- [ ] TEFAS API araştır, endpoint'leri belirle
- [x] `backend/services/tefas_service.py` → Türk yatırım fonlarını çek
- [x] `backend/data/fund_list.json` → fon listesi oluştur:
  - Muhafazakâr fonlar
  - Dengeli fonlar
  - Agresif fonlar

### Algorithm — Volatilite Ağırlıklı Portföy Formülü 🆕

- [x] `backend/services/volatility.py` → volatilite hesaplama modülü
  - Son 252 işlem günü (1 yıl) günlük getirilerini çek
  - `numpy` ile standart sapma hesapla
  - Günde bir kez hesapla ve cache'e yaz
- [x] `backend/services/portfolio_engine.py` → ana portföy motoru (sabit bucket'ları kaldır)
  - **Formül:**
    ```
    Allocation(asset) = (RiskScore × Volatility(asset)) / SUM(RiskScore × Volatility(i))
    ```
  - Ağırlıkların toplamının 1'e normalize edilmesi
- [x] `backend/models/portfolio.py` → portföy veri modeli

### API — Öneri Endpoint'i

- [x] `backend/routers/recommend.py` → `POST /recommend`
  - Girdi: risk skoru + bütçe
  - Çıktı: portföy ağırlıkları + düz dil açıklaması
- [x] `backend/services/explainer.py` → Claude ile portföy açıklaması üret

---

## Phase 3.5 — Real Estate Layer / REIT ETF 🆕 NEW

**Süre:** Hafta 8–10  
**Stack:** yfinance, pandas, VNQ, SCHH

### Data — REIT ETF Verisi

- [x] `backend/data/asset_universe.json` → VNQ ve SCHH'yi varlık evrenine ekle
- [x] `backend/services/market_data.py` → mevcut yfinance pipeline'ını genişlet (sıfır yeni API)

### Algorithm — Hibrit Sepet Mantığı 🆕

- [x] `backend/services/hybrid_basket.py` → hibrit sepet servisi
  - Kullanıcı bütçesi gayrimenkul eşiğinin altındaysa REIT ETF'leri otomatik dahil et
  - Bunu "mülk satın almadan gayrimenkul exposure'ı" olarak sun
- [x] `backend/services/portfolio_engine.py` → hibrit basket mantığını entegre et

### UI — REIT Kartı 🆕

- [ ] `frontend/src/components/ReitCard.jsx`
  - REIT nedir, neden seçildi, tarihsel getirisi
- [ ] `frontend/src/components/AssetExplainer.jsx` — genel varlık açıklayıcı bileşen

### Content — REIT Açıklayıcı Prompt 🆕

- [x] `backend/prompts/reit_explain_prompt.txt`
  - Claude'un bu kullanıcıya özel 2 cümlelik dinamik açıklama üretmesi için prompt
  - Statik template değil — her kullanıcı için kişiselleştirilmiş

> 💡 Neden Zillow değil REIT? REIT'ler hisse gibi işlem gördüğünden yfinance kapsar. Zillow ayrı veri modeli + ücretli API gerektirir.

---

## Phase 4 — Frontend: Chatbot UI & Visualization

**Süre:** Hafta 10–14  
**Stack:** React 18, Recharts, Axios, React Router, Clerk

> 📱 **Strateji: Mobile-First Web → Capacitor**  
> Tüm UI dikey/telefon uyumlu tasarlandı (100dvh, 48px touch targets, bottom nav, safe-area-inset).  
> Phase 5 sonrası Capacitor ile native iOS/Android uygulamasına sarmalanabilir.

### UI — Chatbot Arayüzü

- [x] `frontend/src/components/ChatWindow.jsx`
  - Mesaj balonları, typing animasyonu, iOS momentum scroll
  - `enterKeyHint="send"` — mobil klavye gönder butonu
- [x] `frontend/src/components/MessageBubble.jsx` — kullanıcı/asistan mesaj balonu
- [x] `frontend/src/hooks/useChat.js` — chat state + Clerk JWT ekleme

### UI — Risk Profili Ekranı

- [x] `frontend/src/pages/ProfilePage.jsx` — chat → skor reveal tek sütun akış
- [x] `frontend/src/components/RiskGauge.jsx` — SVG yarı daire gauge (renk: yeşil→amber→kırmızı)

### Charts — Portföy Dağılım Grafiği

- [x] `frontend/src/components/PortfolioChart.jsx`
  - Recharts donut chart: hisseler / REIT / fonlar / altın / nakit
  - Tıklanabilir dilimler → AssetCard açılır
- [x] `frontend/src/components/AssetCard.jsx` — detay paneli

### Charts — Tarihsel Performans Grafiği

- [x] `frontend/src/components/PerformanceChart.jsx`
  - 12 aylık çizgi grafiği + karşılaştırma modu
  - ⚠️ Mock data — Phase 5'te backend cache'e bağlanacak
- [x] `frontend/src/pages/RecommendPage.jsx` — tek sütun: badge → pie → line → REIT → açıklama

### UX — Yasal Uyarı & Onboarding

- [x] `frontend/src/components/DisclaimerModal.jsx`
  - Checkbox zorunlu — kabul etmeden devam yok
- [x] `frontend/src/pages/OnboardingPage.jsx` — hero + 3 özellik kartı + CTA

### UX — Kaydedilmiş Portföy Dashboard'u

- [x] `frontend/src/pages/DashboardPage.jsx`
  - Profil kartı + re-run / re-profile butonları + portföy snapshot
- [x] `frontend/src/hooks/usePortfolio.js` — portföy + profil yönetimi

### Mobile-First Ekstralar 📱

- [x] `frontend/src/components/BottomNav.jsx` — sabit alt navigasyon (desktop'ta gizli)
- [x] `frontend/src/index.css` — mobile-first design system (100dvh, touch targets, safe-area)
- [x] `frontend/index.html` — PWA meta tagları (theme-color, apple-mobile-web-app)
- [x] `frontend/src/utils/errorBoundary.jsx` — React Error Boundary
- [x] `frontend/src/utils/api.js` — Axios istemcisi + Clerk JWT bağlama

> 💡 Bu dashboard yalnızca Phase 1'deki Clerk Auth sayesinde mümkün. Auth önce gelir.

> 🚀 **Capacitor (Opsiyonel — Phase 5 sonrası)**  
> `npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android`  
> `npx cap init && npx cap add ios && npx cap sync`  
> Tek komutla native uygulama.

---

## Phase 5 — Testing, Deployment & Portfolio Presentation

**Süre:** Hafta 14–18  
**Stack:** pytest, Playwright, React Testing Library, Render.com, Vercel, GitHub Actions

### Testing — E2E Testler

- [ ] `tests/e2e/test_full_flow.py` → Playwright ile tam akış testleri
- [ ] `tests/e2e/scenarios.json` → 5 kullanıcı tipi senaryosu:
  1. Muhafazakâr (Conservative)
  2. Orta (Moderate)
  3. Agresif (Aggressive)
  4. Kısa vadeli (Short-term)
  5. Emeklilik (Retirement)
- [ ] Her senaryo: onboarding → chat → risk profili → portföy → dashboard

### Testing — Hata Yönetimi & Edge Case'ler

- [ ] `backend/middleware/error_handler.py` → global hata yakalama middleware'i
  - API çökmesi, saçma input, boş portföy, süresi dolmuş oturum
- [ ] `frontend/src/utils/errorBoundary.jsx` → React Error Boundary
- [ ] Her hata durumu için kullanıcıya anlamlı mesaj göster

### Deploy — Backend → Render.com

- [ ] `Dockerfile` → FastAPI uygulaması için Docker imajı
- [ ] `render.yaml` → Render.com deployment konfigürasyonu
- [ ] `backend/routers/health.py` → `/health` endpoint'i (uptime monitoring)
- [ ] Render'a tüm env var'ları ekle: `ANTHROPIC_API_KEY`, `CLERK_SECRET_KEY`, `DATABASE_URL`
- [ ] Deployment test et, `/health` endpoint'inin döndüğünü doğrula

### Deploy — Frontend → Vercel

- [ ] `vercel.json` → Vercel deployment konfigürasyonu
- [ ] `frontend/.env.production` → `VITE_BACKEND_URL`, `VITE_CLERK_PUBLISHABLE_KEY`
- [ ] Clerk production instance'ına bağlan
- [ ] Vercel'e deploy et ve tam akışı test et

### Portfolio — README & Mimari Dokümantasyon

- [ ] `README.md` — ne yapar, nasıl çalıştırılır, mimari kararlar + gerekçeleri, ekran görüntüleri
- [ ] `docs/architecture.md` — sistem mimarisi diyagramı ve açıklaması
- [ ] `docs/api_reference.md` — tüm API endpoint'leri ve kullanımları

### Portfolio — Demo Video & Case Study

- [ ] `demo/demo_script.md` → 2-3 dakikalık demo için script
  - Tam akış: kayıt → onboarding → chat → risk profili → portföy → dashboard
- [ ] Ekran kaydı çek (Loom / OBS / QuickTime)
- [ ] `docs/case_study.md` → teknik kararlar, zorluklar, öğrenilenler
- [ ] Demo videosunu GitHub repo'suna yükle
- [ ] LinkedIn'de paylaş

> 💡 Bu faz tamamlanıp MVP yayına girdikten sonra AWS migration anlamlı bir adımdır. Öncesinde değil.

---

## 🔑 Kritik Hatırlatmalar

| # | Kural |
|---|-------|
| 1 | `.env` dosyasını **asla** commit etme |
| 2 | Her sistem prompt'una yasal uyarıyı ekle |
| 3 | Tüm API çağrılarını günlük cache'e al |
| 4 | Clerk JWT doğrulamasını backend'de yap |
| 5 | Tüm hata durumları için fallback UI yaz |
| 6 | AWS ve Ollama MVP sonrasına ertele |
| 7 | Temel kural, her işlemden sonra otomatik olarak todo.md dosyasını güncellle |

---

## 📊 İlerleme Özeti

| Faz | Başlık | Hafta | Durum |
|-----|--------|-------|-------|
| 1 | Setup, Scaffolding & Auth | 1–2 | `[/]` Backend ✅ · Frontend ⏳ |
| 2 | NLP Engine & Risk Profile | 3–5 | `[x]` Backend tamamlandı ✅ |
| 3 | Market Data & Portfolio Engine | 5–8 | `[x]` Backend tamamlandı ✅ |
| 3.5 | Real Estate / REIT Layer | 8–10 | `[x]` Backend tamamlandı ✅ |
| 4 | Frontend — Mobile-First Chat UI | 10–14 | `[x]` Tamamlandı ✅ · Build başarılı |
| 5 | Testing, Deploy & Portfolio | 14–18 | `[ ]` |
