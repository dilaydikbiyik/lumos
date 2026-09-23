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
    "quiz.q.budget.title": {
        "tr": "Yatırıma ayırabileceğin tutar ne kadar?",
        "en": "How much can you put aside to invest?",
        "de": "Wie viel kannst du zum Anlegen beiseitelegen?"},
    "quiz.q.budget.help": {
        "tr": "Şu an elinde olan, yatırıma ayırabileceğin miktar. Yaklaşık olsun, sonra değiştirebilirsin.",
        "en": "What you have now and could put to work. A rough figure is fine — you can change it later.",
        "de": "Was du jetzt hast und anlegen könntest. Eine grobe Zahl reicht — du kannst sie später ändern."},
    "quiz.q.monthly_contribution.title": {
        "tr": "Her ay düzenli ekleyebileceğin bir tutar var mı?",
        "en": "Is there an amount you can add every month?",
        "de": "Gibt es einen Betrag, den du jeden Monat hinzufügen kannst?"},
    "quiz.q.monthly_contribution.help": {
        "tr": "Düzenli ekleme, tek seferlik bir tutardan çok daha fazlasını değiştirir. Yoksa boş bırak.",
        "en": "Adding regularly changes the outcome far more than the starting amount does. Leave it blank if there isn't one.",
        "de": "Regelmäßig einzuzahlen verändert das Ergebnis weit mehr als der Startbetrag. Lass es leer, wenn es keinen gibt."},
    "quiz.q.time_horizon.title": {
        "tr": "Bu parayı kaç yıl sonra kullanmayı düşünüyorsun?",
        "en": "When do you think you'll need this money?",
        "de": "Wann wirst du dieses Geld voraussichtlich brauchen?"},
    "quiz.q.time_horizon.help": {
        "tr": "En belirleyici soru bu. Vade uzadıkça kısa vadeli dalgalanmaların önemi azalır.",
        "en": "This is the most decisive question. The longer the horizon, the less short-term swings matter.",
        "de": "Das ist die entscheidendste Frage. Je länger der Horizont, desto weniger zählen kurzfristige Schwankungen."},
    "quiz.q.time_horizon.opt.short": {
        "tr": "2 yıldan kısa",
        "en": "Less than 2 years",
        "de": "Weniger als 2 Jahre"},
    "quiz.q.time_horizon.opt.medium": {
        "tr": "2–10 yıl arası",
        "en": "Between 2 and 10 years",
        "de": "Zwischen 2 und 10 Jahren"},
    "quiz.q.time_horizon.opt.long": {
        "tr": "10 yıldan uzun",
        "en": "More than 10 years",
        "de": "Mehr als 10 Jahre"},
    "quiz.q.loss_tolerance.title": {
        "tr": "Portföyün 6 ayda %20 düşse ne yapardın?",
        "en": "If your portfolio fell 20% in six months, what would you do?",
        "de": "Was würdest du tun, wenn dein Portfolio in sechs Monaten 20 % fiele?"},
    "quiz.q.loss_tolerance.help": {
        "tr": "Doğru ya da yanlış cevabı yok. Bu soru, kötü bir ayda gerçekte ne yapacağını anlamak için.",
        "en": "There's no right answer. This is about what you'd actually do in a bad month, not what sounds brave.",
        "de": "Es gibt keine richtige Antwort. Es geht darum, was du in einem schlechten Monat wirklich tätest."},
    "quiz.q.loss_tolerance.opt.low": {
        "tr": "Satardım — kayıp görmek bana zor gelir",
        "en": "I'd sell — watching a loss is hard for me",
        "de": "Ich würde verkaufen — Verluste zu sehen fällt mir schwer"},
    "quiz.q.loss_tolerance.opt.medium": {
        "tr": "Endişelenirdim ama beklerdim",
        "en": "I'd worry, but I'd wait it out",
        "de": "Ich wäre beunruhigt, würde es aber aussitzen"},
    "quiz.q.loss_tolerance.opt.high": {
        "tr": "Daha fazla alırdım — fırsat olarak görürdüm",
        "en": "I'd buy more — I'd see it as a chance",
        "de": "Ich würde nachkaufen — ich sähe es als Chance"},
    "quiz.q.goal.title": {
        "tr": "Temel hedefin ne?",
        "en": "What are you mainly after?",
        "de": "Worum geht es dir hauptsächlich?"},
    "quiz.q.goal.help": {
        "tr": "Birden fazlası doğru gelebilir; en çok hangisi seni tarif ediyorsa onu seç.",
        "en": "More than one may feel true. Pick the one that describes you most.",
        "de": "Mehreres kann zutreffen. Wähle das, was dich am ehesten beschreibt."},
    "quiz.q.goal.opt.preservation": {
        "tr": "Elimdekini korumak — erimesini istemiyorum",
        "en": "Keeping what I have — I don't want it melting away",
        "de": "Bewahren, was ich habe — es soll nicht dahinschmelzen"},
    "quiz.q.goal.opt.income": {
        "tr": "Düzenli gelir — temettü ya da kira gibi",
        "en": "Regular income — dividends or rent",
        "de": "Regelmäßiges Einkommen — Dividenden oder Miete"},
    "quiz.q.goal.opt.growth": {
        "tr": "Büyüme — enflasyonun üzerinde getiri",
        "en": "Growth — returns above inflation",
        "de": "Wachstum — Rendite über der Inflation"},
    "quiz.q.goal.opt.speculation": {
        "tr": "Yüksek risk, yüksek getiri",
        "en": "High risk, high return",
        "de": "Hohes Risiko, hohe Rendite"},
    "quiz.q.experience.title": {
        "tr": "Yatırım deneyimin ne kadar?",
        "en": "How much investing have you done?",
        "de": "Wie viel Anlageerfahrung hast du?"},
    "quiz.q.experience.help": {
        "tr": "Hiç yoksa da sorun değil — bu uygulama tam olarak onun için var.",
        "en": "None is a perfectly good answer — this app exists for exactly that.",
        "de": "Gar keine ist eine völlig gute Antwort — genau dafür gibt es diese App."},
    "quiz.q.experience.opt.none": {
        "tr": "Hiç yatırım yapmadım",
        "en": "I've never invested",
        "de": "Ich habe noch nie angelegt"},
    "quiz.q.experience.opt.beginner": {
        "tr": "Birikim hesabım ya da bir fonum var",
        "en": "I have savings or a fund",
        "de": "Ich habe Erspartes oder einen Fonds"},
    "quiz.q.experience.opt.intermediate": {
        "tr": "Hisse ya da ETF aldım",
        "en": "I've bought stocks or ETFs",
        "de": "Ich habe Aktien oder ETFs gekauft"},
    "quiz.q.experience.opt.advanced": {
        "tr": "Aktif portföy yönetiyorum",
        "en": "I actively manage a portfolio",
        "de": "Ich verwalte aktiv ein Portfolio"},
    "quiz.q.age.title": {
        "tr": "Yaşını paylaşmak ister misin?",
        "en": "Would you like to share your age?",
        "de": "Möchtest du dein Alter angeben?"},
    "quiz.q.age.help": {
        "tr": "İstersen atla. Genç olmak vadeyi uzatır, bu da geçici düşüşlerden toparlanmak için daha çok zaman demek.",
        "en": "Skip it if you'd rather. Being younger lengthens the horizon, which means more time to recover from a dip.",
        "de": "Überspring es, wenn du magst. Jünger zu sein verlängert den Horizont — mehr Zeit, sich von einem Rückgang zu erholen."},
    "quiz.q.high_interest_debt.title": {
        "tr": "Kredi kartı ya da ihtiyaç kredisi borcun var mı?",
        "en": "Do you have credit-card or consumer-loan debt?",
        "de": "Hast du Kreditkarten- oder Konsumkreditschulden?"},
    "quiz.q.high_interest_debt.help": {
        "tr": "Bunu sormamın sebebi şu: kart faizi yatırım getirisinin çok üstündedir, yani borç varken yatırım çoğu zaman zarar ettirir. Varsa sana dürüst olanı söyleyeceğim. Yoksa boş bırak.",
        "en": "The reason I ask: card interest runs far above investment returns, so investing while carrying it usually loses money. If there is some, I'll tell you the honest thing. Leave it blank if there's none.",
        "de": "Warum ich frage: Kartenzinsen liegen weit über Anlagerenditen, investieren mit solchen Schulden verliert meist Geld. Wenn es welche gibt, sage ich dir ehrlich, was gilt. Sonst lass es leer."},
    "quiz.q.income_stability.title": {
        "tr": "Gelirin ne kadar düzenli?",
        "en": "How steady is your income?",
        "de": "Wie regelmäßig ist dein Einkommen?"},
    "quiz.q.income_stability.help": {
        "tr": "Düzenli gelir daha fazla risk almana izin verir; düzensizse daha büyük bir güvenlik tamponu bırakırız.",
        "en": "Steady income allows more risk; if it's irregular we leave a bigger safety buffer.",
        "de": "Ein regelmäßiges Einkommen erlaubt mehr Risiko; ist es unregelmäßig, lassen wir einen größeren Puffer."},
    "quiz.q.income_stability.opt.stable": {
        "tr": "Sabit maaş",
        "en": "A fixed salary",
        "de": "Festes Gehalt"},
    "quiz.q.income_stability.opt.variable": {
        "tr": "Değişken / serbest çalışıyorum",
        "en": "Variable / freelance",
        "de": "Variabel / freiberuflich"},
    "quiz.q.income_stability.opt.irregular": {
        "tr": "Düzensiz",
        "en": "Irregular",
        "de": "Unregelmäßig"},
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
    "risk.mod.income.stable": {
        "tr": "Sabit maaş", "en": "A fixed salary", "de": "Festes Gehalt"},
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
        "tr": "Güvenli pay = 60 − (5,5 × risk skoru), en az %0 en fazla %60 (nakit + tahvil). Sonuç %10'un altına düşerse sıfıra çekilir: %3'lük bir nakit dilimi portföyü korumaz, sadece takip yükü yaratır — bu yüzden 9,1 üstü skorlarda savunma payı tamamen kapanır. Kalan pay büyüme varlıklarına dağıtılır: her varlığın ağırlığı = (1 − α) × (1 / oynaklık) + α × oynaklık. α risk skorunun onda biridir; yani α büyüdükçe oynak varlıklar daha fazla, küçüldükçe sakin varlıklar daha fazla pay alır. Hiçbir pozisyon %45'i geçemez ve %5'in altında kalan pozisyonlar elenir.",
        "en": "Defensive share = 60 − (5.5 × risk score), floored at 0% and capped at 60% (cash + bonds). If the result falls below 10% it is set to zero: a 3% cash sleeve protects nothing and only adds something to track — so above a score of 9.1 the defensive side closes entirely. What's left is spread across the growth assets: each weight = (1 − α) × (1 / volatility) + α × volatility. α is one tenth of the risk score — so the larger α gets, the more the volatile assets take, and the smaller it gets, the more the calm ones do. No position may exceed 45%, and anything under 5% is dropped.",
        "de": "Defensiver Anteil = 60 − (5,5 × Risikowert), mindestens 0% und höchstens 60% (Bargeld + Anleihen). Fällt das Ergebnis unter 10%, wird es auf null gesetzt: ein Barbestand von 3% schützt nichts und macht nur Arbeit — ab einem Wert über 9,1 entfällt die defensive Seite daher ganz. Der Rest verteilt sich auf die Wachstumsanlagen: Gewicht je Anlage = (1 − α) × (1 / Volatilität) + α × Volatilität. α ist ein Zehntel des Risikowerts — je größer α, desto mehr erhalten die schwankungsreichen Anlagen, je kleiner, desto mehr die ruhigen. Keine Position darf 45% überschreiten, und alles unter 5% entfällt."},

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
    "error.market_data": {
        "tr": "Piyasa verisi şu an alınamıyor — birazdan tekrar dene.",
        "en": "Market data can't be reached right now — try again shortly.",
        "de": "Marktdaten sind gerade nicht erreichbar — versuch es gleich noch einmal."},
    "error.ai_unavailable": {
        "tr": "Yapay zeka asistanı şu an yanıt veremiyor — birazdan tekrar dene.",
        "en": "The AI assistant can't answer right now — try again shortly.",
        "de": "Der KI-Assistent kann gerade nicht antworten — versuch es gleich noch einmal."},
    "error.invalid_value": {
        "tr": "Gönderilen değerlerden biri geçersiz. Lütfen kontrol edip tekrar dene.",
        "en": "One of the values sent was invalid. Please check it and try again.",
        "de": "Einer der gesendeten Werte war ungültig. Bitte prüfe ihn und versuche es erneut."},
    "error.internal": {
        "tr": "Beklenmedik bir hata oluştu — lütfen daha sonra tekrar dene.",
        "en": "Something went wrong — please try again later.",
        "de": "Etwas ist schiefgelaufen — bitte versuch es später noch einmal."},
    "error.ai_down": {
        "tr": "Yapay zeka servisine şu an ulaşılamıyor — lütfen birkaç dakika sonra tekrar dene.",
        "en": "The AI service is unreachable right now — please try again in a few minutes.",
        "de": "Der KI-Dienst ist gerade nicht erreichbar — bitte versuch es in ein paar Minuten noch einmal."},
    "error.quiz_incomplete": {
        "tr": "Sohbet tamamlanmadı — lütfen tüm soruları yanıtla ve tekrar dene.",
        "en": "The conversation isn't finished — please answer every question and try again.",
        "de": "Das Gespräch ist noch nicht abgeschlossen — bitte beantworte alle Fragen und versuch es erneut."},
    "error.unknown_role": {
        "tr": "Bilinmeyen rol. Geçerli roller: {roles}.",
        "en": "Unknown role. Valid roles: {roles}.",
        "de": "Unbekannte Rolle. Gültige Rollen: {roles}."},
    "error.self_demote": {
        "tr": "Kendi yönetici yetkini kaldıramazsın — geri almak için başka bir yöneticiye ihtiyacın olurdu.",
        "en": "You can't remove your own admin access — you'd need another admin to give it back.",
        "de": "Du kannst dir die Administratorrechte nicht selbst entziehen — du bräuchtest eine andere Administratorin, um sie zurückzugeben."},
    "error.last_admin": {
        "tr": "Son yönetici yetkisi kaldırılamaz; önce başka birini yönetici yap.",
        "en": "The last admin can't be demoted; make someone else an admin first.",
        "de": "Die letzte Administratorin kann nicht herabgestuft werden; mach zuerst jemand anderen zur Administratorin."},
    "error.forbidden": {
        "tr": "Bu işlem için yetkin yok.",
        "en": "You don't have permission for this.",
        "de": "Dafür fehlt dir die Berechtigung."},
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
    # ── market pack defaults ──
    # The educational disclaimer is the same promise in every market, so it
    # lives here rather than being copied into each pack in three languages —
    # three copies of one sentence is three chances for it to drift. A pack
    # that needs its own wording (a regulator demanding specific language)
    # still overrides it.
    "market.disclaimer": {
        "tr": "Yalnızca eğitim amaçlıdır — kurallar değişir ve herkesin durumu farklıdır. Her zaman yerel lisanslı bir profesyonele doğrulat.",
        "en": "Educational content only — rules change and individual situations differ. Always confirm with a licensed local professional.",
        "de": "Nur zu Bildungszwecken — Regeln ändern sich und jede Situation ist anders. Bitte bestätige alles mit einer lizenzierten Fachperson."},

    # ── region ranking ──
    "region.real_gain": {
        "tr": "Enflasyonun ÜZERİNDE değerlendi — reel kazanç.",
        "en": "It appreciated ABOVE inflation — a real gain.",
        "de": "Der Wert stieg ÜBER die Inflation — ein realer Gewinn."},
    "region.near_inflation": {
        "tr": "Nominal artışa rağmen enflasyona yakın seyretti.",
        "en": "Despite the nominal rise, it tracked close to inflation.",
        "de": "Trotz nominalem Anstieg lag es nahe an der Inflation."},
    "region.real_loss": {
        "tr": "Nominal artış yanıltıcı: enflasyon karşısında reel kayıp.",
        "en": "The nominal rise is misleading: a real loss against inflation.",
        "de": "Der nominale Anstieg täuscht: real ein Verlust gegenüber der Inflation."},
    "region.note": {
        "tr": "Bu sıralama bölge (NUTS2) seviyesindedir — mahalle/parsel analizi değildir. Geçmiş değerlenme geleceğin garantisi değildir.",
        "en": "This ranking is at regional (NUTS2) level — not a neighbourhood or parcel analysis. Past appreciation guarantees nothing about the future.",
        "de": "Diese Rangfolge liegt auf Regionsebene (NUTS2) — keine Viertel- oder Grundstücksanalyse. Vergangene Wertsteigerung garantiert nichts für die Zukunft."},

    # ── German market segments (nested, not alternatives) ──
    "segment.DE0007": {
        "tr": "Yedi büyük şehir", "en": "Seven largest cities",
        "de": "Sieben größte Städte"},
    "segment.DE0127": {
        "tr": "127 şehir", "en": "127 cities", "de": "127 Städte"},
    "segment.DEK": {
        "tr": "Tüm ilçeler (Almanya geneli)", "en": "All districts (Germany)",
        "de": "Alle Kreise (Deutschland)"},

    # ── sub-national housing breakdown ──
    "province.unavailable": {
        "tr": "Bölge verisi şu an alınamıyor.",
        "en": "Area data can't be reached right now.",
        "de": "Regionaldaten sind gerade nicht erreichbar."},
    "province.no_breakdown": {
        "tr": "{market} pazarı için bölge bölge konut verisi yayınlanmıyor.",
        "en": "No area-by-area housing data is published for the {market} market.",
        "de": "Für den Markt {market} werden keine regionalen Wohndaten veröffentlicht."},
    "province.note_price_level": {
        "tr": "İl ortalaması birim fiyatlardır (TCMB) — mahalle/parsel analizi değildir. Geçmiş değerlenme geleceğin garantisi değildir.",
        "en": "These are province-average unit prices (Turkish central bank) — not a neighbourhood or parcel analysis. Past appreciation guarantees nothing about the future.",
        "de": "Das sind Durchschnittspreise je Provinz (türkische Zentralbank) — keine Viertel- oder Grundstücksanalyse. Vergangene Wertsteigerung garantiert nichts für die Zukunft."},
    "province.note_index": {
        "tr": "Bu bir fiyat ENDEKSİDİR — değerlenmeyi ölçer, metrekare fiyatını değil; o yüzden burada birim fiyat göstermiyoruz. Bölge ortalamasıdır, tek bir şehir ya da mahalle değil. Kaynak: {source}",
        "en": "This is a price INDEX — it measures appreciation, not the price of a square metre, which is why no unit price is shown. It is an area average, not one city or neighbourhood. Source: {source}",
        "de": "Das ist ein Preis-INDEX — er misst die Wertentwicklung, nicht den Quadratmeterpreis; deshalb wird hier kein Einzelpreis angezeigt. Es ist ein Gebietsdurchschnitt, nicht eine Stadt oder ein Viertel. Quelle: {source}"},
    # What a specific index actually measures is a fact about that index, so
    # it travels with the source name rather than with the country.
    "source.fred": {
        "tr": "FHFA eyalet konut fiyat endeksi (FRED). Endeks, satış fiyatlarının yanında yeniden finansman değerlemelerini de içerir; Case-Shiller'ın yalnızca tekrar satışa dayanan yönteminden bu yönüyle ayrılır.",
        "en": "the FHFA state house price index (via FRED). The index draws on appraisals from refinancings as well as sales, which is where it differs from Case-Shiller's repeat-sales method.",
        "de": "der FHFA-Häuserpreisindex je Bundesstaat (über FRED). Er stützt sich neben Verkäufen auch auf Bewertungen aus Refinanzierungen und unterscheidet sich darin von der Wiederverkaufsmethode von Case-Shiller."},
    "source.tcmb_evds": {
        "tr": "TCMB konut fiyat endeksi.",
        "en": "the Turkish central bank's housing price index.",
        "de": "der Wohnpreisindex der türkischen Zentralbank."},
    "source.bundesbank": {
        "tr": "Deutsche Bundesbank konut fiyat endeksi. Almanya'da eyalet (Bundesland) düzeyinde ücretsiz bir endeks yok; bunlar şehir büyüklüğüne göre gruplardır ve İÇ İÇEDİR — yedi büyük şehir, 127 şehrin içindedir. Yani alternatif yerler değil, aynı ülkenin farklı piyasa kesitleridir.",
        "en": "the Deutsche Bundesbank house price index. No free index exists at Bundesland level in Germany; these are city-size groups and they are NESTED — the seven largest cities sit inside the 127. They are segments of one market, not alternative places to buy.",
        "de": "der Häuserpreisindex der Deutschen Bundesbank. Auf Ebene der Bundesländer gibt es keinen frei verfügbaren Index; dies sind Gruppen nach Stadtgröße, und sie sind INEINANDER VERSCHACHTELT — die sieben größten Städte liegen innerhalb der 127. Es sind Segmente eines Marktes, keine alternativen Orte."},
    "source.eurostat": {
        "tr": "Eurostat konut fiyat endeksi.",
        "en": "the Eurostat house price index.",
        "de": "der Eurostat-Häuserpreisindex."},
    "province.no_window": {
        "tr": "{name} için {years} yıllık pencere dağılımına yetecek geçmiş yok.",
        "en": "There isn't enough history for {name} to build a distribution of {years}-year windows.",
        "de": "Für {name} gibt es zu wenig Historie für eine Verteilung über {years}-Jahres-Fenster."},
    "province.projection_note": {
        "tr": "Bu bir tahmin DEĞİL: {name} ortalamasının kendi geçmişindeki tüm {years} yıllık dönemlerin dağılımı. Reel bant, her dönemin kendi enflasyonundan arındırılmıştır.",
        "en": "This is NOT a forecast: it's the distribution of every {years}-year period in {name}'s own history. The real band deflates each period by its own inflation.",
        "de": "Das ist KEINE Prognose: es ist die Verteilung aller {years}-Jahres-Zeiträume aus der eigenen Historie von {name}. Die reale Spanne bereinigt jeden Zeitraum um seine eigene Inflation."},
    "path.reason.short_horizon": {
        "tr": "Vaden kısa. Gayrimenkulde alım masrafları peşin ödenir ve kendini amorti etmesi yıllar alır — bu sürede satmak zorunda kalırsan o masraf cebinden çıkar.",
        "en": "Your horizon is short. Property's purchase costs are paid up front and take years to amortise — if you have to sell inside that window, you absorb them.",
        "de": "Dein Horizont ist kurz. Die Kaufnebenkosten einer Immobilie fallen sofort an und brauchen Jahre, um sich zu amortisieren — musst du vorher verkaufen, trägst du sie selbst."},
    "path.reason.medium_horizon": {
        "tr": "Vaden orta uzunlukta. Gayrimenkul için biraz erken, ama birikimini enflasyona karşı çalıştırmak için fazlasıyla yeterli.",
        "en": "Your horizon is medium. A little early for property, and more than long enough to put your savings to work against inflation.",
        "de": "Dein Horizont ist mittel. Für eine Immobilie etwas früh, für das Arbeiten gegen die Inflation mehr als lang genug."},
    "path.reason.long_horizon": {
        "tr": "Vaden uzun. Gayrimenkulün en büyük dezavantajı olan \"paraya çevirememek\" senin için daha az bağlayıcı; iki dünyayı birden düşünebilirsin.",
        "en": "Your horizon is long. Property's biggest drawback — not being able to turn it back into money quickly — binds you less, so both worlds are open.",
        "de": "Dein Horizont ist lang. Der größte Nachteil von Immobilien — sie nicht schnell wieder zu Geld machen zu können — bindet dich weniger; beide Welten stehen offen."},
    "path.reason.below_entry": {
        "tr": "Bütçen bu pazarda fiziksel gayrimenkule girmek için gereken eşiğin altında. Bu bir eksiklik değil, sadece bir sıralama sorusu: gayrimenkule maruz kalmak istiyorsan GYO'lar küçük tutarlarla da mümkün.",
        "en": "Your budget is below this market's entry bar for physical property. That is not a shortcoming, it is a question of order: if you want property exposure meanwhile, REITs work at small amounts.",
        "de": "Dein Budget liegt unter der Einstiegsschwelle für physische Immobilien in diesem Markt. Das ist kein Mangel, sondern eine Frage der Reihenfolge: Für Immobilien-Exposure in der Zwischenzeit funktionieren REITs auch mit kleinen Beträgen."},
    "path.reason.above_entry": {
        "tr": "Bütçen bu pazarda fiziksel gayrimenkul için gereken eşiğin üzerinde, yani gerçekten bir seçenek.",
        "en": "Your budget is above this market's entry bar for physical property, so it is genuinely an option.",
        "de": "Dein Budget liegt über der Einstiegsschwelle für physische Immobilien in diesem Markt — es ist also tatsächlich eine Option."},
    "path.reason.fear_complexity": {
        "tr": "\"Anlamıyorum\" dedin. Gayrimenkul tarafı noterler, devir vergileri ve resmî süreçlerle dolu — öğrenmeye başlamak için daha zor bir yer. Diğer tarafta tek bir alımla başlayıp ilerleyebilirsin.",
        "en": "You said you don't understand it. The property side is full of notaries, transfer taxes and official procedure — a harder place to start learning. The other side lets you begin with a single purchase.",
        "de": "Du hast gesagt, du verstehst es nicht. Die Immobilienseite steckt voller Notare, Grunderwerbsteuer und Formalitäten — ein schwierigerer Ort zum Anfangen. Auf der anderen Seite reicht ein einziger Kauf zum Start."},
    "path.reason.fear_inflation": {
        "tr": "\"Param eriyor\" dedin. İnsanların enflasyona karşı ilk uzandığı şey çoğu zaman gayrimenkul oluyor — ama vaden buna henüz uygun değil, ve erimeyi durdurmanın tek yolu o değil.",
        "en": "You said your money is melting. Property is often the first thing people reach for against inflation — but your horizon doesn't fit it yet, and it isn't the only way to stop the melting.",
        "de": "Du hast gesagt, dein Geld schmilzt dahin. Immobilien sind oft das Erste, wonach man gegen Inflation greift — aber dein Horizont passt noch nicht dazu, und es ist nicht der einzige Weg."},
    "path.reason.no_signal": {
        "tr": "Henüz bir yön önerecek kadar bilgi yok. Profilini tamamlarsan buraya gerçek bir öneri gelir; o zamana kadar iki dünyayı da görmen en iyisi.",
        "en": "There isn't enough yet to suggest a direction. Finish your profile and a real suggestion appears here; until then, seeing both worlds is the better default.",
        "de": "Es reicht noch nicht, um eine Richtung vorzuschlagen. Vervollständige dein Profil, dann erscheint hier ein echter Vorschlag; bis dahin ist es besser, beide Welten zu sehen."},
    "split.reason.already_committed": {
        "tr": "Gayrimenkule zaten pay ayırmışsın, o yüzden soru artık \"ne kadar gayrimenkul\" değil, \"kalanla ne olacak\". Aşağıdaki plan kalan için.",
        "en": "You already have money in property, so the question is no longer \"how much property\" but \"what happens to the rest\". The plan below is for the rest.",
        "de": "Du hast bereits Geld in Immobilien, die Frage ist also nicht mehr \"wie viel Immobilien\", sondern \"was wird aus dem Rest\". Der Plan unten gilt für den Rest."},
    "split.reason.no_budget": {
        "tr": "Planlanacak bir tutar yok. Bütçeni girdiğinde burada gerçek bir dağılım belirir.",
        "en": "There is no amount to plan yet. Enter your budget and a real split appears here.",
        "de": "Es gibt noch keinen Betrag zu planen. Trag dein Budget ein, dann erscheint hier eine echte Aufteilung."},
    "split.reason.reserve_from_outgoings": {
        "tr": "Önce {months} aylık gideri kenara ayırdık. Bu bir yatırım değil; kötü bir ayın, en kötü fiyattan satmak zorunda kalmaya dönüşmesini engelleyen şey.",
        "en": "We set aside {months} months of outgoings first. It is not an investment; it is what stops a bad month turning into a forced sale at the worst price.",
        "de": "Zuerst haben wir {months} Monatsausgaben zurückgelegt. Das ist keine Anlage, sondern das, was verhindert, dass ein schlechter Monat zum Notverkauf zum schlechtesten Preis wird."},
    "split.reason.reserve_assumed": {
        "tr": "Aylık giderini bilmediğimiz için rezerv olarak %10 varsaydık. Giderini girersen bu rakam tahmin olmaktan çıkar.",
        "en": "We assumed 10% as a reserve because we don't know your monthly outgoings. Enter them and this figure stops being a guess.",
        "de": "Wir haben 10 % als Reserve angenommen, weil wir deine monatlichen Ausgaben nicht kennen. Trag sie ein, dann ist diese Zahl keine Schätzung mehr."},
    "split.reason.path_stocks": {
        "tr": "Hisse yolunu seçtin, bu yüzden rezervden sonra kalan her şey piyasa tarafında planlandı.",
        "en": "You chose the stocks path, so everything after the reserve is planned on the market side.",
        "de": "Du hast den Aktienweg gewählt, also wird alles nach der Reserve auf der Marktseite geplant."},
    "split.reason.path_real_estate": {
        "tr": "Emlak yolunu seçtin, bu yüzden rezervden sonra kalan her şey gayrimenkul tarafında planlandı.",
        "en": "You chose the real-estate path, so everything after the reserve is planned on the property side.",
        "de": "Du hast den Immobilienweg gewählt, also wird alles nach der Reserve auf der Immobilienseite geplant."},
    "split.reason.below_entry_reit": {
        "tr": "Bu tutar bu pazarda fiziksel gayrimenkul almaya yetmiyor. Alamayacağın bir şeye pay ayırmak işe yaramaz bir tavsiye olurdu; onun yerine gayrimenkule GYO üzerinden yer verdik.",
        "en": "This amount cannot buy physical property in this market. Allocating to something you cannot buy would be advice you can't act on, so the property exposure goes through REITs instead.",
        "de": "Mit diesem Betrag lässt sich in diesem Markt keine physische Immobilie kaufen. Etwas zuzuteilen, das du nicht kaufen kannst, wäre ein Rat, dem du nicht folgen kannst — die Immobilienquote läuft daher über REITs."},
    "split.reason.rounded_to_entry": {
        "tr": "Gayrimenkul payını, bu pazarda gerçekten alım yapılabilecek eşiğe yuvarladık. Eşiğin hemen altında kalan bir pay hiçbir şey satın almaz.",
        "en": "We rounded the property share up to what actually buys something in this market. A share that lands just under the threshold buys nothing at all.",
        "de": "Wir haben den Immobilienanteil auf das aufgerundet, womit sich in diesem Markt tatsächlich etwas kaufen lässt. Ein Anteil knapp unter der Schwelle kauft gar nichts."},
    "split.reason.entry_would_overcommit": {
        "tr": "Ama o eşiğe ulaşmak birikiminin çok büyük bir kısmını tek ve satması zor bir varlığa kilitlerdi. Seni on yıl yerinden kıpırdayamaz hâle getiren bir plan iyi bir plan değil, iyi savunulmuş bir tuzaktır.",
        "en": "But reaching that threshold would lock too much of your savings into a single asset that is hard to sell. A plan that leaves you unable to move for a decade is not a good plan, it is a well-argued trap.",
        "de": "Diese Schwelle zu erreichen würde jedoch zu viel deines Ersparten in einem einzigen, schwer verkäuflichen Vermögenswert binden. Ein Plan, der dich ein Jahrzehnt bewegungsunfähig macht, ist kein guter Plan, sondern eine gut begründete Falle."},
    "split.reason.risk_shaped": {
        "tr": "Dağılım risk skorunla şekillendi. Düşük skor gayrimenkule doğru eğilir — daha çok kazandırdığı için değil, kötü bir yılda satmadan tutmanın en kolay olduğu varlık olduğu için.",
        "en": "The split is shaped by your risk score. A lower score leans toward property — not because it returns more, but because it is the asset people find easiest to hold through a bad year without selling.",
        "de": "Die Aufteilung richtet sich nach deinem Risikowert. Ein niedrigerer Wert neigt zu Immobilien — nicht weil sie mehr abwerfen, sondern weil sie sich in einem schlechten Jahr am leichtesten halten lassen, ohne zu verkaufen."},
    "asset_type.cash": {
        "tr": "Nakit",
        "en": "Cash",
        "de": "Bargeld"},
    "asset_type.crypto": {
        "tr": "Kripto",
        "en": "Crypto",
        "de": "Krypto"},
    "asset_type.etf": {
        "tr": "ETF",
        "en": "ETF",
        "de": "ETF"},
    "asset_type.fund": {
        "tr": "Fon",
        "en": "Fund",
        "de": "Fonds"},
    "asset_type.gold": {
        "tr": "Altın",
        "en": "Gold",
        "de": "Gold"},
    "asset_type.land": {
        "tr": "Arsa",
        "en": "Land",
        "de": "Grundstück"},
    "asset_type.other": {
        "tr": "Diğer",
        "en": "Other",
        "de": "Sonstiges"},
    "asset_type.real_estate": {
        "tr": "Konut",
        "en": "Home",
        "de": "Wohnung"},
    "asset_type.stock": {
        "tr": "Hisse",
        "en": "Stock",
        "de": "Aktie"},
    "asset_type.vehicle": {
        "tr": "Araç",
        "en": "Vehicle",
        "de": "Fahrzeug"},
    "region.horizon.short": {
        "tr": "Vaden kısa olduğu için tablo son bir yıllık değişime göre sıralandı. Kısa vadede önemli olan bölgenin on yıllık hikâyesi değil, şu an ne yaptığı.",
        "en": "Your horizon is short, so the table is ranked over the last year. Over a short window what matters is what an area is doing now, not its ten-year story.",
        "de": "Dein Horizont ist kurz, daher ist die Tabelle nach dem letzten Jahr sortiert. Kurzfristig zählt, was eine Gegend jetzt tut, nicht ihre Zehnjahresgeschichte."},
    "region.horizon.medium": {
        "tr": "Vadene göre tablo {years} yıllık değişime göre sıralandı — tek bir yılın gürültüsünü dışarıda bırakacak, ama bugünle ilgisini koruyacak kadar uzun bir pencere.",
        "en": "For your horizon the table is ranked over {years} years — long enough to leave a single year's noise out, short enough to still describe today.",
        "de": "Für deinen Horizont ist die Tabelle über {years} Jahre sortiert — lang genug, um das Rauschen eines einzelnen Jahres auszulassen, kurz genug, um die Gegenwart zu beschreiben."},
    "region.horizon.long": {
        "tr": "Uzun vadeli olduğun için tablo {years} yıllık değişime göre sıralandı. Bekleyebiliyorsan, geçen çeyrekte kimin yükseldiği senin sorunun değil.",
        "en": "You're long-horizon, so the table is ranked over {years} years. If you can wait, who rose last quarter is not your question.",
        "de": "Du denkst langfristig, daher ist die Tabelle über {years} Jahre sortiert. Wer im letzten Quartal gestiegen ist, ist nicht deine Frage, wenn du warten kannst."},
    "region.horizon.unknown": {
        "tr": "Vadeni bilmediğimiz için tablo {years} yıllık değişime göre sıralandı. Profilini tamamlarsan bu pencere sana göre ayarlanır.",
        "en": "We don't know your horizon yet, so the table is ranked over {years} years. Finish your profile and this window adjusts to you.",
        "de": "Wir kennen deinen Horizont noch nicht, daher ist die Tabelle über {years} Jahre sortiert. Vervollständige dein Profil, dann passt sich dieses Fenster an."},
    "character.unknown": {
        "tr": "Bu varlık için yeterli geçmiş yok, o yüzden karakteri hakkında bir şey söylemiyoruz.",
        "en": "There isn't enough history for this asset, so we aren't saying anything about its character.",
        "de": "Für diesen Wert gibt es zu wenig Historie, daher sagen wir nichts über seinen Charakter."},
    "character.too_deep": {
        "tr": "Bu varlık geçmişte %{drawdown} düştü. Sen %{limit} civarına kadar dayanabileceğini söylemiştin — bu ondan derin. Kötü olduğu anlamına gelmez; o düşüşte satmayacağından emin olman gerekir.",
        "en": "This asset has fallen {drawdown}% in the past. You said you could sit through about {limit}% — this goes deeper. That doesn't make it bad; it means you need to be sure you wouldn't sell in that fall.",
        "de": "Dieser Wert ist in der Vergangenheit um {drawdown} % gefallen. Du sagtest, du hältst etwa {limit} % aus — das geht tiefer. Das macht ihn nicht schlecht; du musst nur sicher sein, in diesem Sturz nicht zu verkaufen."},
    "character.slow_recovery": {
        "tr": "Eski seviyesine dönmesi {months} ay sürdü. Senin vaden yaklaşık {years} yıl — paraya o dönüş gerçekleşmeden ihtiyacın olabilir, kâğıt üstündeki zararı gerçek zarara çeviren şey budur.",
        "en": "It took {months} months to get back to where it was. Your horizon is about {years} years — you could need the money before that recovery happens, and that is what turns a paper loss into a real one.",
        "de": "Es dauerte {months} Monate, bis er sein altes Niveau wieder erreichte. Dein Horizont liegt bei etwa {years} Jahren — du könntest das Geld vorher brauchen, und genau das macht aus einem Buchverlust einen echten."},
    "character.long_flat": {
        "tr": "Bir dönem {months} ay boyunca hiçbir yere gitmedi. Çöküşler korkutucu ama kısadır; insanları asıl bıraktıran, grafikte felaket gibi görünmeyen bu düz uzun dönemlerdir.",
        "en": "It once went nowhere for {months} months. Crashes are frightening but brief; it is these long flat stretches — which look like nothing on a chart — that actually make people give up.",
        "de": "Er bewegte sich einmal {months} Monate lang nicht. Abstürze sind beängstigend, aber kurz; es sind diese langen flachen Phasen, die auf keinem Chart nach etwas aussehen, an denen Leute tatsächlich aufgeben."},
    "character.notable_fall": {
        "tr": "Geçmişte %{drawdown} düştüğü oldu. Vadene uyuyor, ama böyle bir dönemde ne hissedeceğini şimdiden bilmen iyi olur.",
        "en": "It has fallen {drawdown}% before. That fits your horizon, but it is worth knowing now how you would feel during a stretch like that.",
        "de": "Er ist schon einmal um {drawdown} % gefallen. Das passt zu deinem Horizont, aber es lohnt sich, jetzt zu wissen, wie du dich in so einer Phase fühlen würdest."},
    "character.steady": {
        "tr": "En kötü düşüşü %{drawdown} olmuş. Senin verdiğin cevaplara göre bu, taşıması rahat bir varlık.",
        "en": "Its worst fall was {drawdown}%. Going by your own answers, this is a comfortable one to hold.",
        "de": "Sein schlimmster Rückgang lag bei {drawdown} %. Nach deinen eigenen Angaben lässt sich dieser Wert bequem halten."},
    "listing.need_numbers": {
        "tr": "Karşılaştırmak için metrekare ve istenen fiyat gerekiyor.",
        "en": "A size in m² and an asking price are needed to compare anything.",
        "de": "Für einen Vergleich braucht es die Fläche in m² und den geforderten Preis."},
    "listing.index_only": {
        "tr": "Bu pazarın verisi bir ENDEKS — fiyatların nasıl hareket ettiğini söyler, ne olduğunu değil. Bir istenen fiyatı endeks sayısına bölmek bir sayı üretir ama o sayı hiçbir şey ifade etmez, o yüzden burada bir yargıda bulunmuyoruz.",
        "en": "This market's data is an INDEX — it says how prices moved, not what they are. Dividing an asking price by an index number produces a number that means nothing, so we are not going to give you a verdict here.",
        "de": "Die Daten dieses Marktes sind ein INDEX — sie sagen, wie sich Preise bewegt haben, nicht wie hoch sie sind. Einen Angebotspreis durch eine Indexzahl zu teilen ergibt eine Zahl, die nichts bedeutet; deshalb gibt es hier kein Urteil."},
    "listing.verdict.below": {
        "tr": "{area} ortalamasının %{pct} ALTINDA. Ucuz olmasının bir sebebi vardır — neden olduğunu bulana kadar iyi haber sayma.",
        "en": "{pct}% BELOW the {area} average. There is usually a reason something is cheap — don't treat it as good news until you know what it is.",
        "de": "{pct} % UNTER dem Durchschnitt von {area}. Billig hat meist einen Grund — halte es nicht für eine gute Nachricht, bevor du ihn kennst."},
    "listing.verdict.fair": {
        "tr": "{area} ortalamasının etrafında, farkı %{pct}. Bu aralık pazarlık payı değil, sokaktan sokağa değişen normal fark.",
        "en": "Around the {area} average, {pct}% apart. That range isn't negotiating room, it's the ordinary difference between one street and the next.",
        "de": "Etwa im Durchschnitt von {area}, {pct} % Abstand. Diese Spanne ist kein Verhandlungsspielraum, sondern der normale Unterschied von Straße zu Straße."},
    "listing.verdict.above": {
        "tr": "{area} ortalamasının %{pct} ÜSTÜNDE. Konum, kat, yaş ya da manzara bunu açıklayabilir — satıcıya neyin açıkladığını sor.",
        "en": "{pct}% ABOVE the {area} average. Location, floor, age or a view can explain that — ask the seller which one does.",
        "de": "{pct} % ÜBER dem Durchschnitt von {area}. Lage, Stockwerk, Alter oder Aussicht können das erklären — frag den Verkäufer, was davon."},
    "listing.verdict.well_above": {
        "tr": "{area} ortalamasının %{pct} ÜSTÜNDE. Bu kadar fark somut bir gerekçe ister; ikna edici bir cevap alamıyorsan fiyat o gerekçeyi değil, satıcının beklentisini yansıtıyor olabilir.",
        "en": "{pct}% ABOVE the {area} average. A gap that size needs a concrete reason; if you can't get a convincing one, the price may reflect the seller's hopes rather than the property.",
        "de": "{pct} % ÜBER dem Durchschnitt von {area}. Ein solcher Abstand braucht einen konkreten Grund; bekommst du keinen überzeugenden, spiegelt der Preis eher die Hoffnung des Verkäufers als die Immobilie."},
    "listing.caveat": {
        "tr": "Karşılaştırma {area} GENELİNİN ortalamasıyla yapıldı. Sahildeki daire de ring yolundaki daire de aynı ortalamanın içinde — bu sayı bir başlangıç noktası, bir değerleme değil.",
        "en": "Compared against the average for {area} AS A WHOLE. A flat by the water and a flat by the ring road are both in that average — this is a starting point, not a valuation.",
        "de": "Verglichen mit dem Durchschnitt von {area} INSGESAMT. Eine Wohnung am Wasser und eine an der Ringstraße stecken beide in diesem Durchschnitt — das ist ein Ausgangspunkt, keine Bewertung."},
    "listing.question.deed": {
        "tr": "Tapu kaydını gördün mü — malik kim, hisseli mi, ipotek ya da şerh var mı?",
        "en": "Have you seen the ownership record — who owns it, is it shared, are there liens or charges?",
        "de": "Hast du den Grundbuchauszug gesehen — wem gehört es, geteilt, Lasten oder Grundschulden?"},
    "listing.question.zoning": {
        "tr": "İmar durumu ne? Üzerine ne yapılabileceğini satıcı değil, belediye söyler.",
        "en": "What does the zoning allow? The planning office answers that, not the seller.",
        "de": "Was erlaubt der Bebauungsplan? Das beantwortet das Bauamt, nicht der Verkäufer."},
    "listing.question.access": {
        "tr": "Yola cephesi ve yasal erişimi var mı? Elektrik, su, kanalizasyon getirilebiliyor mu?",
        "en": "Does it have road frontage and legal access? Can power, water and drainage actually be brought to it?",
        "de": "Hat es Straßenfront und rechtlichen Zugang? Lassen sich Strom, Wasser und Abwasser überhaupt anschließen?"},
    "listing.question.debts": {
        "tr": "Üzerinde birikmiş aidat, vergi ya da borç var mı? Borç taşınmazla birlikte gelir.",
        "en": "Are there unpaid dues, taxes or debts on it? Those come with the property.",
        "de": "Gibt es offene Hausgelder, Steuern oder Schulden? Die kommen mit der Immobilie."},
    "listing.question.survey": {
        "tr": "Sınırlar arazide gördüğünle aynı mı? Ölçüm yaptırdın mı?",
        "en": "Do the boundaries match what you saw on the ground? Have you had it surveyed?",
        "de": "Stimmen die Grenzen mit dem überein, was du vor Ort gesehen hast? Wurde vermessen?"},
    "listing.question.why_selling": {
        "tr": "Neden satılıyor ve ne kadardır ilanda? Uzun süredir duruyorsa sebebini öğren.",
        "en": "Why is it being sold, and how long has it been listed? If it has sat a long time, find out why.",
        "de": "Warum wird verkauft, und wie lange steht es schon im Angebot? Steht es lange, finde heraus warum."},
    "compare.no_region": {
        "tr": "Bu bölge için fiyat endeksi yok, o yüzden karşılaştıracak bir taraf da yok.",
        "en": "There is no price index for this area, so there is no side to compare against.",
        "de": "Für diese Gegend gibt es keinen Preisindex, also auch keine Seite zum Vergleichen."},
    "compare.short_history": {
        "tr": "Bu bölgenin verisi {years} yıl geriye gitmiyor; yalnızca {covered} yıl var. Farklı uzunlukta iki dönemi yan yana koymak karşılaştırma değil, yanıltma olur.",
        "en": "This area's data doesn't reach back {years} years — only {covered}. Setting two different-length periods side by side would not be a comparison, it would be misleading.",
        "de": "Die Daten dieser Gegend reichen keine {years} Jahre zurück, nur {covered}. Zwei unterschiedlich lange Zeiträume nebeneinanderzustellen wäre kein Vergleich, sondern irreführend."},
    "compare.no_portfolio": {
        "tr": "Portföy tarafının geçmişi şu anda okunamadı. Tek taraflı bir karşılaştırma göstermektense hiç göstermemek daha doğru.",
        "en": "The portfolio side's history could not be read right now. Better to show nothing than a one-sided comparison.",
        "de": "Die Historie der Portfolioseite ließ sich gerade nicht lesen. Besser nichts zeigen als einen einseitigen Vergleich."},
    "compare.note": {
        "tr": "Bu bir tahmin değil: aynı tutarın aynı dönemde iki tarafta da gerçekte ne yaptığı. Gayrimenkul tarafına yalnızca onun ödediği masraflar (devir vergisi, komisyon, yıllık bakım) yüklendi ve aldığı kira eklendi. Geçmiş, gelecek için söz vermez.",
        "en": "Not a forecast: what the same amount actually did on both sides over the same period. The property side is charged only the costs it alone pays (transfer tax, commission, yearly upkeep) and credited the rent it earned. The past promises nothing about the future.",
        "de": "Keine Prognose: was derselbe Betrag auf beiden Seiten im selben Zeitraum tatsächlich getan hat. Der Immobilienseite werden nur die Kosten angelastet, die allein sie trägt (Grunderwerbsteuer, Provision, jährliche Instandhaltung), und die erzielte Miete gutgeschrieben. Die Vergangenheit verspricht nichts über die Zukunft."},
    "compare.yield_note": {
        "tr": "Kira getirisi burada bakım ve aidat düşülmüş hâliyle (yılda %{upkeep}). Emlakçıların söylediği brüt rakam bu değildir — temettüyle karşılaştırılacak olan net rakamdır.",
        "en": "The rental yield here is NET of upkeep ({upkeep}% a year). That is not the gross figure agents quote — the net one is what compares like for like with a dividend.",
        "de": "Die Mietrendite ist hier NETTO nach Instandhaltung ({upkeep} % pro Jahr). Das ist nicht die Bruttozahl, die Makler nennen — die Nettozahl ist die, die sich mit einer Dividende vergleichen lässt."},
    "health.what.diversification": {
        "tr": "Servetinin kaç farklı varlık türüne yayıldığını ölçer. Tek bir tür ne kadar ağır basarsa puan o kadar düşer.",
        "en": "Measures how far your wealth is spread across different asset types. The more one type dominates, the lower it goes.",
        "de": "Misst, wie weit dein Vermögen über verschiedene Anlagearten verteilt ist. Je stärker eine Art dominiert, desto niedriger."},
    "health.what.liquidity": {
        "tr": "Servetinin ne kadarını kısa sürede nakde çevirebileceğini ölçer. Arsa ve konut aylar alabilir; hisse ve fon günler.",
        "en": "Measures how much of your wealth could realistically become cash quickly. Land and housing can take months; stocks and funds take days.",
        "de": "Misst, wie viel deines Vermögens sich realistisch schnell zu Bargeld machen lässt. Grundstücke und Wohnungen können Monate dauern, Aktien und Fonds Tage."},
    "health.why.div_low": {
        "tr": "Servetinin %{pct} kadarı tek bir türde ({type}). O tür kötü bir dönem geçirirse portföyünün tamamı aynı anda etkilenir.",
        "en": "About {pct}% of your wealth sits in a single type ({type}). If that type has a bad stretch, your whole portfolio has one at the same time.",
        "de": "Rund {pct} % deines Vermögens liegen in einer einzigen Art ({type}). Läuft es dort schlecht, trifft es dein gesamtes Portfolio gleichzeitig."},
    "health.why.div_mid": {
        "tr": "Dağılmış ama hâlâ {type} ağırlıkta (%{pct}). Fena değil; tek bir kötü haberin seni ne kadar etkileyeceğini belirleyen şey bu oran.",
        "en": "Spread out, but still weighted toward {type} ({pct}%). Not bad — that share is what decides how much a single piece of bad news costs you.",
        "de": "Verteilt, aber weiterhin mit Schwerpunkt auf {type} ({pct} %). Nicht schlecht — dieser Anteil entscheidet, wie viel dich eine einzelne schlechte Nachricht kostet."},
    "health.why.div_high": {
        "tr": "Hiçbir tür ezici çoğunlukta değil; en büyüğü {type} ve %{pct}. Bir varlık kötü giderken diğerleri dengeleyebilir.",
        "en": "No type overwhelms the rest — the largest is {type} at {pct}%. When one asset has a bad year, the others can steady it.",
        "de": "Keine Art überwiegt — die größte ist {type} mit {pct} %. Läuft eine schlecht, können die anderen ausgleichen."},
    "health.why.liq_low": {
        "tr": "Servetinin %{pct} kadarı hızlıca satılamayan türde. Acil bir masraf çıkarsa elinde çevirecek pek bir şey olmayabilir.",
        "en": "About {pct}% of your wealth is in things that cannot be sold quickly. If an urgent expense lands, there may be little you can turn to.",
        "de": "Rund {pct} % deines Vermögens stecken in schwer verkäuflichen Dingen. Kommt eine dringende Ausgabe, bleibt womöglich wenig übrig."},
    "health.why.liq_mid": {
        "tr": "Servetinin %{pct} kadarı yavaş satılan türde. Dengeli sayılır, ama acil durum parasının bunun dışında durması gerekir.",
        "en": "About {pct}% of your wealth is slow to sell. That is a reasonable balance, as long as your emergency money sits outside it.",
        "de": "Rund {pct} % deines Vermögens sind langsam verkäuflich. Das ist eine vernünftige Balance, solange dein Notgroschen außerhalb liegt."},
    "health.why.liq_high": {
        "tr": "Yavaş satılan kısım yalnızca %{pct}. İhtiyacın olduğunda paraya erişebilirsin.",
        "en": "Only {pct}% is slow to sell. You can reach your money when you need it.",
        "de": "Nur {pct} % sind langsam verkäuflich. Du kommst an dein Geld, wenn du es brauchst."},
    "health.how.diversification": {
        "tr": "Yükseltmek için: en küçük payı olan türe ekleme yap, en büyük olanı büyütmek yerine. Mevcut bir şeyi satmak gerekmiyor — yeni para nereye gidiyorsa oran oradan değişir.",
        "en": "To raise it: put new money into the type you hold least of, rather than growing the biggest one. Nothing has to be sold — where the next contribution goes is what moves this.",
        "de": "So steigt er: Neues Geld in die Art stecken, von der du am wenigsten hast, statt die größte weiter auszubauen. Nichts muss verkauft werden — entscheidend ist, wohin der nächste Beitrag geht."},
    "health.how.liquidity": {
        "tr": "Yükseltmek için: bir sonraki birikimi hızlı satılabilir bir şeyde tut. Gayrimenkulünü satman gerekmiyor; yanına nakit ya da fon biriktirmek de aynı işi görür.",
        "en": "To raise it: keep the next of your savings in something quick to sell. You do not have to sell property — building cash or funds beside it does the same job.",
        "de": "So steigt sie: Halte den nächsten Teil deiner Ersparnisse in etwas schnell Verkäuflichem. Du musst keine Immobilie verkaufen — daneben Bargeld oder Fonds aufzubauen wirkt genauso."},
    "account.confirmMismatch": {
        "tr": "Hesap silme onayı eşleşmedi. İşlem yapılmadı.",
        "en": "The deletion confirmation didn't match. Nothing was deleted.",
        "de": "Die Löschbestätigung stimmte nicht. Es wurde nichts gelöscht."},
    "account.deleted": {
        "tr": "Hesabın ve tüm verilerin silindi. Seni ağırlamak güzeldi.",
        "en": "Your account and all of your data have been deleted. It was good to have you here.",
        "de": "Dein Konto und alle deine Daten wurden gelöscht. Schön, dass du da warst."},
    "account.deletedDataOnly": {
        "tr": "Verilerin silindi, ancak giriş hesabın şu anda kaldırılamadı. Destekle iletişime geçersen kalanını da silelim.",
        "en": "Your data has been deleted, but your login could not be removed just now. Contact support and we'll finish the job.",
        "de": "Deine Daten wurden gelöscht, dein Login konnte jedoch gerade nicht entfernt werden. Melde dich beim Support, dann erledigen wir den Rest."},
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
