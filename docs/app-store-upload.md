# App Store'a yükleme — adım adım

Kod ve Xcode projesi yüklemeye hazır. Aşağıdaki adımlar senin hesaplarını
ve bu Mac'te kurulu olmayan Xcode'u gerektiriyor; sırayla yapılmalı, çünkü
her biri bir sonrakinin ön koşulu.

## 0. Bir kez yapılacaklar (hesap ve altyapı)

1. **Apple Developer Program** — developer.apple.com, 99 $/yıl. Onay 1–2 gün
   sürebilir. Bireysel kayıtta uygulama senin adınla yayımlanır.
2. **Xcode** — Mac App Store'dan (≈15 GB). Kurulunca:
   ```bash
   sudo xcode-select -s /Applications/Xcode.app
   ```
3. **Clerk production instance** — kendi alan adınla. Dashboard'da:
   e-posta ile girişi aç; **allowed origins**'e `capacitor://localhost` ekle.
   Yeni `pk_live_…` anahtarını `frontend/.env.production` içindeki
   `VITE_CLERK_PUBLISHABLE_KEY`'e, `sk_live_…` anahtarını Render'a yaz.
4. **Render** — ücretli katman (ücretsiz sunucu uyur; inceleyen kişi 50 sn
   bekleyince performans reddi yazar). Ortam değişkenleri: Clerk canlı
   anahtarı, VAPID anahtarları, `SENTRY_DSN`.
5. **Hukuki görüş** — `docs/legal-review-brief.md`. Apple 5.1.1(ix) finans
   uygulamalarını tüzel kişiden bekler; inceleme notu uygulamanın eğitim
   aracı olduğunu söylüyor, ama bu bir avukatın onaylaması gereken iddia.

## 0.5 Ödeme (isteğe bağlı, ilk sürümde olmayabilir)

Abonelik satılacaksa App Store ürünleri, RevenueCat ve Lemon Squeezy
kurulumu: `docs/billing-setup.md`. Anahtarlar girilmezse uygulama satın
alma düğmesi göstermez; ücretsiz sürüm olarak da gönderilebilir.

## 1. Derleme

```bash
cd frontend
```
```bash
npm run build
```
```bash
npx cap sync ios
```
```bash
npx cap open ios
```

Xcode'da: **App** hedefi → *Signing & Capabilities* → Team'ini seç
(“Automatically manage signing” açık kalsın). Bundle ID `app.lumos.mobile`
— ilk yüklemeden sonra değiştirilemez.

## 2. Cihazda dene (yüklemeden ÖNCE)

Bir iPhone bağla ya da simülatör seç, ▶ ile çalıştır. Sırayla
(`docs/packaging.md` → "Verify on the first TestFlight build"):

1. E-posta ile kayıt ol ve giriş yap — form uygulamanın içinde açılmalı,
   sosyal giriş düğmesi görünmemeli.
2. Uygulamayı kapatıp aç: oturum açık kalmalı, doğrudan Panel gelmeli.
3. Quiz → öneri → "Aldım" → Varlıklar; pazar ve dil değiştir.
4. Uçak modunda aç: boş sayfa değil, uygulamanın kendi arayüzü gelmeli.

## 3. App Store Connect

1. appstoreconnect.apple.com → *My Apps* → **+** → New App. Platform iOS,
   ad "Lumos", birincil dil, Bundle ID `app.lumos.mobile`, SKU `lumos-ios`.
2. **App Privacy** — `docs/store-submission.md` → "Data Safety" tablosunu
   birebir gir (izleme: hiçbirinde yok).
3. **Yaş derecelendirmesi**, **açıklamalar** (TR/EN/DE), **inceleme notu**,
   **demo hesap** — hepsi `docs/store-submission.md` içinde hazır.
4. **Ekran görüntüleri** — yalnızca iPhone (uygulama iPhone'a özel):
   ```bash
   STORE=1 LANG_UI=en node demo/capture.mjs
   ```
5. Gizlilik politikası URL'si: `https://<alan adın>/privacy`.

## 4. Yükle

Xcode'da hedef cihaz olarak **Any iOS Device (arm64)** seç →
*Product → Archive* → Organizer açılınca **Distribute App → App Store
Connect → Upload**. Şifreleme sorusu çıkmaz (Info.plist'te beyan edildi).

10–30 dakika sonra build, App Store Connect → TestFlight'ta görünür.
Önce TestFlight'tan kendi telefonuna kur ve 2. adımı bir kez daha yap;
sonra sürüm sayfasında build'i seçip **Submit for Review**.

## Bilinen sınırlar (inceleme notunda iddia ETME)

- **Yerel bildirim (APNs) yok.** Mağaza sürümünde bildirim gönderilmiyor;
  Apple 4.2 ("paketlenmiş web sitesi") reddine karşı en güçlü argüman bu
  olurdu. Developer hesabı açılınca eklenebilir — ilk gönderimden önce
  eklemek reddi belirgin biçimde azaltır.
- Sürüm `1.0 (1)`. Her yeni yüklemede build numarasını artır
  (Xcode → App hedefi → General → Build).
