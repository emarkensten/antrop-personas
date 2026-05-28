---
name: run-pipeline
description: "Run the whole persona pipeline end-to-end, unattended, with documented defaults — clean → analyse → frame-and-cluster → generate → validate → design (incl. gemini AI portraits) → polish → package (incl. print-PDF). For scheduled / overnight Cowork runs where the analyst wants finished, full-quality personas waiting in the morning. Sets mode:auto, applies and logs every default decision, never reduces quality, and writes a MORNING-REVIEW summary. Distinct from dry-run (preview) and skip-checkpoints (synthetic)."
metadata:
  version: 1.0.0
  pipeline-step: orchestrator
  works-on: persona-research
  triggers:
    - "kör hela personaflödet"
    - "kör hela pipelinen"
    - "automatkör personas"
    - "kör allt automatiskt"
    - "gör personas medan jag sover"
    - "gör klart personas tills imorgon"
    - "kör personas i autopilot"
    - "kör pipelinen med defaultval"
    - "schemalägg personakörning"
    - "run the whole persona pipeline"
    - "run the full pipeline end to end"
    - "autonomous persona run"
    - "run personas unattended"
    - "run the pipeline with defaults"
    - "make the personas overnight"
    - "autopilot personas"
---

# Run pipeline (autonomous orchestrator)

Drive the entire persona pipeline from raw interviews to a packaged client bundle **without a human in the loop**. This is the entry point for scheduled / overnight runs — e.g. an analyst sets up a Claude Cowork schedule that says *"kör hela personaflödet på intervjuerna i `<mapp>` med defaultval, gemini-porträtt och pdf"* and wakes up to a finished, full-quality deliverable plus a review log.

This skill does not do analytical work itself. It **sets `mode: auto` and invokes each pipeline skill in order**, letting every skill run its own full five-beat flow. In auto mode each skill applies its documented default at the Checkpoint beat instead of pausing — see `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)".

## When to use vs. not

- **Use** for unattended, full-quality runs: scheduled jobs, overnight batches, "have it ready when I wake up".
- **Don't use** when the analyst wants to make the analytical decisions themselves — that's the default `interactive` flow via `/antrop-personas:start-persona-project` or invoking each skill by name.
- **Not** `dry-run` (that's a reduced preview) and **not** `skip-checkpoints` (that's a synthetic/test run marked low-quality). Auto mode is real, full-depth output with the human pause removed and every decision logged.

## Pipeline state

This skill is the **orchestrator** — it sits above the eight-step main path. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** none of its own, but it enforces each step's required-before contract (`${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md`) as it advances. It will not skip ahead.
- **Sets `mode: auto`** in `state.json` and `.persona-config.md` (`process.mode: auto`) as its first action, so every downstream skill picks it up at its own Read beat.
- **Resumable:** if `state.json` shows some steps already `completed`, the orchestrator resumes from the first non-completed required step rather than redoing work.

## The five-beat flow (orchestrator level)

### 1. Read
- Resolve the project. If a project name / path was given, use it; otherwise pick the most recent project under `personas-project/`, or scaffold one (delegate to `start-persona-project` logic) if `--input-dir` / an interview folder was supplied.
- Load `state.json` and `.persona-config.md`. Determine `language`, `methodology`, `brand`, `input_dir`, `baseline_path`, and every `process` / `brand-overrides` / `delegation` default.
- **Confirm the dependencies for a full auto run are reachable** (per `${CLAUDE_PLUGIN_ROOT}/DEPENDENCIES.md`): `openpyxl` (xlsx), `pypdf`/`python-docx` (inputs + docx), `gemini-image-gen` (portraits), and a PDF engine (chromium / playwright / weasyprint for `render-pdf.py`). If a *recommended* one is missing, log it and fall back (e.g. `initials-disc` for portraits) — do not halt. If a *required* one is missing, record a blocking entry in the decision log and stop at that step with a clear message rather than producing a broken bundle.

### 2. Propose
- Print the run plan: which project, which steps will run (and which are already `completed`), language/methodology/brand, photo policy, whether the PDF and docx will be produced, and which side-branches (`interview-cards`, `compare-baseline`) are enabled by config.
- In a scheduled/unattended context there is no one to read this — it is logged, not gated.

### 3. Checkpoint
- **Auto mode: no pause.** Set `state.json.mode = "auto"` and write `process.mode: auto` into `.persona-config.md`. Create `09-auto/` and start `09-auto/auto-decisions.md` with a header (project, timestamp, resolved config). Proceed.

### 4. Produce — run the steps in order

Invoke each skill in turn. After each step, re-read `state.json` to confirm `status: completed` (or `skipped`) before advancing. Each skill applies its own defaults and logs its own `AUTO ▸ …` decision line; the orchestrator just sequences them and appends a step-boundary line to `09-auto/auto-decisions.md`.

1. **`clean-interview`** — discover and clean every raw transcript under `input_dir` (recursive). Auto-anonymisation per the configured policy. (If transcripts are already cleaned and the analyst marked the step `skipped`, run the headless `auto-scan` per the E3 contract instead.)
2. **`analyse-themes`** — full thematic analysis, configured methodology. Falsification: emergent-vs-prompted, logged.
3. **`frame-and-cluster`** — build `behavioural-variables.xlsx`, plot, cluster. **B2** applies defaults + logs (no pause).
4. **`generate-archetypes`** — Cooper archetypes with narrative prose. Run `verify-quotes.py` (must pass — falsification is never skipped). **I1** applies defaults + logs (no pause).
5. *(side-branch, if `baseline_path` set and `compare-baseline.auto-prompt-after-generate: yes`)* **`compare-baseline`**.
6. **`validate-archetypes`** — full seven-check audit at full depth. Populates `open_critical_findings`.
7. **`design-archetypes`** — **D0** applies the eight pre-design defaults + logs. Generates AI portraits via `gemini-image-gen` (`initials-disc` only on failure — never stick figures). Renders the print-PDF via `render-pdf.py`. If `open_critical_findings` is non-empty, set `auto_review_required: true` and stamp the review banner (do **not** halt).
8. *(side-branch, if enabled)* **`interview-cards`**.
9. **`polish-language`** — second-pass Swedish/project-language polish over the deliverables.
10. **`package-for-client`** — assemble the full bundle including docx + PDF. Stamp the autonomous-run review banner on the cover (because `mode: auto`). Write `09-auto/MORNING-REVIEW.md` and place it at the top of the bundle.

### 5. Falsify
- Confirm every required step is `completed` in `state.json` and every declared output path exists on disk (especially the portraits batch and `Persona Cards v1.pdf` — the two things most likely to fail silently in an unattended run).
- Confirm `09-auto/MORNING-REVIEW.md` exists and lists: every auto-decision in order, every `[inferred]` slot, audit finding counts, any open CRITICAL findings, and "what to check first".
- Print a final `AUTO ▸ run-pipeline:done — <project> packaged; N archetypes; <M> open CRITICAL findings; review 09-auto/MORNING-REVIEW.md` line.
- If any step recorded a blocking dependency failure, the final summary leads with what is missing and which step stopped, so the analyst can fix it and re-run (the run is resumable from the last completed step).

## What gets logged to `09-auto/auto-decisions.md`

Every step appends, with a timestamp:
- the proposal it would have shown a human,
- the default decision it took (and where the default came from — config vs built-in),
- any `[inferred]` / `[not supported]` slots it had to flag,
- the result of its falsification self-check.

This is the audit trail that makes an unattended run defensible. The `MORNING-REVIEW.md` is the human-readable digest of it.

## Pitfalls

- **Don't let auto mode become quiet low quality.** Auto removes the *pause*, not the *work*. Every interview is read, the full audit runs, portraits and PDF are produced. If you find yourself tempted to shortcut a step "because no one's watching", that's `skip-checkpoints`/`dry-run` territory — not this skill.
- **Open CRITICAL findings must stay loud.** The whole point of finishing unattended is that the analyst reviews in the morning. If the audit found unresolved criticals, the banner on the cover + the top line of `MORNING-REVIEW.md` are how they find out. Never drop them to make the deliverable look clean.
- **Portraits + PDF are the fragile bits.** Generation can fail on network/quota (gemini) or missing engine (PDF). Fall back gracefully (`initials-disc`; leave HTML openable) and record the failure prominently — never produce a bundle that silently lacks portraits or the PDF without flagging it.

## Reference

- `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)" — the full auto-mode contract
- `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` § "Autonomous mode (`mode: auto`)" — state fields and the required-before contract
- `${CLAUDE_PLUGIN_ROOT}/DEPENDENCIES.md` — what must be reachable for a full auto run
