# Changelog

All notable changes to the `antrop-personas` plugin.

The early release-candidate history (rc5–rc7) was not documented in detail at the
time; the entries below reconstruct it honestly from the manifest, the validation
report, and the source. Only the headline changes are recorded for those.

## [0.11.5-rc3] — 2026-05 (current)

Second compatibility pass after rc2 still failed Cowork's install. The blocker
was the **agent** files, not skill metadata. Verified against Anthropic's own
`plugin-dev` → `agent-development` schema (which the `plugin-validator` agent
enforces): agent frontmatter requires `color` and expects `tools` as an **array**.
The Claude Code *runtime* loader is lenient (the plugin installed locally without
them), but the *validator* is strict — that gap is why rc2 passed locally yet
failed in Cowork.

- All 6 agents: added a required `color` (distinct per agent: interview-reader
  blue, thematic-analyser cyan, archetype-drafter magenta, card-renderer green,
  audit-runner yellow, language-polisher red) and converted `tools` from a
  comma-separated string to a YAML array.
- `commands/start-persona-project.md`: shortened `description` to 52 chars (the
  command schema recommends ≤60 for `/help` display). Left `argument-hint`
  unquoted — bare brackets are the canonical form per the official reference.
- `CLAUDE.md`: documented the agent-frontmatter rules so they can't regress.

No behavioural change — same 11 skills / 6 agents / 1 command.

## [0.11.5-rc2] — 2026-05

Compatibility pass so the plugin installs under stricter validators (Cowork
reported "Plugin validation failed" where the local CLI accepted it). Removed
every non-standard manifest/frontmatter element:

- `plugin.json`: removed the non-standard `metadata` block (dependencies /
  components / documentation). That information lives in `DEPENDENCIES.md`,
  `README.md`, and `VALIDATION_REPORT.md` — it was never functional in the
  manifest. Now only standard keys remain (name/version/description/author/keywords).
- Agents: removed the non-standard `effort:` frontmatter field (kept the intent
  documented in `DEPENDENCIES.md` § delegation), and switched `model:` from full
  IDs to the portable `opus` / `sonnet` / `haiku` aliases (which resolve to the
  current top model per tier).
- The packaged `.plugin` archive no longer bundles `marketplace.json` (a direct
  plugin install only needs `plugin.json`; the marketplace manifest stays in the
  repo for the local-marketplace install path).

No behavioural change to the pipeline — same 11 skills / 6 agents / 1 command.

## [0.11.4-rc1] — 2026-05

- **Corrected portrait-model guidance** in `DEPENDENCIES.md` after checking the
  live model list (2026-05-29) and the Nano Banana naming. Both relevant models
  are Gemini 3.1: **Nano Banana Pro = `gemini-3-pro-image`** (professional,
  "Thinking" — the **quality default for portraits**) and Nano Banana 2 =
  `gemini-3.1-flash-image` (high-efficiency, for volume/`--dry-run`). Added an
  instruction to **read the model from the live `client.models.list()`** rather
  than pinning a string, noted Imagen 4 is a weaker fit for the editorial brief,
  and that `gemini-3.5-flash` is text-only (not an image model).

## [0.11.3-rc1] — 2026-05

- **Fixed an install blocker.** `marketplace.json` `plugins[].source` was an object
  (`{source:"local",path:"."}`) which the current `claude plugin validate` rejects
  (`plugins.0.source: Invalid input`). Changed to the string form `"./"`. The
  plugin now passes `claude plugin validate` and installs via the CLI.

- **Documented the current portrait model.** `DEPENDENCIES.md` now names the
  correct, verified image model — `gemini-3-pro-image` (Nano Banana Pro), used at
  `image_size: "2K"`, `aspect_ratio: "4:5"` — with `gemini-2.5-flash-image` as the
  cheap fallback, plus a known-good code snippet. Notes explicitly that there is
  no `gemini-3.5-flash` image model and that the model list should be re-checked
  live before a run. Verified end-to-end by generating the SJ Återförsäljare
  portrait series (Sara/Hanna/Lars) with `gemini-3-pro-image`.

## [0.11.2-rc1] — 2026-05

Card-design pass after a real-data render review (AMF Sparafasen deck).

- **Behaviour dot-scales redesigned.** Label, dots, and end-labels were spread
  across the full card width and read as disconnected. Each scale is now a
  self-contained unit — label directly above 5 large, evenly-spaced dots, with the
  low/high end-labels aligned directly beneath the dot track — laid out as a tight
  horizontal band of 3–4 scales. Legible at a glance on a workshop wall. New
  markup: `.scale-track` with explicit `.on`/`.off` dot spans.
- **Audit markers off the card by default** (`hide-audit-markers: yes`). THIN /
  OVER-REACH / UNGROUNDED verdicts belong in `05-validation/audit-findings.md`, not
  on the printed persona. The badge/legend CSS stays for the opt-in QA case.
- **Removed the on-card "AI-genererat porträtt" disclaimer.** AI portraits are
  flagged in the design-handoff README and the cover instead; the card face stays
  clean. The whole `.card-meta` footer row is gone.
- **Fixed front overflow.** The densest persona's pull-quote was clipping off the
  bottom (verified on AMF "Martin", a 9-interview composite). Reclaimed vertical
  space (smaller portrait, removed meta row, tighter goals block); all four AMF
  cards — including the negative persona with its strategy banner — now fit one A3
  page each with the quote band fully visible.

## [0.11.1-rc1] — 2026-05

Bug-fix pass after an independent review.

- **CRITICAL — `verify-quotes.py` no longer silently passes Swedish quotes.** The
  attribution regex only recognised `INTERVIEW`/`IP`, so quotes attributed the
  Swedish way (`— INTERVJU 02 · RAD 142`, `— Intervju 04`) matched nothing and
  the verifier reported "all VERIFIED / exit 0" without auditing a single quote —
  disabling the plugin's named safety net against fabricated quotes for its
  default language. Added `INTERVJU`/`RESPONDENT`/`R`, made the id grammar handle
  hyphenated ids (`1808-29`, `1805-7`) and trailing `· RAD nnn` suffixes, and made
  `find_interview_file` resolve hyphenated ids instead of over-concatenating them.
- Renamed the misleading `LOOSE_MATCH_MIN_RUN` constant (commented as "characters"
  but used as a word count) to `MINOR_PARAPHRASE_MIN_WORDS = 5`, used directly.
- Fixed a config-key mismatch: `generate-archetypes` now reads
  `project.effect-goals-path` (the key `settings/local.md.example` actually
  defines), not `project.effect-goals`.
- Minor: de-duplicated `Sofo` in the default city-keep-list; reworded the README
  skill-count prose ("eight steps + two side-branches" rather than "ten steps");
  made the `.doc`→txt LibreOffice branch strip the suffix case-insensitively.

## [0.11.0-rc1] — 2026-05

- **Robust input ingestion.** Discovery and conversion now accept whatever the
  analyst already has, in whatever folder layout: added `.doc`, `.rtf`,
  `.vtt`/`.srt` (caption/auto-transcript exports), `.json` (Otter/Whisper/Teams),
  `.html`, and `.csv` on top of `.pdf`/`.docx`/`.md`/`.txt`. New
  `references/input-ingestion.md` contract covers arbitrary folder names,
  interview-vs-support-material triage, and awkward structures (one file →
  many interviews, one participant split across files, mixed cleaned+raw),
  plus stable participant-ID inference recorded in `01-interviews/id-map.md`.
- **Self-contained, redesigned A3 cards.** Rebuilt the double-sided persona-card
  template + tokens: fixed the undefined `--antrop-*` strategy-banner colours,
  added the behaviour dot-scale and goal hierarchy to the template, cleaner
  editorial grid (hero + 3 Cooper columns + quote band on the front; drop-cap
  narrative + 3-quote sidebar on the back), and a more legible offline font
  fallback. **`canvas-design` is now an optional enhancement, OFF by default
  (`use-canvas-design: no`)** — the bundled template + `render-pdf.py` produce
  the complete, print-ready deliverable on their own, so users no longer need a
  separate skill installed for a polished result.
- **`render-pdf.py` finds installed browsers.** The Chromium probe now also
  checks macOS app bundles (`/Applications/Google Chrome.app`, Chromium, Edge,
  Brave) and common Windows paths — so the default render works on a normal Mac
  where Chrome isn't on `PATH`, instead of falling through to absent engines.

## [0.10.0-rc1] — 2026-05

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
