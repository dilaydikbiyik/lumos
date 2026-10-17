"""
What a fund actually is, per market — and what its protections do not cover.

Why this exists. In September 2026 the Turkish regulator closed 131 funds
across seven portfolio companies and moved them to liquidation; its own
press release put the number of individual investors at 455,758. The app
had nothing to say about it, because it taught only ONE kind of liquidity —
"how fast can I sell this", stocks in minutes and land in months. That
misses the thing that actually happened: the asset inside was fine and the
money was unreachable, because what froze was the WRAPPER.

The lesson is the same in all three markets and the details are not, which
is exactly why this is market-keyed rather than written once:

  SEPARATION IS REAL. Türkiye, the United States and Germany all require
  fund assets to be held apart from the manager's own, so the manager's
  creditors cannot reach them. This is genuinely strong and worth knowing.

  SEPARATION IS NOT A VALUE GUARANTEE, and it is not same-day access. It
  protects you from the manager's BANKRUPTCY, not from the manager's
  DECISIONS, and a liquidation still takes months during which the money is
  not yours to spend.

  EACH MARKET HAS ITS OWN MISREADING. "The regulator approved it, so my
  money is guaranteed." "It is SIPC insured, so my losses are covered."
  "Sondervermögen, also geschützt." All three are wrong in the same shape
  and wrong about different schemes.

NOT A LIST OF FUNDS TO BUY, deliberately. Naming funds weeks after 131 were
frozen would be the opposite of this app's purpose. Teaching what the
structure does and does not promise is within it; picking funds is not.

Sources are regulator-level concepts rather than figures. Anything numeric
belongs in a release note the reader can check, not in evergreen copy.
"""

from typing import Optional

# market -> lang -> [ {title, body} ]
FUND_FACTS: dict[str, dict[str, list[dict]]] = {
    "TR": {
        "tr": [
            {"title": "Fon parası yöneticinin parası değildir",
             "body": "Sermaye Piyasası Kanunu'na göre fonun varlıkları, onu kuran portföy şirketinin ve saklayıcının malvarlığından ayrıdır: rehnedilemez, haczedilemez, şirketin iflas masasına girmez. Şirket batarsa varlıklar alacaklılarına gitmez."},
            {"title": "Ayrı olmak, değerinin garantisi değildir",
             "body": "Bu ayrım seni yöneticinin BATMASINDAN korur, KARARLARINDAN korumaz. Fon kötü yatırım yaptıysa zarar senindir. Hiçbir kurum anaparanı geri ödeyeceğini taahhüt etmez; \"SPK'ya kayıtlı\" demek \"devlet garantili\" demek değildir."},
            {"title": "En büyük risk paranı o gün alamamaktır",
             "body": "Bir fon işleme kapatılıp tasfiyeye alınırsa, varlıklar yerinde olsa bile sen aylarca paranı çekemezsin. 2026 Eylül'ündeki tasfiyede süre önce üç ay, sonra altı ay olarak belirlendi. Acil ihtiyaç planını fona bağlama."},
            {"title": "Borsada işlem gören fon farklı bir yapıdır",
             "body": "ETF gibi borsada işlem gören fonlarda payını piyasa açıkken bir başkasına satarsın; fonun kendisinden para çekmen gerekmez. Portföy şirketinin yönettiği fonda ise iadeyi fondan istersin — zincirde bir halka daha vardır. İkisi de \"fon\" adını taşır, riskleri aynı değildir."},
            {"title": "Tek kurumda yığılma da bir yoğunlaşmadır",
             "body": "Beş farklı fon almak, hepsi aynı portföy şirketininse çeşitlenme değildir. Varlık türüne göre dağılmak kadar, kurumlara göre dağılmak da önemlidir — ve bu, hiçbir grafikte görünmez."},
        ],
        "en": [
            {"title": "A fund's money is not the manager's money",
             "body": "Under the Capital Markets Law a fund's assets are separate from those of the portfolio company that founded it and of the custodian: they cannot be pledged, attached, or drawn into the company's bankruptcy estate. If the company fails, the assets do not go to its creditors."},
            {"title": "Separate does not mean guaranteed",
             "body": "That separation protects you from the manager GOING UNDER, not from its DECISIONS. If the fund invested badly, the loss is yours. No institution undertakes to return your principal; \"registered with the regulator\" does not mean \"guaranteed by the state\"."},
            {"title": "The real risk is not getting your money that day",
             "body": "If a fund is closed to trading and moved to liquidation, you cannot withdraw for months even though the assets are where they should be. In the September 2026 liquidation the period was first set at three months and then extended to six. Do not tie your emergency plan to a fund."},
            {"title": "An exchange-traded fund is a different structure",
             "body": "With an ETF you sell your share to another buyer while the market is open; you never have to withdraw from the fund itself. With a fund run by a portfolio company you ask the fund to redeem — one more link in the chain. Both are called funds; their risks are not the same."},
            {"title": "Piling into one institution is concentration too",
             "body": "Buying five different funds is not diversification if they all belong to the same portfolio company. Spreading across institutions matters alongside spreading across asset types — and that kind of concentration appears on no chart."},
        ],
        "de": [
            {"title": "Fondsgeld ist nicht das Geld der Gesellschaft",
             "body": "Nach dem türkischen Kapitalmarktgesetz ist das Fondsvermögen vom Vermögen der gründenden Portfoliogesellschaft und der Verwahrstelle getrennt: es kann nicht verpfändet oder gepfändet werden und fällt nicht in die Insolvenzmasse. Geht die Gesellschaft unter, bekommen ihre Gläubiger es nicht."},
            {"title": "Getrennt heißt nicht garantiert",
             "body": "Diese Trennung schützt dich vor dem UNTERGANG des Verwalters, nicht vor seinen ENTSCHEIDUNGEN. Hat der Fonds schlecht investiert, ist der Verlust deiner. Keine Institution sagt zu, dein eingesetztes Kapital zurückzugeben; \"bei der Aufsicht registriert\" heißt nicht \"staatlich garantiert\"."},
            {"title": "Das eigentliche Risiko ist, am Tag X nicht heranzukommen",
             "body": "Wird ein Fonds für den Handel geschlossen und abgewickelt, kommst du monatelang nicht an dein Geld, obwohl die Werte vorhanden sind. Bei der Abwicklung im September 2026 wurde die Frist zunächst auf drei, dann auf sechs Monate gesetzt. Binde deine Notfallplanung nicht an einen Fonds."},
            {"title": "Ein börsengehandelter Fonds ist eine andere Struktur",
             "body": "Beim ETF verkaufst du deinen Anteil während der Handelszeit an einen anderen Käufer; du musst nie aus dem Fonds selbst aussteigen. Beim Fonds einer Portfoliogesellschaft verlangst du die Rücknahme vom Fonds — ein Glied mehr in der Kette. Beide heißen Fonds, ihre Risiken sind es nicht."},
            {"title": "Alles bei einem Haus ist auch Konzentration",
             "body": "Fünf verschiedene Fonds zu kaufen ist keine Streuung, wenn alle derselben Portfoliogesellschaft gehören. Über Institute zu streuen zählt neben dem Streuen über Anlageklassen — und diese Konzentration zeigt kein Chart."},
        ],
    },
    "US": {
        "en": [
            {"title": "The fund's assets are not the manager's assets",
             "body": "A registered fund's holdings sit with an independent custodian, apart from the management company's own balance sheet. If the manager fails, its creditors cannot reach what the fund owns."},
            {"title": "SIPC is not what most people think it is",
             "body": "SIPC covers your BROKERAGE failing with your securities missing — up to $500,000, including $250,000 for cash. It does not reimburse a single dollar of market loss, and it is not a guarantee of the fund. If your fund halves in value, SIPC has nothing to do with it."},
            {"title": "Separation does not mean same-day access",
             "body": "Protection from the manager's creditors is not the same as being able to spend the money this week. A wind-down takes time, and during it the balance is real and unavailable. Keep an emergency plan outside anything that can be suspended."},
            {"title": "An ETF and a mutual fund are different machines",
             "body": "An ETF share is sold to another buyer while the market is open. A mutual fund share is redeemed from the fund itself, priced once a day at the close. The second has one more link in the chain between you and your money. Both are called funds."},
            {"title": "Several funds, one firm, is still concentration",
             "body": "Holding five funds from the same manager is not diversification. Spreading across institutions matters alongside spreading across assets — and that kind of concentration shows up on no chart."},
        ],
        "tr": [
            {"title": "Fonun varlıkları yöneticinin varlıkları değildir",
             "body": "Kayıtlı bir fonun portföyü, yönetim şirketinin bilançosundan ayrı olarak bağımsız bir saklayıcıda durur. Yönetici batarsa alacaklıları fonun sahip olduklarına ulaşamaz."},
            {"title": "SIPC çoğu kişinin sandığı şey değildir",
             "body": "SIPC, ARACI KURUMUN batıp menkul kıymetlerinin kaybolması durumunu karşılar — 500.000 dolara kadar, 250.000 doları nakit için. Piyasa kaynaklı zararın tek kuruşunu ödemez ve fonun garantisi değildir. Fonun değeri yarıya inerse SIPC'nin bununla ilgisi yoktur."},
            {"title": "Ayrı olmak, aynı gün erişim demek değildir",
             "body": "Yöneticinin alacaklılarından korunmak, parayı bu hafta harcayabilmekle aynı şey değildir. Tasfiye zaman alır ve o süre boyunca bakiye gerçektir ama kullanılamaz. Acil durum planını askıya alınabilecek hiçbir şeye bağlama."},
            {"title": "ETF ile yatırım fonu farklı makinelerdir",
             "body": "ETF payını piyasa açıkken başka bir alıcıya satarsın. Yatırım fonu payını ise fonun kendisine iade edersin, günde bir kez kapanışta fiyatlanır. İkincisinde seninle paran arasında bir halka daha vardır. İkisine de fon denir."},
            {"title": "Aynı şirketten birkaç fon, yine yoğunlaşmadır",
             "body": "Aynı yöneticiden beş fon tutmak çeşitlenme değildir. Kurumlara yayılmak, varlıklara yayılmak kadar önemlidir — ve bu tür yoğunlaşma hiçbir grafikte görünmez."},
        ],
        "de": [
            {"title": "Das Fondsvermögen gehört nicht der Gesellschaft",
             "body": "Die Bestände eines registrierten Fonds liegen bei einer unabhängigen Verwahrstelle, getrennt von der Bilanz der Verwaltungsgesellschaft. Scheitert der Verwalter, kommen seine Gläubiger nicht an das, was dem Fonds gehört."},
            {"title": "SIPC ist nicht, wofür die meisten es halten",
             "body": "SIPC greift, wenn DEIN BROKER scheitert und Wertpapiere fehlen — bis 500.000 Dollar, davon 250.000 für Bargeld. Es ersetzt keinen Dollar Kursverlust und ist keine Garantie für den Fonds. Halbiert sich dein Fonds, hat SIPC damit nichts zu tun."},
            {"title": "Getrennt heißt nicht sofort verfügbar",
             "body": "Vor den Gläubigern des Verwalters geschützt zu sein heißt nicht, das Geld diese Woche ausgeben zu können. Eine Abwicklung dauert, und solange ist der Saldo real und unerreichbar. Halte deine Notfallplanung außerhalb von allem, was ausgesetzt werden kann."},
            {"title": "ETF und Investmentfonds sind verschiedene Maschinen",
             "body": "Einen ETF-Anteil verkaufst du während der Handelszeit an einen anderen Käufer. Einen Investmentfondsanteil gibst du an den Fonds zurück, einmal täglich zum Schlusskurs bewertet. Beim zweiten liegt ein Glied mehr zwischen dir und deinem Geld."},
            {"title": "Mehrere Fonds einer Gesellschaft bleiben Konzentration",
             "body": "Fünf Fonds desselben Verwalters sind keine Streuung. Über Institute zu streuen zählt neben dem Streuen über Anlagen — und diese Konzentration zeigt kein Chart."},
        ],
    },
    "DE": {
        "de": [
            {"title": "Ein Fonds ist Sondervermögen",
             "body": "Nach deutschem Recht gehört das Fondsvermögen den Anlegern gemeinsam und ist vom Vermögen der Verwaltungsgesellschaft getrennt. Geht die Gesellschaft insolvent, fällt es nicht in die Masse — eine Verwahrstelle hält es getrennt."},
            {"title": "Getrennt heißt nicht garantiert",
             "body": "Die Trennung schützt dich vor der INSOLVENZ des Verwalters, nicht vor seinen ENTSCHEIDUNGEN. Fällt der Wert, ist der Verlust deiner. Es gibt keine Einlagensicherung für Kursverluste: die gesetzliche Sicherung von 100.000 Euro gilt für Bankeinlagen, nicht für Fondsanteile."},
            {"title": "Getrennt heißt auch nicht sofort verfügbar",
             "body": "Die Rücknahme von Anteilen kann ausgesetzt werden, bei offenen Immobilienfonds zudem mit gesetzlichen Mindesthalte- und Kündigungsfristen. Dein Notgroschen gehört nicht in etwas, das ausgesetzt werden kann."},
            {"title": "ETF und klassischer Fonds sind verschiedene Maschinen",
             "body": "Einen ETF-Anteil verkaufst du während der Börsenzeit an einen anderen Käufer. Einen klassischen Fondsanteil gibst du an die Gesellschaft zurück, zu einem einmal täglich festgestellten Preis. Das ist ein Glied mehr in der Kette zwischen dir und deinem Geld."},
            {"title": "Mehrere Fonds, ein Haus, bleibt Konzentration",
             "body": "Fünf Fonds derselben Gesellschaft sind keine Streuung. Über Institute zu streuen zählt neben dem Streuen über Anlageklassen — und diese Art von Konzentration zeigt kein Chart."},
        ],
        "tr": [
            {"title": "Fon, Sondervermögen'dir",
             "body": "Alman hukukunda fon varlığı yatırımcılara ortaklaşa aittir ve yönetim şirketinin malvarlığından ayrıdır. Şirket iflas ederse bu varlık masaya girmez; bir saklayıcı (Verwahrstelle) onu ayrı tutar."},
            {"title": "Ayrı olmak garanti demek değildir",
             "body": "Ayrım seni yöneticinin İFLASINDAN korur, KARARLARINDAN korumaz. Değer düşerse zarar senindir. Kur kayıpları için mevduat güvencesi yoktur: 100.000 euroluk yasal güvence banka mevduatı içindir, fon payları için değil."},
            {"title": "Ayrı olmak, anında erişilebilir de demek değildir",
             "body": "Payların geri alımı askıya alınabilir; açık uçlu gayrimenkul fonlarında ayrıca yasal asgari tutma ve ihbar süreleri vardır. Acil paran, askıya alınabilecek bir şeyin içinde durmamalı."},
            {"title": "ETF ile klasik fon farklı makinelerdir",
             "body": "ETF payını borsa saatlerinde başka bir alıcıya satarsın. Klasik fon payını ise şirkete iade edersin, günde bir kez belirlenen fiyattan. Bu, seninle paran arasında bir halka daha demektir."},
            {"title": "Birkaç fon, tek kurum — yine yoğunlaşma",
             "body": "Aynı şirketin beş fonu çeşitlenme değildir. Kurumlara yayılmak, varlık sınıflarına yayılmak kadar önemlidir — ve bu tür yoğunlaşmayı hiçbir grafik göstermez."},
        ],
        "en": [
            {"title": "A fund is Sondervermögen — a separate estate",
             "body": "Under German law the fund's assets belong to the investors in common and sit apart from the management company's own estate. If the company becomes insolvent they do not fall into the estate; a depositary holds them separately."},
            {"title": "Separate does not mean guaranteed",
             "body": "The separation protects you from the manager's INSOLVENCY, not from its DECISIONS. If the value falls, the loss is yours. There is no deposit protection for market losses: the statutory 100,000 euro cover applies to bank deposits, not to fund units."},
            {"title": "Separate does not mean available today either",
             "body": "Redemption of units can be suspended, and open-ended property funds additionally carry statutory minimum holding and notice periods. Your emergency money does not belong in anything that can be suspended."},
            {"title": "An ETF and a classic fund are different machines",
             "body": "An ETF unit is sold to another buyer during market hours. A classic fund unit is returned to the company, at a price struck once a day. That is one more link in the chain between you and your money."},
            {"title": "Several funds, one house, is still concentration",
             "body": "Five funds from the same company are not diversification. Spreading across institutions counts alongside spreading across asset classes — and no chart shows this kind of concentration."},
        ],
    },
}

_FALLBACK_ORDER = ("en", "tr", "de")


def for_market(market: str, lang: str = "tr") -> Optional[list[dict]]:
    """The fund facts for this market, in the reader's language."""
    by_lang = FUND_FACTS.get((market or "").upper())
    if not by_lang:
        return None
    if lang in by_lang:
        return by_lang[lang]
    for alt in _FALLBACK_ORDER:
        if alt in by_lang:
            return by_lang[alt]
    return next(iter(by_lang.values()), None)


def available_markets() -> set[str]:
    return set(FUND_FACTS)
