# Copy decisions (owner's call)

Drafted 2026-11-26 from UI audit items 1.18, 6.4 and 6.18 (`docs/ui-audit.md`). **Nothing here is
applied.** Pick one option per string (or edit one); the change is then a locale-file edit plus
the two code notes marked below.

The rule behind all three: *describe instruments, never recommend one*. A finance reviewer (App
Store, Play, and in Germany anyone reading "Berater") treats "fits you", "suggestions" and "consider
adding" as personalised advice — which the same app says, in the same modal, that it does not give.

Pattern used in the options: **A** = smallest change that removes the advice reading; **B** =
reframed as education (what this is, what would change it).

---

## 1.18 — Disclaimer modal + meta tags

### `disclaimerModal.doesBody`

| | Text |
|---|---|
| en (now) | builds your risk profile, **computes a portfolio allocation that fits it**, deflates every number with live market and official inflation data, and explains the formula behind **each decision**. |
| tr (now) | risk profilini çıkarır, **sana uygun bir portföy dağılımı hesaplar**, her rakamı canlı piyasa ve resmî enflasyon verisiyle arındırıp gösterir, **kararlarının** arkasındaki formülü açıklar. |
| de (now) | erstellt dein Risikoprofil, **berechnet eine dazu passende Portfolioaufteilung**, bereinigt jede Zahl mit Live-Markt- und offiziellen Inflationsdaten und erklärt die Formel hinter **jeder Entscheidung**. |

**Why it reads as advice:** "an allocation that fits you" is the definition of a personal
recommendation. "Each decision" (en/de) also implies the app decides.

**Option A — "example for a profile like yours"**
- en: builds your risk profile, shows an example allocation for a profile like yours, deflates every number with live market and official inflation data, and explains the formula behind each figure.
- tr: risk profilini çıkarır, senin gibi bir profil için örnek bir portföy dağılımı gösterir, her rakamı canlı piyasa ve resmî enflasyon verisiyle arındırır ve her hesabın arkasındaki formülü açıklar.
- de: erstellt dein Risikoprofil, zeigt eine Beispielaufteilung für ein Profil wie deins, bereinigt jede Zahl mit Live-Markt- und offiziellen Inflationsdaten und erklärt die Formel hinter jeder Zahl.

**Option B — "how portfolios are usually split"**
- en: builds your risk profile, shows how portfolios at that level of risk are usually split and why, deflates every number with live market and official inflation data, and shows the formula behind each figure.
- tr: risk profilini çıkarır, bu risk düzeyindeki portföylerin genellikle nasıl ve neden bölündüğünü gösterir, her rakamı canlı piyasa ve resmî enflasyon verisiyle arındırır ve her hesabın formülünü gösterir.
- de: erstellt dein Risikoprofil, zeigt, wie Portfolios auf diesem Risikoniveau üblicherweise aufgeteilt werden und warum, bereinigt jede Zahl mit Live-Markt- und offiziellen Inflationsdaten und zeigt die Formel hinter jeder Zahl.

### `disclaimerModal.detail`

| | Text |
|---|---|
| en (now) | **The portfolio suggestions this app produces** are based on public market data and AI analysis. They should never be the sole basis of any investment decision. Always consult a licensed financial advisor before investing. |
| tr (now) | **Bu uygulamanın ürettiği portföy önerileri**, halka açık piyasa verilerine ve yapay zeka analizine dayanır. Hiçbir yatırım kararının tek dayanağı olmamalıdır. Yatırım yapmadan önce mutlaka lisanslı bir finansal danışmana **başvurun**. |
| de (now) | **Die Portfoliovorschläge dieser App** beruhen auf öffentlichen Marktdaten und KI-Analyse. Sie dürfen nie die alleinige Grundlage einer Anlageentscheidung sein. Sprich vor dem Investieren mit einer lizenzierten Fachperson. |

**Why it reads as advice:** the disclaimer itself calls the output "suggestions/öneriler/Vorschläge".
(Side note: tr switches to formal *başvurun* while the rest of the app says *sen*.)

**Option A — "example allocations, for learning"**
- en: The example allocations in this app are calculated from public market data and AI analysis. They are for learning, not advice, and should never be the sole basis of an investment decision. Before investing, talk to a licensed financial advisor.
- tr: Bu uygulamadaki örnek dağılımlar halka açık piyasa verileri ve yapay zekâ analiziyle hesaplanır. Öğrenmek içindir, tavsiye değildir; hiçbir yatırım kararının tek dayanağı olmamalıdır. Yatırım yapmadan önce lisanslı bir finansal danışmana başvur.
- de: Die Beispielaufteilungen dieser App werden aus öffentlichen Marktdaten und KI-Analyse berechnet. Sie dienen dem Lernen, nicht der Beratung, und dürfen nie die alleinige Grundlage einer Anlageentscheidung sein. Sprich vor dem Investieren mit einer lizenzierten Fachperson.

**Option B — "it does not know your whole situation"**
- en: Everything this app shows — example allocations, scenarios, figures — is general education built from public market data and AI analysis. It does not know your whole situation, so it is not personal advice. Before investing, talk to a licensed financial advisor.
- tr: Bu uygulamanın gösterdiği her şey — örnek dağılımlar, senaryolar, rakamlar — halka açık piyasa verisi ve yapay zekâ analiziyle hazırlanmış genel bir eğitimdir. Senin durumunun tamamını bilmez, bu yüzden kişisel tavsiye değildir. Yatırım yapmadan önce lisanslı bir finansal danışmana başvur.
- de: Alles, was diese App zeigt — Beispielaufteilungen, Szenarien, Zahlen — ist allgemeine Bildung aus öffentlichen Marktdaten und KI-Analyse. Sie kennt deine Gesamtsituation nicht und ist daher keine persönliche Beratung. Sprich vor dem Investieren mit einer lizenzierten Fachperson.

### `frontend/index.html` `<meta name="description">` (TR only today)

- now: Korkusuz, öğrenerek yatırım: yapay zeka destekli risk profili, **şeffaf portföy önerisi**, emlak + borsa tek çatıda. Eğitim amaçlıdır.
- `og:description` ("…şeffaf risk profili ve portföy rehberi") is fine; `<title>` is English while the meta tags are Turkish — pick one language for all three.

**Option A**
- tr: Korkusuz, öğrenerek yatırım: yapay zekâ destekli risk profili, açıklamalı örnek portföy dağılımları, emlak + borsa tek çatıda. Eğitim amaçlıdır.
- en: Invest without fear, learning as you go: an AI-assisted risk profile, example portfolio splits explained step by step, property and markets in one place. For education only.
- de: Ohne Angst investieren und dabei lernen: KI-gestütztes Risikoprofil, erklärte Beispielaufteilungen, Immobilien und Börse an einem Ort. Nur zu Bildungszwecken.

**Option B**
- tr: Korkusuz, öğrenerek yatırım: yapay zekâ destekli risk profili, portföylerin nasıl çalıştığını sade bir dille anlatan rehber, emlak + borsa tek çatıda. Eğitim amaçlıdır.
- en: Invest without fear, learning as you go: an AI-assisted risk profile, a plain-language guide to how portfolios work, property and markets in one place. For education only.
- de: Ohne Angst investieren und dabei lernen: KI-gestütztes Risikoprofil, ein Leitfaden in einfacher Sprache dazu, wie Portfolios funktionieren, Immobilien und Börse an einem Ort. Nur zu Bildungszwecken.

---

## 6.4 — Currency card (`fx.highMsg`, shown at ≥ 80 % home currency)

| | Text |
|---|---|
| en (now) | Most of your portfolio is in your home currency ({{currency}}). When it weakens, your whole portfolio feels it. **Consider adding foreign-currency assets.** |
| tr (now) | Portföyünün çoğu yerel parada ({{currency}}). {{currency}} değer kaybederse bütün portföy bunu hisseder. **Döviz bazlı varlık eklemeyi düşünebilirsin.** |
| de (now) | Der Großteil deines Portfolios liegt in deiner Heimatwährung ({{currency}}). Wenn sie schwächer wird, spürt es das ganze Portfolio. **Erwäge Anlagen in Fremdwährung.** |

**Why it reads as advice:** the last sentence is a direct portfolio instruction, shown under a red
"Currency risk: High" badge, for an ordinary position — the same rule fires for a German reader who
holds euros and spends euros. The card's own `fxHeavyMsg` (the opposite case) already does it the
right way: both sides, then "make it a deliberate choice".

**Option A — describe, then say what would move it**
- en: Most of your portfolio is in {{currency}}, the currency you also spend. If {{currency}} weakens, the whole portfolio weakens with it. Assets priced in other currencies are what would change this split.
- tr: Portföyünün çoğu, harcamalarını da yaptığın para olan {{currency}} cinsinden. {{currency}} değer kaybederse portföyün tamamı bunu hisseder. Bu dağılımı değiştiren şey, başka para birimleriyle fiyatlanan varlıklardır.
- de: Der Großteil deines Portfolios liegt in {{currency}}, der Währung, in der du auch ausgibst. Wird {{currency}} schwächer, spürt das das ganze Portfolio. Ändern würden diese Aufteilung Anlagen in anderen Währungen.

**Option B — both sides, mirrors `fxHeavyMsg`**
- en: Most of your portfolio is in {{currency}}. That matches your rent and shopping, which are priced in it too; the flip side is that if {{currency}} loses value against other currencies, nothing in the portfolio offsets it. Neither split is right or wrong — it helps to know which one you have.
- tr: Portföyünün çoğu {{currency}} cinsinden. Kiran ve mutfak masrafların da {{currency}} ile fiyatlandığı için bu, harcamalarınla örtüşür; öbür yüzü, {{currency}} diğer paralar karşısında değer kaybederse portföyde bunu dengeleyen bir şey olmamasıdır. İki dağılımın da doğrusu ya da yanlışı yok; hangisine sahip olduğunu bilmek işe yarar.
- de: Der Großteil deines Portfolios liegt in {{currency}}. Das passt zu Miete und Einkäufen, die ebenfalls darin bezahlt werden; die Kehrseite: Verliert {{currency}} gegenüber anderen Währungen an Wert, gleicht im Portfolio nichts das aus. Keine Aufteilung ist richtig oder falsch — gut zu wissen, welche du hast.

**Code note (goes with either option):** the badge says `fx.riskLabel` + `fx.high` ("Currency risk:
High") in `var(--red)` (`CurrencyExposure.jsx:64`). Suggest the same neutral `--firefly` the
`fxHeavyMsg` case already uses, and a descriptive badge instead of "High":
- tr: "Ağırlıklı yerel para" · en: "Mostly home currency" · de: "Überwiegend Heimatwährung"

**Related, not in the audit item:** `fx.midMsg` grades the split ("a reasonable balance… gives
partial protection"). Milder, but still a verdict; worth deciding at the same time.

---

## 6.18 — Plans page and the holdings "rebuild" button

### `plans.sameAdvice`

| | Text |
|---|---|
| en (now) | A paid plan changes the AI advisor only: more daily messages and a stronger model. **Recommendations**, calculations and every figure are the same for everyone. |
| tr (now) | Ücretli plan yalnızca yapay zekâ danışmanını değiştirir: günlük mesaj hakkı ve daha güçlü bir model. **Öneriler**, hesaplar ve her rakam herkes için aynıdır. |
| de (now) | Ein bezahlter Plan ändert nur den KI-Berater: mehr Nachrichten am Tag und ein stärkeres Modell. **Empfehlungen**, Berechnungen und jede Zahl sind für alle gleich. |

**Why it reads as advice:** it names "recommendations" as something the app produces — on the page
where money changes hands.

**Option A — swap one word**
- en: A paid plan changes the AI advisor only: more daily messages and a stronger model. Examples, calculations and every figure are the same for everyone.
- tr: Ücretli plan yalnızca yapay zekâ danışmanını değiştirir: günlük mesaj hakkı ve daha güçlü bir model. Örnekler, hesaplar ve her rakam herkes için aynıdır.
- de: Ein bezahlter Plan ändert nur den KI-Berater: mehr Nachrichten am Tag und ein stärkeres Modell. Beispiele, Berechnungen und jede Zahl sind für alle gleich.

**Option B — say what stays the same, free included**
- en: A paid plan changes the AI advisor only: more daily messages and a stronger model. Everything else — the example portfolios, the calculations, every figure and explanation — is the same on every plan, free included.
- tr: Ücretli plan yalnızca yapay zekâ danışmanını değiştirir: günlük mesaj hakkı ve daha güçlü bir model. Geri kalan her şey — örnek portföyler, hesaplar, her rakam ve açıklama — ücretsiz dahil her planda aynıdır.
- de: Ein bezahlter Plan ändert nur den KI-Berater: mehr Nachrichten am Tag und ein stärkeres Modell. Alles andere — Beispielportfolios, Berechnungen, jede Zahl und Erklärung — ist in jedem Plan gleich, auch im kostenlosen.

**Related question:** "advisor / danışman / **Berater**" is the paid product's name. In German
*Berater* sits next to *Anlageberatung* (regulated investment advice), and selling "a stronger
Berater" is close to selling better advice. Worth a separate decision (e.g. "KI-Assistent",
"yapay zekâ asistanı", "AI guide").

### `holdings.rebuildCta` (button → `/recommend`)

| | Text |
|---|---|
| en (now) | ↻ **Update my portfolio** with the remaining {{amount}} |
| tr (now) | ↻ Kalan {{amount}} ile **portföyümü güncelle** |
| de (now) | ↻ **Portfolio** mit den verbleibenden {{amount}} **aktualisieren** |

**Why it reads as advice:** "update my portfolio" implies the app will tell the reader what to buy
next with real money they still hold.

**Option A — "see an example"**
- en: ↻ See an example split for the remaining {{amount}}
- tr: ↻ Kalan {{amount}} için örnek bir dağılım gör
- de: ↻ Beispielaufteilung für die verbleibenden {{amount}} ansehen

**Option B — a question**
- en: ↻ How could the remaining {{amount}} be split?
- tr: ↻ Kalan {{amount}} nasıl bölünebilir?
- de: ↻ Wie ließen sich die verbleibenden {{amount}} aufteilen?

---

## Your choices

| Item | String | Choice (A / B / edit) |
|---|---|---|
| 1.18 | `disclaimerModal.doesBody` | |
| 1.18 | `disclaimerModal.detail` | |
| 1.18 | `index.html` meta description (+ one language for title/meta) | |
| 6.4 | `fx.highMsg` | |
| 6.4 | badge colour + text | |
| 6.4 | `fx.midMsg` (related) | |
| 6.18 | `plans.sameAdvice` | |
| 6.18 | `holdings.rebuildCta` | |
| 6.18 | "advisor / danışman / Berater" name (related) | |
