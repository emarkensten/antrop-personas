# Changelog

All notable changes to the `antrop-personas` plugin.

The early release-candidate history (rc5–rc7) was not documented in detail at the
time; the entries below reconstruct it honestly from the manifest, the validation
report, and the source. Only the headline changes are recorded for those.

## [0.10.0-rc1] — 2026-05 (current)

- **Autonomous mode (`process.mode: auto`)** — a deliberate, explicit switch for
  unattended end-to-end runs (scheduled / overnight Cowork jobs). Every
  checkpoint — including the three otherwise-non-skippable ones (cluster lock B2,
  archetype line-up I1, pre-design briefing D0) — applies its **documented
  default**, logs the decision to `09-auto/auto-decisions.md`, and proceeds
  without pausing. **Quality is not reduced**: every interview is read, the full
  seven-check audit runs, AI portraits (`gemini-image-gen`) and the print-PDF are
  produced, the Swedish polish pass runs, the full bundle is built. Distinct from
  `dry-run` (reduced preview) and `skip-checkpoints` (synthetic/test).
- Open CRITICAL audit findings no longer halt an auto run — they stamp a loud
  *"⚠ AUTONOMOUS RUN — analyst review pending"* banner on the cards + cover and
  set `state.json.auto_review_required`, preserving the H22 safety signal.
- **`run-pipeline` orchestrator skill** (11th skill) — sets `mode: auto` and
  drives all eight main steps + enabled side-branches in order, ending with
  `09-auto/MORNING-REVIEW.md` (ordered decisions, `[inferred]` slots, audit
  counts, open criticals, "what to check first").
- **`start-persona-project`** gains `--auto` and `--run-all` flags; `--run-all`
  scaffolds then hands off to `run-pipeline` for a one-shot scheduled run.
- New state fields: `mode`, `auto_decision_log`, `auto_review_required`. New
  config keys: `process.mode`, `process.auto-decision-log`. New project folder:
  `09-auto/`.
- Fixed stale counts in the `start-persona-project` command ("six required
  steps", "seven cross-cutting principles", "seven skills").

## [0.9.0-rc7.1] — 2026-05

- **`polish-language` skill** (main-path step 7) added: second-pass language
  polish of validated deliverables — catches non-idiomatic Swedish (or the
  project language), anglicisms, and mixed-language drift. Never touches verbatim
  quotes, audit verdicts, or role labels. Produces a diff log.
- **`language-polisher` agent** (sonnet) added to back the new skill.
- **Critical-finding gating** between `validate-archetypes` and `design-archetypes`:
  `validate-archetypes` records open critical findings in `state.json`;
  `design-archetypes` halts at its Read beat until the analyst resolves or
  overrides them.
- Pipeline is now **eight main-path steps** (clean → analyse → frame-and-cluster
  → generate → validate → design → polish-language → package) plus two side
  branches (`interview-cards`, `compare-baseline`).
- Documentation reconciled with the shipped component set (10 skills, 6 agents).

## [0.9.0-rc4] — 2026-05-28

- Excel as the primary working artefact in `frame-and-cluster`
  (`behavioural-variables.xlsx`, three sheets) + non-skippable analyst checkpoint.
- Narrative-prose field per archetype (≥200 words) + double-sided A3 cards.
- AI-photo portraits by default via `gemini-image-gen`, locked series style in
  `portrait-style.md`; `initials-disc` as the only acceptable fallback — never
  stick figures.
- `design-handoff/` folder, sub-variant mini-cards, Outliers card.
- New **`compare-baseline`** skill (Mode B: current archetypes vs a prior
  deliverable, verdict-graded against the source interviews).
- Trigger phrases moved to an explicit `metadata.triggers` YAML list.
- Auto-discovery of interviews in any subfolder; `.pdf`/`.docx`/`.md`/`.txt`
  input; `--input-dir` override.
- WeasyPrint fallback for card PDF rendering; gemini-image-gen ESM-resolution doc.

## [0.9.0-rc3] — 2026-05-27

- Hand-off procedure for running the end-to-end test in a fresh session.
- Two test modes: Mode A (no baseline) and Mode B (compare against human-made
  personas).

## [0.9.0-rc2] — 2026-05-27

- `agents/` directory with sub-agents (haiku/sonnet/opus).
- `settings/local.md.example`, `references/pipeline-state.md`, `DEPENDENCIES.md`.
- Per-skill `## Pipeline state` section; working-format policy (`.md` everywhere
  except client deliveries; `.docx` input converted at `clean-interview`).
- Fixed `marketplace.json` `source` shape and SKILL.md frontmatter
  (`version:` moved under `metadata`).

## [0.1.0]

- Initial pipeline extracted from the Naturvårdsverket v1 project.
