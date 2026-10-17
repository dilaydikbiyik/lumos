# Legal review brief

What to take to a lawyer, and what to ask. Written because "is this
regulated?" is not a question a lawyer can price or answer — they need to
know what the thing does, and the answer turns on specifics.

Take this document, a login to the app, and `docs/architecture.md`.

---

## 1. What Lumos does, in the terms a regulator uses

State these as facts; they are all verifiable in the codebase and a lawyer
will ask for each one.

- **It does not execute.** There is no order path, no broker integration, no
  API key for any venue. A reader who decides to act does so at their own
  broker, outside the app.
- **It does not hold client money.** There is no wallet, no balance, no
  payment flow. "Holdings" are rows a user types in themselves.
- **It does not take custody of assets.**
- **It produces a deterministic illustration, not a human judgement.** The
  allocation comes from a published formula over a risk score; the same
  answers always give the same output, and the formula is printed on screen
  beside the result.
- **It names specific instruments.** This is the part that matters most. The
  portfolio shows real tickers a reader can go and buy.
- **It personalises to the individual** — budget, horizon, loss tolerance,
  age, debt and income stability all change the output.
- **It is paid-for-nothing today.** No subscription, no commission, no
  referral fee, no payment for order flow, no relationship with any issuer
  of anything it names. A tier table exists in the code but nothing is sold.
- **Three markets:** Türkiye, United States, Germany. Content is tailored per
  market.

## 2. The questions

### The one that decides everything

1. **Does naming specific instruments, personalised to an individual's
   circumstances, constitute investment advice under Turkish capital markets
   law — even with no execution, no custody and no fee?** If yes, what would
   have to change for it not to: generic asset CLASSES instead of tickers,
   removing the personalisation, or something else?

### Then

2. Does the answer change in **Germany (BaFin)** and the **United States
   (SEC / state RIA registration)**? An app on a store is available in all
   three, and the Investment Advisers Act has a different shape from MiFID II.
3. If a licence or registration is needed in any of them, is **geo-blocking a
   market** a realistic alternative to obtaining it?
4. Does **charging money later** change the classification, and if so at what
   point — subscription, one-off, anything at all?
5. Does an **AI-generated explanatory sentence** alongside a deterministic
   allocation change anything? The numbers never come from the model, but the
   prose does.
6. What **disclaimer wording** is actually load-bearing in Turkish law, rather
   than merely customary? The app currently says it is educational and not
   advice, on every screen that states a figure.
7. **Who is liable** if a reader loses money after following an illustration?
   Does a limited company meaningfully change that exposure versus a sole
   trader, and is professional indemnity insurance available and sensible here?
8. The app publishes **educational content about third parties** — regulators,
   fund structures, a real sector event. Any defamation or
   financial-promotion exposure in describing, for example, how a fund
   liquidation worked?
9. **KVKK / GDPR:** the app stores income, debts and holdings. That is
   personal financial data. What does it oblige beyond the privacy policy
   already published — a data controller registration (VERBİS), a DPIA, a
   retention schedule?

### Ask about structure last, not first

10. Given all the above, **does a limited company help, and which kind?** The
    App Store's 5.1.1(ix) prefers a legal entity for financial-services apps,
    which is a reason on its own — but if the answer to question 1 is "this
    needs a licence", the licence decides the structure and not the reverse.

## 3. What NOT to ask

Do not open with "should I set up a limited company?" — a lawyer will say
yes, because it is almost always a reasonable answer, and you will have paid
for advice that did not touch the question that actually gates the product.
Question 1 is the gate.

## 4. Who to ask

A **capital markets (sermaye piyasası) lawyer**, not a general commercial
one. The distinction between investment advice, investment research and
general information is specialist ground, and a generalist will either
over-caution or miss it.

An hour of the right person's time answers questions 1 and 2, which are the
only two that can change what gets built.
