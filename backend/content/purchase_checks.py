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
        "en": [
            {"title": "See the title deed with your own eyes",
             "body": "Do not settle for the photocopy the seller shows you. Check the record at the Land Registry or through e-Devlet: who the owner is, whether it is held in shares, and whether there is a mortgage, a lien or an annotation on it."},
            {"title": "Ask the municipality for the zoning status",
             "body": "The most critical step for land. Get the zoning certificate from the municipality: what the parcel may be used for, how many storeys are permitted, whether it falls within a road or green-space expropriation. \"Zoned for building\" means nothing until a document says it."},
            {"title": "Compare the cadastre against the ground",
             "body": "Do the parcel boundaries on the deed match what you see on the land? You can ask the Cadastre Office to stake it out. A neighbour's encroachment becomes your problem the day you buy."},
            {"title": "For a home: building permit and occupancy",
             "body": "Without an occupancy permit the building is not officially habitable; mortgages and utility connections run into trouble. Ask too whether it holds construction servitude or full condominium title."},
            {"title": "Dues, debts and earthquake insurance",
             "body": "Ask the building management IN WRITING whether there are unpaid dues — the debt travels with the property. Compulsory earthquake insurance is required at transfer; find out where the building stands against the seismic code."},
            {"title": "Pay at the land registry",
             "body": "Hand over the money at the same moment as the transfer. Put any deposit in a written contract that states when it is refundable. Declaring the real sale price on the deed is a legal requirement; understating it puts the buyer at risk too."},
            {"title": "Talk to a lawyer",
             "body": "This is educational content, not legal advice. If the amount is the largest you will ever spend, having a property lawyer read the contract before you sign is the cheapest insurance available."},
        ],
        "de": [
            {"title": "Den Grundbucheintrag selbst ansehen",
             "body": "Gib dich nicht mit der Kopie des Verkäufers zufrieden. Prüfe den Eintrag beim Grundbuchamt oder über e-Devlet: wer Eigentümer ist, ob Miteigentumsanteile bestehen und ob Hypotheken, Pfändungen oder Vermerke eingetragen sind."},
            {"title": "Den Bebauungsstatus bei der Gemeinde erfragen",
             "body": "Der wichtigste Schritt bei Grundstücken. Hol dir die Bebauungsbescheinigung: wofür das Grundstück genutzt werden darf, wie viele Geschosse zulässig sind, ob es von einer Enteignung für Straßen oder Grünflächen betroffen ist. \"Bebaubar\" bedeutet nichts ohne Dokument."},
            {"title": "Kataster und Gelände vergleichen",
             "body": "Stimmen die Grenzen im Grundbuch mit dem überein, was du auf dem Grundstück siehst? Du kannst beim Katasteramt eine Einmessung beantragen. Ein Übergriff des Nachbarn wird am Kauftag zu deinem Problem."},
            {"title": "Bei Wohnungen: Baugenehmigung und Abnahme",
             "body": "Ohne Abnahmebescheinigung gilt das Gebäude nicht als offiziell bewohnbar; Kredite und Versorgungsanschlüsse werden schwierig. Frag auch, ob Bauerbbaurecht oder volles Wohnungseigentum begründet wurde."},
            {"title": "Hausgeld, Schulden und Erdbebenversicherung",
             "body": "Lass dir von der Verwaltung SCHRIFTLICH bestätigen, ob Hausgeld offen ist — die Schuld geht mit der Immobilie über. Die Pflicht-Erdbebenversicherung wird bei der Übertragung verlangt; kläre auch den Zustand des Gebäudes nach Erdbebennorm."},
            {"title": "Die Zahlung beim Grundbuchamt leisten",
             "body": "Zahle im selben Moment wie die Übertragung. Halte eine Anzahlung schriftlich fest, samt der Bedingung für eine Rückzahlung. Den tatsächlichen Kaufpreis anzugeben ist gesetzlich vorgeschrieben; ein zu niedriger Wert gefährdet auch die kaufende Seite."},
            {"title": "Eine Anwältin oder einen Anwalt fragen",
             "body": "Das hier ist Bildungsinhalt, keine Rechtsberatung. Wenn es die größte Ausgabe deines Lebens ist, ist ein Blick von einer Immobilienanwältin vor der Unterschrift die günstigste Versicherung."},
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
        "tr": [
            {"title": "Tapu araştırması ve tapu sigortası yaptır",
             "body": "Bir tapu şirketi (title company) satıcının mülkü gerçekten borçsuz sahiplendiğini kontrol eder — hacizler, ödenmemiş vergiler, geçit hakları, kimsenin bahsetmediği bir mirasçı. Tapu sigortası da sonradan çıkan bir sorunu karşılar. Bu standart bir adımdır ve tasarruf edilecek yer değildir."},
            {"title": "İmar durumunu ve izinli kullanımı kontrol et",
             "body": "Arsada en önemli adım. Şehrin veya ilçenin imar ofisini ara: ne inşa edilebilir, çekme mesafeleri neler, asgari parsel büyüklüğü nedir, altyapı oraya getirilebiliyor mu. İlanda \"inşaata uygun\" yazması, ilçe onaylayana kadar satıcının görüşüdür."},
            {"title": "Sınır ölçümü (survey) ısmarla",
             "body": "Sınır ölçümü mülkün gerçekte nerede bittiğini gösterir. Çitler sınır değildir, ve bir tecavüz tapuyu devraldığın gün senin anlaşmazlığın olur."},
            {"title": "Ev incelemesi, ve bölgeye özgü olanlar",
             "body": "Genel bir inceleme, artı bölgenin gerektirdikleri: radon, termit, fosseptik, kuyu suyu, temel. Teklifini bu incelemeye bağla ve özeti değil raporun kendisini oku."},
            {"title": "Sel bölgesi ve sigorta teklifi",
             "body": "Duygusal olarak bağlanmadan önce FEMA sel haritasına bak ve gerçek bir sigorta teklifi al. Ülkenin bazı bölgelerinde satın alınabilirliği belirleyen şey kredi taksiti değil, sigorta primidir."},
            {"title": "Site yönetimi (HOA) belgelerini oku",
             "body": "Bir yönetim birliği varsa: kurallar, aylık aidat, rezerv fonu ve gelmekte olan özel katkı payları. Yetersiz bir rezerv, henüz gönderilmemiş bir faturadır."},
            {"title": "Gelenek olan eyaletlerde avukat kullan",
             "body": "Burası eğitim içeriğidir, hukuki görüş değil. Birçok eyalette sözleşmeyi bir avukatın incelemesi olağan bir adımdır; isteğe bağlı olduğu yerlerde bile satın alma tutarının yanında ucuz kalır."},
        ],
        "de": [
            {"title": "Eigentumsrecherche und Title Insurance",
             "body": "Eine Title Company prüft, ob die verkaufende Seite das Objekt tatsächlich lastenfrei besitzt — Pfandrechte, offene Steuern, Wegerechte, eine Erbin, von der niemand sprach. Die Title Insurance deckt danach, was später auftaucht. Das ist Standard und nicht die Stelle zum Sparen."},
            {"title": "Zoning und zulässige Nutzung prüfen",
             "body": "Der wichtigste Schritt bei Grundstücken. Ruf das Planungsamt der Stadt oder des County an: was gebaut werden darf, Abstandsflächen, Mindestgrundstücksgröße, ob Versorgungsleitungen überhaupt hinführbar sind. \"Bebaubar\" im Inserat ist die Meinung der verkaufenden Seite, bis das County es bestätigt."},
            {"title": "Eine Vermessung beauftragen",
             "body": "Eine Grenzvermessung zeigt, wo das Grundstück wirklich endet. Zäune sind keine Grenzen, und ein Übergriff wird am Tag des Closings zu deinem Streitfall."},
            {"title": "Hausinspektion, und die speziellen",
             "body": "Eine allgemeine Inspektion, dazu was die Region verlangt: Radon, Termiten, Klärgrube, Brunnenwasser, Fundament. Mach das Angebot davon abhängig und lies den Bericht, nicht die Zusammenfassung."},
            {"title": "Überschwemmungszone und Versicherungsangebote",
             "body": "Sieh dir die FEMA-Hochwasserkarte an, bevor du emotional gebunden bist, und hol ein echtes Versicherungsangebot ein. In manchen Landesteilen entscheidet die Prämie über die Leistbarkeit, nicht die Kreditrate."},
            {"title": "Die HOA-Unterlagen lesen",
             "body": "Falls es eine Eigentümergemeinschaft gibt: die Regeln, das monatliche Hausgeld, die Rücklage und jede anstehende Sonderumlage. Eine zu dünne Rücklage ist eine Rechnung, die nur noch nicht verschickt wurde."},
            {"title": "Wo üblich, eine Immobilienanwältin einschalten",
             "body": "Das hier ist Bildungsinhalt, keine Rechtsberatung. In vielen Bundesstaaten prüft eine Anwältin den Vertrag ganz selbstverständlich; wo es optional ist, bleibt es neben dem Kaufpreis trotzdem günstig."},
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
        "tr": [
            {"title": "Tapu kaydını (Grundbuch) kendin incele",
             "body": "Satıcının kopyasıyla yetinme. Güncel bir Grundbuch özeti iste: Bölüm I malikleri, Bölüm II yükleri ve kısıtlamaları (geçit hakkı, oturma hakkı), Bölüm III ipotekleri gösterir. Bölüm II'de yazan her şey satın aldıktan sonra da geçerli kalır."},
            {"title": "İmar planını ve Baulast kaydını gör",
             "body": "İmar dairesinde: arsada ne yapılabilir, ne yükseklikte, ne yoğunlukta? Ayrıca Baulastenverzeichnis'i de sor — Baulast'lar tapu kaydında GÖRÜNMEZ ama yapılaşmayı belirleyici biçimde kısıtlayabilir."},
            {"title": "Daire alıyorsan Teilungserklärung",
             "body": "Neyin sana, neyin kat malikleri birliğine ait olduğunu ve özel kullanım alanlarındaki hakları belirler. Yanında son üç yılın kat malikleri toplantı tutanaklarını da iste: anlaşmazlıklar ve alınacak kararlar orada yazar."},
            {"title": "Bakım rezervi ve aidat (Hausgeld)",
             "body": "Rezerv ne kadar ve ne kadarı şimdiden planlanmış? Yetersiz bir rezerv, henüz karara bağlanmamış bir ek katkı payıdır. Yıllık bütçeyi ve hesap dökümünü iste."},
            {"title": "Enerji belgesi ve tadilat yükümlülükleri",
             "body": "Enerji belgesi (Energieausweis) satışta zorunludur ve istenmeden sunulmalıdır. Malik değişiminde hangi sonradan iyileştirme yükümlülüklerinin doğduğunu — ısıtma, yalıtım — ve maliyetini kontrol et."},
            {"title": "Alım yan maliyetlerini önceden hesapla",
             "body": "Eyalete göre değişen devir vergisi, noter ve tapu sicili, varsa emlakçı komisyonu. Bu toplam kendi özkaynağından çıkmak zorundadır; bankalar genellikle bu kısmı finanse etmez."},
            {"title": "Noter taslağını acele etmeden oku",
             "body": "Burası eğitim içeriğidir, hukuki görüş değil. Taslak, resmî işlemden iki hafta önce elinde olmalıdır — bu süre senin için vardır. Gerekirse kendi avukatınla birlikte kullan."},
        ],
        "en": [
            {"title": "Read the land register entry yourself",
             "body": "Not the seller's copy. Ask for a current Grundbuch extract: Section I shows the owners, Section II encumbrances and restrictions (rights of way, rights of residence), Section III mortgages. Whatever stands in Section II survives the purchase."},
            {"title": "Inspect the development plan and the Baulast register",
             "body": "At the building authority: what may be built on the plot, how high, how dense? Ask separately for the Baulastenverzeichnis — these obligations do NOT appear in the land register and can still decisively limit what you may build."},
            {"title": "For an apartment: the Teilungserklärung",
             "body": "It sets out what belongs to you and what to the owners' association, and what rights exist over exclusive-use areas. With it, ask for the last three years of owners' meeting minutes: the disputes and the coming resolutions are recorded there."},
            {"title": "Maintenance reserve and monthly charges",
             "body": "How large is the reserve and how much of it is already committed? A thin reserve is a special levy that has simply not been voted on yet. Ask for the budget and the annual statement."},
            {"title": "Energy certificate and renovation obligations",
             "body": "The Energieausweis is mandatory on a sale and must be produced without being asked for. Check which retrofit duties are triggered by a change of owner — heating, insulation — and what they cost."},
            {"title": "Work out the purchase costs beforehand",
             "body": "Transfer tax varying by federal state, notary and land registry, and an agent's commission where one applies. That sum has to come from your own capital; banks generally will not finance it."},
            {"title": "Read the notary's draft without hurrying",
             "body": "This is educational content, not legal advice. The draft must be in your hands two weeks before the notarial appointment — that period exists for your benefit. Use it, with your own lawyer if need be."},
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
