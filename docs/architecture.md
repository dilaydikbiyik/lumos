# Lumos — Sistem Mimarisi

## Genel Bakış

Lumos, yatırım dünyasına yeni adım atacak bireylere **eğitim odaklı** rehberlik sunan bir finans asistanıdır. **Alım-satım yapmaz**, yatırım tavsiyesi vermez — öğretir, planlar ve takip eder.

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│     React 18 + Vite · Clerk Auth · Mobile-first     │
│                                                     │
│  Onboarding → Seni Tanıyalım → Portföy → Dashboard │
│                                                     │
│  Components: PortfolioChart, AssetExplainer,         │
│  TimeMachine, CurrencyExposure, DailyTip,           │
│  NewsDigest, GoalPlanner, PortfolioComparison        │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (axios)
                       ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│     FastAPI + SQLAlchemy (async) · Uvicorn           │
│                                                     │
│  ┌─────────┐  ┌───────────┐  ┌──────────────┐      │
│  │  AI      │  │  Market   │  │  Portfolio   │      │
│  │  Service │  │  Data     │  │  Engine      │      │
│  │(Gemini/  │  │(yfinance  │  │(volatilite   │      │
│  │Anthropic)│  │ +TEFAS    │  │ ağırlıklı    │      │
│  │          │  │ +TCMB)    │  │ dağılım)     │      │
│  └─────────┘  └───────────┘  └──────────────┘      │
│                                                     │
│  Services: explainer, coach, backtest, news,        │
│  planning (rent-vs-buy, region-intel, goals)         │
│                                                     │
│  DB: SQLite (dev) → PostgreSQL (prod)               │
│  Cache: diskcache (24h taze + 7g stale)             │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                      │
│                                                     │
│  🤖 AI: Google Gemini (free) / Anthropic Claude     │
│  📈 Market: yfinance (hisse fiyatları)              │
│  🏛️ TCMB: EVDS API (TÜFE + konut endeksi)          │
│  🔐 Auth: Clerk (JWT + user management)             │
└─────────────────────────────────────────────────────┘
```

## Tasarım Kararları

| Karar | Gerekçe |
|---|---|
| **AI Provider Switch** | Gemini free tier kota dolunca Anthropic'e geçiş — `.env` ile tek değişken |
| **Volatilite Ağırlıklı Dağılım** | Market-cap weighting yerine risk bazlı — yeni yatırımcı için daha tutarlı |
| **No-Execution Model** | Lumos alım-satım yapmaz — eğitim + takip — düzenleyici risk sıfır |
| **Korku = Veri** | FearCheckIn ile yatırım psikolojisi profil girdisi olarak kullanılır |
| **Mobile-First** | Hedef kitle mobil ağırlıklı — tüm UI 375px'den tasarlandı |
| **Outfit Font** | Sıcak, yumuşak köşeli premium tipografi — güven veren modernlik |
| **Ateş Böceği Teması** | Marka kimliği: karanlık orman + ışık metaforu — amber/turuncu dominant |

## Klasör Yapısı

```
lumos/
├── backend/
│   ├── main.py              # FastAPI app + CORS + middleware
│   ├── config.py             # Pydantic settings (.env)
│   ├── db/                   # SQLAlchemy + Alembic migrations
│   ├── models/               # DB modelleri (User, Holding)
│   ├── routers/              # API endpoint'leri (10 router)
│   ├── services/             # İş mantığı (AI, market, engine)
│   ├── prompts/              # LLM prompt şablonları
│   ├── data/                 # Statik veri (asset_universe, tufe)
│   ├── middleware/            # Auth, error handler, rate limit
│   └── tests/                # 93 pytest testi
├── frontend/
│   ├── src/
│   │   ├── pages/            # 7 sayfa (Onboarding → Dashboard)
│   │   ├── components/       # 18 bileşen
│   │   ├── hooks/            # usePortfolio, useChat, useIllumination
│   │   ├── utils/            # api.js, errorBoundary
│   │   └── data/             # glossary.js (12 terim)
│   └── index.html
├── Dockerfile
├── render.yaml               # Backend deploy config
├── vercel.json               # Frontend deploy config
└── todo.md                   # 800 satırlık yol haritası
```
