"""
Gold is already in every portfolio this app builds — and it is not one thing.

GLD in Türkiye and the US, 4GLD.DE in Germany. The app recommends it,
values it and charts it, and has never said what a reader is actually
holding when they hold it. In Türkiye especially, most people's gold is not
the thing the app recommends: it is metal in a drawer, or a number in a bank
app, and those have different failure modes from each other and from a fund.

The series this belongs to: separation is real, separation is not a value
guarantee, and the failure mode is usually about ACCESS or ENTITLEMENT
rather than the money vanishing. Gold adds a fourth variation that the fund
lesson does not cover — in Europe most gold products are NOT funds at all.
They are debt securities of an issuer, which means the protection a reader
has learned to expect from a fund simply does not apply.

Deliberately absent: spreads, premiums, tax rates and purity figures. They
move, they differ by dealer and by year, and evergreen copy carrying one
goes quietly wrong. The reader is told what to ASK, not what the answer is.

No product or dealer is named. A test enforces it, as with the other
catalogues.
"""

from typing import Optional

GOLD: dict[str, dict[str, list[dict]]] = {
    "TR": {
        "tr": [
            {"title": "Elindeki altın mı, altın alacağın mı?",
             "body": "Fiziksel altında karşı taraf yoktur — kimse batsa da o senin elindedir. Banka altın hesabında ise metal değil, bankadan bir ALACAĞIN vardır. ETF'te ise bir fonun payını tutarsın. Üçü de 'altın' diye anılır; biri kasandaki, ikisi bir kurumun vaadi."},
            {"title": "Fizikselin bedeli makastır, riski saklamadır",
             "body": "Kuyumcu alışta ve satışta farklı fiyat verir; aradaki fark ve ziynette işçilik, daha ilk günden senden çıkar. Karşılığında taşıdığın risk hırsızlık ve kayıptır, bir kurumun batması değil. Hangi riski tercih ettiğini bilerek seç."},
            {"title": "Banka altın hesabında soru 'fiziken var mı' değildir",
             "body": "Sorulacak soru şudur: sözleşme sana fiziki teslim hakkı veriyor mu, yoksa yalnızca TL karşılığı ödeme mi? İkisi aynı şey değildir ve bu, hesap açarken sorulup öğrenilecek bir şeydir."},
            {"title": "ETF'te fon dersinin tamamı geçerlidir",
             "body": "Borsada işlem gören altın fonu bir fondur: varlık yöneticiden ayrıdır, ama bu değerin garantisi değildir ve tasfiye hâlinde erişim anında olmaz. Fonlar için öğrendiğin her şey burada da geçerli."},
        ],
        "en": [
            {"title": "Is it gold, or a claim to gold?",
             "body": "Physical gold has no counterparty — nobody failing takes it out of your safe. A Turkish bank gold account gives you a CLAIM on the bank, not metal. An ETF gives you a fund share. All three are called gold; one is in your drawer, two are an institution's promise."},
            {"title": "Physical costs you the spread and risks storage",
             "body": "A jeweller buys lower than it sells, and that gap — plus the workmanship charge on jewellery — leaves you on day one. What you carry in exchange is theft and loss rather than an institution failing. Choose which risk you prefer knowingly."},
            {"title": "The question on a bank gold account is not 'is the metal there'",
             "body": "The question is whether the contract gives you a right to physical delivery, or only a payment in lira. Those are not the same thing, and it is something to ask and settle when you open the account."},
            {"title": "For an ETF the whole fund lesson applies",
             "body": "An exchange-traded gold fund is a fund: its assets sit apart from the manager's, but that is not a guarantee of value, and in a wind-down access is not immediate. Everything you learned about funds holds here."},
        ],
        "de": [
            {"title": "Gold oder nur ein Anspruch auf Gold?",
             "body": "Physisches Gold hat keine Gegenpartei — keine Insolvenz holt es aus deinem Safe. Ein türkisches Bank-Goldkonto gibt dir eine FORDERUNG gegen die Bank, kein Metall. Ein ETF gibt dir einen Fondsanteil. Alle drei heißen Gold; eines liegt bei dir, zwei sind das Versprechen eines Hauses."},
            {"title": "Physisch kostet den Spread und riskiert die Lagerung",
             "body": "Der Juwelier kauft günstiger, als er verkauft; diese Spanne und bei Schmuck der Arbeitslohn verlassen dich am ersten Tag. Dafür trägst du Diebstahl und Verlust statt der Insolvenz eines Instituts. Entscheide wissentlich, welches Risiko dir lieber ist."},
            {"title": "Beim Bank-Goldkonto ist die Frage nicht, ob das Metall da ist",
             "body": "Die Frage ist, ob der Vertrag dir einen Anspruch auf physische Lieferung gibt oder nur eine Zahlung in Lira. Das ist nicht dasselbe, und es gehört bei der Kontoeröffnung geklärt."},
            {"title": "Beim ETF gilt die Fondslektion vollständig",
             "body": "Ein börsengehandelter Goldfonds ist ein Fonds: sein Vermögen liegt getrennt vom Verwalter, aber das garantiert keinen Wert, und bei einer Abwicklung ist der Zugang nicht sofort da. Alles, was du über Fonds gelernt hast, gilt auch hier."},
        ],
    },
    "US": {
        "en": [
            {"title": "Metal, a fund, or a promise — three different things",
             "body": "Physical gold has no counterparty: nobody failing takes it from your safe. A gold ETF is a fund — the fund lesson applies in full. A gold 'account' or certificate is somebody's promise to you, and the question is whose."},
            {"title": "Physical costs you the spread and risks storage",
             "body": "A dealer buys lower than it sells, and the gap plus any premium leaves you on day one. What you carry in exchange is theft and loss rather than an institution failing. Choose which risk you prefer knowingly."},
            {"title": "Watch for anything calling itself a gold retirement account",
             "body": "Aggressive marketing clusters around moving retirement savings into physical gold, with fees that are difficult to see and custodians that are difficult to check. The product may be legitimate; the sales pressure is the signal, and the custodian is the thing to verify."},
            {"title": "A gold ETF is still a fund",
             "body": "Its assets sit apart from the manager's, which protects you from the manager's creditors — not from the gold price and not from a wind-down taking time. Everything true of funds is true here."},
        ],
        "tr": [
            {"title": "Metal, fon ya da bir vaat — üç ayrı şey",
             "body": "Fiziksel altında karşı taraf yoktur: kimse batsa da kasandaki altın senin kalır. Altın ETF'i bir fondur — fon dersinin tamamı geçerlidir. 'Altın hesabı' ya da sertifika ise birinin sana verdiği bir vaattir ve asıl soru, o birinin kim olduğudur."},
            {"title": "Fizikselin bedeli makastır, riski saklamadır",
             "body": "Satıcı aldığından pahalıya satar; aradaki fark ve varsa prim, ilk günden senden çıkar. Karşılığında taşıdığın risk hırsızlık ve kayıptır, bir kurumun batması değil. Hangi riski seçtiğini bilerek seç."},
            {"title": "Kendini 'altın emeklilik hesabı' diye tanıtan şeylere dikkat",
             "body": "Agresif pazarlama, emeklilik birikimini fiziksel altına taşıma etrafında kümelenir; ücretleri görmek zor, saklayan kurumu doğrulamak daha zordur. Ürün meşru olabilir; sinyal satış baskısıdır ve doğrulanacak şey saklayan kurumdur."},
            {"title": "Altın ETF'i yine bir fondur",
             "body": "Varlıkları yöneticinin varlıklarından ayrıdır; bu seni yöneticinin alacaklılarından korur — altın fiyatından ve tasfiyenin zaman almasından korumaz. Fonlar için doğru olan her şey burada da doğrudur."},
        ],
        "de": [
            {"title": "Metall, Fonds oder Versprechen — drei verschiedene Dinge",
             "body": "Physisches Gold hat keine Gegenpartei: keine Insolvenz nimmt es aus deinem Safe. Ein Gold-ETF ist ein Fonds — die Fondslektion gilt vollständig. Ein 'Goldkonto' oder ein Zertifikat ist das Versprechen von jemandem, und die Frage ist, von wem."},
            {"title": "Physisch kostet den Spread und riskiert die Lagerung",
             "body": "Ein Händler kauft günstiger, als er verkauft, und diese Spanne samt Aufschlag verlässt dich am ersten Tag. Dafür trägst du Diebstahl und Verlust statt der Insolvenz eines Hauses. Entscheide wissentlich, welches Risiko dir lieber ist."},
            {"title": "Achte auf alles, was sich Gold-Rentenkonto nennt",
             "body": "Aggressives Marketing sammelt sich dort, wo Altersvorsorge in physisches Gold überführt wird — mit schwer sichtbaren Gebühren und schwer prüfbaren Verwahrstellen. Das Produkt kann seriös sein; das Signal ist der Verkaufsdruck, und zu prüfen ist die Verwahrstelle."},
            {"title": "Ein Gold-ETF bleibt ein Fonds",
             "body": "Sein Vermögen liegt getrennt vom Verwalter, was dich vor dessen Gläubigern schützt — nicht vor dem Goldpreis und nicht davor, dass eine Abwicklung Zeit braucht. Alles, was für Fonds gilt, gilt hier."},
        ],
    },
    "DE": {
        "de": [
            {"title": "Barren, Fonds oder Schuldverschreibung — drei Dinge",
             "body": "Physisches Gold hat keine Gegenpartei. Ein Goldfonds ist ein Fonds. Und das in Europa verbreitetste Goldprodukt ist weder das eine noch das andere: ein ETC, also eine Schuldverschreibung des Emittenten."},
            {"title": "Ein Gold-ETC ist KEIN Sondervermögen",
             "body": "Das ist der Unterschied, der zählt. Ein ETC ist rechtlich eine Schuldverschreibung, kein Fondsanteil — du trägst das Insolvenzrisiko des Emittenten, und der Schutz, den du von Fonds kennst, greift hier nicht. Ob und wie das hinterlegte Gold im Insolvenzfall behandelt wird, steht im Prospekt und nirgendwo sonst."},
            {"title": "Physisch kostet den Spread und riskiert die Lagerung",
             "body": "Der Händler kauft günstiger, als er verkauft; die Spanne verlässt dich am ersten Tag. Dafür trägst du Diebstahl und Verlust statt der Insolvenz eines Hauses. Entscheide wissentlich, welches Risiko dir lieber ist."},
            {"title": "Lies im Prospekt nach, was du wirklich hältst",
             "body": "Bei einem Goldprodukt sind drei Fragen entscheidend: Fonds oder Schuldverschreibung, besteht ein Lieferanspruch, und wer ist der Emittent. Marketingunterlagen beantworten keine davon verbindlich."},
        ],
        "tr": [
            {"title": "Külçe, fon ya da borçlanma aracı — üç ayrı şey",
             "body": "Fiziksel altında karşı taraf yoktur. Altın fonu bir fondur. Avrupa'da en yaygın altın ürünü ise ikisi de değildir: bir ETC, yani ihraççının borçlanma aracı."},
            {"title": "Altın ETC'si bir fon DEĞİLDİR",
             "body": "Önemli olan fark budur. ETC hukuken bir borçlanma aracıdır, fon payı değil — ihraççının batma riskini sen taşırsın ve fonlardan bildiğin koruma burada devreye girmez. Teminat altının iflas hâlinde nasıl işlem göreceği yalnızca izahnamede yazar, başka hiçbir yerde."},
            {"title": "Fizikselin bedeli makastır, riski saklamadır",
             "body": "Satıcı aldığından pahalıya satar; aradaki fark ilk günden senden çıkar. Karşılığında bir kurumun batması yerine hırsızlık ve kayıp riski taşırsın. Hangi riski tercih ettiğini bilerek seç."},
            {"title": "Ne tuttuğunu izahnameden oku",
             "body": "Bir altın ürününde üç soru belirleyicidir: fon mu borçlanma aracı mı, teslim hakkı var mı, ihraççı kim. Tanıtım belgeleri bunların hiçbirini bağlayıcı biçimde yanıtlamaz."},
        ],
        "en": [
            {"title": "Bullion, a fund, or a debt security — three things",
             "body": "Physical gold has no counterparty. A gold fund is a fund. And the most common gold product in Europe is neither: an ETC, which is a debt security of its issuer."},
            {"title": "A gold ETC is NOT a segregated fund",
             "body": "This is the difference that matters. An ETC is legally a debt security, not a fund share — you carry the issuer's insolvency risk, and the protection you know from funds does not apply. How the backing gold is treated in an insolvency is written in the prospectus and nowhere else."},
            {"title": "Physical costs you the spread and risks storage",
             "body": "A dealer buys lower than it sells, and that gap leaves you on day one. What you carry in exchange is theft and loss rather than an institution failing. Choose which risk you prefer knowingly."},
            {"title": "Read the prospectus for what you actually hold",
             "body": "Three questions decide a gold product: fund or debt security, is there a right to delivery, and who is the issuer. Marketing material answers none of them bindingly."},
        ],
    },
}

_FALLBACK_ORDER = ("en", "tr", "de")


def for_market(market: str, lang: str = "tr") -> Optional[list[dict]]:
    by_lang = GOLD.get((market or "").upper())
    if not by_lang:
        return None
    if lang in by_lang:
        return by_lang[lang]
    for alt in _FALLBACK_ORDER:
        if alt in by_lang:
            return by_lang[alt]
    return next(iter(by_lang.values()), None)


def available_markets() -> set[str]:
    return set(GOLD)
