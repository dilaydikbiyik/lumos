# Store submission pack

Everything a reviewer or a form asks for, written once and kept here so the
answers stay consistent between Apple and Google — the two questionnaires ask
the same things in different words, and answering them differently is how an
app gets a follow-up question it doesn't need.

Anything marked **[you]** needs an account, a payment or a signature and
cannot be done from the codebase.

---

## Identity

| Field | Value |
|---|---|
| App name | Lumos |
| Subtitle (iOS, ≤30 chars) | Learn investing without fear |
| Short description (Play, ≤80) | Learn investing with real data, before you risk real money. |
| Bundle id / package | `app.lumos.mobile` |
| Category | **Finance** (secondary: Education) |
| Content rating target | 4+ / PEGI 3 — no gambling, no user-to-user content |
| Support email | dilaydikbiyik@gmail.com |
| Privacy policy URL | `https://<domain>/privacy` |
| Terms URL | `https://<domain>/terms` |

The bundle id is decided and must never change — it is the one value both
stores treat as permanent identity. `app.lumos.mobile` is chosen over a
`com.` reverse domain because the domain isn't bought yet and a bundle id
naming a domain someone else owns is a rejection waiting to happen.

---

## Review notes (paste into both consoles)

> Lumos is an educational tool for first-time investors. It does not execute
> trades, hold funds, connect to any brokerage, or provide personalised
> investment advice. Every portfolio it shows is an illustration built from
> public data — the Turkish central bank, the US Bureau of Labor Statistics,
> the St. Louis Fed, Eurostat and the Deutsche Bundesbank — and every screen
> that shows one also shows the assumptions behind it and a disclaimer that
> it is not advice. There is no payment flow and no real money anywhere in
> the app. The "practice" feature is explicitly play money.
>
> The app supports Turkish, English and German, and three markets (Türkiye,
> United States, Germany). Language and market are independent: a reviewer
> reading English can inspect the German market. Both are switchable from the
> header on every screen.
>
> Account deletion is at Profile → Delete my account. It erases the profile,
> all holdings and all feedback, then deletes the login itself. Please use the
> demo account below rather than the deletion flow if you would like the
> account to remain available for a second review pass.

## Demo account for reviewers

**[you]** Create a dedicated reviewer account — do not hand over a personal
one, because the review may delete it while testing the deletion flow.

- Email: `review@<domain>` · password stored in the console's credential field
- Seed it with: a completed risk profile, 3–4 holdings across asset types, and
  a market set to **US** so an English-speaking reviewer sees familiar tickers
- The free AI tier allows 50 messages/day, which is ample for a review

---

## Data Safety (Play) and App Privacy (Apple)

Both forms ask the same three questions per data type: is it **collected**, is
it **linked to the user**, and is it used for **tracking**. Lumos answers
*no tracking* to every row — there are no advertising identifiers and no
third-party analytics.

| Data type | Collected | Linked to user | Tracking | Purpose |
|---|---|---|---|---|
| Email address | Yes | Yes | No | Account management, authentication |
| Name | Yes | Yes | No | Account management |
| Financial info — *other financial info* | Yes | Yes | No | App functionality (the profile and holdings the user types in) |
| User content — *other user content* | Yes | Yes | No | App functionality, support (feedback messages, advisor chat) |
| Diagnostics / crash data | Yes (if Sentry enabled) | No | No | Diagnostics |
| Identifiers — advertising | **No** | — | — | — |
| Location | **No** | — | — | — |
| Contacts, photos, health, browsing history | **No** | — | — | — |

Notes both forms have a field for:

- **No payment or banking data is collected.** The app never asks for card
  numbers, bank credentials or brokerage logins. Holdings are figures the user
  types by hand; there is no account linking of any kind.
- **Data is encrypted in transit** (HTTPS everywhere).
- **The user can request deletion, and can delete in-app** — Play's form has a
  specific question for this; the answer is yes to both, and the URL is the
  privacy policy above.
- **Third parties that receive data:** Clerk (authentication), Neon (database,
  Frankfurt), Render (application server, Oregon), Vercel (web delivery), and
  one AI provider per request (Google Gemini, Groq or OpenRouter) which
  receives the message plus the profile context needed to answer, never the
  name or email.

### Age rating questionnaire

- Does the app contain financial services or advice? → **Financial information
  and education only. No trading, no brokerage, no advice.** Both stores allow
  a free-text qualifier here; use that sentence. Answering a bare "yes" to
  "financial services" invites a licence question the app cannot answer,
  because it holds no licence and needs none.
- Gambling, contests, simulated gambling → **No.** The practice mode uses play
  money to rehearse a decision; it has no wagering, no odds and no prizes.
- User-generated content shared between users → **No.** Feedback goes to the
  developer only; nothing a user writes is visible to any other user.
- Unrestricted web access → **No.** Outbound links go to named listing portals
  and open in the system browser.

---

## Store descriptions

The same three languages the app itself ships. Each store keeps its own copy;
these are the source of truth.

### English

**Short:** Learn investing with real data, before you risk real money.

**Full:**
> Most investing apps assume you already know what you're doing. Lumos assumes
> you don't, and treats that as the normal place to start.
>
> It builds you an illustrative portfolio from a short risk questionnaire, then
> spends the rest of its time explaining it: why this split, what each asset
> actually is, and what it would have done through the worst stretch of its own
> history. You can rehearse the whole thing with play money first.
>
> Every number is real. Inflation, house prices and rents come from official
> sources — the Turkish central bank, the US Bureau of Labor Statistics, the
> St. Louis Fed and the Deutsche Bundesbank — and when a figure is out of date,
> the app says so instead of quietly showing you an old one.
>
> Lumos also answers the question most investing apps ignore: should you be
> buying a home instead? The rent-vs-buy tool uses your market's actual
> mortgage rate, transfer taxes and agency fees, and prints every assumption
> underneath the answer so you can disagree with it.
>
> Three markets — Türkiye, the United States and Germany — and three languages,
> chosen independently. Read in English while investing in Türkiye, or in
> Turkish while looking at Germany.
>
> Lumos is educational. It executes no trades, holds no money, connects to no
> brokerage, and is not investment advice.

**Keywords (iOS, ≤100 chars):**
`investing,beginner,portfolio,ETF,inflation,rent vs buy,real estate,finance,learn,risk`

### Türkçe

**Kısa:** Gerçek parayı riske atmadan önce, gerçek veriyle yatırımı öğren.

**Uzun:**
> Çoğu yatırım uygulaması ne yaptığını zaten bildiğini varsayar. Lumos
> bilmediğini varsayar ve bunu başlamak için gayet normal bir yer sayar.
>
> Kısa bir risk anketinden örnek bir portföy kurar, sonra kalan bütün zamanını
> onu anlatmaya harcar: neden bu dağılım, her varlık aslında nedir ve kendi
> geçmişinin en kötü döneminde ne yapmıştır. Hepsini önce sahte parayla prova
> edebilirsin.
>
> Her sayı gerçek. Enflasyon, konut fiyatları ve kiralar resmî kaynaklardan
> gelir — TCMB, ABD Çalışma İstatistikleri Bürosu, St. Louis Fed ve Deutsche
> Bundesbank — ve bir veri eskidiğinde uygulama bunu sessizce göstermek yerine
> sana söyler.
>
> Lumos çoğu yatırım uygulamasının görmezden geldiği soruyu da yanıtlar: acaba
> ev mi almalısın? Kira–satın alma aracı, pazarının gerçek kredi faizini, tapu
> harcını ve emlakçı komisyonunu kullanır ve her varsayımı cevabın altına
> yazar; itiraz edebilesin diye.
>
> Üç pazar — Türkiye, ABD ve Almanya — ve üç dil, birbirinden bağımsız
> seçilir. İngilizce okuyup Türkiye'de yatırım yapabilir, Türkçe okuyup
> Almanya'ya bakabilirsin.
>
> Lumos eğitim amaçlıdır. İşlem gerçekleştirmez, para tutmaz, hiçbir aracı
> kuruma bağlanmaz ve yatırım danışmanlığı değildir.

**Anahtar kelimeler:**
`yatırım,başlangıç,portföy,ETF,enflasyon,kira mı ev mi,emlak,finans,öğren,risk`

### Deutsch

**Kurz:** Investieren mit echten Daten lernen, bevor echtes Geld im Spiel ist.

**Lang:**
> Die meisten Anlage-Apps setzen voraus, dass du schon weißt, was du tust.
> Lumos setzt das Gegenteil voraus — und behandelt es als den normalen Anfang.
>
> Aus einem kurzen Risiko-Fragebogen entsteht ein beispielhaftes Portfolio, und
> danach erklärt die App vor allem: warum diese Aufteilung, was jede Position
> wirklich ist und wie sie sich in der schlechtesten Phase ihrer eigenen
> Geschichte verhalten hat. Alles lässt sich zuerst mit Spielgeld proben.
>
> Alle Zahlen sind echt. Inflation, Immobilienpreise und Mieten stammen aus
> offiziellen Quellen — der türkischen Zentralbank, dem US Bureau of Labor
> Statistics, der St. Louis Fed und der Deutschen Bundesbank — und wenn ein
> Wert veraltet ist, sagt die App es, statt ihn stillschweigend zu zeigen.
>
> Lumos beantwortet auch die Frage, die andere Apps auslassen: solltest du
> stattdessen kaufen? Der Mieten-oder-Kaufen-Rechner nutzt den tatsächlichen
> Kreditzins deines Marktes, Grunderwerbsteuer und Maklerprovision und schreibt
> jede Annahme unter das Ergebnis — damit du widersprechen kannst.
>
> Drei Märkte — Türkei, USA und Deutschland — und drei Sprachen, unabhängig
> voneinander wählbar. Lies auf Deutsch und schau auf die Türkei, oder
> umgekehrt.
>
> Lumos ist ein Lernwerkzeug. Es führt keine Order aus, hält kein Geld, ist mit
> keinem Broker verbunden und ist keine Anlageberatung.

**Keywords:**
`investieren,anfänger,portfolio,ETF,inflation,mieten oder kaufen,immobilien,finanzen,lernen,risiko`

---

## What's new (first release)

- **en:** First release. Three markets, three languages, and every number
  sourced from official data.
- **tr:** İlk sürüm. Üç pazar, üç dil ve resmî kaynaklardan gelen her sayı.
- **de:** Erste Version. Drei Märkte, drei Sprachen und jede Zahl aus
  offiziellen Quellen.

---

## Screenshots

`node demo/capture.mjs` produces the gallery, and `STORE=1` adds the exact
canvas sizes both stores require. Run it once per language:

```bash
STORE=1 LANG_UI=en node demo/capture.mjs
```

Output lands in `demo/screens/<lang>/store/`. Required sizes:

| Store | Size | Pixels |
|---|---|---|
| Apple | 6.7" (iPhone 15/16 Pro Max) | 1290 × 2796 |
| Apple | 6.5" (iPhone 11 Pro Max) | 1242 × 2688 |
| Google Play | Phone | 1080 × 1920 (min 320px shortest side) |
| Google Play | Feature graphic | 1024 × 500 — **[you]**, a designed banner, not a screenshot |

Apple accepts the 6.7" set for the 6.5" slot in most cases, but supplying both
avoids the one review round-trip where it doesn't.

---

## Still **[you]**

1. Apple Developer Program, $99/yr — individual enrolment publishes under your
   legal name unless you register a company.
2. Google Play Console, $25 once — individual accounts need identity
   verification and a 14-day closed test with 12 testers before production.
3. A domain, and a **Clerk production instance** on it with your own Google
   OAuth credentials. The dev instance is rate-limited and its sign-in portal
   is a `accounts.dev` subdomain, which reviewers do notice.
4. Render paid tier — a free instance sleeps, and a reviewer who waits 50
   seconds for a cold start files a performance rejection.
5. `SENTRY_DSN`, `GROQ_API_KEY` and `OPENROUTER_API_KEY` in the Render
   dashboard.
6. Whether SPK, BaFin or the SEC consider any of this regulated activity. The
   app is written to stay on the education side of that line — no personalised
   advice, no execution, no custody — but that is a question for a lawyer in
   each jurisdiction, not for a disclaimer.
7. A real device pass: safe-area insets, the language switcher under a thumb,
   and the cold-start path with the backend asleep on a slow connection.
