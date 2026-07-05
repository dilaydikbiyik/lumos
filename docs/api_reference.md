# Lumos — API Reference

Base URL: `http://localhost:8000` (dev) · `https://lumos-backend.onrender.com` (prod)

All endpoints except `/health` require Clerk JWT Bearer token in `Authorization` header.

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Sistem sağlık durumu (DB + AI provider) |

**Response:**
```json
{ "status": "ok", "version": "0.2.0", "db": "ok", "ai": "ok" }
```

---

## Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Kullanıcı bilgilerini getir |
| PATCH | `/users/me/investment-path` | Yatırım yolunu güncelle (`stocks` / `real_estate` / `both`) |
| PATCH | `/users/me/fear-check-in` | Korku check-in cevaplarını kaydet |
| GET | `/users/me/readiness` | Kullanıcının hangi adımları tamamladığını göster |

---

## Chat

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Sohbet mesajı gönder, AI yanıtı al |
| POST | `/chat/extract-profile` | Sohbet geçmişinden risk profili çıkar (3 aşamalı JSON parsing) |

**Chat Request:**
```json
{
  "messages": [
    { "role": "user", "content": "50 bin TL bütçem var..." }
  ]
}
```

---

## Profile

| Method | Path | Description |
|--------|------|-------------|
| POST | `/profile` | Risk profili oluştur/güncelle |
| GET | `/profile` | Mevcut risk profilini getir |

**Response:**
```json
{
  "risk_score": 5,
  "label": "Dengeli",
  "summary": "Orta riskli, dengeli bir profil...",
  "answers": { "budget": 100000, "time_horizon": "medium", ... }
}
```

---

## Recommend

| Method | Path | Description |
|--------|------|-------------|
| POST | `/recommend` | Risk skoruna göre portföy önerisi |

**Request:**
```json
{ "risk_score": 5, "budget": 100000 }
```

**Response:**
```json
{
  "risk_score": 5,
  "budget": 100000,
  "allocations": [
    { "ticker": "SPY", "name": "S&P 500 ETF", "weight": 0.30, "category": "stocks" }
  ],
  "includes_reits": true,
  "plain_explanation": "...",
  "metadata": { "reit_explanation": "..." }
}
```

---

## Holdings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/holdings` | Kullanıcının tüm varlıklarını listele |
| POST | `/holdings` | Yeni varlık ekle |
| PATCH | `/holdings/{id}` | Varlığı güncelle |
| DELETE | `/holdings/{id}` | Varlığı sil |
| GET | `/holdings/summary` | Özet: toplam değer, kalan bütçe, tip dağılımı, nakit erimesi |
| GET | `/holdings/health` | Fener skoru: çeşitlendirme + likidite (0-100) |

**Holding Request:**
```json
{
  "asset_type": "stock",
  "name": "SPY ETF",
  "ticker": "SPY",
  "purchase_amount": 50000,
  "manual_current_value": 55000,
  "emotion_tag": "plan"
}
```

---

## Backtest

| Method | Path | Description |
|--------|------|-------------|
| POST | `/backtest/snapshot` | Zaman Makinesi: geçmiş performans simülasyonu |

**Request:**
```json
{
  "allocations": [{ "ticker": "SPY", "weight": 0.5 }, ...],
  "budget": 100000,
  "years": 5
}
```

---

## News

| Method | Path | Description |
|--------|------|-------------|
| GET | `/news/digest` | Bugün ne oldu? — en fazla 3 sakin haber |

---

## Coach

| Method | Path | Description |
|--------|------|-------------|
| POST | `/coach/market-move` | Piyasa hareketi mesajı (düşüş/yükseliş) |
| GET | `/coach/behavior-mirror` | Davranış aynası: emotion_tag dağılımı |

---

## Planning

| Method | Path | Description |
|--------|------|-------------|
| POST | `/planning/rent-vs-buy` | Kirada mı otur, ev mi al? karşılaştırması |
| POST | `/planning/goal-plan` | Hedef belirleme ve aylık birikim hesaplama |
| POST | `/planning/goal-progress` | Hedefe ilerleme + sapma kontrolü |
| GET | `/planning/region-intelligence` | Bölge konut endeksi (TCMB verisi) |
| POST | `/planning/listing-links` | İlan sitesi filtrelenmiş linkler |

---

## Practice

| Method | Path | Description |
|--------|------|-------------|
| POST | `/practice/snapshot` | Sanal portföy anlık değeri |

---

## Rate Limiting

- Chat: 50 mesaj/gün (yapılandırılabilir: `DAILY_MESSAGE_QUOTA`)
- Diğer endpoint'ler: 60 istek/dakika

## Error Format

```json
{ "detail": "Hata açıklaması" }
```

HTTP durum kodları: `400` (validation), `401` (auth), `429` (rate limit), `500` (server error)
