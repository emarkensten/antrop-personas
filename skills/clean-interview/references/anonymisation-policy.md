# Anonymisation policy — default (from NV v1)

This is the default policy. Override on project setup if the research design differs.

## Direct identifiers — always redact

| Original | Replace with |
|---|---|
| Real first/last names | `[Name]` |
| Employer (specific firm) | `[Employer]` |
| Exact age | Age bracket (`25–34`) **only if explicitly stated** by the participant. Otherwise leave blank. |
| Email, phone, address | `[contact]` |
| Specific personal social media handles | `[social]` |
| Children's / partner's names | `[child]`, `[partner]` |

## Indirect identifiers — judgement, log every call

Combinations that could re-identify even after direct redaction. The risk is multiplicative: any two of (rare job, rare neighbourhood, rare life event, rare degree) is usually enough to identify.

Default rules:
- **Stockholm-internal neighbourhoods, streets, the city itself** → KEEP. They are research-relevant for this study population.
- **Locations outside Stockholm** → redact to `[city]`
- **Specific degree programmes** at named universities → redact to `[study]`
- **Rare role titles** combined with sector → generalise (e.g. "Head of X at named NGO" → "leadership role at NGO")
- **Specific events that participant attended** (a named conference, a specific protest with date) → generalise to category if attendance could be identifying

Log every indirect-identifier judgement in the cleaning-summary.md with rationale. The user can override before the file goes anywhere.

## Redaction tokens

Use these consistently so downstream skills can parse them:

- `[Name]` — person's name
- `[child]` / `[partner]` / `[employer]` — relationship/employer placeholders
- `[city]` — city outside Stockholm
- `[study]` — degree programme
- `[?]` — transcription uncertain
- `[pause]` — emotionally meaningful pause
- `[unclear]` — speech genuinely indecipherable

Never use real names inside brackets (even with markup), and never use partial redactions like `J.` for "Johanna".

## What you do NOT redact

- Verbatim opinions (even if controversial — that's the data)
- Mentioned brands, products, services unless the brand identifies a specific employer
- Inside-Stockholm neighbourhoods (per the carve-out)
- Filler words that carry emotional weight ("um", "I mean" when paired with hesitation about a sensitive topic)
