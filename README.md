# antrop-personas

Antrop's qualitative-research pipeline for behavioural personas — from raw interview to brand-designed deliverable. **Ten** checkpoint-gated skills that keep the analyst as the decision-maker and Claude as the heavy-lifter.

Built from the Naturvårdsverket v1 project (Stockholm, 2026); v0.9.0-rc7.1 bakes in lessons from the second end-to-end test (2026-05-28) — Excel as the working format for frame-and-cluster, narrative prose on the back of every persona card, AI-photo portraits with locked series style, baseline comparison as a built-in capability, and a dedicated language-polish pass.

## What this plugin does

It walks an analyst through the full pipeline:

1. **clean-interview** — raw `.pdf` / `.docx` / `.md` / `.txt` transcript → cleaned, anonymised, analysis-ready (A2). Recursive auto-discovery of interviews in any subfolder (A1). Auto-PII-scan when skipped (E3).
2. **analyse-themes** — N cleaned interviews → 4–7 cross-cutting themes
3. **frame-and-cluster** — themes → **behavioural-variables.xlsx** (primary artefact, three sheets — B1) + emergent clusters + cluster plot. Non-skippable analyst checkpoint after Produce (B2).
4. **generate-archetypes** — clusters → Cooper-style archetypes **with narrative prose ≥ 200 words per archetype** (C1-C2). Demographics verified against cleaned interviews (E1). Non-skippable checkpoint after Produce (I1).
5. **validate-archetypes** — archetypes + interviews → seven-check validity audit
6. **design-archetypes** — archetypes → Antrop-branded **double-sided** A3 persona cards (C3) with **AI-photo portraits** in locked series style (D1b + D2), audit badges (E2), optional sub-variant mini-cards (D5), Outliers card (H1), and a format-neutral **design-handoff** folder for designers / claude/design (D4b)
7. **polish-language** — second-pass language polish of validated deliverables: catches non-idiomatic Swedish (or the project language), anglicisms, and mixed-language drift. Never touches verbatim quotes, audit verdicts, or role labels. Produces a diff log.
8. **package-for-client** — everything → ordered client deliverable bundle

Plus two **side-branch** skills:

- **interview-cards** — cleaned interviews → A3 workshop cards, one per individual participant (not composites). Same portrait policy (D1b) as `design-archetypes`.
- **compare-baseline** — current archetypes vs a previous deliverable (PDF / docx / markdown / zip). Verdict-grades each pair against the source interviews: PLUGIN-DEFENSIBLE / MANUAL-DEFENSIBLE / BOTH / NEITHER. (F1-F3, new in v0.9.0-rc4.)

Every skill follows the same five-beat checkpoint flow (read → propose → checkpoint → produce → falsify). The analyst owns every decision; Claude does the reading, cross-referencing, and drafting.

## Why a plugin, not one big skill

Qualitative analysis is a sequence of judgement calls, not a pipeline. A monolithic skill hides those calls. Ten skills make them visible — and let you re-run any single step without restarting.

## Installation

Drop the `.plugin` file into Cowork via the plugin install flow, or copy this directory into your Cowork plugins folder.

## Usage

Start a new project:

```
/antrop-personas:start-persona-project <project-name> [--input-dir <path>] [--baseline <path>]
```

`--input-dir` points at the folder where raw interviews live (A3 — for shared Drive folders, atypical subfolder names, etc). `--baseline` points at a prior persona deliverable (PDF / docx / markdown / zip) to be picked up by `compare-baseline` later (F2).

Or invoke any skill directly by mentioning it:

- *"städa intervju 03"* → triggers `clean-interview`
- *"kör tematisk analys på allt under cleaned interviews"* → triggers `analyse-themes`
- *"bygg ett ramverk och plotta deltagarna"* → triggers `frame-and-cluster`
- *"generera arketyper från klustren"* → triggers `generate-archetypes`
- *"jämför med tidigare personor"* → triggers `compare-baseline`
- *"validera arketyperna mot intervjuerna"* → triggers `validate-archetypes`
- *"designa personas i Antrops brand"* → triggers `design-archetypes`
- *"putsa språket i leveransen"* → triggers `polish-language`
- *"paketera leveransen"* → triggers `package-for-client`
- *"gör intervjukort till workshopväggen"* → triggers `interview-cards`

Triggers work in Swedish and English. See each `skills/<name>/SKILL.md` `metadata.triggers` for the full list (G1 — explicit YAML list, not embedded in description).

## Components

| Component | Count | Purpose |
|-----------|-------|---------|
| Skills | 10 | 8 main-path steps + `interview-cards` and `compare-baseline` side-branches |
| Commands | 1 | `/start-persona-project` orchestration entry point |
| Agents | 6 | `interview-reader` (haiku, parallel), `thematic-analyser` (opus), `archetype-drafter` (opus — produces bullets + narrative), `audit-runner` (opus), `card-renderer` (sonnet — double-sided cards, AI portraits, audit badges, handoff folder), `language-polisher` (sonnet — second-pass language polish) |
| Hooks | 0 | None |
| MCP servers | 0 | None — the plugin works with files only |

### Required dependencies

- `docx` — for client-facing reports
- `xlsx` (or `openpyxl`) — for `behavioural-variables.xlsx` (B1)
- Python libraries: `python-docx`, `pypdf`, `openpyxl`

See `DEPENDENCIES.md` for graceful-fail behaviour.

### Recommended dependencies

- `gemini-image-gen` — AI-photo portraits (D1b default policy)
- `canvas-design` — print-PDF iteration loop (D1)
- Python libraries: `pdfplumber` (PDF baseline extraction fallback), `weasyprint` (PDF fallback when chromium unavailable)

## Key design decisions

- **Checkpoint-gated** — no step proceeds to producing output without explicit user approval of the proposed approach. The pitfalls in `references/pitfalls-from-nv-v1.md` mostly came from skipping this.
- **Working markdown + HTML artifact + (optional) docx** — every step produces a markdown file (for the next step and for hand-editing), an HTML artifact (for inspection), and a docx or PDF only when the artefact will leave the project as a client deliverable.
- **Verbatim-source rule** — every claim in any archetype must trace to a verbatim quote in the named composite members' interviews. Strategic recommendations live in their own section, never folded back into participant voice.
- **Antrop brand baked into `design-archetypes`** — the design step has the full Antrop persona-card brand spec in its references and refuses to render without an eight-question pre-design briefing. The brand spec is editable for non-Antrop projects.
- **Swedish default** — analytical writing and client deliverables default to Swedish. Drift to English is treated as a pitfall.

## Reference material in this plugin

- `references/cross-cutting-principles.md` — the five principles every skill follows
- `references/pitfalls-from-nv-v1.md` — concrete misstakes from the Naturvårdsverket project, mapped to the skill they apply to
- `skills/design-archetypes/references/antrop-design-spec.md` — full Antrop persona-card brand spec
- `skills/design-archetypes/references/pre-design-checklist.md` — eight pre-design questions, with defaults
- Per-skill: templates, conventions, and method notes

## Customisation

This plugin is currently tuned for Antrop's workflow. If you fork it for another team:

- Edit `skills/clean-interview/references/anonymisation-policy.md` to remove the Stockholm carve-out and add your own
- Edit `skills/design-archetypes/references/antrop-design-spec.md` to swap in your brand
- Rename the plugin (`antrop-personas` → `<your>-personas`) in `.claude-plugin/plugin.json`

## Version

**0.9.0-rc7.1** — release candidate. Incorporates all HIGH + MEDIUM improvements from `IMPROVEMENT_SPEC_v0.9.0-rc4.md` and the post-rc3 E2E test (2026-05-28).

Since rc4, rc5–rc7.1 added incremental refinements: a dedicated `polish-language` skill (step 7) with its `language-polisher` agent, and critical-finding gating between `validate-archetypes` and `design-archetypes` (design halts on open critical findings until the analyst resolves or overrides).

What's new vs rc3:
- A1-A3 · Auto-discover interviews in any subfolder; `.pdf` / `.docx` / `.md` / `.txt` input; `--input-dir` override
- B1-B2 · Excel as primary artefact in `frame-and-cluster` + non-skippable analyst checkpoint
- C1-C3 · Narrative prose field per archetype (≥200 words) + double-sided A3 cards
- D1-D5 · `canvas-design` routing, locked portrait-style.md, preview iteration, open-source font fallback, `design-handoff/` folder, sub-variant mini-cards. **D1b — AI-photo by default, `initials-disc` as only acceptable fallback, never stick figures.**
- E1-E3 · Demographics verified against cleaned interviews; audit badges on cards; auto-PII-scan when clean-interview is skipped
- F1-F3 · New `compare-baseline` skill (Mode B)
- G1 · Trigger phrases moved to explicit YAML list in `metadata.triggers`
- H1 · Outliers card for edge-zone participants
- I1-I2 · Two non-skippable checkpoints; `--dry-run` mode
- J1-J2 · WeasyPrint fallback for card-renderer; gemini-image-gen ESM-resolution doc

Bump to 1.0.0 only after the next E2E test passes cleanly.
