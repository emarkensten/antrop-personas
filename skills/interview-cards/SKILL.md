---
name: interview-cards
description: "Produce A3 landscape workshop cards summarising each individual interview participant. One card per actual participant, with AI-photo portrait (D1b policy applies — never stick figures). Distinct from design-archetypes which produces composites."
metadata:
  version: "1.1.0"
  pipeline-step: "1b"
  works-on: persona-research
  side-branch: "true"
  triggers: "gör intervjukort, skapa kort per intervju, intervjukort till workshop, intervju-kort, deltagarkort, wall cards, participant cards, make a card for each interview, ge mig ett kort per deltagare, kort till workshopväggen, kort att klistra upp, summary card per participant"
---

## Portrait policy (D1b — hard rule)

**Default photo policy = `ai-photo`** via `gemini-image-gen`, using the locked series brief in `${CLAUDE_PLUGIN_ROOT}/skills/design-archetypes/references/portrait-style.md`. On generation failure, fall back to `initials-disc` — large accent-coloured disc with IP-id or initials. **NEVER** stick figures, empty silhouettes, geometric placeholders, or stock-photo avatars.

Other styles (stipple, illustration, animal) require explicit analyst choice in pre-design briefing question #2.

# Interview cards

Turn cleaned interviews into A3 landscape workshop cards — one card per participant. The card is a wall-poster summary the workshop team can stand around and discuss. Verbatim quotes, structured fields, AI-generated portrait avatar.

This is a **side-step**, not part of the eight-step persona pipeline. It can be invoked any time after `clean-interview` has produced cleaned transcripts. It does not depend on themes, framework, or archetypes — and nothing in the persona pipeline depends on it. Pure workshop artefact.

## Pipeline state

This skill is **step `1b-interview-cards`** — a side-branch off step 1. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `clean-interview` (with at least 1 completed cleaned interview for whichever participants the cards are being made for). If the requested interview hasn't been cleaned yet, halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md`.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, brand, and illustration policy. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, list of card paths). Does **not** block any downstream skill — even if cards are never made, the persona pipeline runs cleanly.

## What this skill does

- Walks the analyst through a short pre-render briefing (which interviews to make cards for, which fields to use, language, photo policy)
- Reads the cleaned interview(s) and extracts the field content per the configured template
- Generates an AI portrait avatar for each participant via the `gemini-image-gen` skill — stipple/duotone style, matching Antrop brand
- Renders A3 landscape HTML + PDF, one card per participant
- Saves everything under `personas-project/01-interviews/cards/`

## When to use this skill vs `design-archetypes`

| Question | This skill | `design-archetypes` |
|----------|------------|---------------------|
| What does each card show? | One real participant | A composite of 2–4 participants |
| Identifies real people? | Yes (pseudonymous IP-id) | No (composite name + age) |
| Purpose | Workshop wall — get familiar with respondents | Strategy work — design targets |
| When in pipeline | After `clean-interview` (any time) | After `validate-archetypes` |
| Photo / illustration | AI portrait (stipple/duotone) | AI illustration (metaphor, not person) |

If the analyst asks for "designa personas" → that's `design-archetypes`. If "gör kort per intervju / per deltagare / till workshop-väggen" → that's this skill.

## Inputs

- Cleaned interviews in `personas-project/01-interviews/cleaned/` (or wherever `clean-interview` saved them)
- The card field template — defaults to `references/card-template.md` (the AMF/Sparafasen field set). Per-project overrides allowed via `personas-project/<project>/.persona-config.md` or a project-local `card-template.md`.
- Optional: a research brief that names the project (used in the card header — e.g. "INTERVJUKORT AMF SPARAFASEN")

## The five-beat checkpoint flow

### 1. Read

Open `state.json`. Confirm `clean-interview` has produced ≥1 cleaned interview. List the available cleaned interviews. Open the card template (default or project-local). Open `state.json.language` and `state.json.brand`.

### 2. Propose

Tell the analyst:

- **Scope** — which interviews to make cards for. Options: all cleaned interviews, a specific subset (by IP-id), or just one. Default: ask explicitly.
- **Field set** — list the current card-template fields (from `references/card-template.md` by default). Allow the analyst to add, remove, or rename fields. Lock the field set before rendering.
- **Photo / illustration policy** — three options (default: AI portrait via `gemini-image-gen`):
  - `ai-portrait` — stipple/duotone illustration, gender-ambiguous unless interview explicitly names. Consistent style across the series.
  - `initials-disc` — no portrait, just the IP-id or pseudonym in a large accent-coloured disc. Fastest, most anonymous.
  - `per-card` — analyst chooses for each card individually.
- **Card header** — what goes in the top-left ("INTERVJUKORT <PROJECT-NAME>" by default). Pull from research brief if available.
- **Format** — A3 landscape, one card per participant, PDF + HTML. Fixed.
- **Language** — from `state.json.language`. Quotes always stay in source language.

### 3. Checkpoint

Analyst confirms scope, field set, photo policy, header. Lock these before any heavy work. Refuse to render until confirmed — same rule as `design-archetypes`.

### 4. Produce

Three deliverables:

- `personas-project/01-interviews/cards/<ip-id>-card.md` (per participant) — the working markdown: each field populated with the analyst-approved content + verbatim source quotes
- `personas-project/01-interviews/cards/interview-cards.html` — the master HTML, self-contained, with Antrop brand CSS variables, A3 landscape via `@page` rules, one section per participant, `page-break-after` on each. `window.print()` produces the PDF.
- `personas-project/01-interviews/cards/Interview Cards v1.pdf` — printed PDF version

**Delegation.** For samples ≥4 cards, delegate the per-card rendering to `card-renderer` (sonnet) — the same agent used by `design-archetypes`. Pass it the field set, the photo policy, and the per-card content. For samples <4, render inline.

**Portrait generation.** When `ai-portrait` is selected, invoke `gemini-image-gen` once per participant with a stipple/duotone prompt template that produces consistent style across the series. Save under `personas-project/01-interviews/cards/portraits/<ip-id>.png`.

For the field content, extract verbatim from the cleaned interview:

- Demographic fields (age, civil status, occupation, segment) — only populate from explicit statements in the interview. **Never infer from context** — that's the NV-v1 age-bracket pitfall.
- Quote fields (Bra citat or equivalent) — verbatim only, with line anchors so the analyst can verify.
- Insight fields (Inställning, drivkrafter, etc.) — concise bullet points that paraphrase the participant's actual points. Each bullet must trace to at least one verbatim quote in the interview, even if the quote isn't shown on the card.
- Strategic recommendation fields (Skulle vara bättre om… or equivalent) — these are *participant-stated wishes*, not designer recommendations. Keep the wall between the two.

### 5. Falsify

Before declaring done:

- Open each card markdown. Spot-check 3 bullet points against the source interview — each must trace to a verbatim quote.
- Open the HTML, render at A3 in a browser, verify each card is single-page with no overflow.
- Print to PDF, verify the per-card portrait loaded and the typography matches `antrop-design-spec.md`.
- Confirm no real names slipped through (only IP-id / pseudonym from cleaned interview).
- Confirm language consistency — no Swedish/English mid-deliverable mix.

If any check fails, fix and re-render.

## Pitfalls

These are the same anti-patterns from the rest of the plugin, scoped to interview cards.

### Pitfall · Inferring demographic fields

If the interview doesn't state the age, the card's Age field stays empty or `[?]`. Don't back-calculate from context. Same rule as `clean-interview`.

### Pitfall · Sharpening quotes to fit the card layout

If the chosen quote is too long for the layout, pick a different verbatim quote — don't paraphrase inside quotation marks. Same rule as `generate-archetypes` and `design-archetypes`.

### Pitfall · Putting designer recommendations in participant fields

The "Skulle vara bättre om…" field is for *participant-stated wishes*. If the participant didn't say it, it doesn't go there. Designer-side recommendations live in a separate document, never on the card.

### Pitfall · AI portraits that drift in style

If you generate one portrait at a time without locked consistency rules, the series ends up with mixed aesthetics (one looks like a watercolour, one looks like a photo, one looks like a logo). Lock the prompt template at the start and reuse for every portrait. Verify visually that the series is consistent before declaring done.

### Pitfall · Cards that quietly re-identify

Combinations of fields (rare role + specific neighbourhood + specific age) can re-identify even with the name redacted. The interview-card combines several such fields by design. Apply the indirect-identifier check from `clean-interview/references/anonymisation-policy.md` to each card before declaring done. If the combination is risky, drop or redact one of the fields.

## Delegation

- `${CLAUDE_PLUGIN_ROOT}/agents/card-renderer.md` (sonnet) — handles per-card HTML + PDF rendering when sample ≥4
- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` (haiku, parallel) — first-pass extraction of field content per interview; analyst then approves before render

The `gemini-image-gen` skill (external) handles portrait generation.

## References

- `references/card-template.md` — Default field set (AMF/Sparafasen template) with editing instructions
- `references/card-html-template.html` — Self-contained A3 print-ready HTML template, populated per participant
- `../../references/cross-cutting-principles.md` — The five principles all skills follow
- `../../skills/design-archetypes/references/antrop-design-spec.md` — Brand spec (typography, colour palette, layout) reused for cards
- `../../skills/design-archetypes/references/antrop-design-tokens.css` — CSS variables for Antrop colours

## Output

- `personas-project/01-interviews/cards/<ip-id>-card.md` (one per participant)
- `personas-project/01-interviews/cards/portraits/<ip-id>.png` (one per participant, if AI-portrait selected)
- `personas-project/01-interviews/cards/interview-cards.html`
- `personas-project/01-interviews/cards/Interview Cards v1.pdf`
- Inline HTML artifact in chat — preview of one representative card
