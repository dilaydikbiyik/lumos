"""
Backend copy catalogue.

The engines write sentences, not just numbers: "your loss tolerance carried
the most weight", "cash is the safety cushion", "the biggest drift is on the
gold side". Those sentences were Turkish literals, so a reader who picked
English still met Turkish the moment the backend spoke — the UI translation
only ever covered half the screen.

Keys live here, one catalogue, three languages. `t()` falls back the same way
the frontend does: de → en → tr, so a key added in Turkish only is readable
rather than missing.
"""

from typing import Any

FALLBACK = {"de": ("en", "tr"), "en": ("tr",), "tr": ()}

_C: dict[str, dict[str, str]] = {
    # ── risk engine: labels ──
    "risk.label.conservative": {
        "tr": "Muhafazakâr", "en": "Conservative", "de": "Konservativ"},
    "risk.label.balanced": {
        "tr": "Dengeli", "en": "Balanced", "de": "Ausgewogen"},
    "risk.label.growth": {
        "tr": "Büyüme Odaklı", "en": "Growth-Focused", "de": "Wachstumsorientiert"},
    "risk.label.aggressive": {
        "tr": "Atılgan", "en": "Aggressive", "de": "Offensiv"},

    # ── risk engine: answer labels ──
    "risk.time_horizon.short": {
        "tr": "Kısa (<2 yıl)", "en": "Short (<2 years)", "de": "Kurz (<2 Jahre)"},
    "risk.time_horizon.medium": {
        "tr": "Orta (2-10 yıl)", "en": "Medium (2-10 years)", "de": "Mittel (2-10 Jahre)"},
    "risk.time_horizon.long": {
        "tr": "Uzun (10+ yıl)", "en": "Long (10+ years)", "de": "Lang (10+ Jahre)"},
    "risk.loss_tolerance.low": {
        "tr": "Düşüşte satarım", "en": "I'd sell in a drop", "de": "Im Rückgang verkaufe ich"},
    "risk.loss_tolerance.medium": {
        "tr": "Bekler, tutarım", "en": "I'd wait and hold", "de": "Ich warte ab und halte"},
    "risk.loss_tolerance.high": {
        "tr": "Düşüşte alırım", "en": "I'd buy the drop", "de": "Im Rückgang kaufe ich"},
    "risk.goal.preservation": {
        "tr": "Koruma", "en": "Preservation", "de": "Werterhalt"},
    "risk.goal.income": {
        "tr": "Düzenli gelir", "en": "Regular income", "de": "Regelmäßiges Einkommen"},
    "risk.goal.growth": {
        "tr": "Büyüme", "en": "Growth", "de": "Wachstum"},
    "risk.goal.speculation": {
        "tr": "Spekülasyon", "en": "Speculation", "de": "Spekulation"},
    "risk.experience.none": {
        "tr": "Hiç yok", "en": "None at all", "de": "Gar keine"},
    "risk.experience.beginner": {
        "tr": "Yeni başlayan", "en": "Beginner", "de": "Anfänger"},
    "risk.experience.intermediate": {
        "tr": "Orta", "en": "Intermediate", "de": "Fortgeschritten"},
    "risk.experience.advanced": {
        "tr": "İleri", "en": "Advanced", "de": "Erfahren"},

    # ── risk engine: factor names and explanations ──
    "risk.factor.time_horizon": {
        "tr": "Yatırım vaden", "en": "Your time horizon", "de": "Dein Anlagehorizont"},
    "risk.factor.loss_tolerance": {
        "tr": "Kayıp toleransın", "en": "Your loss tolerance", "de": "Deine Verlusttoleranz"},
    "risk.factor.goal": {
        "tr": "Hedefin", "en": "Your goal", "de": "Dein Ziel"},
    "risk.factor.experience": {
        "tr": "Deneyimin", "en": "Your experience", "de": "Deine Erfahrung"},
    "risk.factor.weighted": {
        "tr": "{name} (ağırlık %{pct})",
        "en": "{name} (weight {pct}%)",
        "de": "{name} (Gewicht {pct}%)"},
    "risk.why.time_horizon": {
        "tr": "Vade uzadıkça kısa vadeli dalgalanmaların önemi azalır — en belirleyici faktör budur",
        "en": "The longer the horizon, the less short-term swings matter — this is the most decisive factor",
        "de": "Je länger der Horizont, desto weniger zählen kurzfristige Schwankungen — der entscheidendste Faktor"},
    "risk.why.loss_tolerance": {
        "tr": "Düşüş anındaki gerçek davranışın, teoriden daha önemlidir — en yüksek ağırlık bunda",
        "en": "How you actually behave in a drop matters more than theory — this carries the highest weight",
        "de": "Wie du dich im Rückgang wirklich verhältst, zählt mehr als die Theorie — höchstes Gewicht"},
    "risk.why.goal": {
        "tr": "Hedefin, kabul etmen gereken risk seviyesini belirler",
        "en": "Your goal sets the level of risk you need to accept",
        "de": "Dein Ziel bestimmt, welches Risiko du eingehen musst"},
    "risk.why.experience": {
        "tr": "Deneyim, dalgalanmayı tanımayı ve panik yapmamayı kolaylaştırır",
        "en": "Experience makes swings recognisable and panic less likely",
        "de": "Erfahrung macht Schwankungen vertraut und Panik unwahrscheinlicher"},

    # ── risk engine: modifiers ──
    "risk.mod.age": {
        "tr": "Yaş düzeltmesi", "en": "Age adjustment", "de": "Altersanpassung"},
    "risk.mod.age.answer": {
        "tr": "{age} yaş", "en": "age {age}", "de": "{age} Jahre"},
    "risk.mod.age.older": {
        "tr": "55+ yaşta koruma önceliği artar",
        "en": "At 55+, preserving capital takes priority",
        "de": "Ab 55 gewinnt der Kapitalerhalt an Priorität"},
    "risk.mod.age.younger": {
        "tr": "30 yaş altı: uzun toparlanma süresi risk kapasitesini artırır",
        "en": "Under 30: a long runway to recover raises risk capacity",
        "de": "Unter 30: viel Zeit zur Erholung erhöht die Risikotragfähigkeit"},
    "risk.mod.income": {
        "tr": "Gelir istikrarı düzeltmesi",
        "en": "Income stability adjustment",
        "de": "Anpassung für Einkommensstabilität"},
    "risk.mod.income.variable": {
        "tr": "Değişken gelir", "en": "Variable income", "de": "Schwankendes Einkommen"},
    "risk.mod.income.irregular": {
        "tr": "Düzensiz gelir", "en": "Irregular income", "de": "Unregelmäßiges Einkommen"},
    "risk.mod.income.why": {
        "tr": "Öngörülemeyen gelir daha büyük güvenlik payı gerektirir — skor aşağı çekilir",
        "en": "Unpredictable income calls for a bigger safety margin — the score is pulled down",
        "de": "Unvorhersehbares Einkommen verlangt mehr Sicherheitspuffer — der Wert sinkt"},

    # ── risk engine: summary ──
    "risk.summary": {
        "tr": "Risk skoru {score}/10 ({label}). {horizon} yatırım ufku, \"{tolerance}\" kayıp toleransı ve {goal} hedefi temel alındı.{note}",
        "en": "Risk score {score}/10 ({label}). Based on a {horizon} horizon, a \"{tolerance}\" loss tolerance and a {goal} goal.{note}",
        "de": "Risikowert {score}/10 ({label}). Grundlage: Horizont {horizon}, Verlusttoleranz \"{tolerance}\" und das Ziel {goal}.{note}"},
    "risk.note.older": {
        "tr": " Yaşın göz önünde bulunduruldu — koruma ağırlığı artırıldı.",
        "en": " Your age was taken into account — the weight on preservation was raised.",
        "de": " Dein Alter wurde berücksichtigt — der Werterhalt wurde stärker gewichtet."},
    "risk.note.younger": {
        "tr": " Genç yaşın uzun bir yatırım ufku sağlıyor — hafifçe yukarı güncellendi.",
        "en": " Being young gives you a long horizon — nudged slightly upward.",
        "de": " Dein junges Alter verschafft dir einen langen Horizont — leicht nach oben angepasst."},
    "risk.note.irregular": {
        "tr": " Düzensiz geliriniz risk kapasiteni sınırlıyor.",
        "en": " Your irregular income limits your risk capacity.",
        "de": " Dein unregelmäßiges Einkommen begrenzt deine Risikotragfähigkeit."},
    "risk.note.variable": {
        "tr": " Değişken geliriniz hafifçe dikkate alındı.",
        "en": " Your variable income was taken into account slightly.",
        "de": " Dein schwankendes Einkommen wurde leicht berücksichtigt."},

    # ── portfolio engine: asset names and roles ──
    "asset.cash.name": {
        "tr": "Nakit / Kısa Vade", "en": "Cash / Short Term", "de": "Bargeld / Kurzfristig"},
    "asset.bond.name": {
        "tr": "Tahvil Fonu (geniş tabanlı)",
        "en": "Bond Fund (broad-based)",
        "de": "Anleihenfonds (breit gestreut)"},
    "role.stocks": {
        "tr": "büyüme motoru — uzun vadeli getiri buradan gelir",
        "en": "the growth engine — long-run returns come from here",
        "de": "der Wachstumsmotor — hier entsteht die langfristige Rendite"},
    "role.gold": {
        "tr": "dengeleyici — hisseler düşerken genellikle farklı davranır, portföyü yumuşatır",
        "en": "the counterweight — it usually moves differently when stocks fall, softening the portfolio",
        "de": "das Gegengewicht — bei fallenden Aktien bewegt es sich meist anders und dämpft das Portfolio"},
    "role.reit": {
        "tr": "gayrimenkul penceresi — mülk almadan emlak getirisine ortaklık",
        "en": "your window on real estate — a share of property returns without buying property",
        "de": "dein Fenster zu Immobilien — Anteil an Immobilienerträgen ohne Immobilienkauf"},
    "role.bond": {
        "tr": "sabit getirili tampon — hisse dalgalanmasını yumuşatır, düzenli faiz üretir",
        "en": "the fixed-income buffer — it dampens equity swings and pays regular interest",
        "de": "der Zinspuffer — er dämpft Aktienschwankungen und zahlt regelmäßig Zinsen"},
    "role.cash": {
        "tr": "güvenlik yastığı — düşüşte değer kaybetmez, fırsat ve acil durum likiditesi",
        "en": "the safety cushion — it doesn't fall in a drop, and it's your liquidity for opportunities and emergencies",
        "de": "das Sicherheitspolster — es fällt im Rückgang nicht und ist Liquidität für Chancen und Notfälle"},
    "role.fund": {
        "tr": "hazır sepet — tek kalemde çeşitlendirme",
        "en": "a ready-made basket — diversification in a single line",
        "de": "ein fertiger Korb — Streuung in einer einzigen Position"},
    "role.default": {
        "tr": "çeşitlendirici", "en": "a diversifier", "de": "ein Streuungsbaustein"},

    # ── portfolio engine: weight rationale ──
    "weight.tilt.cautious": {
        "tr": "profilin temkinli olduğu için düşük oynaklık (%{vol}) ağırlığı artırdı",
        "en": "your profile is cautious, so low volatility ({vol}%) raised the weight",
        "de": "dein Profil ist vorsichtig, daher erhöhte die niedrige Volatilität ({vol}%) das Gewicht"},
    "weight.tilt.bold": {
        "tr": "yüksek risk iştahın oynaklığı (%{vol}) getiri motoruna çevirdi",
        "en": "your high risk appetite turned volatility ({vol}%) into a return engine",
        "de": "deine hohe Risikobereitschaft macht die Volatilität ({vol}%) zum Renditemotor"},
    "weight.tilt.balanced": {
        "tr": "dengeli profilinde %{vol} oynaklık orta ağırlık aldı",
        "en": "in your balanced profile, {vol}% volatility earned a middling weight",
        "de": "in deinem ausgewogenen Profil erhielt {vol}% Volatilität ein mittleres Gewicht"},
    "weight.growth": {
        "tr": "Rolü: {role}. Ağırlığın gerekçesi: {tilt} → %{pct}.",
        "en": "Its role: {role}. Why this weight: {tilt} → {pct}%.",
        "de": "Seine Rolle: {role}. Warum dieses Gewicht: {tilt} → {pct}%."},
    "weight.defensive": {
        "tr": "Rolü: {role}. Ağırlığın gerekçesi: risk profilin portföyün ~%{defensive}'ünü savunmaya (nakit/tahvil) ayırmayı gerektiriyor → %{pct}.",
        "en": "Its role: {role}. Why this weight: your risk profile calls for roughly {defensive}% of the portfolio to sit on the defensive side (cash/bonds) → {pct}%.",
        "de": "Seine Rolle: {role}. Warum dieses Gewicht: dein Risikoprofil verlangt rund {defensive}% des Portfolios auf der defensiven Seite (Bargeld/Anleihen) → {pct}%."},

    # ── portfolio engine: why an asset was dropped ──
    "drop.same_category": {
        "tr": "Aynı kategoriden ({category}) bir varlık zaten seçildi — aynı şeyi izleyen iki fonu birlikte tutmak çeşitlendirme görüntüsü verir ama riski azaltmaz",
        "en": "An asset from the same category ({category}) was already picked — holding two funds that track the same thing looks like diversification but doesn't reduce risk",
        "de": "Aus derselben Kategorie ({category}) wurde bereits eine Anlage gewählt — zwei Fonds auf dasselbe zu halten sieht nach Streuung aus, senkt das Risiko aber nicht"},
    "drop.position_cap": {
        "tr": "{budget} bütçe için azami {cap} pozisyon hedeflendi — küçük bütçeyi çok parçaya bölmek pratik değil",
        "en": "At most {cap} positions were targeted for a {budget} budget — splitting a small budget into many pieces isn't practical",
        "de": "Für ein Budget von {budget} wurden höchstens {cap} Positionen angestrebt — ein kleines Budget in viele Teile zu zerlegen ist unpraktisch"},
    "drop.crumb": {
        "tr": "%{min} altı kırıntı pozisyon — takip yükü ve işlem maliyeti katkısını aşar",
        "en": "A crumb position under {min}% — the tracking effort and trading costs exceed what it contributes",
        "de": "Eine Krümelposition unter {min}% — Aufwand und Handelskosten übersteigen ihren Beitrag"},

    # ── portfolio engine: the formula ──
    "formula.allocation": {
        "tr": "Güvenli pay = 60 − (5,5 × risk skoru), en az %0 en fazla %60 (nakit + tahvil). Kalan pay büyüme varlıklarına dağıtılır: her varlığın ağırlığı = (1 − α) × (1 / oynaklık) + α × oynaklık. α risk skorunun onda biridir; yani α büyüdükçe oynak varlıklar daha fazla, küçüldükçe sakin varlıklar daha fazla pay alır.",
        "en": "Defensive share = 60 − (5.5 × risk score), floored at 0% and capped at 60% (cash + bonds). What's left is spread across the growth assets: each weight = (1 − α) × (1 / volatility) + α × volatility. α is one tenth of the risk score — so the larger α gets, the more the volatile assets take, and the smaller it gets, the more the calm ones do.",
        "de": "Defensiver Anteil = 60 − (5,5 × Risikowert), mindestens 0% und höchstens 60% (Bargeld + Anleihen). Der Rest verteilt sich auf die Wachstumsanlagen: Gewicht je Anlage = (1 − α) × (1 / Volatilität) + α × Volatilität. α ist ein Zehntel des Risikowerts — je größer α, desto mehr erhalten die schwankungsreichen Anlagen, je kleiner, desto mehr die ruhigen."},

    # ── health score ──
    "health.none": {
        "tr": "Henüz varlığın yok — ilk ışığı birlikte yakalım.",
        "en": "No holdings yet — let's light the first one together.",
        "de": "Noch keine Anlagen — zünden wir das erste Licht gemeinsam an."},
    "health.concentrated": {
        "tr": "Servetin büyük ölçüde tek varlık tipinde toplanmış — çeşitlendirme, tek bir kötü gün senaryosunun etkisini azaltır.",
        "en": "Your wealth sits largely in a single asset type — diversifying softens the impact of any one bad day.",
        "de": "Dein Vermögen steckt größtenteils in einer einzigen Anlageart — Streuung dämpft die Wirkung eines schlechten Tages."},
    "health.illiquid": {
        "tr": "Varlıklarının ~%{pct}'i hızla nakde dönmez (arsa/ev/araç). Acil bir ihtiyaç planın var mı?",
        "en": "About {pct}% of your holdings can't be turned into cash quickly (land/home/vehicle). Do you have a plan for an emergency?",
        "de": "Rund {pct}% deiner Anlagen lassen sich nicht schnell zu Geld machen (Grundstück/Haus/Fahrzeug). Hast du einen Plan für den Notfall?"},
    "health.balanced": {
        "tr": "Dengeli görünüyor — fenerin gür yanıyor. 🔦",
        "en": "This looks balanced — your lantern is burning bright. 🔦",
        "de": "Das wirkt ausgewogen — deine Laterne brennt hell. 🔦"},

    # ── drift ──
    "drift.none": {
        "tr": "Henüz takip ettiğin bir varlık yok.",
        "en": "You're not tracking any holdings yet.",
        "de": "Du verfolgst noch keine Anlagen."},
    "drift.ok": {
        "tr": "Portföyün hedefine yakın duruyor. Şu an bir şey yapman gerekmiyor — dengeleme işlem masrafı ve vergi doğurur, gereksizken yapılmaz.",
        "en": "Your portfolio is close to its target. Nothing to do right now — rebalancing costs fees and tax, so it isn't done when it isn't needed.",
        "de": "Dein Portfolio liegt nahe am Ziel. Gerade ist nichts zu tun — Umschichten kostet Gebühren und Steuern und unterbleibt, wenn es nicht nötig ist."},
    "drift.grew": {"tr": "büyüdü", "en": "grown", "de": "gewachsen"},
    "drift.shrank": {"tr": "küçüldü", "en": "shrunk", "de": "geschrumpft"},
    "drift.biggest": {
        "tr": "En büyük sapma {label} tarafında: hedefin %{target} iken şu an %{actual} — bu taraf {direction}. ",
        "en": "The biggest drift is on the {label} side: your target is {target}% and it now sits at {actual}% — that side has {direction}. ",
        "de": "Die größte Abweichung liegt bei {label}: dein Ziel sind {target}%, aktuell sind es {actual}% — diese Seite ist {direction}. "},
    "drift.serious": {
        "tr": "Bu, risk profilinin öngördüğünden belirgin bir sapma; yeni katkılarını geride kalan tarafa yönlendirmek, satmadan dengelemenin en ucuz yoludur.",
        "en": "That's a clear departure from what your risk profile called for; steering new contributions toward the lagging side is the cheapest way to rebalance without selling.",
        "de": "Das weicht deutlich von deinem Risikoprofil ab; neue Beiträge auf die zurückgebliebene Seite zu lenken ist der günstigste Weg, ohne Verkauf auszugleichen."},
    "drift.mild": {
        "tr": "Henüz küçük bir sapma; acele etmene gerek yok, bir sonraki katkında dengeleyebilirsin.",
        "en": "It's still a small drift; no need to rush — you can even it out with your next contribution.",
        "de": "Noch eine kleine Abweichung; keine Eile — du kannst sie mit deinem nächsten Beitrag ausgleichen."},
    "drift.disclaimer": {
        "tr": "Dengeleme bir zorunluluk değil, bir tercihtir. Satış vergi ve masraf doğurabilir; çoğu durumda yeni alımları geride kalan tarafa yönlendirmek yeterlidir. Lumos senin adına işlem yapmaz.",
        "en": "Rebalancing is a choice, not an obligation. Selling can trigger tax and fees; in most cases steering new purchases toward the lagging side is enough. Lumos never trades on your behalf.",
        "de": "Umschichten ist eine Wahl, keine Pflicht. Verkäufe können Steuern und Gebühren auslösen; meist genügt es, neue Käufe auf die zurückgebliebene Seite zu lenken. Lumos handelt nie in deinem Namen."},

    # ── category labels shared by drift and the UI ──
    "category.stocks": {"tr": "hisse/ETF", "en": "stocks/ETF", "de": "Aktien/ETF"},
    "category.reit": {"tr": "gayrimenkul", "en": "real estate", "de": "Immobilien"},
    "category.bond": {"tr": "tahvil", "en": "bonds", "de": "Anleihen"},
    "category.fund": {"tr": "fon", "en": "funds", "de": "Fonds"},
    "category.gold": {"tr": "altın", "en": "gold", "de": "Gold"},
    "category.cash": {"tr": "nakit", "en": "cash", "de": "Bargeld"},
    "category.other": {"tr": "diğer", "en": "other", "de": "Sonstiges"},

    # ── behaviour coach: drops ──
    "coach.drop.low": {
        "tr": "Piyasada bir düşüş görüyorsun ve bu seni tedirgin edebilir — bu son derece doğal. Geçmişte benzer düşüşlerin çoğu zamanla toparlandı. Şu an hiçbir şey yapmana gerek yok; planın zaten bu tür dalgalanmaları hesaba katarak kuruldu.",
        "en": "You're seeing a drop in the market and it may unsettle you — that's entirely natural. Most similar drops in the past recovered with time. There's nothing you need to do right now; your plan was built to absorb swings like this.",
        "de": "Du siehst einen Rückgang am Markt, und das kann beunruhigen — das ist völlig natürlich. Die meisten vergleichbaren Rückgänge haben sich mit der Zeit erholt. Du musst gerade nichts tun; dein Plan wurde für solche Schwankungen gebaut."},
    "coach.drop.medium": {
        "tr": "Bugünkü düşüş, uzun vadeli planının bir parçası olarak beklenen türden bir dalgalanma. Elindeki bilgiye göre karar ver, ana haber başlıklarına göre değil.",
        "en": "Today's drop is the kind of swing your long-term plan already expects. Decide on what you know, not on the headlines.",
        "de": "Der heutige Rückgang ist genau die Art Schwankung, die dein langfristiger Plan einkalkuliert. Entscheide nach dem, was du weißt, nicht nach den Schlagzeilen."},
    "coach.drop.high": {
        "tr": "Düşüş gördün ve belki de bunu bir fırsat olarak değerlendirmeyi düşünüyorsun — bu senin profiline uygun bir tepki. Yine de acele etme; planlı hareket, dürtüsel hareketten güçlüdür.",
        "en": "You've seen a drop and you may be thinking of it as an opportunity — that fits your profile. Still, don't rush: a planned move beats an impulsive one.",
        "de": "Du hast einen Rückgang gesehen und denkst vielleicht an eine Gelegenheit — das passt zu deinem Profil. Überstürze trotzdem nichts: ein geplanter Schritt schlägt einen impulsiven."},

    # ── behaviour coach: rises ──
    "coach.rise.low": {
        "tr": "Piyasa yükseldi — güzel haber, ama bu bir sonraki düşüşte satmak için bir sebep değil. Plana sadık kalmak burada da geçerli.",
        "en": "The market rose — good news, but it's no reason to sell in the next drop. Sticking to the plan applies here too.",
        "de": "Der Markt ist gestiegen — schöne Nachricht, aber kein Grund, beim nächsten Rückgang zu verkaufen. Am Plan festhalten gilt auch hier."},
    "coach.rise.medium": {
        "tr": "Yükseliş iyi gidiyor. Bu, riskini artırmak için bir işaret değil — planın zaten dengeli kurulu.",
        "en": "The rally is going well. That's not a signal to take on more risk — your plan is already built balanced.",
        "de": "Die Rally läuft gut. Das ist kein Signal für mehr Risiko — dein Plan ist bereits ausgewogen angelegt."},
    "coach.rise.high": {
        "tr": "Yükseliş moralini yükseltebilir, ama aşırı güven riskli kararlara yol açabilir. Disiplin, coşkudan önce gelir.",
        "en": "A rally can lift your mood, but overconfidence leads to risky decisions. Discipline comes before excitement.",
        "de": "Eine Rally kann die Stimmung heben, doch Selbstüberschätzung führt zu riskanten Entscheidungen. Disziplin kommt vor Euphorie."},

    # ── behaviour coach: the mirror ──
    "coach.mirror.brave": {
        "tr": "Profilinde düşüşlerde tedirgin olduğunu belirtmiştin, ama düşüş sırasında alım yaptın — bu güzel bir cesaret işareti. Bu deneyimi not al; belki risk toleransın düşündüğünden yüksek.",
        "en": "Your profile said drops make you uneasy, yet you bought during one — that's a real sign of courage. Note the experience; your risk tolerance may be higher than you thought.",
        "de": "In deinem Profil stand, dass Rückgänge dich beunruhigen — gekauft hast du trotzdem in einem. Ein echtes Zeichen von Mut. Merk dir das; deine Risikotoleranz ist vielleicht höher als gedacht."},
    "coach.mirror.sold": {
        "tr": "Profilinde düşüşleri fırsat olarak gördüğünü belirtmiştin, ama bu düşüşte sattın. Bu tamamen senin kararın — sadece fark etmeni istedik, çünkü bazen an içindeki duygu profildeki niyetten farklı olabilir.",
        "en": "Your profile said you see drops as opportunities, yet you sold into this one. That's entirely your call — we just wanted you to notice, because the feeling in the moment can differ from the intention in the profile.",
        "de": "In deinem Profil stand, dass du Rückgänge als Chance siehst — in diesem hast du verkauft. Das ist ganz deine Entscheidung — wir wollten es dir nur zeigen, denn das Gefühl im Moment kann von der Absicht im Profil abweichen."},

    # ── projection ──
    "projection.no_history_asset": {
        "tr": "{ticker} için {years} yıllık pencere dağılımı çıkaracak kadar geçmiş veri yok — daha kısa bir vade dene.",
        "en": "There isn't enough history for {ticker} to build a distribution of {years}-year windows — try a shorter horizon.",
        "de": "Für {ticker} gibt es zu wenig Historie, um eine Verteilung über {years}-Jahres-Fenster zu bilden — versuch einen kürzeren Zeitraum."},
    "projection.no_history_portfolio": {
        "tr": "Portföyün için {years} yıllık pencere dağılımı çıkaracak kadar ortak geçmiş veri yok — daha kısa bir vade dene.",
        "en": "There isn't enough shared history in your portfolio to build a distribution of {years}-year windows — try a shorter horizon.",
        "de": "In deinem Portfolio gibt es zu wenig gemeinsame Historie für eine Verteilung über {years}-Jahres-Fenster — versuch einen kürzeren Zeitraum."},
    "projection.note_asset": {
        "tr": "Bu bir tahmin DEĞİL: {ticker}'nin kendi geçmişindeki tüm {years} yıllık dönemlerin dağılımı. Gelecek bu aralığın dışına da çıkabilir.",
        "en": "This is NOT a forecast: it's the distribution of every {years}-year period in {ticker}'s own history. The future can land outside this range.",
        "de": "Das ist KEINE Prognose: es ist die Verteilung aller {years}-Jahres-Zeiträume aus der eigenen Historie von {ticker}. Die Zukunft kann außerhalb dieser Spanne liegen."},
    "projection.note_portfolio": {
        "tr": "Bu bir tahmin DEĞİL: tüm portföyünün (ağırlıklı) kendi geçmişindeki tüm {years} yıllık dönemlerin dağılımı. Çeşitlendirme bandı daraltabilir ama garanti vermez.",
        "en": "This is NOT a forecast: it's the distribution of every {years}-year period in your whole (weighted) portfolio's own history. Diversification can narrow the band but guarantees nothing.",
        "de": "Das ist KEINE Prognose: es ist die Verteilung aller {years}-Jahres-Zeiträume aus der eigenen (gewichteten) Historie deines gesamten Portfolios. Streuung kann die Spanne verengen, garantiert aber nichts."},
    "projection.no_region": {
        "tr": "Bölge verisi şu an alınamıyor.",
        "en": "Regional data can't be reached right now.",
        "de": "Regionaldaten sind gerade nicht erreichbar."},
    "projection.region_short": {
        "tr": "TCMB bölge endeksi {available} yıllık geçmişe sahip — {years} yıllık senaryo bandı için yeterli pencere yok. Daha kısa vade dene (endeks 2023'te yeniden bazlandı).",
        "en": "The central bank's regional index has {available} years of history — not enough windows for a {years}-year scenario band. Try a shorter horizon (the index was rebased in 2023).",
        "de": "Der Regionalindex der Zentralbank reicht {available} Jahre zurück — zu wenige Fenster für eine {years}-Jahres-Spanne. Versuch einen kürzeren Zeitraum (der Index wurde 2023 neu basiert)."},
    "projection.region_note": {
        "tr": "Bölge (NUTS2) endeksi dağılımıdır — tek bir mahalle/parsel değil. \"60 kat arttı\" anekdotları genelde nominal ve seçilmiş örneklerdir; reel karşılığı yanında gösteriyoruz.",
        "en": "This is the distribution of a regional (NUTS2) index — not one neighbourhood or plot. \"It went up 60x\" stories are usually nominal and cherry-picked; we show the real figure alongside.",
        "de": "Das ist die Verteilung eines Regionalindex (NUTS2) — nicht eines einzelnen Viertels oder Grundstücks. Geschichten wie „das 60-Fache\" sind meist nominal und herausgepickt; wir zeigen den realen Wert daneben."},

    # ── panic button ──
    "panic.fact.recovery": {
        "tr": "Tarihte her büyük düşüşün bir toparlanma dönemi oldu — süresi değişir, yönü genelde değişmedi.",
        "en": "Every major drop in history has been followed by a recovery — how long it takes varies, the direction usually hasn't.",
        "de": "Auf jeden großen Rückgang der Geschichte folgte eine Erholung — wie lange sie dauert, variiert, die Richtung meist nicht."},
    "panic.fact.paper_loss": {
        "tr": "Panik anında satanlar, düşüşü 'gerçekleşmiş zarara' çevirir. Satmadığın sürece kayıp kağıt üstündedir.",
        "en": "Selling in a panic turns a drop into a realised loss. Until you sell, the loss is only on paper.",
        "de": "Wer in Panik verkauft, macht aus einem Rückgang einen realisierten Verlust. Solange du nicht verkaufst, steht er nur auf dem Papier."},
    "panic.fact.best_days": {
        "tr": "En kötü günlerde satıp en iyi günleri kaçırmak, uzun vadeli getirinin en büyük düşmanıdır — en iyi günler çoğu zaman en kötü günlerin hemen yanındadır.",
        "en": "Selling on the worst days and missing the best ones is the biggest enemy of long-run returns — the best days usually sit right next to the worst.",
        "de": "An den schlechtesten Tagen zu verkaufen und die besten zu verpassen ist der größte Feind der Langfristrendite — die besten Tage liegen meist direkt neben den schlechtesten."},
    "panic.fact.do_nothing": {
        "tr": "Bu ekranı kapattıktan sonra hiçbir şey yapmaman da tamamen geçerli bir karardır.",
        "en": "Closing this screen and doing nothing at all is a perfectly valid decision too.",
        "de": "Diesen Bildschirm zu schließen und gar nichts zu tun ist ebenfalls eine völlig gültige Entscheidung."},
    "panic.held": {
        "tr": "Plana sadık kalmak, panik anında verilebilecek en güçlü karardır. 🕯️",
        "en": "Sticking to the plan is the strongest decision you can make in a panic. 🕯️",
        "de": "Am Plan festzuhalten ist die stärkste Entscheidung, die du in Panik treffen kannst. 🕯️"},
    "panic.sold": {
        "tr": "Endişen meşru. Büyük bir karar vermeden önce 24 saat beklemek ve lisanslı bir danışmanla konuşmak hiçbir şey kaybettirmez.",
        "en": "Your worry is legitimate. Waiting 24 hours before a big decision and talking to a licensed advisor costs you nothing.",
        "de": "Deine Sorge ist berechtigt. Vor einer großen Entscheidung 24 Stunden zu warten und mit einer lizenzierten Fachperson zu sprechen kostet dich nichts."},
    "coach.mirror.fomo": {
        "tr": "Kararların çoğu FOMO etiketli görünüyor — bu tamamen normal, ama farkında olmak bir sonraki kararını daha bilinçli hale getirir.",
        "en": "Most of your decisions are tagged FOMO — that's entirely normal, but noticing it makes the next one more deliberate.",
        "de": "Die meisten deiner Entscheidungen sind mit FOMO markiert — völlig normal, aber es zu bemerken macht die nächste bewusster."},

    # ── errors and gates ──
    "error.invalid_symbol": {
        "tr": "Geçersiz sembol.", "en": "Invalid symbol.", "de": "Ungültiges Symbol."},
    "error.symbol_unverified": {
        "tr": "Sembol şu an doğrulanamadı.",
        "en": "The symbol couldn't be verified right now.",
        "de": "Das Symbol konnte gerade nicht überprüft werden."},
    "error.no_profile": {
        "tr": "Önce risk profilini tamamla.",
        "en": "Complete your risk profile first.",
        "de": "Erstelle zuerst dein Risikoprofil."},
    "error.quota": {
        "tr": "Günlük mesaj hakkın doldu ({quota}/gün) — yarın yenilenir. Daha fazla mesaj için planını yükseltebilirsin.",
        "en": "You've used your daily messages ({quota}/day) — it resets tomorrow. Upgrade your plan for more.",
        "de": "Dein Tageskontingent an Nachrichten ist aufgebraucht ({quota}/Tag) — morgen wird es zurückgesetzt. Für mehr kannst du deinen Plan upgraden."},

    # ── fear check-in reassurance ──
    "fear.param_eriyor": {
        "tr": "Anlıyoruz — bu yüzden her portföyde enflasyona karşı reel getiriyi de göstereceğiz, sadece nominal sayıyı değil.",
        "en": "We understand — that's why every portfolio shows the real return after inflation, not just the nominal number.",
        "de": "Wir verstehen das — deshalb zeigt jedes Portfolio die reale Rendite nach Inflation, nicht nur die nominale Zahl."},
    "fear.kandirilirim": {
        "tr": "Bu haklı bir endişe. Lumos sana hiçbir hisse/fon satmıyor, komisyon almıyor — sadece bilgi veriyor. Kararı hep sen verirsin.",
        "en": "That's a fair worry. Lumos sells you no stock or fund and takes no commission — it only informs. The decision is always yours.",
        "de": "Eine berechtigte Sorge. Lumos verkauft dir weder Aktie noch Fonds und nimmt keine Provision — es informiert nur. Die Entscheidung bleibt immer deine."},
    "fear.anlamiyorum": {
        "tr": "Sorun değil, kimse doğuştan bilmiyor. Her terimi günlük dille açıklayacağız — anlamadığın hiçbir şeyi geçmeyeceğiz.",
        "en": "That's fine, nobody is born knowing this. We'll explain every term in everyday language and skip nothing you don't follow.",
        "de": "Das ist in Ordnung, niemand wird damit geboren. Wir erklären jeden Begriff in Alltagssprache und überspringen nichts, was du nicht verstehst."},
    "fear.batiririm": {
        "tr": "Bu korku çoğu yeni başlayanda var. Küçük adımlarla, sanal pratikle başlayacağız — gerçek parayla asla acele etmeyeceksin.",
        "en": "Most beginners feel this. We'll start with small steps and virtual practice — you'll never be rushed with real money.",
        "de": "Diese Angst haben die meisten Anfänger. Wir starten mit kleinen Schritten und virtueller Übung — mit echtem Geld wird nichts überstürzt."},
}


def t(key: str, lang: str = "tr", **kw: Any) -> str:
    """Look a key up in `lang`, falling back de → en → tr, then format it."""
    entry = _C.get(key)
    if entry is None:
        return key
    text = entry.get(lang)
    if text is None:
        for alt in FALLBACK.get(lang, ("tr",)):
            text = entry.get(alt)
            if text is not None:
                break
    if text is None:
        return key
    return text.format(**kw) if kw else text
