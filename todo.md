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

- [x] Clerk hesabı oluştur, uygulama kaydet (free tier — 10.000 MAU)
- [x] Clerk SDK'yı frontend'e kur (`@clerk/clerk-react`)
- [x] `frontend/src/main.jsx` → `<ClerkProvider>` ile uygulamayı sar
- [x] `frontend/src/middleware/auth.js` → korunan route'lar için middleware yaz (App.jsx ProtectedRoute)
  - Kimlik doğrulanmamış kullanıcılar portföy ve chat sayfalarına erişememeli
- [x] `backend/middleware/verify_clerk.py` → Clerk JWT token doğrulama middleware'i
- [x] Clerk publishable key ve secret key'i `.env`'e ekle

### Auth — Kullanıcı Profili Kalıcılığı 🆕

- [x] `backend/models/user.py` — kullanıcı veri modeli
- [x] `backend/routers/users.py` — kullanıcı endpoint'leri
- [x] `backend/db/database.py` — DB bağlantısı (SQLite başlangıç, Postgres üretime geçişte)
- [x] Risk profili sonuçlarını Clerk user ID'ye bağlı DB'ye kaydet
- [x] Geri dönen kullanıcı kendi portföyünü görüntüleyebilmeli

### Config & DevOps

- [x] Anthropic API anahtarını al ve `.env`'e ekle
- [x] Clerk publishable + secret key'leri `.env`'e ekle
- [x] `.env.example` → tüm değişken isimlerini içeren örnek dosya oluştur
- [x] `.gitignore` → `.env`, `__pycache__`, `node_modules`, `venv/` ekle
- [x] Git repo başlat: `main / dev / feature/*` branch modeli
- [x] İlk commit'i yap
- [!] GitHub'da `main` branch'ini koru — private repo + free plan'da GitHub branch protection kilitli ("Upgrade to GitHub Pro or make public"); repo public yapılırsa veya Pro'ya geçilirse `gh api repos/.../branches/main/protection` ile tek komutla açılır
- [x] `README.md` — temel proje açıklaması (158 satır)

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
- [x] Prompt regresyon testleri: marker/güvenlik/sıfır-bilgi/korku/etik kuralları + extraction JSON şartı (6 test)

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

- [x] TEFAS araştırması: resmi public API yok; mevcut servis korunuyor (değerlendirme notu Phase 6'da)
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

- [x] `frontend/src/components/ReitCard.jsx`
  - REIT nedir, neden seçildi, tarihsel getirisi — Türkçe, jargonsuz
- [x] `frontend/src/components/AssetExplainer.jsx` — genel varlık açıklayıcı bileşen (3 sekmeli: nedir/neden/risk)

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

- [x] `test_full_flow.py` → API-seviyesi tam akış (TestClient; Playwright yerine pragmatik seçim — Clerk'siz gerçek HTTP yüzeyi)
- [x] `tests/e2e/scenarios.json` → 5 kullanıcı tipi senaryosu:
  1. Muhafazakâr (Conservative)
  2. Orta (Moderate)
  3. Agresif (Aggressive)
  4. Kısa vadeli (Short-term)
  5. Emeklilik (Retirement)
- [x] Her senaryo: yol seçimi → korku check-in → profil → öneri → "Aldım" → servet özeti → cesaret skoru (5 persona parametrize)

### Testing — Hata Yönetimi & Edge Case'ler

- [x] `backend/middleware/error_handler.py` → global hata yakalama middleware'i
  - API çökmesi, saçma input, boş portföy, süresi dolmuş oturum
- [x] `frontend/src/utils/errorBoundary.jsx` → React Error Boundary
- [x] Her hata durumu için kullanıcıya anlamlı mesaj göster (Türkçe hata mesajları)

### Deploy — Backend → Render.com

- [x] `Dockerfile` → FastAPI uygulaması için Docker imajı
- [x] `render.yaml` → Render.com deployment konfigürasyonu (free plan, Docker, health check)
- [x] `backend/routers/health.py` → `/health` endpoint'i (uptime monitoring)
- [ ] Render'a tüm env var'ları ekle: `ANTHROPIC_API_KEY`, `CLERK_SECRET_KEY`, `DATABASE_URL`
- [ ] Deployment test et, `/health` endpoint'inin döndüğünü doğrula

### Deploy — Frontend → Vercel

- [x] `vercel.json` → Vercel deployment konfigürasyonu (Vite framework, SPA rewrite, asset caching)
- [x] `frontend/.env.production` → `VITE_BACKEND_URL`, `VITE_CLERK_PUBLISHABLE_KEY`
- [ ] Clerk production instance'ına bağlan
- [ ] Vercel'e deploy et ve tam akışı test et

### Portfolio — README & Mimari Dokümantasyon

- [x] `README.md` — ne yapar, nasıl çalıştırılır, mimari kararlar + gerekçeleri (158 satır)
- [x] `docs/architecture.md` — sistem mimarisi diyagramı ve açıklaması (ASCII art + tasarım kararları tablosu)
- [x] `docs/api_reference.md` — tüm API endpoint'leri ve kullanımları (10 router, 26 endpoint)

### Portfolio — Demo Video & Case Study

- [x] `demo/demo_script.md` → 3 dakikalık sahne sahne demo scripti (çekim notlarıyla)
  - Tam akış: kayıt → onboarding → chat → risk profili → portföy → dashboard
- [ ] Ekran kaydı çek (Loom / OBS / QuickTime)
- [x] `docs/case_study.md` → problem, ürün kararları, 4 teknik zorluk+çözüm, öğrenilenler
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
- [x] `tests/e2e/` dolduruldu (scenarios.json + backend test_full_flow.py)

### CI/CD

- [x] `.github/workflows/ci.yml` → push/PR'da ruff + pytest (backend, Python 3.9)
- [x] Aynı workflow'a eslint + build (frontend, Node 22) adımı eklendi — vitest frontend testleri yazılınca eklenecek
- [!] Branch protection: aynı GitHub Pro/public kısıtı (yukarıdaki maddeyle aynı)

### Veritabanı


- [x] `alembic init` (async template) + baseline migration (`04f9da6e7e6d`: users tablosu + indexler); dev DB `alembic stamp head` ile damgalandı
- [/] `create_all` → migration geçiş planı: dev'de create_all kalıyor (zararsız, checkfirst); yeni şema değişikliği geldiğinde akış = model değiştir → `alembic revision --autogenerate` → `alembic upgrade head`; prod deploy'da startup öncesi `alembic upgrade head` çalıştırılacak, create_all prod'da kaldırılacak

### Deployment

- [x] `Dockerfile` (backend) — python:3.9-slim, migration + uvicorn startup; build doğrulaması CI'da (lokalde Docker yok)
- [/] docker-compose.yml hazır (kalıcı volume + healthcheck) — lokal test için Docker Desktop kurulumu gerekiyor

### Veri Sağlayıcı Riski

- [x] yfinance rate-limit / kırılma senaryolarına fallback: 7 günlük stale cache kopyası — indirme çökerse bayat veriyle devam, o da yoksa MarketDataError → 503
- [x] TEFAS değerlendirmesi: resmi/ücretsiz API yok (fintables vb. ücretli); mevcut tefas_service scraping'i + cache yeterli — Market Pack'te kaynak adaptörü olarak soyutlanacak
- [x] Cache TTL stratejisi gözden geçirildi: taze 24s + stale 7g çift katman

### AI Servis Gözlemlenebilirliği

- [x] AI çağrıları için structured logging (`lumos.ai` logger: provider, prompt_version, latency_ms, mesaj sayısı, durum, hata tipi)
- [x] Prompt versiyonlama: system prompt SHA1 hash'i (`PROMPT_VERSION`) her log satırında — hangi cevabın hangi prompt sürümünden geldiği izlenebilir
- [x] Anthropic SDK güncellendi (0.39.0 → 0.112.0); prompt caching Anthropic'e geçilirse eklenecek

### Güvenlik & Compliance

- [x] `slowapi` ile AI endpoint'lerine rate limiting ekle (chat, recommend)
- [x] Prompt injection koruması: rol/uzunluk validasyonu (Literal rol, 4000 char, 80 mesaj) + system prompt'a SECURITY RULES bloğu (marker sahteciliği, prompt sızdırma, rol değiştirme reddi)
- [/] Structured output: risk profili çıkarımı yapılandırıldı (`/chat/extract-profile` + JSON extraction prompt'u) — portföy çıktısı tool-use'a geçirilecek

### AI Danışman Kalitesi 🆕

> ✅ **Çözüldü (2026-07-04):** Kopuk profil akışı onarıldı — AI tamamlanınca `[PROFILE_COMPLETE]` işareti veriyor, frontend `/chat/extract-profile` ile yapılandırılmış cevapları çekip skor ekranına geçiyor.

- [x] `system_prompt.txt`'i derinleştir: MPT/risk-getiri çerçevesine açık referans, karşı soru sorma davranışı, yasal/etik sınırların net ifadesi
- [x] Few-shot örnek diyaloglar ekle (1 örnek embedded) — danışman tonunu örnekten öğret
- [x] `reit_explain_prompt.txt`'i derinleştir: 3 cümle yapısı, profil-spesifik ton, dürüst risk uyarısı, MPT bağlamı
- [x] RAG: `chat_context.py` — günlük piyasa özeti (BIST/SPY/GLD + aylık TÜFE) system prompt'a inject ediliyor, 6 saatlik cache, fail-open (3 test)
- [ ] Tool-use mimarisi: `get_market_data(ticker)`, `calculate_volatility(asset)`, `get_risk_score(profile)` tool tanımları — Claude veriyi kendi üretmek yerine servislerden çeksin
- [/] Geri bildirim döngüsü v1: `recommendation_served` structured log + admin/stats holdings kıyası; UI-tabanlı kabul/red eventi sonraki sürüm
- [ ] Prompt versiyonlarını A/B test et, Anthropic Console Prompt Improver ile mevcut prompt'u güçlendir

---

## Phase 7 — Ürün Derinleştirme & Kişisel Yatırım Takibi 🆕

**Süre:** Phase 6 ile paralel yürütülebilir
**Kaynak:** Ürün vizyonu görüşmesi (2026-06-28)

### AI Sağlayıcı Esnekliği (maliyet çözümü)

- [x] `ai_service.py`'yi provider-agnostic yap: tek `chat()` / `generate_text()` interface'i, arkasında adapter'lar
- [x] Gemini adapter ekle (`google-generativeai`) — free tier, geliştirme/demo varsayılanı
- [x] `google-generativeai` → `google-genai` (2.10.0) SDK migrasyonu — deprecated uyarısı gitti, canlı doğrulandı
- [x] `.env`'e `AI_PROVIDER=gemini|anthropic` seçimi; Claude adapter'ı mevcut kodu sarmalasın
- [x] Provider'a özel hata yönetimi (kredi bitti / kota doldu → kullanıcıya anlamlı mesaj)
- [x] Gemini free-tier fallback zinciri: 2.5-flash → 2.5-flash-lite → 2.0-flash — her modelin AYRI ücretsiz kotası olduğundan 429/5xx'te otomatik geçiş; ücretsiz kapasite ~3x, kullanıcı hata görmez (5 test)

### Risk Profili Derinleştirme

- [x] 7 soruya iki boyut yedir: yaş/emekliliğe kalan süre (Q2) + gelir istikrarı (Q7)
- [x] Dinamik follow-up: profil belirsizse LLM ek soru sorabilsin (7–10 soru arası esnek akış)
- [x] `risk_engine.py`'yi yeni boyutlara göre güncelle (yaş ve gelir istikrarı skora etki etsin)

### Kişisel Yatırım Takibi 💰 (abi fikri)

- [x] `backend/models/holding.py` — kullanıcı varlık modeli (10 tip: hisse/fon/etf/konut/arsa/araç/altın/kripto/nakit/diğer) + Alembic migration
- [x] Araç varlık tipi — dürüst çerçeveyle: net servet resminde yer alır AMA amortisman hesabıyla gösterilir (yıllık değer kaybı + kasko/MTV/bakım maliyeti); "Araban serveti mi, gideri mi?" eğitim kartı eşlik eder — AI asla araç almayı yatırım olarak ÖNERMEZ
- [x] `backend/routers/holdings.py` — CRUD + borsa varlığına ticker zorunluluğu (7 test)
- [x] Bütçe takibi: `/holdings/summary` — toplam yatırılan, güncel değer, kalan bütçe, tip bazlı dağılım
- [/] Borsa dışı varlıklar için manuel değerleme alanı ✅; borsa varlıklarının yfinance canlı değerlemesi sonraki adım
- [x] `frontend/src/pages/HoldingsPage.jsx` — "Varlıklarım": toplam değer + kalan bütçe + Fener skoru + liste + ekleme formu (BottomNav'a eklendi)
- [x] Dashboard'a özet kart: toplam varlık değeri + kalan bütçe + günlük değişim
- [x] Gerçek portföy vs önerilen portföy karşılaştırması ("hedef dağılımından sapma" göstergesi)

### Mimari & Kod Kalitesi 🏛️ (clean architecture revizyonu)

> Sıralama önerisi: repository/schema refactor → error handling → RBAC → Python 3.12

- [x] `backend/repositories/` katmanı: user_repository + holding_repository; router'larda inline SQL kalmadı
- [x] `backend/schemas/` klasörü: user_profile/portfolio/risk_score/holding şemaları taşındı; `models/` sadece ORM (user, holding)
- [/] Domain exception sınıfları: `MarketDataError` + `AIServiceError` eklendi (`backend/exceptions.py`), error_handler'da 503'e map'leniyor — `QuotaExceededError` kota özelliğiyle gelecek
- [x] Standart hata zarfı: `{detail, error:{code,message,request_id}}` — detail frontend uyumluluğu için korunuyor
- [x] `X-Request-ID` middleware: contextvar tabanlı korelasyon — header'da döner, hata zarfında ve loglarda görünür (3 test)
- [ ] API versiyonlama: tüm router'ları `/api/v1` prefix'i altına al (frontend api.js baseURL güncelle)
- [x] Hafif RBAC: `role` kolonu (migration 734ca3a1) + `require_role()` + admin-only /admin/stats (kullanıcı/varlık/mesaj hacmi, yol dağılımı) (2 test)
- [x] Health check'i derinleştir: `/health` DB bağlantısını ve AI provider erişimini gerçekten yoklusın (`{"db": "ok", "ai": "ok"}`)
- [x] Python 3.9 → 3.12 migrasyonu: venv yeniden kuruldu, Dockerfile+CI 3.12'ye çekildi, `datetime.utcnow` deprecation'ları giderildi (Optional→| None dönüşümü kozmetik, kademeli yapılacak)
- [x] pre-commit config: ruff + ruff-format + temel hijyen hook'ları (`pip install pre-commit && pre-commit install`)
- [ ] Sızan Anthropic API anahtarını rotate et (Console → API Keys)

### Mobil Strateji 📱 (karar: 3 kademe — 2026-06-28)

> Kademe 1: mobile-first web ✅ (Phase 4'te yapıldı) → Kademe 2: tam PWA (MVP ile) → Kademe 3: Capacitor native (MVP sonrası, bütçe olunca)
> React Native/Flutter'a geçiş YOK — mevcut React kod tabanı korunur.

- [x] PWA tamamlandı: manifest.webmanifest + sw.js (network-first, API cache'lenmez) + prod-only kayıt
- [ ] Capacitor sarma (MVP sonrası): store meşruiyeti + **push notification = davranışsal koçun taşıyıcısı** ("piyasa düştü, sakin ol" gerçek zamanlı ancak push ile çalışır; iOS web push güdük) — Apple $99/yıl + Google $25 bütçesi gerekir

### Kullanım Kotası

- [x] Kullanıcı başına günlük mesaj kotası (users.quota_date/quota_used, DAILY_MESSAGE_QUOTA=50, 429 + kibar TR/EN mesaj)
- [x] Kota dolunca kibar bilgilendirme (backend mesajı chat error alanında görünüyor)

### Eğitim Katmanı 📚 (vizyonun kalbi — öncelik yükseltildi)

- [ ] Varlık bazlı eğitim: her portföy kalemi için "nedir / neden portföyünde / riski ne" LLM açıklaması (generalize edilmiş explain prompt)
- [x] `AssetExplainer.jsx`'i bu içeriği gösterecek şekilde doldur — 6 bilinen ticker + 3 kategori fallback, 3 sekmeli statik kart
- [x] Temel kavramlar sözlüğü (`frontend/src/data/glossary.js`, 12 terim, jargonsuz TR)
- [ ] Kullanıcının yatırım yaptığı her varlık tipinde ilk alımda otomatik eğitim kartı göster
- [/] Jargon tooltip sistemi: `IsikTut` bileşeni + 12 terimlik sözlük hazır; tüm sayfalara yayma devam edecek
- [x] system_prompt'a "sıfır bilgi varsay" kuralı: her cevapta terimleri günlük dille açıkla, kullanıcı bilgi seviyesi gösterirse dili kademeli teknikleştir (+ korku-farkındalık kuralı: endişeyi önce karşıla, sonra cevapla)
- [ ] UI metin denetimi: tüm sayfalardaki mevcut metinleri jargonsuzluk ilkesine göre elden geçir — RecommendPage + ReitCard Türkçeye çevrildi ✅, diğer sayfalar devam edecek

---

## Phase 8 — Farklılaştırıcı Özellikler 🚀 (piyasa analizi: 2026-06-28)

> Konumlandırma: Midas/Getir Finans = işlem, robo-advisor'lar = kara kutu öneri, Fintables = analiz.
> Lumos'un boşluğu: **"anlayarak yatırım"** — öneriyi açıklayan, davranışı koçlayan, Türkiye gerçeklerine göre konuşan asistan.

### Zaman Makinesi & Varlık Karakteri 🕰️ (en güçlü demo özelliği)

- [x] "Bu portföyü 5 yıl önce kursaydın?" — `backtest.py` servisi + POST /backtest (1y/3y/5y)
- [x] `backend/services/backtest.py` → kümülatif seri + max drawdown + toparlanma süresi + grafik verisi (5 test)
- [x] Duraklama dönemi tespiti: ±%5 bant algoritması → varlık başına `longest_stagnation_months` (profil eşleştirme rozeti sonraki adım)
- [ ] Varlık karakter kartı: her varlık için "en uzun duraklama", "en derin düşüş", "toparlanma süresi" özeti — profil uyum rozeti (bu varlık senin sabrına uygun mu?)
- [x] RecommendPage'e `TimeMachine` bileşeni: 1/3/5 yıl simülasyon + "en kötü anında X TL" dürüst vurgusu + çizgi grafik
- [x] Risk toleransı sorusunu somutlaştır: soyut "%20 düşerse" yerine kullanıcının kendi bütçesiyle "50.000 TL'n 40.000 TL olurdu" göster

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

- [x] Onboarding'de dürüst beklenti cümlesi: "Lumos sana yol gösterir; alım-satımı kendi aracı kurumunda yaparsın, sonra burada takip ederiz"
- [x] Borsa "Aldım" akışı: `BoughtItBridge` — öneri dağılımını tek tıkla holdings'e işler, kalan bütçe otomatik güncellenir
- [ ] "Aracı kurum hesabı nasıl açılır" rehberi (Korkusuz Başlangıç'taki rehberli yolculukla aynı madde — çift kayıt değil, referans)

#### Akış 0 — Yol Seçimi 🧭 (yapısal ilke: akışlar zorunlu değil, seçilebilir)

> ⚠️ Not (2026-07-04): Onboardingdaki yol seçimi + backend `investment_path` alanı canlı çalışıyor. Ama koşullu modül gizleme henüz uygulanamadı çünkü emlağa özel SAYFALAR (bölge kartları, ilan değerlendirme, kira/ev karar UI'ı) henüz yok — sadece backend endpoint'leri hazır (planning router). Bu sayfalar yazılınca gizleme mantığı () eklenecek.

> Kullanıcı emlak seçmek ZORUNDA değil. Üç eşit yol: sadece borsa (Midas tarzı) / sadece emlak keşfi / karma. Her akış bağımsız çalışır.

- [x] Onboarding'e yol sorusu: `PathSelectionPage` (4 kart) → PATCH /users/me/investment-path → users.investment_path
- [x] Yol-bazlı modül uyarlaması: BottomNav seçilen yola göre filtreleniyor (sadece-borsa → Keşfet gizli; sadece-emlak → Portfolio gizli)
- [ ] "Sadece emlak" yolu: risk profili yine yapılır (vade + likidite kritik) ama çıktı bölge kartları + ilan değerlendirme + eğitim; borsa önerisi dayatılmaz
- [ ] "Kararsızım" yolu: profil + korku check-in sonucuna göre AI yol önerir ("düzenli birikim + uzun vade → önce borsa fonlarıyla başla, emlak eşiğine gelince haber veririm")
- [ ] Yol her an değiştirilebilir (ayarlar + dashboard'da "emlak dünyasını keşfet" yumuşak daveti — dayatma yok)
- [ ] Bütçe bölüşüm danışmanı yalnızca karma/kararsız yolda aktif; tek-yol kullanıcıda bütçenin tamamı seçili dünyaya planlanır

#### Akış 1 — Bütçe Bölüşüm Danışmanı (giriş noktası)

- [ ] Emlağı tahsis edilebilir varlık sınıfı yap: portfolio_engine "1.000.000 TL + profil" → "600K emlak / 300K hisse-fon / 100K nakit yedek" bölüşümü önersin (risk skoru + likidite ihtiyacı + bütçe eşiği girdileriyle)
- [ ] Bölüşüm gerekçesi LLM anlatımı: neden bu oranlar, hangi profilde nasıl değişirdi (öğreten ton)
- [ ] REIT vs fiziksel emlak karar noktası: bütçe eşik altındaysa veya likidite ihtiyacı yüksekse "fiziksel yerine REIT" yönlendirmesi (hybrid_basket çift yönlü)

#### Akış 2 — Bölge Değerlenme İstihbaratı (AI "nereden alayım?" cevabı)

- [x] TCMB Konut Fiyat Endeksi CANLI: 19 NUTS2 bölgesi (TP.KFE.*), 1-3 yıl nominal + reel değerlenme sıralaması (`region_intelligence.py`)
- [ ] TÜİK nüfus/göç verisi entegrasyonu: net göç alan + genç nüfuslu ilçeler = talep sinyali
- [x] "Değerlenme Potansiyeli" bölge kartları: GET /planning/region-intelligence + ExplorePage UI (1/2/3 yıl seçimli, reel sıralı, dürüstlük notu) — canlı TCMB verisiyle tarayıcıda doğrulandı; TÜİK göç sinyali sonraki adım
- [ ] Kullanıcı hedefiyle eşleştir: "20 yıl bekleyebilirim" → uzun vade değerlenme bölgeleri; "5 yılda satarım" → likiditesi yüksek merkezi bölgeler

#### Akış 3 — İlan Köprüsü (satın almaya yönlendirme)

- [x] Filtre-hazır dış linkler: servis + endpoint + ExplorePage "İlanlara Git" kartı (il/ilçe/tip formu → dış linkler)
- [ ] **İlan değerlendirme asistanı**: kullanıcı beğendiği ilanın bilgilerini yapıştırır (konum, m², fiyat) → AI bölge ortalama m² fiyatıyla kıyaslar: "bölge ortalamasının %20 üstünde" + pazarlık/kontrol listesi (imar durumu, tapu cinsi, yola cephe...)
- [ ] Satın alma kontrol listesi rehberi: arsa/daire alırken adım adım ne kontrol edilir (statik eğitim içeriği, TR'ye özgü: tapu, imar, DASK...)
- [ ] (İleri faz — iş geliştirme) Emlak platformu API ortaklığı: gerçek ilan + emlakçı iletişimi in-app gösterim

#### Akış 4 — Döngüyü Kapat (alım sonrası)

- [ ] "Aldım" akışı: ilan değerlendirmeden tek tıkla holdings'e kayıt (Phase 7 formu ön dolu gelir)
- [ ] Kalan bütçeyi otomatik yeniden planla: "600K'yı arsaya bağladın, kalan 400K için hisse-fon planın hazır" → recommend akışına köprü
- [ ] TCMB endeksiyle emlak varlığının değerini dönemsel güncelle ("endekse göre tahmin" etiketiyle)
- [ ] Kira getirisi vs temettü verimi karşılaştırması: "bu daire yıllık %4 kira getirir, bu temettü portföyü %6 öder"
- [x] Likidite skoru: Fener'in %40 ağırlıklı bileşeni — illikit ağırlıklı portföyde uyarı notu üretiyor
- [ ] "500.000 TL'lik arsa mı, 500.000 TL'lik portföy mü?" karşılaştırma ekranı: aynı tutar, geçmiş 5 yıl, konut endeksi vs portföy getirisi yan yana (+ likidite ve masraf farkları tablosu)

#### Akış 5 — Kira & Ev Kararları 🏠 (giriş kapısı özelliği)

> Türkiye'de yatırım bilmeyenin ilk finansal sorusu: "kirada mı oturayım, ev mi alayım?" — bu soruya cevap veren araç, uygulamaya kullanıcı çeken kapı olur.

- [x] "Kirada mı otur, ev mi al?" karar aracı: servis + endpoint + ExplorePage UI kartı (iki senaryo yan yana + duygusal değer notu) — canlı doğrulandı
- [ ] Karar aracına duygu boyutu: "ev sahibi olma güvencesi"nin parasal olmayan değerini de anlat (vizyon ilkesi: korku/duygu = veri)
- [ ] Aylık ödenen kirayı profil girdisi yap: yatırılabilir gerçek tutar = gelir − kira − zorunlu giderler → bütçe bölüşüm danışmanı bu net tutarla konuşsun
- [x] Kapsam sınırı (bilinçli karar): kiralık ilan arama / mortgage pazaryeri EKLENMEDİ — listing_bridge.py sadece filtre-hazır dış link üretir, ilan verisi hiç saklanmaz

### Enflasyon Gerçekliği 🇹🇷 (yerel farklılaştırıcı — kimse yapmıyor)

- [x] Tüm getirilere nominal + reel çift gösterim: Zaman Makinesi sonucunda `real_return_pct` alanı, UI'da "Enflasyon sonrası (reel)" satırı
- [x] TÜFE verisi: CANLI TCMB EVDS entegrasyonu (`evds_service.py`, TP.FG.J0, günlük cache) — statik dosya fallback olarak korunuyor
- [x] Portföyde TL/döviz dağılımı ve kur riski göstergesi — `CurrencyExposure.jsx` (HoldingsPage'e entegre)
- [x] "Param eriyor mu?" kartı: Varlıklarım sayfasında boştaki bütçe + nakit için aylık reel erime tutarı (5 test)

### Davranışsal Koç 🧠 (robo-advisor'ların yapmadığı)

- [x] Piyasa hareketi mesajları: `behavior_coach.py` + POST /coach/market-move — loss_tolerance'a göre düşüş/yükseliş mesajı (şablon tabanlı, AI maliyeti yok)
- [x] Davranış aynası: GET /coach/behavior-mirror — emotion_tag dağılımı + profil/davranış uyumsuzluğunda nazik not
- [x] Alımda opsiyonel 1-tık duygu etiketi (plan/fomo/tüyo/panik) — `holdings.emotion_tag`; aylık rapor UI'ı sonraki adım

### Hedef Bazlı Yatırım 🎯

- [x] Hedef tanımlama: servis + endpoint + Dashboard `GoalPlanner` kartı — canlı doğrulandı (800K/3yıl → 17.993 TL/ay)
- [x] Hedefe ilerleme + sapma: endpoint + UI ilerleme çubuğu — canlı doğrulandı (10K temponla "21 ay gecikir" uyarısı)
- [x] Hedef sapma uyarısı: UI'da "⏳ Bu tempoda hedefin X ay gecikir" kartı canlı çalışıyor

### Portföy Sağlık Skoru 💯

- [/] Fener skoru v1: çeşitlendirme (HHI) + likidite bileşenleri, 0-100 + jargonsuz notlar (hedef uyum + kur dengesi sonraki sürüm)
- [ ] Her bileşen için "neden düşük, nasıl yükselir" LLM açıklaması
- [/] Fener kartı Varlıklarım sayfasında ✅; zaman içinde skor grafiği sonra
- [x] Cesaret Skoru UI: `ReadinessScore.jsx` — Dashboard'da 5 kilometre taşı + dairesel skor göstergesi, %60 eşiğinde "gerçek yatırıma hazırsın" mesajı

### What-If Asistanı 🔮

- [x] Chat'te senaryo soruları: "10.000 TL daha eklesem?", "daha agresif olsam?" — `what_if.py` tool-use: LLM sadece niyeti JSON'a çıkarır, `portfolio_engine` gerçek before/after hesaplar, LLM sadece sonucu yorumlar (asla matematik uydurmaz); `/chat/what-if` + `WhatIfAssistant` UI kartı, 6 test, canlı Gemini ile doğrulandı


### Gelecek Senaryoları 🔮 (kullanıcı fikri — 2026-07-05)

> "SPY'a koysam 5 yılda ne olur?" sorusunun dürüst cevabı: tahmin DEĞİL, varlığın kendi
> geçmişindeki tüm N-yıllık pencerelerin dağılımı (kötü p10 / tipik p50 / iyi p90).

- [x] `projection.py`: kaymalı pencere dağılımı motoru — varlık (yfinance 10y, aylık örnekleme) + bölge (TCMB KFE) (7 test)
- [x] POST /planning/projection/asset + /projection/region — yetersiz geçmişte dürüst ret ("yeterli pencere yok")
- [x] RecommendPage `FutureScenarios` kartı: varlık + vade seç → bütçenle 3 senaryo çubuğu
- [x] ExplorePage bölge kartları tıklanınca senaryo bandı: "X TL burada 2 yılda ne olurdu?" + reel karşılık + "60 kat" anekdot uyarısı — canlı doğrulandı (Ankara 1M → tipik +85.9% nominal / +15.15% reel)
- [ ] Senaryo kartına LLM güncel bağlam cümlesi (sakin haber özetinden beslenerek, sayılara karışmadan)
- [ ] Portföyün tamamı için birleşik senaryo bandı (ağırlıklı pencere dağılımı)

### Sakin Haber Akışı 📰 (haber = eğitim, gürültü değil)

> Ham haber akışı yeni başlayan için korku makinesidir. Lumos haberi süzer, sakinleştirir, öğretir.

- [x] RSS entegrasyonu: AA Ekonomi + Bloomberg HT (httpx + stdlib XML, ek bağımlılık yok) → `news_service.py`
- [x] LLM haber süzgeci: yol-bazlı seçim, headline + why_it_matters + calmness_note JSON'u, günlük cache (5 test)
- [/] GET /news/digest hazır (≤3 haber, path-bazlı); dashboard kartı UI'ı sonraki adım
- [/] Haber + koç altyapısı hazır (`news_service.py` + `behavior_coach.py`) — otomatik tetikleme köprüsü (haber → koç) sonraki entegrasyon adımı
- [x] Manşet dili eğitimi: "BORSA ÇAKILDI manşeti gördüğünde gerçekte ne olur?" mikro-eğitim kartı — `HeadlineEducation.jsx` (4 senaryo, localStorage)

### Korkusuz Başlangıç 🐣 (vizyonun ta kendisi — en yüksek öncelik)

> Yatırım bilmeyen biri gerçek para riske atmadan önce güven kazanmalı.

- [x] Sanal portföy: servis + endpoint + RecommendPage `PracticeMode` kartı ("Önce Sahte Parayla Dene")
- [x] Haftalık değişim hesabı hazır (weekly_change_amount + biggest_mover); LLM anlatım katmanı sonraki adım
- [x] İlk yatırım rehberli yolculuğu: adım adım sihirbaz — \"aracı kurum hesabı nedir → nasıl açılır → ilk emir nasıl verilir\" (Türkiye'ye özgü, statik 5 adım) — `BeginnerGuide.jsx`
- [x] Korku check-in'i: `FearCheckInPage.jsx` + PATCH /users/me/fear-check-in — 4 korku etiketi + anında kişiselleştirilmiş güvence mesajı (canlı doğrulandı)
- [x] "Bugün öğrendin" mikro-kartları: her oturumda tek küçük kavram ("ETF aslında bir sepettir") — 15 saniyelik okuma, ilerleme sayacı — `DailyTip.jsx` (12 kart, localStorage takibi)
- [x] Kademeli arayüz: yeni kullanıcıda sade görünüm (3 metrik), "detay göster" ile zenginleşir — `ProgressiveDetails` Dashboard'da, toggle butonu
- [x] Cesaret göstergesi: GET /users/me/readiness — 5 şeffaf kilometre taşı, 0-100 skor, %60 eşiği "gerçek yatırıma hazır" (canlı doğrulandı: skor 60, eşik geçildi)

---

## Phase 8.5 — Globalleşme Mimarisi 🌍 "Market Pack" Sistemi

> Karar (2026-06-28): proje GLOBAL tasarlanacak. Yöntem: ülkeye özgü her şey tek pakette — kod ülke bilmez, pakete sorar.
> Yeni ülke eklemek = yeni kod değil, yeni config + veri adaptörü + içerik paketi. TR ilk referans pack olarak eksiril yapılır.

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
- [ ] İkinci pack adayını veriye göre seç (US genel pazar mı, DE gurbetci segmenti mi) — MVP SONRASI
- [ ] Hardcode denetimi: kod tabanında TL/TÜFE/Sahibinden geçen her yer pack referansına taşınmış mı kontrolü

## Phase 9 — Marka & Özgün UI Kimliği ✨ "Işık" Tasarım Dili

> Marka hikayesi = ürün vizyonu: **bilinmezlik karanlıktır, bilgi ışık tutar.** HP'den esinlenilmiş, telif-güvenli özgün yorum.

### Logo & Marka — KARAR: Ateş Böceği 🪰✨ (2026-06-28)

- [x] Logo kararı: ateş böceği (karanlıkta yol gösteren minik ışık) — telif-güvenli, sıcak, özgün
- [x] Logo tasarımı: minimalist SVG ateş böceği (amber ışık halesi + mor/mavi kanatlar) — favicon + navbar LumosLogo bileşeni, nefes alan ışıma animasyonlu
- [x] Giriş animasyonu: onboarding hero'da 10 CSS-particle ateş böceği başlığa süzülüyor (2.6sn, prefers-reduced-motion saygılı)
- [x] Ateş böceği boş durum/onboarding illüstrasyonlarında rehber karakter olarak kullanılır
- [x] Marka manifestosu (onboarding ilk ekran): "Yatırım karanlık bir orman gibi görünür. Lumos, elindeki ışık." — hero section'da aktif
- [x] Telif kontrolü: şimşek, asa çizimi, HP fontları KULLANILMAZ — ateş böceği + soyut ışık motifi bizim

### "Aydınlanan Arayüz" 🌗 (imza özellik — başka finans uygulamasında yok)

- [x] Aydınlanan Arayüz v1: `useIllumination` hook'u — cesaret skoru 25/50/80 eşiklerinde zemin gece→alacakaranlık→şafak öncesi→şafak (1.2sn yumuşak geçiş)
- [x] "Öğrendikçe dünyan aydınlanıyor" — skor artınca geçiş anında 1 kerelik yumuşak ışıma animasyonu + tebrik mikro-kartı

### İmza Etkileşimler

- [x] "İşık Tut" tooltip: jargon terime tıklayınca minik ışık patlaması + sade açıklama balonu — ateş böceği temalı, amber renk, ok işaretli
- [x] Sayı animasyonu: değerler ekrana soğuk griden "ısınarak" (amber'e) gelir — `.number-warm` CSS classı
- [x] Loading state: spinner yerine uçta büyüyen ışık noktası — `.light-loader` CSS animasyonu
- [x] Eğitim mikro-kartları tılsım kartı çevirme animasyonuyla açılır
- [x] Portföy sağlık skoru = "Fener": sağlık arttıkça fener ikonu daha gür yanar

### Tasarım Sistemi

- [x] Palet token'ları: `--firefly/--firefly-soft/--firefly-glow` + `--bg-night/dusk/predawn/dawn` kademeleri index.css'te
- [x] Tipografi: Outfit fontu eklendi (`'Outfit', 'Inter', system-ui, sans-serif`), yumuşak köşeli sıcak premium sans — gotik/fantezi font YOK
- [x] Türkçe özellik adlandırması: "Seni Tanıyalım" (profil), "İşık Tut" (açıkla), "Fener" (portföy sağlık), "Şafak Skoru" (hazırlık), "Zaman Makinesi" (backtest) — tüm sayfalarda aktif
- [x] Boş durumlar (empty state): karanlıkta ateş böceği + radial glow animasyon + cesaretlendiren mesaj (Dashboard + Holdings)

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
| 1 | Setup, Scaffolding & Auth | 1–2 | `[x]` Tamamlandı ✅ |
| 2 | NLP Engine & Risk Profile | 3–5 | `[x]` Tamamlandı ✅ |
| 3 | Market Data & Portfolio Engine | 5–8 | `[x]` Tamamlandı ✅ |
| 3.5 | Real Estate / REIT Layer | 8–10 | `[x]` Tamamlandı ✅ |
| 4 | Frontend — Mobile-First Chat UI | 10–14 | `[x]` Tamamlandı ✅ |
| 5 | Testing, Deploy & Portfolio | 14–18 | `[/]` Hata yönetimi ✅ · Deploy bekliyor |
| 6 | Teknik Borç & Production Sağlamlaştırma | 18+ | `[/]` Test + CI ✅ · Yapısal iyileştirmeler devam |
| 7 | Ürün Derinleştirme & Yatırım Takibi | 18+ | `[/]` Holdings + coach + goal ✅ · Karşılaştırma bekliyor |
| 8 | Farklılaştırıcı Özellikler | 20+ | `[/]` Backtest + TCMB + haber ✅ · Varlık kartı bekliyor |
| 9 | Marka & Özgün UI Kimliği | 20+ | `[/]` Logo + palet + font ✅ · Animasyonlar devam |

