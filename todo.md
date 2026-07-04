# Lumos - Smart Investment Assistant — TODO 

> **~18 hafta · 8 faz · $0 başlangıç maliyeti**
> Başlangıç: 2026-05-09

## 🌟 Ürün Vizyonu

**Yatırım hakkında hiçbir fikri olmayan insanların KORKMADAN, ÖĞRENEREK yatırım yapabilmesi.**

Her özellik şu filtreden geçmeli: *"Bu, çekingen bir yeni başlayanın anlamasına ve harekete geçmesine yardım ediyor mu?"*

| İlke | Anlamı |
|------|--------|
| Önce anlat, sonra göster | Hiçbir grafik/terim açıklamasız ekrana gelmez |
| Jargonsuz varsayılan | "Volatilite" değil "fiyatın inişli çıkışlılığı" — terim isteyen detaya tıklar |
| Küçük ilk adım | Kullanıcıyı büyük tutarla değil, alıştırma ve küçük adımlarla başlat |
| Korku = veri | Kullanıcının çekincesi bastırılacak değil, adreslenecek bir sinyal |
| İki dünya tek çatı | Emlak + borsa aynı portföyde, aynı dilde |

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
│   │   ├── ai_service.py       ← Provider-agnostic AI istemcisi (Gemini/Claude)
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
- [x] `backend/tests/test_chat.py` → chat endpoint testleri
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

## Phase 6 — Teknik Borç & Production Sağlamlaştırma 🆕

**Süre:** Phase 5 sonrası  
**Kaynak:** Proje analizi raporu (2026-06-16)

### Test Kapsamı

- [x] `backend/tests/test_chat.py` → chat router integration testi (AI mock'lanmış, 4 test)
- [x] `backend/tests/test_recommend.py` → recommend endpoint testi (engine + explainer mock'lu, 4 test)
- [x] `backend/tests/test_profile.py` → profile router testi (in-memory DB, 5 test)
- [x] AI servis testleri için AI mock fixture'ı (`conftest.py` — `_dispatch` patch + auth bypass)
- [ ] `tests/e2e/` içeriğini doldur (şu an boş/iskelet)

### CI/CD

- [x] `.github/workflows/ci.yml` → push/PR'da ruff + pytest (backend, Python 3.9)
- [x] Aynı workflow'a eslint + build (frontend, Node 22) adımı eklendi — vitest frontend testleri yazılınca eklenecek
- [ ] Branch protection: CI geçmeden main'e merge engellensin

### Veritabanı


- [x] `alembic init` (async template) + baseline migration (`04f9da6e7e6d`: users tablosu + indexler); dev DB `alembic stamp head` ile damgalandı
- [/] `create_all` → migration geçiş planı: dev'de create_all kalıyor (zararsız, checkfirst); yeni şema değişikliği geldiğinde akış = model değiştir → `alembic revision --autogenerate` → `alembic upgrade head`; prod deploy'da startup öncesi `alembic upgrade head` çalıştırılacak, create_all prod'da kaldırılacak

### Deployment

- [ ] `Dockerfile` (backend) — Phase 5'te planlı, henüz yok
- [ ] Local docker-compose ile backend+db'yi ayağa kaldırma testi

### Veri Sağlayıcı Riski

- [ ] yfinance rate-limit / kırılma senaryolarına fallback ekle
- [ ] TEFAS resmi API'sine kademeli geçiş değerlendirmesi
- [ ] Cache TTL stratejisini (cache.py) veri tazeliği ihtiyacına göre gözden geçir

### AI Servis Gözlemlenebilirliği

- [ ] Claude çağrıları için structured logging (latency, token sayımı, hata)
- [ ] Prompt versiyonlama (system_prompt.txt, reit_explain_prompt.txt değişiklik takibi)
- [ ] Anthropic SDK güncelle (0.39.0 → güncel) — prompt caching ile maliyet düşür

### Güvenlik & Compliance

- [x] `slowapi` ile AI endpoint'lerine rate limiting ekle (chat, recommend)
- [ ] Prompt injection koruması: kullanıcı girdisini system prompt'tan ayrıştır
- [/] Structured output: risk profili çıkarımı yapılandırıldı (`/chat/extract-profile` + JSON extraction prompt'u) — portföy çıktısı tool-use'a geçirilecek

### AI Danışman Kalitesi 🆕

> ✅ **Çözüldü (2026-07-04):** Kopuk profil akışı onarıldı — AI tamamlanınca `[PROFILE_COMPLETE]` işareti veriyor, frontend `/chat/extract-profile` ile yapılandırılmış cevapları çekip skor ekranına geçiyor.

- [x] `system_prompt.txt`'i derinleştir: MPT/risk-getiri çerçevesine açık referans, karşı soru sorma davranışı, yasal/etik sınırların net ifadesi
- [x] Few-shot örnek diyaloglar ekle (1 örnek embedded) — danışman tonunu örnekten öğret
- [x] `reit_explain_prompt.txt`'i derinleştir: 3 cümle yapısı, profil-spesifik ton, dürüst risk uyarısı, MPT bağlamı
- [ ] RAG: `market_data.py` / `tefas_service.py`'den çekilen gerçek zamanlı veriyi chat akışına context olarak inject et (şu an sadece `explainer.py`'de kısmen var)
- [ ] Tool-use mimarisi: `get_market_data(ticker)`, `calculate_volatility(asset)`, `get_risk_score(profile)` tool tanımları — Claude veriyi kendi üretmek yerine servislerden çeksin
- [ ] Kullanıcı geri bildirim döngüsü: portföy önerisi kabul/red oranını ve soru pattern'lerini logla
- [ ] Prompt versiyonlarını A/B test et, Anthropic Console Prompt Improver ile mevcut prompt'u güçlendir

---

## Phase 7 — Ürün Derinleştirme & Kişisel Yatırım Takibi 🆕

**Süre:** Phase 6 ile paralel yürütülebilir
**Kaynak:** Ürün vizyonu görüşmesi (2026-06-28)

### AI Sağlayıcı Esnekliği (maliyet çözümü)

- [x] `ai_service.py`'yi provider-agnostic yap: tek `chat()` / `generate_text()` interface'i, arkasında adapter'lar
- [x] Gemini adapter ekle (`google-generativeai`) — free tier, geliştirme/demo varsayılanı
- [ ] `google-generativeai` → `google-genai` SDK migrasyonu (eski paket deprecated, uyarı veriyor)
- [x] `.env`'e `AI_PROVIDER=gemini|anthropic` seçimi; Claude adapter'ı mevcut kodu sarmalasın
- [x] Provider'a özel hata yönetimi (kredi bitti / kota doldu → kullanıcıya anlamlı mesaj)

### Risk Profili Derinleştirme

- [x] 7 soruya iki boyut yedir: yaş/emekliliğe kalan süre (Q2) + gelir istikrarı (Q7)
- [ ] Dinamik follow-up: profil belirsizse LLM ek soru sorabilsin (7–10 soru arası esnek akış)
- [ ] `risk_engine.py`'yi yeni boyutlara göre güncelle (yaş ve gelir istikrarı skora etki etsin)

### Kişisel Yatırım Takibi 💰 (abi fikri)

- [ ] `backend/models/holding.py` — kullanıcı varlık modeli: tip (hisse/fon/arsa/altın/nakit/araç...), ad, alış tarihi, alış tutarı, adet/miktar, serbest not
- [ ] Araç varlık tipi — dürüst çerçeveyle: net servet resminde yer alır AMA amortisman hesabıyla gösterilir (yıllık değer kaybı + kasko/MTV/bakım maliyeti); "Araban serveti mi, gideri mi?" eğitim kartı eşlik eder — AI asla araç almayı yatırım olarak ÖNERMEZ
- [ ] `backend/routers/holdings.py` — CRUD endpoint'leri: varlık ekle/güncelle/sil/listele
- [ ] Bütçe takibi: kullanıcı toplam yatırım bütçesini girer → her yatırım sonrası "kalan bütçe" otomatik hesaplanır
- [ ] Borsa dışı varlıklar (arsa, gayrimenkul) için manuel değerleme alanı; borsa varlıkları için yfinance'ten güncel fiyatla otomatik değerleme
- [ ] `frontend/src/pages/PortfolioPage.jsx` — "Varlıklarım" sayfası: toplam değer, kalan bütçe, varlık listesi, dağılım grafiği
- [ ] Dashboard'a özet kart: toplam varlık değeri + kalan bütçe + günlük değişim
- [ ] Gerçek portföy vs önerilen portföy karşılaştırması ("hedef dağılımından sapma" göstergesi)

### Mimari & Kod Kalitesi 🏛️ (clean architecture revizyonu)

> Sıralama önerisi: repository/schema refactor → error handling → RBAC → Python 3.12

- [ ] `backend/repositories/` katmanı: tüm SQLAlchemy sorgularını router'lardan buraya taşı (`user_repository.py` ile başla — recommend.py'deki inline select buraya)
- [ ] `backend/schemas/` klasörü: Pydantic request/response şemalarını `models/`'tan ayır; `models/` sadece ORM
- [ ] Domain exception sınıfları: `AIServiceError`, `MarketDataError`, `QuotaExceededError` (`backend/exceptions.py`) + error_handler'da tip bazlı yakalama
- [ ] Standart hata yanıt şeması: `{"error": {"code", "message", "request_id"}}` — tüm hata yolları aynı formatı dönsün
- [ ] `X-Request-ID` middleware: her isteğe correlation ID, log satırlarına ve hata yanıtlarına ekle
- [ ] API versiyonlama: tüm router'ları `/api/v1` prefix'i altına al (frontend api.js baseURL güncelle)
- [ ] Hafif RBAC: User modeline `role` alanı (`user`/`admin`) + `require_role()` dependency; admin-only `/api/v1/admin/stats` endpoint'i (kullanıcı sayısı, mesaj hacmi, kota durumu)
- [ ] Health check'i derinleştir: `/health` DB bağlantısını ve AI provider erişimini gerçekten yoklasın (`{"db": "ok", "ai": "ok"}`)
- [ ] Python 3.9 → 3.12 migrasyonu: venv'i yeniden kur, `Optional[X]`'leri `X | None`'a geri çevir, greenlet pin'ini kaldır
- [ ] pre-commit hook: ruff + black otomatik format (`.pre-commit-config.yaml`)
- [ ] Sızan Anthropic API anahtarını rotate et (Console → API Keys)

### Mobil Strateji 📱 (karar: 3 kademe — 2026-06-28)

> Kademe 1: mobile-first web ✅ (Phase 4'te yapıldı) → Kademe 2: tam PWA (MVP ile) → Kademe 3: Capacitor native (MVP sonrası, bütçe olunca)
> React Native/Flutter'a geçiş YOK — mevcut React kod tabanı korunur.

- [ ] PWA'yı tamamla: service worker + manifest.json + temel offline ekranı ("Ana ekrana ekle" ile native his, store'suz, $0)
- [ ] Capacitor sarma (MVP sonrası): store meşruiyeti + **push notification = davranışsal koçun taşıyıcısı** ("piyasa düştü, sakin ol" gerçek zamanlı ancak push ile çalışır; iOS web push güdük) — Apple $99/yıl + Google $25 bütçesi gerekir

### Kullanım Kotası

- [ ] Kullanıcı başına günlük mesaj kotası (DB tabanlı sayaç, örn. 50 mesaj/gün)
- [ ] Kota dolunca kibar bilgilendirme UI'ı (yarın sıfırlanır mesajı)

### Eğitim Katmanı 📚 (vizyonun kalbi — öncelik yükseltildi)

- [ ] Varlık bazlı eğitim: her portföy kalemi için "nedir / neden portföyünde / riski ne" LLM açıklaması (generalize edilmiş explain prompt)
- [ ] `AssetExplainer.jsx`'i bu içeriği gösterecek şekilde doldur
- [ ] Temel kavramlar sözlüğü (volatilite, çeşitlendirme, ETF vs fon, REIT...) — statik içerik, LLM maliyeti sıfır
- [ ] Kullanıcının yatırım yaptığı her varlık tipinde ilk alımda otomatik eğitim kartı göster
- [ ] Jargon tooltip sistemi: UI'da geçen her finans terimi altı çizili + tık → sade Türkçe açıklama balonu (sözlükten beslenir, tüm sayfalarda)
- [x] system_prompt'a "sıfır bilgi varsay" kuralı: her cevapta terimleri günlük dille açıkla, kullanıcı bilgi seviyesi gösterirse dili kademeli teknikleştir (+ korku-farkındalık kuralı: endişeyi önce karşıla, sonra cevapla)
- [ ] UI metin denetimi: tüm sayfalardaki mevcut metinleri jargonsuzluk ilkesine göre elden geçir ("Risk Profiling" → "Seni Tanıyalım" gibi)

---

## Phase 8 — Farklılaştırıcı Özellikler 🚀 (piyasa analizi: 2026-06-28)

> Konumlandırma: Midas/Getir Finans = işlem, robo-advisor'lar = kara kutu öneri, Fintables = analiz.
> Lumos'un boşluğu: **"anlayarak yatırım"** — öneriyi açıklayan, davranışı koçlayan, Türkiye gerçeklerine göre konuşan asistan.

### Zaman Makinesi & Varlık Karakteri 🕰️ (en güçlü demo özelliği)

- [ ] "Bu portföyü 5 yıl önce kursaydın bugün ne olurdu?" — yfinance geçmiş verisiyle backtest
- [ ] `backend/services/backtest.py` → verilen ağırlıklar + tarih aralığı → kümülatif getiri serisi
- [ ] Duraklama dönemi tespiti: varlığın geçmişindeki yatay/durgun dönemleri algıla ("bu hisse 2018-2021 arası 3 yıl yatay seyretti") — garanti getiri isteyen profillere uzun duraklama geçmişi olan varlıkları işaretle
- [ ] Varlık karakter kartı: her varlık için "en uzun duraklama", "en derin düşüş", "toparlanma süresi" özeti — profil uyum rozeti (bu varlık senin sabrına uygun mu?)
- [ ] RecommendPage'e interaktif grafik: önerilen portföyün 1/3/5 yıllık geçmiş simülasyonu + en kötü dönem vurgusu ("2022'de %18 düşecekti — buna hazır mısın?")
- [ ] Risk toleransı sorusunu somutlaştır: soyut "%20 düşerse" yerine kullanıcının kendi bütçesiyle "50.000 TL'n 40.000 TL olurdu" göster

### Emlak + Borsa Hibrit 🏘️📈 (Midas'a karşı ana koz)

> Midas yatırım aracıdır ama emlak derinliği sıfır. Lumos'un kimliği: **satın alma yolculuğunun tamamına** rehberlik —
> "1M TL'm var" → AI bölüşümü önerir → değerlenecek bölgeyi gösterir → ilana yönlendirir → alınca portföye işler → kalanla borsa planı yapar.

#### ⚖️ İşlem Modeli (kesin karar — 2026-06-28)

> **Lumos işlem GERÇEKLEŞTİRMEZ — iki dünyada da model: rehberlik et → dışarıda satın al → uygulamada takip et.**
>
> | | Borsa | Emlak |
> |---|---|---|
> | Neden in-app alım yok | SPK aracı kurum lisansı gerekir (sermaye + denetim + yıllar) | Fiziksel dünya işlemi (tapu) |
> | Rehberlik | Portföy önerisi + "aracı kurumda nasıl alınır" rehberi | Bölge kartları + ilan köprüsü + değerlendirme asistanı |
> | Satın alma | Kullanıcının kendi aracı kurumu (Midas, İş Yatırım...) | Sahibinden/emlakçı üzerinden |
> | Dönüş | "Aldım" → holdings'e işle → portföy güncellenir | "Aldım" → holdings'e işle → portföy güncellenir |
>
> Avantajlar: sıfır regülasyon riski, para emanet alınmaz (güven eşiği düşük — korkak başlayan için artı), $0 maliyet korunur.
> İleri faz (iş geliştirme): aracı kurum API ortaklığı ile "tek tık emir iletimi" — emlak platform ortaklığıyla aynı statüde, MVP dışı.

- [ ] Onboarding'de dürüst beklenti cümlesi: "Lumos sana yol gösterir; alım-satımı kendi aracı kurumunda/emlakçında yaparsın, sonra burada takip ederiz"
- [ ] Borsa "Aldım" akışı: öneri ekranından tek tıkla holdings'e ön-dolu kayıt (emlaktaki Akış 4 ile simetrik)
- [ ] "Aracı kurum hesabı nasıl açılır" rehberi (Korkusuz Başlangıç'taki rehberli yolculukla aynı madde — çift kayıt değil, referans)

#### Akış 0 — Yol Seçimi 🧭 (yapısal ilke: akışlar zorunlu değil, seçilebilir)

> Kullanıcı emlak seçmek ZORUNDA değil. Üç eşit yol: sadece borsa (Midas tarzı) / sadece emlak keşfi / karma. Her akış bağımsız çalışır.

- [ ] Onboarding'e ilgi sorusu: "Nasıl yatırım yapmak istersin?" → 🏦 Sadece borsa · 🏘️ Sadece emlak · ⚖️ İkisi birden · 🤷 Kararsızım (AI profil sonrası önerir)
- [ ] "Sadece borsa" yolu: emlak modülleri hiç görünmez — mevcut risk profili → portföy önerisi akışı aynen (bütçe bölüşümünde emlak dilimi çıkmaz)
- [ ] "Sadece emlak" yolu: risk profili yine yapılır (vade + likidite kritik) ama çıktı bölge kartları + ilan değerlendirme + eğitim; borsa önerisi dayatılmaz
- [ ] "Kararsızım" yolu: profil + korku check-in sonucuna göre AI yol önerir ("düzenli birikim + uzun vade → önce borsa fonlarıyla başla, emlak eşiğine gelince haber veririm")
- [ ] Yol her an değiştirilebilir (ayarlar + dashboard'da "emlak dünyasını keşfet" yumuşak daveti — dayatma yok)
- [ ] Bütçe bölüşüm danışmanı yalnızca karma/kararsız yolda aktif; tek-yol kullanıcıda bütçenin tamamı seçili dünyaya planlanır

#### Akış 1 — Bütçe Bölüşüm Danışmanı (giriş noktası)

- [ ] Emlağı tahsis edilebilir varlık sınıfı yap: portfolio_engine "1.000.000 TL + profil" → "600K emlak / 300K hisse-fon / 100K nakit yedek" bölüşümü önersin (risk skoru + likidite ihtiyacı + bütçe eşiği girdileriyle)
- [ ] Bölüşüm gerekçesi LLM anlatımı: neden bu oranlar, hangi profilde nasıl değişirdi (öğreten ton)
- [ ] REIT vs fiziksel emlak karar noktası: bütçe eşik altındaysa veya likidite ihtiyacı yüksekse "fiziksel yerine REIT" yönlendirmesi (hybrid_basket çift yönlü)

#### Akış 2 — Bölge Değerlenme İstihbaratı (AI "nereden alayım?" cevabı)

- [ ] TCMB Konut Fiyat Endeksi (EVDS, il bazlı, ücretsiz): illerin 1/3/5 yıllık nominal + reel değerlenme sıralaması
- [ ] TÜİK nüfus/göç verisi entegrasyonu: net göç alan + genç nüfuslu ilçeler = talep sinyali
- [ ] "Değerlenme Potansiyeli" bölge kartları: veri (endeks trendi + göç + LLM bağlam yorumu) → "uzun vadede öne çıkan bölgeler" listesi — il/ilçe seviyesinde, parsel iddiası YOK (dürüstlük ilkesi: "mahalle/parsel analizi yapamayız, bölge trendi gösteririz")
- [ ] Kullanıcı hedefiyle eşleştir: "20 yıl bekleyebilirim" → uzun vade değerlenme bölgeleri; "5 yılda satarım" → likiditesi yüksek merkezi bölgeler

#### Akış 3 — İlan Köprüsü (satın almaya yönlendirme)

- [ ] Filtre-hazır dış linkler: AI bölge önerince Sahibinden/Emlakjet'e o ilçe+arsa filtreli arama linki üret ("Bu bölgedeki ilanları gör →") — ilan verisi bizde durmaz, hukuki risk yok
- [ ] **İlan değerlendirme asistanı**: kullanıcı beğendiği ilanın bilgilerini yapıştırır (konum, m², fiyat) → AI bölge ortalama m² fiyatıyla kıyaslar: "bölge ortalamasının %20 üstünde" + pazarlık/kontrol listesi (imar durumu, tapu cinsi, yola cephe...)
- [ ] Satın alma kontrol listesi rehberi: arsa/daire alırken adım adım ne kontrol edilir (statik eğitim içeriği, TR'ye özgü: tapu, imar, DASK...)
- [ ] (İleri faz — iş geliştirme) Emlak platformu API ortaklığı: gerçek ilan + emlakçı iletişimi in-app gösterim

#### Akış 4 — Döngüyü Kapat (alım sonrası)

- [ ] "Aldım" akışı: ilan değerlendirmeden tek tıkla holdings'e kayıt (Phase 7 formu ön dolu gelir)
- [ ] Kalan bütçeyi otomatik yeniden planla: "600K'yı arsaya bağladın, kalan 400K için hisse-fon planın hazır" → recommend akışına köprü
- [ ] TCMB endeksiyle emlak varlığının değerini dönemsel güncelle ("endekse göre tahmin" etiketiyle)
- [ ] Kira getirisi vs temettü verimi karşılaştırması: "bu daire yıllık %4 kira getirir, bu temettü portföyü %6 öder"
- [ ] Likidite skoru: portföy sağlık skoruna emlak likidite bileşeni ("varlıklarının %70'i 6 ayda nakde dönmez — acil ihtiyaç planın var mı?")
- [ ] "500.000 TL'lik arsa mı, 500.000 TL'lik portföy mü?" karşılaştırma ekranı: aynı tutar, geçmiş 5 yıl, konut endeksi vs portföy getirisi yan yana (+ likidite ve masraf farkları tablosu)

#### Akış 5 — Kira & Ev Kararları 🏠 (giriş kapısı özelliği)

> Türkiye'de yatırım bilmeyenin ilk finansal sorusu: "kirada mı oturayım, ev mi alayım?" — bu soruya cevap veren araç, uygulamaya kullanıcı çeken kapı olur.

- [ ] **"Kirada mı otur, ev mi al?" karar aracı**: peşinat tutarı + aylık kira + il girdisi → iki senaryo yan yana: (A) ev al: kira ödemezsin, paran konut endeksiyle değerlenir; (B) kirada kal: peşinat portföyde çalışır, kirayı ödersin — 5/10/20 yıllık projeksiyon, jargonsuz LLM anlatımıyla ("ev almak her zaman kazanç değildir" dürüstlüğü)
- [ ] Karar aracına duygu boyutu: "ev sahibi olma güvencesi"nin parasal olmayan değerini de anlat (vizyon ilkesi: korku/duygu = veri)
- [ ] Aylık ödenen kirayı profil girdisi yap: yatırılabilir gerçek tutar = gelir − kira − zorunlu giderler → bütçe bölüşüm danışmanı bu net tutarla konuşsun
- [ ] Kapsam sınırı (bilinçli karar): kiralık ilan arama / mortgage pazaryeri EKLENMEYECEK — Lumos karar destek uygulamasıdır, emlak portalı değil

### Enflasyon Gerçekliği 🇹🇷 (yerel farklılaştırıcı — kimse yapmıyor)

- [ ] Tüm getirileri nominal + reel (TÜFE arındırılmış) çift gösterim — "mevduat %45 kazandırdı ama reel %-12"
- [ ] TÜFE verisi entegrasyonu (TCMB EVDS API ücretsiz)
- [ ] Portföyde TL/döviz dağılımı ve kur riski göstergesi
- [ ] "Param eriyor mu?" kartı: kullanıcının nakit pozisyonunun aylık reel kaybı

### Davranışsal Koç 🧠 (robo-advisor'ların yapmadığı)

- [ ] Piyasa sert düştüğünde profil-bazlı sakinleştirme: panik satıcı profiline özel "tarihsel toparlanma" mesajı, fırsatçı profiline "plana sadık kal" uyarısı
- [ ] Kullanıcının davranış günlüğü: profilde "düşüşte satarım" deyip yükselişte alım yapıyorsa nazikçe aynayı tut
- [ ] "Yatırım kararını duygu mu veri mi verdi?" — alım kaydında opsiyonel 1-tık duygu etiketi (FOMO/plan/tüyo), aylık davranış raporu

### Hedef Bazlı Yatırım 🎯

- [ ] Hedef tanımlama: "3 yılda ev peşinatı 800.000 TL" → gereken aylık katkı + uygun risk bandı hesabı
- [ ] Hedefe ilerleme çubuğu (mevcut varlıklar + planlanan katkıyla projeksiyon)
- [ ] Hedef sapma uyarısı: "bu tempoda hedefin 8 ay gecikir"

### Portföy Sağlık Skoru 💯

- [ ] Tek bakışta 0-100 skor: çeşitlendirme + hedef dağılıma uyum + maliyet + kur dengesi bileşenleri
- [ ] Her bileşen için "neden düşük, nasıl yükselir" LLM açıklaması
- [ ] Dashboard'a skor kartı + zaman içinde skor grafiği

### What-If Asistanı 🔮

- [ ] Chat'te senaryo soruları: "10.000 TL daha eklesem ne değişir?", "altını çıkarsam risk ne olur?" — portfolio_engine'i tool olarak çağırıp gerçek hesapla cevapla (tool-use maddesiyle birleşir)

### Sakin Haber Akışı 📰 (haber = eğitim, gürültü değil)

> Ham haber akışı yeni başlayan için korku makinesidir. Lumos haberi süzer, sakinleştirir, öğretir.

- [ ] RSS entegrasyonu (ücretsiz): AA Ekonomi, Bloomberg HT, KAP bildirimleri → `backend/services/news_service.py`
- [ ] LLM haber süzgeci: kullanıcının portföyüne/yoluna göre alakalı haberleri seç, jargonsuz 2 cümle özet + "seni etkiler mi?" değerlendirmesi + sakinlik notu ("panik gerektirmez")
- [ ] Günlük "Bugün Ne Oldu?" kartı (dashboard): en fazla 3 haber — bilgi bombardımanı yok (kademeli arayüz ilkesi)
- [ ] Haber → davranışsal koç köprüsü: sert düşüş haberi geldiğinde koç mesajı otomatik tetiklenir (Phase 8 davranışsal koç ile birleşir)
- [ ] Manşet dili eğitimi: "BORSA ÇAKILDI manşeti gördüğünde gerçekte ne olur?" mikro-eğitim kartı

### Korkusuz Başlangıç 🐣 (vizyonun ta kendisi — en yüksek öncelik)

> Yatırım bilmeyen biri gerçek para riske atmadan önce güven kazanmalı.

- [ ] **Sanal portföy (alıştırma modu)**: kullanıcı sahte 100.000 TL ile önerilen portföyü "kurar", gerçek piyasa verisiyle canlı izler — sıfır risk, gerçek öğrenme. Gerçek yatırıma geçiş butonu hazır olunca
- [ ] Sanal portföy haftalık özeti: "Bu hafta 2.300 TL kazandın — işte nedeni" LLM anlatımı (neyin niye oynadığını öğretir)
- [ ] İlk yatırım rehberli yolculuğu: adım adım sihirbaz — "aracı kurum hesabı nedir → nasıl açılır → ilk emir nasıl verilir" (Türkiye'ye özgü, ekran görüntülü statik rehber)
- [ ] Korku check-in'i: onboarding'de "yatırımda seni en çok ne korkutuyor?" sorusu (param erir / kandırılırım / anlamam / batırırım) → LLM cevaplarında bu korkuya özel güvence dili kullansın
- [ ] "Bugün öğrendin" mikro-kartları: her oturumda tek küçük kavram ("ETF aslında bir sepettir") — 15 saniyelik okuma, ilerleme sayacı
- [ ] Kademeli arayüz: yeni kullanıcıda sade görünüm (3 metrik), "detay göster" ile zenginleşir — bilgi bombardımanı korkuyu büyütür
- [ ] Cesaret göstergesi: kullanıcının bilgi yolculuğu ilerledikçe "hazırlık skoru" artar — "gerçek yatırıma hazırsın" eşiği

---

## Phase 8.5 — Globalleşme Mimarisi 🌍 "Market Pack" Sistemi

> Karar (2026-06-28): proje GLOBAL tasarlanacak. Yöntem: ülkeye özgü her şey tek pakette — kod ülke bilmez, pakete sorar.
> Yeni ülke eklemek = yeni kod değil, yeni config + veri adaptörü + içerik paketi. TR ilk referans pack olarak eksiksiz yapılır.

### Market Pack Çekirdeği

- [ ] `backend/markets/` yapısı: her ülke bir pack — `tr.py` / `us.py`... + `base.py` (MarketPack interface)
- [ ] Pack içeriği tanımı: para birimi & format, enflasyon veri kaynağı adaptörü (TR: TCMB EVDS → US: FRED), konut endeksi kaynağı, ilan sitesi köprü şablonları (Sahibinden → Zillow → ImmoScout24), aracı kurum rehber içeriği, varlık evreni (BIST+TEFAS → NYSE+ETF'ler)
- [ ] Kullanıcı profiline `market` alanı; tüm servisler pack üzerinden veri kaynağı seçer (doğrudan TCMB/TEFAS import'u kalmaz)
- [ ] i18n altyapısı: UI metinleri + LLM prompt'ları locale dosyalarında (react-i18next + prompt şablonlarına dil parametresi)

### İçerik Yerelleştirme (LLM avantajı)

- [ ] Hukuk/vergi eğitim içeriği pack başına LLM ile üretilir + "genel bilgidir, yerel uzmana danış" disclaimer'ı (hukuki iddia yok, eğitim var)
- [ ] Kültürel korku haritası pack'e dahil: TR "param enflasyona erir" / US "kandırılırım" / DE "risk sevmem" — korku check-in seçenekleri ülkeye uyarlanır
- [ ] Kavram sözlüğü çeviri değil yerelleştirme: örnekler yerel para ve yerel ürünlerle ("ETF bir sepettir — içinde THY, Aselsan..." vs "...Apple, Microsoft...")

### Uygulama Sırası

- [ ] TR pack'i referans implementasyon olarak eksiksiz bitir (MVP = TR)
- [ ] İkinci pack adayını veriye göre seç (US genel pazar mı, DE gurbetçi segmenti mi) — MVP SONRASI
- [ ] Hardcode denetimi: kod tabanında TL/TÜFE/Sahibinden geçen her yer pack referansına taşınmış mı kontrolü

## Phase 9 — Marka & Özgün UI Kimliği ✨ "Işık" Tasarım Dili

> Marka hikayesi = ürün vizyonu: **bilinmezlik karanlıktır, bilgi ışık tutar.** HP'den esinlenilmiş, telif-güvenli özgün yorum.

### Logo & Marka — KARAR: Ateş Böceği 🪰✨ (2026-06-28)

- [x] Logo kararı: ateş böceği (karanlıkta yol gösteren minik ışık) — telif-güvenli, sıcak, özgün
- [ ] Logo tasarımı: minimalist ateş böceği — gövde basit, ışık halesi vurgulu; favicon'da sadece parlayan nokta
- [ ] Giriş animasyonu: açılışta uçuşan ateş böcekleri "Lumos" yazısının üzerine konar, yazı ışıldar (canvas/CSS particle — 2-3 sn, skip edilebilir)
- [ ] Ateş böceği boş durum/onboarding illüstrasyonlarında rehber karakter olarak kullanılır
- [ ] Marka manifestosu (onboarding ilk ekran): "Yatırım karanlık bir orman gibi görünür. Lumos, elindeki ışık." — 2 cümle, jargonsuz
- [ ] Telif kontrolü: şimşek, asa çizimi, HP fontları KULLANILMAZ — ateş böceği + soyut ışık motifi bizim

### "Aydınlanan Arayüz" 🌗 (imza özellik — başka finans uygulamasında yok)

- [ ] Tema tonu kullanıcının hazırlık/cesaret skoruna bağlı: gece laciverti → alacakaranlık → şafak degradesi (CSS custom property ile skor-tabanlı zemin)
- [ ] "Öğrendikçe dünyan aydınlanıyor" — skor artınca geçiş anında 1 kerelik yumuşak ışıma animasyonu + tebrik mikro-kartı

### İmza Etkileşimler

- [ ] "Işık Tut" tooltip: jargon terime tıklayınca minik ışık patlaması + sade açıklama balonu (Phase 7 tooltip sistemiyle aynı madde — marka adı bu)
- [ ] Sayı animasyonu: değerler ekrana soğuk griden "ısınarak" (amber'e) gelir
- [ ] Loading state: spinner yerine uçta büyüyen ışık noktası
- [ ] Eğitim mikro-kartları tılsım kartı çevirme animasyonuyla açılır
- [ ] Portföy sağlık skoru = "Fener": sağlık arttıkça fener ikonu daha gür yanar

### Tasarım Sistemi

- [ ] Palet dokümante et: gece laciverti zemin + sıcak altın-amber ana vurgu (ışık/para çift çağrışım) + lavanta ikincil + şafak degradesi (`index.css` design token'ları)
- [ ] Tipografi: yumuşak köşeli sıcak sans (Nunito/Outfit değerlendir) — gotik/fantezi font YOK, güven veren modernlik
- [ ] Türkçe özellik adlandırması: "Seni Tanıyalım" (profil), "Işık Tut" (açıkla), "Fener" (koç/rehber), "Şafak Skoru" (hazırlık), "Zaman Makinesi" (backtest)
- [ ] Boş durumlar (empty state): karanlıkta tek ışık illüstrasyonu + cesaretlendiren tek cümle ("Henüz varlığın yok — ilk ışığı birlikte yakalım")

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
| 6 | Teknik Borç & Production Sağlamlaştırma | 18+ | `[/]` Prompt kalitesi + rate limit ✅ |
| 7 | Ürün Derinleştirme & Yatırım Takibi | 18+ | `[ ]` |
| 8 | Farklılaştırıcı Özellikler | 20+ | `[ ]` |
| 9 | Marka & Özgün UI Kimliği | 20+ | `[ ]` |
