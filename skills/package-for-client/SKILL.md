---
name: package-for-client
description: "Collate the full persona-research project into a single client deliverable. Produces a Cover document + ordered zip bundle including themes, framework, archetypes, validity audit, persona cards, and design-handoff folder."
metadata:
  version: "1.2.0"
  pipeline-step: "8"
  works-on: persona-research
  triggers: "paketera leverans, skapa slutleverans, samla allt till kund, client bundle, package the deliverable, ihop till slutleverans, skicka till kund, leveransbundle, ihopsamlat, allt på ett ställe, samla artefakterna, build the final handover, wrap this up for the client, make a bundle to send out, färdigställ projektet, deliver to the client"
---

# Package for client

Collate the full persona-research project into a single, well-structured client deliverable. The final bundle includes the research brief, themes, archetypes, audit, and designed cards — plus a short executive cover document that orients the reader.

This is step 8 of 8. It assumes all earlier skills have produced their outputs in `personas-project/`.

## Pipeline state

This skill is step `8-package-for-client` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `polish-language` (or `design-archetypes` if `polish-language` is marked `skipped`; or `validate-archetypes` if `design-archetypes` is marked `skipped` for text-only deliveries). If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.

### Surface unrun optional side-branches at this Read beat

Before producing the bundle, scan `state.json` for unrun optional side-branches and surface them to the analyst as a last-chance offer:

- If `state.json.steps['interview-cards'].status` is not `completed` AND ≥1 cleaned interview exists, surface:
  > "Sidogren ej körd: **interview-cards** — per-deltagare workshop-kort. Vill du producera dem innan paketering? (default: nej)"
- If `state.json.steps['compare-baseline'].status` is not `completed` AND `state.json.baseline_path` is set, surface:
  > "Sidogren ej körd: **compare-baseline** — jämför nuvarande arketyper mot tidigare leverans `<baseline_path>`. Vill du köra jämförelsen innan paketering? (default: nej)"
- If `state.json.steps['polish-language'].status` is not `completed`, surface:
  > "**polish-language** har inte körts — andra passet på svenskan rekommenderas före kundleverans. Vill du köra det nu? (default: ja — kraftigt rekommenderat)"

The analyst's answer for each is sticky — if they say nej, the side-branch is recorded as explicitly declined in the cover's "known limitations" section.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Reads the outputs of all earlier steps
- Generates a short executive cover document that explains *what's in the bundle, in what order to read it, and what's known/unknown*
- Assembles the bundle in the right order, with consistent file naming
- Honours the verbatim-quote and strategic-recommendation-wall rules one more time before anything ships
- Produces a single zip or a Notion-/Confluence-ready folder structure

## Inputs

- Everything under `personas-project/` (steps 01–06)
- Optional: client-facing project name (used in cover document and file names)
- Optional: which audience the bundle is for (strategy team, design team, executive readout — controls the cover's framing)

## The five-beat checkpoint flow

### 1. Read
Open the outputs of each step. Confirm everything that the cover document will reference actually exists.

### 2. Propose
Tell the user:

- What the bundle will include — exact list of files
- The order of the cover document (executive summary, what's in the bundle, what each artefact is for, known limitations from the audit, next steps)
- The known weaknesses from `audit-findings.md` that will be surfaced in the cover (don't hide them)
- The bundle format (zip, folder, Notion import) and the file naming convention

### 3. Checkpoint
The user approves the contents, the cover framing, and the bundle format. Edits to the cover happen here.

### 4. Produce
Two deliverables:

- `personas-project/08-package/Cover.md` (also rendered as docx) — the executive cover
- `personas-project/08-package/<client>-personas-bundle.zip` — the full bundle, ordered

Bundle structure:

```
<client>-personas-bundle.zip
├── 00 — Cover.docx                       # executive cover, read first
├── 01 — Themes.docx                      # from analyse-themes
├── 02 — Behavioural variables.xlsx       # from frame-and-cluster (primary artefact, B1)
├── 02 — Framework.docx                   # from frame-and-cluster (text export)
├── 03 — Participant plot.pdf             # from frame-and-cluster
├── 04 — Archetypes.docx                  # from generate-archetypes (text version, includes narrative)
├── 04b — Baseline comparison.docx        # from compare-baseline (if run, F1-F3)
├── 05 — Validity audit.docx              # from validate-archetypes
├── 06 — Persona cards.pdf                # from design-archetypes (double-sided, C3)
├── 06 — Persona cards — clean.pdf        # client version with audit badges hidden (if rendered, E2)
├── 06 — Persona cards.html               # for iterative editing
├── 06 — Design handoff/                  # raw material for designers / claude/design (D4b)
└── 07 — Auto-anonymisation summary.md    # only when clean-interview was skipped (E3)
```

Cover document structure:
- **Review banner (conditional)** — if `state.json.mode == "auto"` OR `state.json.auto_review_required == true`, the cover opens with a prominent banner before the executive summary: **"⚠ AUTONOMOUS RUN — this bundle was produced unattended with documented defaults. Decisions are logged in `09-auto/auto-decisions.md` / `09-auto/MORNING-REVIEW.md`. \<N\> open CRITICAL audit findings were not reviewed by an analyst. Review before any client use."** (Drop the open-CRITICAL clause if `open_critical_findings` is empty.) This is the review-pending stamp for full-quality auto runs — distinct from the `skip-checkpoints` synthetic stamp.
- **Executive summary** — 3-5 sentences: what the research found, how many archetypes, what's primary and what's negative
- **What's in this bundle** — the file list with one-line descriptions
- **How to read it** — recommended order, with notes on which artefact answers which question
- **Known limitations** — surface the top 3 findings from the audit. Don't hide them.
- **Next steps** — what the client could do with this (workshop, strategy work, further quantitative validation)

**Morning-review summary (auto mode).** When `state.json.mode == "auto"`, also write `09-auto/MORNING-REVIEW.md` and place it at the top of the bundle (`00b — MORNING-REVIEW.md`): the ordered list of every auto-decision from `auto-decisions.md`, every `[inferred]` slot across archetypes, the audit finding counts, any open CRITICAL findings, and a one-line "what to check first". This is the analyst's entry point when they wake up.

### 5. Falsify
Run a **last-mile self-check** before declaring done:

- Open the bundle, walk through it in the suggested reading order, confirm it makes sense to someone who hasn't seen the project
- Spot-check three random quotes in the designed cards against archetypes.md and against the source interviews
- Confirm the audit's most important findings appear in the cover (a buried audit is no audit)
- Confirm no Anthropic-internal or sandbox-internal paths leak into any document

## Pitfalls — what went wrong on NV v1

### Pitfall · Burying the audit
The validity audit is the most important risk-management artefact in the bundle. If the cover doesn't surface its top findings, the client will likely never read it and will treat the archetypes as fully validated.

### Pitfall · Late-stage quote changes
A designer adjusting the layout for visual fit might shorten or paraphrase a quote on a card. **Don't.** Either pick a different shorter quote that exists verbatim, or change the layout. The verbatim rule holds all the way to delivery.

### Pitfall · Strategic recommendations creeping into archetype descriptions in the bundle
The cover can recommend next steps. The archetype text cannot. Re-check the bundle for strategic-recommendation language that has migrated into the persona descriptions.

### Pitfall · Inconsistent language across the bundle
If half the cover is in Swedish and the archetype cards are in English, the bundle reads as half-finished. Lock language at the start of the cover step and apply it consistently.

## References

- `references/cover-template.md` — Full cover-document template
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/08-package/Cover.docx`
- `personas-project/08-package/<client>-personas-bundle.zip`
