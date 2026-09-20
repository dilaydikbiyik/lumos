"""
What to check before buying property, per market.

MARKET-keyed, not language-keyed. The broker guide taught this the hard way:
it was written for Türkiye and keyed by language, so a German reader in the
German market was told to verify an SPK licence and produce a Turkish
national ID number. A purchase checklist is even less forgiving — these are
the checks that stop somebody buying a plot they cannot build on.

Educational content, not legal advice, and it says so. Every market's list
ends by pointing at a local professional, because none of this replaces one.
"""

from typing import Optional

# market -> lang -> [ {title, body} ]
CHECKS: dict[str, dict[str, list[dict]]] = {
    "TR": {
        "tr": [
            {"title": "Tapuyu kendi gözünle gör",
             "body": "Satıcının gösterdiği fotokopiyle yetinme. Tapu Müdürlüğü'nden ya da e-Devlet üzerinden taşınmazın kaydını kontrol et: malik kim, hisseli mi, üzerinde ipotek, haciz ya da şerh var mı."},
            {"title": "İmar durumunu belediyeden sor",
             "body": "Arsa için en kritik adım. Belediyeden imar durum belgesi al: parsel hangi amaçla kullanılabiliyor, kaç kat izni var, yol/yeşil alan kamulaştırmasına giriyor mu. \"İmarlı\" sözü belgeyle doğrulanmadıkça bir şey ifade etmez."},
            {"title": "Kadastro ile zemini karşılaştır",
             "body": "Tapudaki parsel sınırlarıyla arazide gördüğün sınırlar aynı mı? Kadastro Müdürlüğü'nden aplikasyon (yer gösterme) isteyebilirsin. Komşu tecavüzü satın aldıktan sonra senin sorunun olur."},
            {"title": "Konutta yapı ruhsatı ve iskân",
             "body": "Yapı kullanma izni (iskân) yoksa bina resmen oturulabilir sayılmaz; kredi kullanımı ve abonelikler sorun çıkarır. Kat irtifakı mı kat mülkiyeti mi kurulmuş, bunu da sor."},
            {"title": "Aidat, borç ve DASK",
             "body": "Yönetimden birikmiş aidat borcu olup olmadığını yazılı iste — borç taşınmazla birlikte gelir. DASK (zorunlu deprem sigortası) tapu devrinde aranır; binanın deprem yönetmeliği durumunu da öğren."},
            {"title": "Ödemeyi tapuda yap",
             "body": "Parayı tapu devriyle aynı anda öde. Kapora için yazılı sözleşme yap ve hangi şartta iade edileceğini yaz. Tapu harcını gerçek satış bedeli üzerinden göstermek yasal zorunluluktur; düşük göstermek alıcıyı da riske atar."},
            {"title": "Bir avukata danış",
             "body": "Burası eğitim içeriğidir, hukuki görüş değil. Tutar hayatındaki en büyük harcamaysa, sözleşmeyi imzalamadan önce bir gayrimenkul avukatına okutmak en ucuz sigortadır."},
        ],
    },
    "US": {
        "en": [
            {"title": "Get a title search and title insurance",
             "body": "A title company checks whether the seller actually owns it free and clear — liens, unpaid taxes, easements, an heir nobody mentioned. Title insurance then covers you if something surfaces later. This is standard and it is not the place to save money."},
            {"title": "Check zoning and permitted use",
             "body": "The most important step for land. Call the city or county planning office: what may be built, setbacks, minimum lot size, whether utilities can even be brought to it. A listing that says \"buildable\" is a seller's opinion until the county says it."},
            {"title": "Order a survey",
             "body": "A boundary survey shows where the property actually ends. Fences are not boundaries, and an encroachment becomes your dispute the day you close."},
            {"title": "Home inspection, and the specific ones",
             "body": "A general inspection, plus whatever the region demands: radon, termites, septic, well water, foundation. Make the offer contingent on it, and read the report rather than the summary."},
            {"title": "Flood zone and insurance quotes",
             "body": "Check the FEMA flood map before you are emotionally committed, and get an actual insurance quote. In parts of the country the premium, not the mortgage, is what decides affordability."},
            {"title": "Read the HOA documents",
             "body": "If there is an association: the rules, the monthly dues, the reserve fund and any special assessment coming. An underfunded reserve is a bill that has not been sent yet."},
            {"title": "Use a real estate attorney where it is customary",
             "body": "This is educational content, not legal advice. In many states an attorney reviews the contract as a matter of course; where it is optional it is still cheap next to the purchase."},
        ],
    },
    "DE": {
        "de": [
            {"title": "Grundbuchauszug selbst prüfen",
             "body": "Nicht die Kopie des Verkäufers. Lass dir einen aktuellen Grundbuchauszug geben: Abteilung I zeigt die Eigentümer, Abteilung II Lasten und Beschränkungen (Wegerechte, Wohnrechte), Abteilung III Grundschulden. Was in Abteilung II steht, bleibt nach dem Kauf bestehen."},
            {"title": "Bebauungsplan und Baulast einsehen",
             "body": "Beim Bauamt: Was darf auf dem Grundstück entstehen, wie hoch, wie dicht? Frag zusätzlich das Baulastenverzeichnis ab — Baulasten stehen NICHT im Grundbuch und können die Bebaubarkeit trotzdem entscheidend einschränken."},
            {"title": "Teilungserklärung bei einer Eigentumswohnung",
             "body": "Sie regelt, was dir gehört und was der Gemeinschaft, und welche Rechte an Sondernutzungsflächen bestehen. Dazu die Protokolle der Eigentümerversammlungen der letzten drei Jahre: dort stehen die Streitpunkte und die anstehenden Beschlüsse."},
            {"title": "Instandhaltungsrücklage und Hausgeld",
             "body": "Wie hoch ist die Rücklage und wofür ist sie schon verplant? Eine zu dünne Rücklage ist eine Sonderumlage, die nur noch nicht beschlossen wurde. Lass dir Wirtschaftsplan und Jahresabrechnung geben."},
            {"title": "Energieausweis und Sanierungspflichten",
             "body": "Der Energieausweis ist beim Verkauf Pflicht und muss unaufgefordert vorgelegt werden. Prüfe, welche Nachrüstpflichten beim Eigentümerwechsel greifen — Heizung, Dämmung — und was sie kosten."},
            {"title": "Kaufnebenkosten vorher durchrechnen",
             "body": "Grunderwerbsteuer je nach Bundesland, Notar und Grundbuch, gegebenenfalls Maklerprovision. Diese Summe muss aus Eigenkapital kommen; Banken finanzieren sie in der Regel nicht mit."},
            {"title": "Den Notarentwurf in Ruhe lesen",
             "body": "Das hier ist Bildungsinhalt, keine Rechtsberatung. Der Entwurf muss dir zwei Wochen vor der Beurkundung vorliegen — diese Frist ist für dich da. Nutze sie, notfalls mit einem eigenen Anwalt."},
        ],
    },
}

# Where a market has no list in the reader's language, fall back the way the
# rest of the app does: the market's own language first, then English, then
# whatever exists. A checklist in a language you half-read beats none.
_FALLBACK_ORDER = ("en", "tr", "de")


def for_market(market: str, lang: str = "tr") -> Optional[list[dict]]:
    """The checklist for this market, in the closest available language."""
    by_lang = CHECKS.get((market or "").upper())
    if not by_lang:
        return None
    if lang in by_lang:
        return by_lang[lang]
    for alt in _FALLBACK_ORDER:
        if alt in by_lang:
            return by_lang[alt]
    return next(iter(by_lang.values()), None)


def available_markets() -> set[str]:
    return set(CHECKS)
