# Lumos — Case Study

*Korkmadan, öğrenerek yatırım: sıfır bütçeyle üretim kalitesinde bir AI ürünü inşa etmek*

## Problem

Türkiye'de yatırım araçlarına erişim hiç olmadığı kadar kolay — ama ilk adımı atamayan
milyonlar var. Sebep bilgi eksikliği değil, **korku**: "param erir", "kandırılırım",
"hiçbir şey anlamıyorum". Mevcut uygulamalar (Midas vb.) işlem katmanını çözdü;
işlemden ÖNCE gelen güven katmanını kimse çözmedi.

İkinci boşluk: Türkiye'nin en sevilen varlık sınıfı emlak ile sermaye piyasalarını
aynı çatı altında değerlendiren araç yok — ve hiçbir uygulama getirileri
**enflasyondan arındırılmış** göstermiyor.

## Ürün Kararları

| Karar | Gerekçe |
|---|---|
| İşlem yok, rehberlik var | SPK aracı kurum lisansı gerektirmez; kullanıcı parasını bize emanet etmez — korkak başlayan için güven eşiği düşer |
| Korku = veri | Onboarding'de korku sorulur; AI cevap dilini o korkuya göre uyarlar |
| Tahmin yok, senaryo bandı var | "SPY 5 yılda ne getirir?" → varlığın kendi geçmişindeki tüm 5-yıllık pencerelerin p10/p50/p90 dağılımı |
| Nominal + reel çift gösterim | %40 kazanan bölge %60 enflasyonda gerçekte kaybetmiştir — Lumos bunu söyleyen tek araç |
| Bölge-seviyesi dürüstlük | Mahalle/parsel iddiası asla; "60 kat arttı" anekdotlarına açık uyarı |

## Teknik Zorluklar ve Çözümler

**1. $0 bütçeyle AI:** Anthropic kredisi bitince tek sağlayıcıya bağımlılığın riski
somutlaştı. Çözüm: provider-agnostic adapter katmanı (`AI_PROVIDER` env ile Gemini
free-tier ↔ Claude geçişi) + kullanıcı başına günlük kota + yapılandırılmış çağrı
logları (sağlayıcı, prompt sürüm hash'i, gecikme).

**2. Serbest sohbetten yapılandırılmış veri:** Risk profili bir sohbette toplanıyor ama
skor motoru 5 alanlı şema bekliyor. Çözüm: AI tamamlanınca gizli `[PROFILE_COMPLETE]`
işareti basar; ayrı bir extraction çağrısı konuşmayı katı JSON'a çevirir; Pydantic
doğrulayamazsa kullanıcı sohbete devam eder. İşaret sahteciliğine karşı system prompt'ta
güvenlik kuralları + rol/uzunluk validasyonu.

**3. Kırılgan veri kaynakları:** yfinance rate-limit yer, TCMB API'si sessizce adres
değiştirir (evds2→evds3'ü çalışırken keşfettik). Çözüm: çift katmanlı cache (taze 24s +
bayat 7 gün fallback), her dış kaynak için "fail-open" tasarım — haber özeti çökerse
chat çalışmaya devam eder.

**4. Python 3.9 → 3.12 + SDK EOL'leri:** `google-generativeai` paketi ve Python 3.9
aynı ay EOL oldu. Migrasyon sırasında pip'in lokalde sessizce çözdüğü pydantic
çakışması CI'da patladı — ders: lokal "çalışıyor" ≠ temiz kurulum; pin'ler test edilen
sürümle birebir olmalı.

## Mimari Öne Çıkanlar

- **Katmanlı backend:** routers (ince HTTP) → services (domain) → repositories (tüm SQL) → models/schemas ayrımı
- **125+ test**, dış sınırlar (AI, piyasa verisi) tamamen mock — suite 0.5 saniyede koşar
- **API-seviyesi e2e:** 5 kullanıcı personası gerçek HTTP yüzeyinden tam yolculuk yürür (yol seçimi → korku → profil → öneri → "Aldım" → servet özeti → cesaret skoru)
- **Alembic tek şema otoritesi**; CI'da taze-DB migration kontrolü + Docker build kapısı
- **X-Request-ID korelasyonu** + standart hata zarfı; hafif RBAC (user/admin)

## Öğrenilenler

1. **Vizyon cümlesi filtre görevi görür.** "Bu, çekingen bir başlayana yardım ediyor mu?"
   sorusu onlarca özellik kararını saniyeler içinde verdirdi (araba: takip edilir ama
   asla önerilmez; haberler: ham akış değil sakinleştirilmiş özet).
2. **Dürüstlük bir özellik olabilir.** En kötü anı önce göstermek, reel getiriyi
   saklamamak — bunlar UX maliyeti değil, güven inşasının kendisi.
3. **Ücretsiz kaynaklar üretim kalitesine yeter** ama her birinin arkasına fallback
   koyarsan: Gemini free-tier + TCMB EVDS + yfinance + Clerk free = $0/ay.

## Yol Haritası

Aydınlanan Arayüz'ün derinleştirilmesi, Market Pack mimarisiyle globalleşme
(TR referans pazar), Capacitor ile store'a çıkış (push = davranışsal koçun taşıyıcısı).
