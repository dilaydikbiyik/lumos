# Lumos — marka varlıkları ve tescil dosyası

Bu klasör, marka tescili başvurusu ve basın/mağaza kullanımı için hazırlanmış
görselleri içerir. Uygulamanın içinde kullanılan ikonlar `frontend/public/`
altındadır; buradakiler yalnızca **başvuru ve dış kullanım** içindir.

## Dosyalar

| Dosya | Boyut | Nerede kullanılır |
|---|---|---|
| `lumos-wordmark-dark.png` | 2000×700 | **Tescil başvurusu için önerilen** — ad + logo, markanın gerçek kullanım hâli |
| `lumos-wordmark-white.png` | 2000×700 | Beyaz zeminli basılı kullanım, sunum |
| `lumos-wordmark-transparent.png` | 2000×700 | Serbest zemin |
| `lumos-mark-1024-dark.png` | 1024×1024 | Yalnızca simge — sosyal medya profil görseli |
| `lumos-mark-1024-white.png` | 1024×1024 | Beyaz zeminli simge |
| `lumos-mark-1024-transparent.png` | 1024×1024 | Serbest zemin simge |

Kaynak vektör: `frontend/public/favicon.svg` (ateşböceği), yazı tipi **Outfit 800**.
Marka renkleri: ateşböceği gövdesi `#FFB300 → #FF8C00 → #E64A00`, kanatlar `#C8A84B`,
koyu zemin `#0A0B12`.

## Tescil başvurusu — hazırlık notları

Başvuru **TÜRKPATENT'in EPATS sistemi** üzerinden çevrimiçi yapılır
(turkpatent.gov.tr). Aşağıdakiler hazırlıktır; başvurunun kendisi kimlik
doğrulama ve ödeme gerektirdiği için bizzat yapılmalıdır.

### 1. Önce benzerlik araştırması — bu adımı atlama

**"Lumos" yaygın bir kelimedir** (Latince "ışık") ve dünyada aynı adı taşıyan
tescilli markalar mevcuttur — örneğin Lumosity'nin sahibi Lumos Labs ve enerji
sektöründen Lumos Global. Türkiye'de ilgili sınıflarda tescil bulunup
bulunmadığını başvurudan **önce** EPATS'ın ücretsiz marka araştırma ekranından
kontrol et. Karışıklık ihtimali varsa iki yol vardır:

- ad + logo **birlikte** başvurulur (ayırt edicilik artar), ya da
- ada ayırt edici bir ek yapılır (ör. "Lumos Finans").

Bu yüzden başvuru için önerilen görsel, yalnız simge değil **kelime markasıdır**.

### 2. Sınıf seçimi (Nice sınıflandırması)

Ürünün kapsamına göre üç sınıf anlamlıdır:

| Sınıf | Kapsam | Neden |
|---|---|---|
| **42** | Yazılım geliştirme, SaaS, bilgisayar hizmetleri | Lumos bir web/PWA yazılım hizmetidir — **birincil sınıf** |
| **36** | Finansal işler, parasal işler, gayrimenkul işleri | Finansal eğitim ve gayrimenkul bilgisi sunar |
| **9** | İndirilebilir bilgisayar yazılımları, mobil uygulamalar | İleride mağazalara çıkarsa gerekir |

Her ek sınıf ücreti artırır; bütçeye göre 42 tek başına da başlangıç olabilir.

### 3. Görsel gereklilikleri

TÜRKPATENT marka örneğini belirli bir çözünürlüğün altında kabul etmez
(genellikle en az 591×591 piksel istenir). Buradaki dosyalar 1024×1024 ve
2000×700 olduğu için bu eşiğin üzerindedir. Başvuruda **hangi zeminle
başvurulursa marka o hâliyle tescillenir**: koyu zeminli sürüm ürünün gerçek
kullanımını yansıtır, şeffaf/beyaz sürüm ise zeminden bağımsız daha geniş
koruma sağlar. Bu tercihi başvuru sırasında bilinçli yap.

### 4. Bilmediklerim — kontrol etmen gerekenler

Güncel **başvuru ücretlerini ve süreleri** bilmiyorum; bunlar her yıl
değiştiği için TÜRKPATENT'in resmî ücret tarifesinden teyit et. Genel olarak
süreç, itiraz süreleri dâhil aylar sürer ve başvuru tarihi öncelik hakkı
doğurur — yani başvuruyu erken yapmak, tescilin geç bitmesinden daha önemlidir.

### 5. Neyin korunduğunu unutma

Marka tescili **adı ve logoyu** korur; ürün fikrini veya özellik setini
korumaz. Kodun ise `LICENSE` dosyasındaki "All Rights Reserved" şartlarıyla
zaten korunmaktadır: herkes okuyabilir, kimse kopyalayıp kullanamaz.
