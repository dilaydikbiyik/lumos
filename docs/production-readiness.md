# Yayına hazırlık: development kalıntılarını temizlemek

Uygulama canlı ve çalışıyor, ama iki bileşen hâlâ **geliştirme modunda**.
Portfolyo ve demo için sorun değil; gerçek kullanıcı trafiği veya mağaza
başvurusu öncesinde ikisi de değişmeli.

Kod tarafında **hiçbir değişiklik gerekmiyor** — her iki bileşen de tamamen
ortam değişkenleriyle yapılandırılıyor (`settings.CLERK_*`, `VITE_CLERK_*`).
Aşağıdakiler yalnızca panel işlemleridir.

---

## 1. Clerk: development → production instance

**Belirti:** Giriş ekranının altında turuncu **"Development mode"** yazısı
görünüyor, anahtarlar `pk_test_` / `sk_test_` ile başlıyor.

**Neden önemli:** Development instance'ın oturum güvenliği gevşektir ve
Clerk bunu üretim trafiği için desteklemez. App Store/Play Store incelemesinde
de "geliştirme sürümü" olarak değerlendirilme riski taşır.

**Ön koşul: kendi alan adın.** Clerk production instance, `clerk.alanadi.com`
biçiminde bir CNAME kaydı ister. `lumos-sooty.vercel.app` bir Vercel alt alan
adı olduğu için bu adımda kullanılamaz. Yani sıra şu:

1. Bir alan adı al (ör. `lumos.app.tr`, `lumosapp.com` — yıllık birkaç yüz lira).
2. Alan adını Vercel'e bağla (Vercel → Project → Settings → Domains).
3. Clerk Dashboard → **Create production instance** → alan adını gir.
4. Clerk'in verdiği CNAME kayıtlarını alan adı sağlayıcına ekle, doğrulanmasını bekle.
5. Google ile giriş kullanılacaksa, production instance için **kendi Google OAuth
   kimlik bilgilerini** oluşturman gerekir (development'ta Clerk'in paylaşımlı
   kimlik bilgileri kullanılır, üretimde kullanılamaz).

**Sonra güncellenecek değerler** (yalnızca panel, kod değil):

| Nerede | Değişken | Yeni değer |
|---|---|---|
| Vercel → Environment Variables | `VITE_CLERK_PUBLISHABLE_KEY` | `pk_live_…` |
| Render → Environment | `CLERK_SECRET_KEY` | `sk_live_…` |
| Render → Environment | `CLERK_JWT_ISSUER` | production JWKS adresi |

> `CLERK_JWT_ISSUER` doğrudan JWKS URL'i olarak kullanılıyor
> (`backend/middleware/verify_clerk.py`), production instance'ın adresiyle
> değiştirilmeli — aksi hâlde tüm istekler 401 döner.

**Dikkat:** Development ve production instance'lar **ayrı kullanıcı
veritabanlarıdır**. Geçişte mevcut test kullanıcıları taşınmaz; uygulamadaki
gerçek veriler Neon'da Clerk kullanıcı kimliğine bağlı olduğu için, kendi
hesabınla yeniden kayıt olup profili yeniden oluşturman gerekecek.

---

## 2. Render: ücretsiz katman → her zaman açık

**Belirti:** 15 dakika hareketsizlikten sonra servis uyuyor; uyanması 50
saniyeye kadar sürebiliyor.

**Neden önemli:** Mağaza incelemesinde uygulamanın yanıt vermemesi doğrudan
ret sebebidir. Ayrıca ilk izlenimi bozar — LinkedIn'den gelen biri boş ekranla
karşılaşabilir.

**Şu an ne yapılıyor:** GitHub Actions her 10 dakikada bir `/health` çağırarak
servisi ayakta tutmaya çalışıyor (`.github/workflows/keepalive.yml`), frontend
de açılışta sessiz bir uyandırma isteği gönderiyor. Bunlar palyatif; GitHub'ın
cron zamanlaması garanti değildir.

**Kalıcı çözüm:** Render'da ücretli katmana geçmek (aylık birkaç dolar
mertebesinde). Geçildiğinde keepalive iş akışı silinebilir.

---

## 3. Ephemeral önbellek (bilinen sınırlama)

Piyasa ve TCMB verileri `diskcache` ile diskte tutuluyor. Render'ın dosya
sistemi kalıcı değildir: **her deploy'da önbellek sıfırlanır**, "son bilinen
iyi veri" yedeği de dâhil. Sonuç, deploy sonrası ilk isteğin yavaş olmasıdır.

Çözüm, önbelleği Neon'da küçük bir tabloya veya bir Redis örneğine taşımaktır.
Bugünkü kullanım hacminde aciliyeti yoktur; trafik artarsa öncelik kazanır.

---

## Sıralama önerisi

1. LinkedIn paylaşımı + gerçek kullanıcı geri bildirimi *(şimdi — mevcut hâliyle sorun yok)*
2. Alan adı + Clerk production + Render ücretli katman *(ciddi trafik öncesi)*
3. Kalıcı önbellek *(trafik artınca)*
4. Capacitor ile mağaza paketleme *(en son)*
