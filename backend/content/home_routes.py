"""
The ways into a home in this market, and what each one actually protects.

Why this exists. The app offered a reader two routes — keep renting, or buy
with a mortgage — and in Türkiye that is an incomplete question. A large
number of people get into a home through SAVINGS-BASED FINANCING: pay in
monthly, wait your turn, no interest. The rent-versus-buy calculator said
nothing about it, so the app was silent on the route a sizeable part of its
own audience is actually taking.

NO COMPANY IS NAMED, anywhere, deliberately. Describing a licensed category
and what the law does for a customer is education; naming a firm in a piece
about what happens when firms fail is a different thing with a different
exposure. A reader who wants to check a specific company is told where the
register is instead.

THE SHAPE IS THE SAME AS THE FUND LESSON, which is why both exist:
segregation is real, segregation is not a guarantee, and the failure mode
is about ACCESS and ENTITLEMENT rather than about the money vanishing. In
savings-based financing the specific twist is sharper than with a fund —
on liquidation the entitlement changes KIND. What you signed up for was a
house. What the law then gives you back is your savings.

Accuracy notes for whoever edits this next:
  - Article numbers are Law 6361 as described in secondary sources; the
    statute is the authority and should be re-read before any of this is
    reworded.
  - Figures (limits, ratios, day counts) are deliberately ABSENT. The
    regulator changed several of them twice during 2026, and evergreen copy
    that carries a number goes quietly wrong.
"""

from typing import Optional

ROUTES: dict[str, dict[str, list[dict]]] = {
    "TR": {
        "tr": [
            {"title": "Üçüncü bir yol var: tasarruf finansmanı",
             "body": "Kirada kalmak ve kredi çekmek dışında, faizsiz bir yol daha var: aylık ödersin, sıran gelince konut ya da taşıt finansmanı kullanırsın. Bu sektör BDDK tarafından düzenlenir ve 6361 sayılı Kanun'a tabidir — yani denetimsiz bir alan değil."},
            {"title": "Havuzdaki paran şirketin parası değildir",
             "body": "Kanun, müşterilerden toplanan birikimlerin şirketin kendi hesaplarından ayrı tutulmasını zorunlu kılar. Bu varlıklar şirketin borçları için haczedilemez, rehnedilemez ve iflas masasına dâhil edilemez. Koruma gerçektir ve zayıf değildir."},
            {"title": "Ama mevduat güvencesi değildir",
             "body": "Bu yapı TMSF güvencesi ya da devlet ödeme garantisi DEĞİLDİR. Bankadaki paranın 'şu tutara kadar sigortalı' olması gibi bir mekanizma burada yoktur; koruma, havuzun ayrıştırılmasından ve denetimden gelir."},
            {"title": "Şirket tasfiyeye girerse beklentin tür değiştirir",
             "body": "Faaliyet izni kaldırılır ve şirket tasfiyeye girerse, sözleşmedeki finansman kullanma hakkın uygulanmaz. Yani 'ev' beklentisi 'birikimin iadesi'ne dönüşür. Paranı kaybetmeyebilirsin — ama almak için beklediğin şeyi almazsın, ve bu aynı şey değildir."},
            {"title": "İzinli mi, önce ona bak",
             "body": "İzinsiz tasarruf finansman faaliyeti suçtur ve bu şirketlerde kanuni havuz koruması ile denetim kuralları UYGULANMAZ. Yani yukarıdaki korumaların hepsi, şirketin BDDK izinli olmasına bağlıdır. Sözleşme imzalamadan önce BDDK'nın yayımladığı izinli şirketler listesinden doğrula."},
        ],
        "en": [
            {"title": "There is a third way: savings-based financing",
             "body": "Besides renting and taking a loan, there is an interest-free route: you pay monthly and, when your turn comes, you draw financing for a home or a vehicle. The sector is regulated by the banking authority under Law 6361 — it is not an unsupervised corner of the market."},
            {"title": "The pool is not the company's money",
             "body": "The law requires savings collected from customers to be held apart from the company's own accounts. Those assets cannot be attached or pledged for the company's debts and cannot be drawn into its bankruptcy estate. The protection is real and it is not weak."},
            {"title": "But it is not deposit insurance",
             "body": "This structure is NOT a state payment guarantee or a deposit-insurance scheme. There is no \"covered up to X\" the way money in a bank is covered; the protection comes from the pool being separated and from supervision."},
            {"title": "In liquidation your expectation changes kind",
             "body": "If the licence is withdrawn and the company is wound up, the right to draw financing under your contract does not apply. The expectation of a HOME becomes the return of your SAVINGS. You may not lose the money — but you do not get the thing you were waiting for, and those are not the same outcome."},
            {"title": "Check the licence first",
             "body": "Operating this business without a licence is a criminal offence, and in unlicensed firms the statutory pool protection and supervision rules DO NOT APPLY. Every protection above depends on the company being licensed. Verify against the regulator's published list before signing."},
        ],
        "de": [
            {"title": "Es gibt einen dritten Weg: Sparbasierte Finanzierung",
             "body": "Neben Miete und Kredit gibt es einen zinsfreien Weg: du zahlst monatlich ein und ziehst, wenn du an der Reihe bist, eine Finanzierung für Wohnung oder Fahrzeug. Der Sektor wird von der Bankenaufsicht nach Gesetz 6361 reguliert — kein unbeaufsichtigter Winkel des Marktes."},
            {"title": "Der Pool ist nicht das Geld der Gesellschaft",
             "body": "Das Gesetz verlangt, die von Kundinnen eingezahlten Ersparnisse getrennt von den eigenen Konten der Gesellschaft zu halten. Diese Werte können für deren Schulden weder gepfändet noch verpfändet werden und fallen nicht in die Insolvenzmasse. Der Schutz ist real und nicht schwach."},
            {"title": "Aber es ist keine Einlagensicherung",
             "body": "Diese Struktur ist KEINE staatliche Zahlungsgarantie und keine Einlagensicherung. Ein \"gedeckt bis X\" wie bei Bankguthaben gibt es hier nicht; der Schutz entsteht aus der Trennung des Pools und aus der Aufsicht."},
            {"title": "In der Abwicklung ändert deine Erwartung ihre Art",
             "body": "Wird die Erlaubnis entzogen und die Gesellschaft abgewickelt, gilt das vertragliche Recht auf Finanzierung nicht mehr. Aus der Erwartung einer WOHNUNG wird die Rückzahlung deiner ERSPARNISSE. Vielleicht verlierst du das Geld nicht — aber du bekommst nicht das, worauf du gewartet hast, und das ist nicht dasselbe."},
            {"title": "Prüfe zuerst die Erlaubnis",
             "body": "Dieses Geschäft ohne Erlaubnis zu betreiben ist strafbar, und bei nicht zugelassenen Firmen gelten der gesetzliche Poolschutz und die Aufsichtsregeln NICHT. Jeder Schutz oben hängt an der Zulassung. Prüfe die veröffentlichte Liste der Aufsicht, bevor du unterschreibst."},
        ],
    },
    "DE": {
        "de": [
            {"title": "Der dritte Weg heißt hier Bausparvertrag",
             "body": "Neben Mieten und einer gewöhnlichen Finanzierung gibt es die Bausparvariante: erst eine Sparphase, danach die Möglichkeit eines Darlehens zu einem im Tarif festgelegten Zinssatz. Bausparkassen unterliegen dem Bausparkassengesetz und dürfen die Spareinlagen nur für Wohnzwecke und risikoarme Anlagen verwenden."},
            {"title": "Hier gibt es tatsächlich eine Einlagensicherung",
             "body": "Anders als bei vielen vergleichbaren Modellen im Ausland ist eine Bausparkasse eine Bank. Die Spareinlagen sind über die gesetzliche Einlagensicherung geschützt, in der Regel bis 100.000 Euro je Einleger. Das ist eine andere Qualität von Schutz als bloße Vermögenstrennung."},
            {"title": "Geschützt ist das Geld, nicht der Termin",
             "body": "Der Zuteilungszeitpunkt steht nicht im Voraus fest: solange die Zuteilungsreife nicht erreicht ist, ist er nicht garantiert. Die Einlagensicherung schützt deine Ersparnisse, nicht den Tag, an dem du das Darlehen bekommst."},
            {"title": "Rechne den Tarif durch, nicht nur den Zinssatz",
             "body": "Abschlussgebühr, Jahresentgelte und ein niedriger Guthabenzins in der Sparphase gehören in dieselbe Rechnung wie der günstige Darlehenszins später. Ein Tarif ist erst dann günstig, wenn er es über beide Phasen zusammen ist."},
            {"title": "Prüfe die Zulassung",
             "body": "Bausparkassen stehen unter Aufsicht der BaFin. Wenn ein Anbieter ein ähnliches Modell ohne Banklizenz anbietet, gilt die Einlagensicherung nicht — und genau das ist der Unterschied, auf den es ankommt."},
        ],
        "tr": [
            {"title": "Almanya'daki üçüncü yol: Bausparvertrag",
             "body": "Kira ve normal kredi dışında bir yol daha var: önce bir birikim dönemi, sonra tarifede önceden belirlenmiş faiz oranıyla kredi kullanma imkânı. Bausparkasse'ler Bauspar yasasına tabidir ve topladıkları birikimi yalnızca konut amaçlı ve düşük riskli yatırımlarda kullanabilir."},
            {"title": "Burada gerçekten mevduat güvencesi var",
             "body": "Benzeri birçok yurtdışı modelden farklı olarak Bausparkasse bir bankadır. Birikimler yasal mevduat güvencesi kapsamındadır, genellikle mudi başına 100.000 euroya kadar. Bu, sadece malvarlığı ayrıştırmasından farklı ve daha güçlü bir koruma türüdür."},
            {"title": "Korunan para, tarih değil",
             "body": "Tahsis zamanı önceden kesin değildir: tahsis olgunluğuna ulaşılmadığı sürece o tarih garanti edilmez. Mevduat güvencesi birikimini korur, krediyi alacağın günü değil."},
            {"title": "Faizi değil, tarifenin tamamını hesapla",
             "body": "Açılış ücreti, yıllık masraflar ve birikim döneminde düşük olan mevduat faizi, sonradan gelen düşük kredi faiziyle aynı hesaba girer. Bir tarife ancak iki dönemin toplamında ucuzsa ucuzdur."},
            {"title": "Lisansı kontrol et",
             "body": "Bausparkasse'ler BaFin denetimindedir. Bir sağlayıcı benzer bir modeli banka lisansı olmadan sunuyorsa mevduat güvencesi geçerli değildir — ve asıl fark tam olarak budur."},
        ],
        "en": [
            {"title": "The third route here is the Bausparvertrag",
             "body": "Besides renting and an ordinary mortgage there is the building-society route: a savings phase first, then the option of a loan at a rate fixed in the tariff. Building societies fall under the Building Society Act and may use savers' deposits only for housing purposes and low-risk investments."},
            {"title": "This one really does carry deposit insurance",
             "body": "Unlike many comparable models abroad, a Bausparkasse is a bank. The savings are covered by the statutory deposit guarantee scheme, generally up to 100,000 euro per depositor. That is a different quality of protection from mere segregation of assets."},
            {"title": "What is protected is the money, not the date",
             "body": "The allocation date is not fixed in advance: until allocation readiness is reached, it is not guaranteed. Deposit insurance protects your savings, not the day you get the loan."},
            {"title": "Price the whole tariff, not just the rate",
             "body": "The arrangement fee, the annual charges and the low credit interest during the savings phase belong in the same sum as the cheap loan rate later. A tariff is only cheap if it is cheap across both phases together."},
            {"title": "Check the licence",
             "body": "Building societies are supervised by BaFin. If a provider offers a similar model without a banking licence, the deposit guarantee does not apply — and that is exactly the difference that matters."},
        ],
    },
    "US": {
        "en": [
            {"title": "There is no savings-pool route here",
             "body": "Some countries run a third way into a home: pay into a pool month by month, wait your turn, no interest. The United States does not have a licensed equivalent. The routes are renting, a mortgage, or paying cash."},
            {"title": "Treat any pool that looks like one with suspicion",
             "body": "If something offers a home in exchange for monthly payments into a shared pool and is not a bank or a licensed lender, there is no deposit insurance behind it and no supervisor checking the ratios. The absence of a regulated category is not an opening in the market; it is the reason to be careful."},
            {"title": "The equivalent protections attach to the institution",
             "body": "FDIC insurance covers deposits at an insured bank, up to the limit, and it covers the BANK failing — not your house falling in value and not a builder failing to deliver. Knowing which institution holds your money, and what covers that institution, is the question worth asking."},
            {"title": "Down-payment assistance is the real third option",
             "body": "State and city programmes, and some employer schemes, help with a down payment rather than replacing the mortgage. They are the closest thing to a third route, they are public, and they are worth checking before assuming the choice is only rent or buy."},
            {"title": "Check the licence before the terms",
             "body": "A lender's registration can be checked through the NMLS consumer access register. Whatever the terms look like, they only mean something if the counterparty is licensed to offer them."},
        ],
        "tr": [
            {"title": "Burada havuz yöntemi yok",
             "body": "Bazı ülkelerde eve giden üçüncü bir yol vardır: ortak havuza ay ay ödersin, sıranı beklersin, faiz yoktur. ABD'de bunun lisanslı bir karşılığı YOKTUR. Yollar kira, mortgage ya da peşin ödemedir."},
            {"title": "Buna benzeyen her havuza şüpheyle yaklaş",
             "body": "Ortak bir havuza aylık ödeme karşılığında ev vaat eden ve banka ya da lisanslı kredi kuruluşu olmayan bir yapının arkasında mevduat sigortası da yoktur, oranlarını denetleyen bir kurum da. Düzenlenmiş bir kategorinin yokluğu piyasada bir boşluk değil, dikkatli olma sebebidir."},
            {"title": "Buradaki korumalar kuruma bağlıdır",
             "body": "FDIC sigortası, sigortalı bir bankadaki mevduatı limite kadar ve BANKANIN batması hâlinde korur — evinin değer kaybetmesini ya da müteahhidin teslim etmemesini değil. Sorulmaya değer soru: paranı hangi kurum tutuyor ve o kurumu ne koruyor?"},
            {"title": "Gerçek üçüncü seçenek peşinat desteğidir",
             "body": "Eyalet ve şehir programları, bazı işveren düzenlemeleri, mortgage'ın yerini almak yerine peşinata yardım eder. Üçüncü yola en yakın şey budur, kamuya açıktır ve 'ya kira ya satın alma' demeden önce bakmaya değer."},
            {"title": "Şartlardan önce lisansa bak",
             "body": "Bir kredi kuruluşunun kaydı NMLS tüketici erişim kütüğünden doğrulanabilir. Şartlar ne kadar iyi görünürse görünsün, ancak karşı taraf onları sunmaya yetkiliyse bir anlam taşır."},
        ],
        "de": [
            {"title": "Einen Sparpool-Weg gibt es hier nicht",
             "body": "In manchen Ländern führt ein dritter Weg ins Eigenheim: Monat für Monat in einen gemeinsamen Pool einzahlen, warten bis man an der Reihe ist, ohne Zinsen. In den USA gibt es dafür KEINE zugelassene Entsprechung. Die Wege sind Miete, Hypothek oder Barzahlung."},
            {"title": "Begegne jedem ähnlichen Pool mit Misstrauen",
             "body": "Wer ein Eigenheim gegen monatliche Einzahlungen in einen gemeinsamen Pool verspricht und weder Bank noch zugelassener Kreditgeber ist, hat keine Einlagensicherung im Rücken und keine Aufsicht, die Kennzahlen prüft. Das Fehlen einer regulierten Kategorie ist keine Marktlücke, sondern der Grund zur Vorsicht."},
            {"title": "Der Schutz hängt hier am Institut",
             "body": "Die FDIC-Versicherung deckt Einlagen bei einer versicherten Bank bis zur Grenze ab, und zwar für den Fall, dass die BANK scheitert — nicht dafür, dass dein Haus an Wert verliert oder ein Bauträger nicht liefert. Die lohnende Frage ist, welches Institut dein Geld hält und was dieses Institut absichert."},
            {"title": "Die echte dritte Option ist Eigenkapitalhilfe",
             "body": "Programme von Bundesstaaten und Städten, teils auch von Arbeitgebern, helfen beim Eigenkapital, statt die Hypothek zu ersetzen. Das kommt einem dritten Weg am nächsten, ist öffentlich und lohnt einen Blick, bevor man die Wahl auf Miete oder Kauf verengt."},
            {"title": "Prüfe die Zulassung vor den Konditionen",
             "body": "Die Registrierung eines Kreditgebers lässt sich über das NMLS-Verbraucherregister prüfen. Wie gut die Konditionen auch aussehen — sie bedeuten nur etwas, wenn die Gegenseite zugelassen ist, sie anzubieten."},
        ],
    },
}

_FALLBACK_ORDER = ("en", "tr", "de")


def for_market(market: str, lang: str = "tr") -> Optional[list[dict]]:
    by_lang = ROUTES.get((market or "").upper())
    if not by_lang:
        return None
    if lang in by_lang:
        return by_lang[lang]
    for alt in _FALLBACK_ORDER:
        if alt in by_lang:
            return by_lang[alt]
    return next(iter(by_lang.values()), None)


def available_markets() -> set[str]:
    return set(ROUTES)
