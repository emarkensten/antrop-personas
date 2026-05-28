---
name: polish-language
description: "Run a second-pass language polish over all working files and designed cards after the design step. Catches non-idiomatic Swedish, anglicisms, mixed-language drift, and 'translation-y' phrasings that survive the first opus draft. Sonnet-based — better Swedish prose at the polish stage than opus."
metadata:
  version: "1.0.0"
  pipeline-step: "7"
  works-on: persona-research
  triggers: "putsa svenskan, språkkontroll, andra passet svenska, kolla språket, polera texten, polish the language, second pass on the language, fixa svenskan, svenskan känns konstig, språkkoll på personas, review the language across the deliverables, klingar inte naturligt"
---

# Polish language

Second-pass language polish over every Swedish-language (or other-project-language) deliverable produced upstream — themes, archetypes, audit findings, designed cards, cover document. Catches the non-idiomatic, "translation-y" phrasings that survive the opus draft.

This is step 7 of 8 in the post-Opus-4.8 pipeline. Runs **after** `design-archetypes` completes (HTML + portraits exist) and **before** `package-for-client`. Sonnet-based because Sonnet's prose handling in Swedish is noticeably more natural than Opus at the second-pass stage, where the structural work is done and only voice/idiom remain.

## Why this exists

The user's observation, encoded as a rule: *"Svenska blir ofta lite dåligt första passet."* Opus is excellent at structure, traceability, and judgement — but its Swedish prose can read as translated-from-English even when no translation happened. The fix isn't to switch the upstream agents to Sonnet (we'd lose the structural quality); the fix is a *second pass* with Sonnet over already-validated material.

The polish step does **not** change facts, verdicts, quotes, or claims. It rewrites only at the prose level: word order, idiom, register, conjunction choice, the "klingar det som svenska?" test. Every change is logged in `07-polish/polish-diff.md` so the analyst can spot-check or reject.

## Pipeline state

This skill is step `7-polish-language` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `design-archetypes` (HTML + portraits must exist; polish runs on the rendered deliverables too).
- **Required-after:** `package-for-client` (the cover document and final bundle should incorporate the polished text).

At its **Produce** beat it updates `state.json` for this step (status `completed`, `polished_files` count, output paths).

## What this skill does

- Scans the project's deliverables for Swedish-language working files (or other project language)
- Identifies sentences and phrases that read as non-idiomatic, machine-translated, or anglicised
- Rewrites at the prose level — never at the claim level
- Produces a per-file diff for the analyst to scan
- Regenerates `persona-cards.html` if any card text was changed, so the HTML stays in sync with the working markdown

## Inputs

- `personas-project/<project>/02-themes/themes.md`
- `personas-project/<project>/04-archetypes/archetypes.md`
- `personas-project/<project>/05-validation/audit-findings.md`
- `personas-project/<project>/06-design/persona-cards.html` *(the rendered HTML — text only; do not touch CSS / layout)*
- `personas-project/<project>/08-package/cover.md` *(if it already exists)*
- The project language from `state.json` (default `sv`)

## The five-beat checkpoint flow

### 1. Read
Open every Swedish-language deliverable. Catalogue length, headings, and any *.md or *.html content under the project root with project-language text.

### 2. Propose
Surface a short summary to the analyst:
- Files in scope (N files, M words of project-language text)
- Top 5–10 phrases that read most strongly as non-idiomatic, anglicised, or "translation-y" — with proposed rewrites
- Anything the polisher will **refuse** to touch (verbatim quotes inside `"…"`, interview-id attributions, technical terms in `code spans`, audit verdicts)

### 3. Checkpoint
Analyst approves the policy: *polish all files, polish only selected files, polish only obvious issues*. Default is "polish all". Verbatim quotes are **never** polished — the quotation mark is a promise across the entire plugin.

### 4. Produce

Run the polisher over every file in scope. For each file:

1. Read the original
2. Identify polish opportunities — non-idiomatic phrasings, anglicisms (e.g. "addressera" → "ta itu med", "actionable" → "konkret", "engagemang" used as a verb), passive voice where active is cleaner, run-on sentences
3. Apply the polish at the prose level only — preserve every fact, quote, claim, and structural marker (`##` headings, `**bold**`, `> blockquote`)
4. Write the polished version back over the original
5. Append a per-file diff entry to `07-polish/polish-diff.md`

For `persona-cards.html`:
1. Extract the text content of every section
2. Polish the text (NOT the CSS, NOT the structure, NOT the role labels in mono)
3. Re-render the HTML by editing only the inner text of each element
4. Re-run `render-pdf.py` from `design-archetypes/references/` to refresh the PDF
5. Log the changes

**Strict no-touch list (never modify):**
- Verbatim quotes inside `"…"` or `«…»`
- Interview-id attributions (`— IP02`, `— INTERVIEW 04`)
- Audit verdicts (`GROUNDED`, `THIN`, `OVER-REACH`, `UNGROUNDED`, `VERIFIED`, `FABRICATED`)
- Cooper role labels (`PRIMARY`, `SECONDARY`, `CUSTOMER`, `SERVED`, `NEGATIVE`, `OUTLIER`)
- Mono / eyebrow labels (`COMPOSITE OF`, `DRIVKRAFTER`, `SMÄRTOR`, `BEHOV`)
- Effect-goal statements in `effektmål.md` (those are client-facing claims; analyst owns them)
- File names, path references, code spans

### 5. Falsify

Before declaring done:

- Open the polished `archetypes.md`. Confirm every verbatim quote still matches the source interview word-for-word.
- Confirm every audit verdict in `audit-findings.md` is still the same letter-string it was before.
- Confirm `persona-cards.html` still renders without overflow at A3 (PDF re-run output).
- Confirm `polish-diff.md` has one entry per polished file, with before / after pairs.

If any verbatim quote shifted, **revert the change**. The polish never overrides the verbatim rule.

## Languages this skill handles

- **Swedish (sv)** — default. Idiom, word order, conjunction choice, register. Catches anglicisms common in machine output (e.g. "addressera", "actionable", "leverage" used as a verb, "engagemang" misused, run-on conditional clauses).
- **English (en)** — when project language is English: catches translation-from-Swedish patterns ("the user shall be able to" → "users can"), passive-voice overuse, register drift.
- **Bilingual (sv + en)** — runs over both layers; checks that Swedish quotes stay in Swedish and English-language client-deliverable text reads natively.
- **Other languages** — the polisher reads `state.json.language` and applies generic idiom-polish rules; quality is lower for languages outside sv/en. Surface this in the Propose beat so the analyst knows.

## Delegation

After the checkpoint is approved, delegate the actual polish to `language-polisher` (sonnet at high effort) — see `agents/language-polisher.md`. The agent processes one file at a time, returns the polished text + diff, and the parent skill writes both.

- `${CLAUDE_PLUGIN_ROOT}/agents/language-polisher.md`

## Output

- Modified deliverables (in-place) — `themes.md`, `archetypes.md`, `audit-findings.md`, `persona-cards.html`, optional `cover.md`
- `personas-project/<project>/07-polish/polish-diff.md` — per-file diff log, scannable
- Refreshed `personas-project/<project>/06-design/Persona Cards v1.pdf` if any card text changed

## What this skill does NOT do

It does not change facts. It does not re-do the audit. It does not touch verbatim quotes. It does not move sections, re-cluster, or rewrite the narrative wholesale. If the analyst wants any of those, they re-run the relevant upstream skill — `polish-language` is purely a prose-level second pass.
