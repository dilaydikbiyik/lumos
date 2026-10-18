"""
Crypto — the one asset this app refuses to recommend, and therefore the one
it owes the clearest explanation.

People who enjoy risk hold crypto. The app has always let them RECORD it
(holding type "crypto" has existed since the first migration) and has never
said a word about what they are holding. Silence beside a recorded asset
reads as endorsement.

Why it stays out of every recommended portfolio is methodological, and the
copy says so rather than moralising: the projection method draws bands from
the INDEPENDENT periods in an asset's own history, and crypto's record is
not long enough to carry one. That is the same guard that now refuses a
ten-year band for gold and for the Nasdaq ETF — applied consistently, not
invented for crypto.

The series this completes:
  funds       — separation is real, separation is not a value guarantee
  home routes — the pool is segregated, the DATE is not promised
  gold        — metal, a claim, or a fund; and in Europe usually neither
  crypto      — your keys or someone else's; and a licence is not insurance

Deliberately absent: the custody percentages and capital requirements of the
Turkish regime. The custody rule itself is confirmed and is in the copy as
"the large majority"; the figures conflict between sources, and a number
that might be wrong is worse here than no number. Price levels, platform
names and token names are absent for the same reasons as everywhere else.
"""

from typing import Optional

CRYPTO: dict[str, dict[str, list[dict]]] = {
    "TR": {
        "tr": [
            {"title": "Bu uygulama kripto önermiyor — kaydetmene izin veriyor",
             "body": "Önerdiğimiz portföylerde kripto yok ve olmayacak. Sebebi ahlaki değil, yöntemsel: bu uygulamanın bantları bir varlığın kendi geçmişindeki bağımsız dönemlerden çıkar, kriptonun geçmişi ise o bantları dürüstçe taşıyacak kadar uzun değil. Ama elinde varsa görmezden gelmek işe yaramaz — portföyünün gerçeğini görmen için kaydını tutabilirsin."},
            {"title": "Anahtar sende mi, bir kurumda mı?",
             "body": "Kriptoda tek gerçek ayrım budur. Anahtar sendeyse karşı taraf yoktur: kimse batsa da varlık senin kalır, ama anahtarı kaybedersen kimse geri getiremez. Bir platformda tutuyorsan elinde varlık değil, platformdan bir ALACAK vardır. İkisi de 'bitcoinim var' diye anılır."},
            {"title": "Lisans gerçek bir denetimdir, değer garantisi değildir",
             "body": "Türkiye'de artık lisanslı platformlar müşteri kriptosunun büyük çoğunluğunu yetkili bir saklayıcıda tutmak ve bakiyeleri raporlamak zorunda. Bu gerçek ve kıymetli bir korumadır — ama bu uygulamadaki her koruma gibi, varlığın FİYATINI korumaz ve mevduat sigortası değildir. Lisanslı bir platformda düşen bir varlık yine düşer."},
            {"title": "Transfer geri alınamaz, ve bu bir özelliktir",
             "body": "Yanlış adrese gönderilen tutarın iadesi yoktur; itiraz mekanizması, ters ibra, arayacak bir merci yoktur. Banka havalesinden farklı olan şey tam budur ve dolandırıcılığın bu alanda yoğunlaşmasının sebebi de budur. Acele ettiren her teklif, acele ettirdiği için şüphelidir."},
        ],
        "en": [
            {"title": "This app does not recommend crypto — it lets you record it",
             "body": "There is no crypto in the portfolios we build, and there will not be. The reason is methodological rather than moral: this app's bands come from the independent periods in an asset's own history, and crypto's history is not long enough to carry one honestly. But ignoring what you already hold does not help — you can record it so the picture of your portfolio is the true one."},
            {"title": "Do you hold the keys, or does an institution?",
             "body": "This is the only real distinction in crypto. If you hold the keys there is no counterparty: nobody failing takes the asset from you, but if you lose the key nobody can bring it back. If you hold it on a platform you do not have the asset, you have a CLAIM on the platform. Both get called \"I own bitcoin\"."},
            {"title": "A licence is real supervision, not a guarantee of value",
             "body": "Licensed platforms in Türkiye must now keep the large majority of customer crypto with an authorised custodian and report balances. That is a real and valuable protection — but like every protection in this app it does not protect the asset's PRICE, and it is not deposit insurance. An asset that falls on a licensed platform still falls."},
            {"title": "Transfers cannot be reversed, and that is a feature",
             "body": "An amount sent to the wrong address does not come back: no dispute process, no chargeback, no desk to call. That is precisely what differs from a bank transfer, and it is why fraud concentrates here. Any offer that rushes you is suspect for the rushing alone."},
        ],
        "de": [
            {"title": "Diese App empfiehlt kein Krypto — sie lässt dich es erfassen",
             "body": "In den Portfolios, die wir bauen, ist kein Krypto, und das bleibt so. Der Grund ist methodisch, nicht moralisch: die Bänder dieser App entstehen aus den unabhängigen Zeiträumen der eigenen Historie eines Vermögenswerts, und Kryptos Historie ist dafür nicht lang genug. Was du aber schon hältst, hilft nicht zu ignorieren — erfasse es, damit das Bild deines Portfolios das wahre ist."},
            {"title": "Hast du die Schlüssel, oder hat sie ein Institut?",
             "body": "Das ist der einzige echte Unterschied bei Krypto. Mit eigenen Schlüsseln gibt es keine Gegenpartei: keine Insolvenz nimmt dir den Wert, aber verlierst du den Schlüssel, bringt ihn niemand zurück. Auf einer Plattform hältst du nicht den Wert, sondern eine FORDERUNG gegen die Plattform. Beides heißt \"ich habe Bitcoin\"."},
            {"title": "Eine Zulassung ist echte Aufsicht, keine Wertgarantie",
             "body": "Zugelassene Plattformen in der Türkei müssen den überwiegenden Teil der Kundenbestände bei einer zugelassenen Verwahrstelle halten und Bestände melden. Das ist ein echter und wertvoller Schutz — aber wie jeder Schutz in dieser App schützt er nicht den PREIS, und er ist keine Einlagensicherung. Ein Wert, der auf einer zugelassenen Plattform fällt, fällt trotzdem."},
            {"title": "Überweisungen sind unwiderruflich, und das ist gewollt",
             "body": "Ein an die falsche Adresse gesendeter Betrag kommt nicht zurück: kein Widerspruch, keine Rückbuchung, keine Stelle zum Anrufen. Genau das unterscheidet es von einer Banküberweisung, und deshalb sammelt sich hier der Betrug. Jedes Angebot, das dich drängt, ist allein wegen des Drängens verdächtig."},
        ],
    },
    "US": {
        "tr": [
            {"title": "Bu uygulama kripto önermiyor — kaydetmene izin veriyor",
             "body": "Önerdiğimiz portföylerde kripto yok ve olmayacak. Sebebi ahlaki değil, yöntemsel: bu uygulamanın bantları bir varlığın kendi geçmişindeki bağımsız dönemlerden çıkar, kriptonun geçmişi ise o bantları dürüstçe taşıyacak kadar uzun değil. Ama elinde varsa görmezden gelmek işe yaramaz — portföyünün gerçeğini görmen için kaydını tutabilirsin."},
            {"title": "Anahtar sende mi, bir kurumda mı?",
             "body": "Kriptoda tek gerçek ayrım budur. Anahtar sendeyse karşı taraf yoktur: kimse batsa da varlık senin kalır, ama anahtarı kaybedersen kimse geri getiremez. Bir borsada tutuyorsan elinde varlık değil, borsadan bir ALACAK vardır. İkisi de 'bitcoinim var' diye anılır."},
            {"title": "Mevduat sigortası yok, ve iflasta sıradan alacaklı olabilirsin",
             "body": "Bankadan ya da aracı kurumdan alışık olduğun korumalar, bir borsada tutulan kriptoya uzanmaz. Müşteri varlıklarının gerçekten ayrılmadığı yerlerde müşteriler iflas masasının genel alacaklısı sayıldı ve küçük bir kısmı için yıllarca bekledi. Platformun varlıklarını nasıl tuttuğunu yazdığı yeri oku; pazarlamadaki 'sigortalı' kelimesini bir cevap değil, bir soru olarak gör."},
            {"title": "Transfer geri alınamaz, ve bu bir özelliktir",
             "body": "Yanlış adrese gönderilen tutarın iadesi yoktur; itiraz mekanizması, ters ibra, arayacak bir merci yoktur. Banka havalesinden farklı olan şey tam budur ve dolandırıcılığın bu alanda yoğunlaşmasının sebebi de budur. Acele ettiren her teklif, acele ettirdiği için şüphelidir."},
        ],
        "en": [
            {"title": "This app does not recommend crypto — it lets you record it",
             "body": "There is no crypto in the portfolios we build, and there will not be. The reason is methodological rather than moral: this app's bands come from the independent periods in an asset's own history, and crypto's history is not long enough to carry one honestly. But ignoring what you already hold does not help — you can record it so the picture of your portfolio is the true one."},
            {"title": "Do you hold the keys, or does an institution?",
             "body": "This is the only real distinction in crypto. If you hold the keys there is no counterparty: nobody failing takes the asset from you, but if you lose the key nobody can bring it back. If you hold it on an exchange you do not have the asset, you have a CLAIM on the exchange. Both get called \"I own bitcoin\"."},
            {"title": "No deposit insurance, and in a bankruptcy you may be an unsecured creditor",
             "body": "The protections you may be used to from a bank or a brokerage do not extend to crypto held on an exchange. Where customer assets were not genuinely segregated, customers have been treated as general creditors of the estate and waited years for a fraction. Read how the platform says it holds your assets, and treat the word \"insured\" in marketing as a question rather than an answer."},
            {"title": "Transfers cannot be reversed, and that is a feature",
             "body": "An amount sent to the wrong address does not come back: no dispute process, no chargeback, no desk to call. That is precisely what differs from a bank transfer, and it is why fraud concentrates here. Any offer that rushes you is suspect for the rushing alone."},
        ],
        "de": [
            {"title": "Diese App empfiehlt kein Krypto — sie lässt dich es erfassen",
             "body": "In den Portfolios, die wir bauen, ist kein Krypto, und das bleibt so. Der Grund ist methodisch, nicht moralisch: die Bänder dieser App entstehen aus den unabhängigen Zeiträumen der eigenen Historie eines Vermögenswerts, und Kryptos Historie ist dafür nicht lang genug. Was du aber schon hältst, hilft nicht zu ignorieren — erfasse es, damit das Bild deines Portfolios das wahre ist."},
            {"title": "Hast du die Schlüssel, oder hat sie ein Institut?",
             "body": "Das ist der einzige echte Unterschied bei Krypto. Mit eigenen Schlüsseln gibt es keine Gegenpartei: keine Insolvenz nimmt dir den Wert, aber verlierst du den Schlüssel, bringt ihn niemand zurück. Auf einer Börse hältst du nicht den Wert, sondern eine FORDERUNG gegen die Börse. Beides heißt \"ich habe Bitcoin\"."},
            {"title": "Keine Einlagensicherung, und in der Insolvenz bist du vielleicht einfacher Gläubiger",
             "body": "Der Schutz, den du von einer Bank oder einem Broker kennst, erstreckt sich nicht auf Krypto, das auf einer Börse liegt. Wo Kundenbestände nicht wirklich getrennt waren, wurden Kunden als allgemeine Gläubiger der Masse behandelt und warteten Jahre auf einen Bruchteil. Lies, wie die Plattform die Verwahrung beschreibt, und nimm das Wort \"versichert\" im Marketing als Frage, nicht als Antwort."},
            {"title": "Überweisungen sind unwiderruflich, und das ist gewollt",
             "body": "Ein an die falsche Adresse gesendeter Betrag kommt nicht zurück: kein Widerspruch, keine Rückbuchung, keine Stelle zum Anrufen. Genau das unterscheidet es von einer Banküberweisung, und deshalb sammelt sich hier der Betrug. Jedes Angebot, das dich drängt, ist allein wegen des Drängens verdächtig."},
        ],
    },
    "DE": {
        "tr": [
            {"title": "Bu uygulama kripto önermiyor — kaydetmene izin veriyor",
             "body": "Önerdiğimiz portföylerde kripto yok ve olmayacak. Sebebi ahlaki değil, yöntemsel: bu uygulamanın bantları bir varlığın kendi geçmişindeki bağımsız dönemlerden çıkar, kriptonun geçmişi ise o bantları dürüstçe taşıyacak kadar uzun değil. Ama elinde varsa görmezden gelmek işe yaramaz — portföyünün gerçeğini görmen için kaydını tutabilirsin."},
            {"title": "Anahtar sende mi, bir kurumda mı?",
             "body": "Kriptoda tek gerçek ayrım budur. Anahtar sendeyse karşı taraf yoktur: kimse batsa da varlık senin kalır, ama anahtarı kaybedersen kimse geri getiremez. Bir platformda tutuyorsan elinde varlık değil, platformdan bir ALACAK vardır. İkisi de 'bitcoinim var' diye anılır."},
            {"title": "AB lisansı denetimdir, mevduat sigortası değildir",
             "body": "AB'de hizmet sağlayıcıların lisans alması ve müşteri varlıklarını ayrı tutması zorunlu. Bu gerçek bir denetimdir — ama mevduat sigortası değildir: banka hesabından bildiğin yasal güvence burada geçerli olmaz, fiyat ise hiçbir koşulda korunmaz."},
            {"title": "Kripto ETP'si de altın ETC'si gibi bir borçlanma aracıdır",
             "body": "Altındaki ayrımın aynısı, ve en az o kadar sık yanlış okunuyor: Avrupa'da borsada işlem gören kripto ürünü çoğunlukla bir fon değil, ihraççının borçlanma aracıdır. İhraççının batma riskini sen taşırsın ve teminatın iflasta ne olacağı izahnamede yazar."},
        ],
        "en": [
            {"title": "This app does not recommend crypto — it lets you record it",
             "body": "There is no crypto in the portfolios we build, and there will not be. The reason is methodological rather than moral: this app's bands come from the independent periods in an asset's own history, and crypto's history is not long enough to carry one honestly. But ignoring what you already hold does not help — you can record it so the picture of your portfolio is the true one."},
            {"title": "Do you hold the keys, or does an institution?",
             "body": "This is the only real distinction in crypto. If you hold the keys there is no counterparty: nobody failing takes the asset from you, but if you lose the key nobody can bring it back. If you hold it on a platform you do not have the asset, you have a CLAIM on the platform. Both get called \"I own bitcoin\"."},
            {"title": "An EU licence is supervision, not deposit insurance",
             "body": "Providers in the EU need an authorisation and must keep customer holdings separate. That is real supervision — but it is not deposit insurance: the statutory protection you know from a bank account does not apply here, and the price is never protected in any case."},
            {"title": "A crypto ETP, like a gold ETC, is a debt security",
             "body": "The same distinction as with gold, and misread just as often: the exchange-traded crypto product in Europe is usually not a fund but a debt security of its issuer. You carry that issuer's insolvency risk, and what happens to the collateral in an insolvency is written in the prospectus."},
        ],
        "de": [
            {"title": "Diese App empfiehlt kein Krypto — sie lässt dich es erfassen",
             "body": "In den Portfolios, die wir bauen, ist kein Krypto, und das bleibt so. Der Grund ist methodisch, nicht moralisch: die Bänder dieser App entstehen aus den unabhängigen Zeiträumen der eigenen Historie eines Vermögenswerts, und Kryptos Historie ist dafür nicht lang genug. Was du aber schon hältst, hilft nicht zu ignorieren — erfasse es, damit das Bild deines Portfolios das wahre ist."},
            {"title": "Hast du die Schlüssel, oder hat sie ein Institut?",
             "body": "Das ist der einzige echte Unterschied bei Krypto. Mit eigenen Schlüsseln gibt es keine Gegenpartei: keine Insolvenz nimmt dir den Wert, aber verlierst du den Schlüssel, bringt ihn niemand zurück. Auf einer Plattform hältst du nicht den Wert, sondern eine FORDERUNG gegen die Plattform. Beides heißt \"ich habe Bitcoin\"."},
            {"title": "Die EU-Zulassung ist Aufsicht, keine Einlagensicherung",
             "body": "Anbieter brauchen in der EU eine Zulassung und müssen Kundenbestände getrennt halten. Das ist echte Aufsicht — aber keine Einlagensicherung: der gesetzliche Schutz, den du vom Bankkonto kennst, gilt hier nicht, und der Preis ist ohnehin nie geschützt."},
            {"title": "Ein Krypto-ETP ist wie ein Gold-ETC eine Schuldverschreibung",
             "body": "Dieselbe Unterscheidung wie beim Gold, und sie wird genauso oft falsch gelesen: das börsengehandelte Krypto-Produkt ist in Europa meist kein Sondervermögen, sondern eine Schuldverschreibung des Emittenten. Du trägst dessen Insolvenzrisiko, und was mit der Besicherung im Insolvenzfall passiert, steht im Prospekt."},
        ],
    },
}

_FALLBACK_ORDER = ("en", "tr", "de")


def for_market(market: str, lang: str = "tr") -> Optional[list[dict]]:
    by_lang = CRYPTO.get((market or "").upper())
    if not by_lang:
        return None
    if lang in by_lang:
        return by_lang[lang]
    for alt in _FALLBACK_ORDER:
        if alt in by_lang:
            return by_lang[alt]
    return next(iter(by_lang.values()), None)


def available_markets() -> set[str]:
    return set(CRYPTO)
