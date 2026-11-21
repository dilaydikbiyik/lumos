# Ödeme kurulumu — Lemon Squeezy (web) + RevenueCat (iOS)

Kod hazır: anahtarlar girilene kadar Planlar sayfası planları gösterir ama
satın alma düğmesi göstermez ve hiçbir şey hata vermez. Aşağıdakiler
senin hesaplarınla yapılır. Fiyatlar `backend/services/ai_tiers.py`'de:
Fener 4,99 $/ay, Şafak 14,99 $/ay.

> Önce hukuki görüş (`docs/legal-review-brief.md`). Ücretli plan yalnızca
> yapay zekâ danışmanının sınırını ve modelini değiştiriyor — sayfa da
> koşullar da bunu açıkça söylüyor — ama para almaya başlamadan bu
> çerçeveyi bir avukatın onaylaması gerekir.

## 1. Lemon Squeezy (web)

1. lemonsqueezy.com → hesap aç → **Store** oluştur. Kimlik ve ödeme
   (payout) doğrulamasını tamamla; Türkiye'den bireysel satıcı kabul
   ediliyor, vergiyi (KDV, ABD satış vergisi) Lemon Squeezy öder.
2. **Products** → "Lumos" ürünü → iki **variant**, ikisi de *subscription*,
   aylık: "Fener" 4,99 USD, "Şafak" 14,99 USD.
3. Her variant'ın sayısal ID'sini not et (variant sayfasının URL'sinde).
4. **Settings → API** → yeni API anahtarı. **Store ID** aynı sayfada.
5. **Settings → Webhooks** → yeni webhook:
   - URL: `https://lumos-api-yowm.onrender.com/api/v1/billing/webhook/lemonsqueezy`
   - Signing secret: uzun rastgele bir değer üret ve kaydet.
   - Olaylar: `subscription_created`, `subscription_updated`,
     `subscription_cancelled`, `subscription_resumed`,
     `subscription_expired`, `subscription_paused`, `subscription_unpaused`.
6. Render → lumos-api → Environment:
   `LEMONSQUEEZY_API_KEY`, `LEMONSQUEEZY_STORE_ID`,
   `LEMONSQUEEZY_WEBHOOK_SECRET`, `LEMONSQUEEZY_VARIANT_PLUS`,
   `LEMONSQUEEZY_VARIANT_PRO`.
7. Lemon Squeezy'nin **test mode**'unda bir satın alma yap; Planlar
   sayfasında planın birkaç saniye içinde "Mevcut planın" olduğunu, iptal
   edince bitiş tarihinin göründüğünü kontrol et.

## 2. App Store abonelikleri (Apple Developer hesabı gerekir)

1. App Store Connect → Lumos → **Subscriptions** → bir subscription group
   ("Lumos Plans") → iki ürün:
   - `lumos_plus_monthly` — 1 ay — Fener — fiyat kademesi ≈ 4,99 $
   - `lumos_pro_monthly` — 1 ay — Şafak — fiyat kademesi ≈ 14,99 $
   Her biri için TR/EN/DE ad ve açıklama, inceleme ekran görüntüsü (Planlar
   sayfası) gerekir.
2. **Agreements, Tax, and Banking** → Paid Apps sözleşmesini imzala, banka
   ve vergi bilgisini gir (yoksa satın alma çalışmaz).

## 3. RevenueCat (iOS)

1. revenuecat.com → proje → **App Store** uygulaması ekle (bundle ID
   `app.lumos.mobile`, App Store Connect'ten In-App Purchase anahtarı).
2. **Entitlements**: `plus` ve `pro` (tam bu adlarla — backend bunları okur).
   `lumos_plus_monthly` → `plus`, `lumos_pro_monthly` → `pro`.
3. **Offerings** → `default` offering → iki **package**, *custom* identifier
   ile: `plus` (lumos_plus_monthly) ve `pro` (lumos_pro_monthly).
4. **Integrations → Webhooks**:
   - URL: `https://lumos-api-yowm.onrender.com/api/v1/billing/webhook/revenuecat`
   - Authorization header: uzun rastgele bir değer; aynısını Render'da
     `REVENUECAT_WEBHOOK_AUTH` olarak gir.
5. **API keys** → Apple public SDK key (`appl_…`) →
   `frontend/.env.production` içine `VITE_REVENUECAT_IOS_KEY=appl_…`.
   Sonra `npm run build && npx cap sync ios`.
6. TestFlight'ta **sandbox** hesabıyla satın al, geri yükle, iptal et.

## Nasıl çalışıyor (kısaca)

- Web: Planlar → "Bu planı seç" → `POST /billing/checkout` Lemon Squeezy
  ödeme sayfası açar; kullanıcı kimliği ödeme verisinde gider, webhook
  geri getirir. Tarayıcının söylediği hiçbir şeye güvenilmez.
- iOS: RevenueCat, Clerk kullanıcı kimliğiyle yapılandırılır; Apple'dan
  gelen olayları webhook ile backend'e iletir. iOS'ta web ödemesine
  bağlantı YOK (Apple kuralı); "Satın alımları geri yükle" var.
- Bir mağazadaki iptal, diğer mağazadan alınmış planı düşürmez. İptal edilen
  plan ödenen dönemin sonuna kadar sürer; mağaza "süresi doldu" olayını
  gönderince ücretsiz plana döner.
- App Store'dan abone olan biri web'de ikinci kez abone olamaz (409).
- Şafak planı Anthropic modeli kullanır: Render'da `ANTHROPIC_API_KEY`
  olmalı, yoksa ücretsiz katmanın modellerine düşer.
