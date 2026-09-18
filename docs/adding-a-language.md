# Adding a language

Language is a **device preference**, deliberately independent of the market: an
expat in Istanbul wants the English UI with Turkish market data, and a Turk in
Berlin may want the opposite. Neither setting implies the other, and
`frontend/src/independence.test.js` enforces that at the source level.

A half-added language is worse than a missing one. i18next falls back silently,
so the app keeps rendering — in the wrong language — and nobody notices. That is
how 163 German keys sat behind the English fallback. Two tests make it loud:

- `test_adding_a_language_means_adding_it_everywhere` (backend) — the six
  registries below must agree exactly.
- `frontend/src/locales/locales.test.js` — the locale files must carry identical
  keys, matching placeholders and matching `<0>` slots.

## The six registries

All six must list the new code, or CI fails.

| # | Where | What |
|---|---|---|
| 1 | `frontend/src/i18n.js` → `LANGUAGES` | `{ code, label }`, label written in that language |
| 2 | `backend/middleware/language.py` → `SUPPORTED` | accepted `X-Lumos-Lang` values |
| 3 | `frontend/src/locales/<code>.json` | the UI copy |
| 4 | `backend/i18n.py` → `_C` | the backend catalogue: every key needs the new language |
| 5 | `backend/prompts/system_prompt.<code>.txt` | the 9-question risk quiz |
| 6 | `backend/prompts/advisor_prompt.<code>.txt` | the free-form advisor |

Plus: every market pack's `broker_note`, `tax_note` and `transfer_cost_note`
needs the new language. The conformance suite checks this per market.

## The steps

### 1. Frontend copy

Copy `frontend/src/locales/en.json` and translate. Keep the keys identical —
that is not a style preference but load-bearing: because the files are proven
complete, the app ships **only the reader's locale** and never downloads the
other two. The fallback chain is a backstop that by contract never fires.

Two things the tests check that are easy to get wrong:

- `{{placeholders}}` must match the reference file exactly. A translation that
  drops `{{amount}}` renders a sentence with a hole in it.
- `<0>` slots must match. A `<0>` without its component swallows the text inside.

Glossary entries carry **both** a `label` (the word as that language writes it)
and a `text` (the explanation). Printing the key as display text is how "reel
getiri" ended up mid-sentence in English.

### 2. Backend catalogue

Every key in `backend/i18n.py` needs the new language. The engines write
sentences, not just numbers — "your loss tolerance carried the most weight",
"cash is the safety cushion" — and those used to be Turkish literals, so a
reader who picked English met Turkish the moment the backend spoke.

Watch for grammar the catalogue cannot express. German capitalises nouns, so
`risk_engine._goal_in_sentence` does not lowercase the goal for `de`; lowercasing
"Wachstum" mid-sentence reads as a typo.

### 3. Prompts

Copy `system_prompt.en.txt` and `advisor_prompt.en.txt`. Keep the marker protocol
(`[PROFILE_COMPLETE]`) and the guardrails identical — `test_prompt_rules.py`
checks the contract, and the quiz is restricted to Gemini/Claude-class models
because weaker ones paraphrase the script.

Prompts that are **instructions to the model** stay in English: the advisor's
USER CONTEXT block and the market snapshot. Written in Turkish they pulled
replies into Turkish whatever the system prompt said. Only the system prompt
decides the answer's language.

### 4. Market packs

Add the language to `broker_note`, `tax_note` and `transfer_cost_note` in every
pack under `backend/markets/`. `market.disclaimer` in the catalogue covers the
shared notice.

### 5. Run both suites

```bash
./venv/bin/pytest -q
cd frontend && npm test && npm run build
```

## Fallback order

`de → en → tr`, `en → tr`, everything else → `tr`. Showing a German reader
English is better than showing them Turkish; Turkish stays the final backstop
because it is the reference file. Both the frontend (`i18n.js`) and the backend
(`i18n.FALLBACK`) implement the same chain.
