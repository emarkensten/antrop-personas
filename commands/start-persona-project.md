---
description: Scaffold a persona project and choose where to start
argument-hint: "[project-name] [--input-dir <path>] [--baseline <path>] [--auto] [--run-all]"
allowed-tools: Read, Write, Bash, AskUserQuestion, Glob
---

Set up a new persona-research project in the user's working folder and orient them to the eight-step pipeline.

## Arguments

- `$1` (optional) — short project name (e.g. "naturvardsverket-v1"). If omitted, ask the user.
- `--input-dir <path>` (optional) — absolute or relative path to a folder containing raw interview files. When set, the plugin records this in `state.json` and `.persona-config.md` and **every later skill reads interviews from there instead of the default `01-interviews/`**. Useful when interviews live in a shared Drive folder or any subfolder layout the analyst already has (`intervjuer/pdf/`, `Transkriberingar/`, `cleaned interviews/`, etc — see A1 below).
- `--baseline <path>` (optional) — absolute or relative path to a previous persona deliverable (PDF, docx, markdown folder, or zip). Recorded in `state.json`; after `generate-archetypes` the plugin asks "want to run compare-baseline against `<path>` now?". See `compare-baseline` skill for the full Mode-B comparison flow.
- `--auto` (optional) — set the project to **autonomous mode** (`process.mode: auto` in `.persona-config.md` and `mode: "auto"` in `state.json`). Every later checkpoint applies its documented default and logs it instead of pausing — for unattended / scheduled runs. Full quality is preserved (portraits + PDF still produced); distinct from `dry-run` and `skip-checkpoints`. See `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)".
- `--run-all` (optional, implies `--auto`) — after scaffolding, **immediately run the whole pipeline end-to-end** by handing off to the `run-pipeline` skill. This is the one-shot entry for scheduled Cowork jobs: `/antrop-personas:start-persona-project <name> --input-dir <path> --run-all` scaffolds the project and produces a finished, packaged deliverable plus `09-auto/MORNING-REVIEW.md` with no further input.

## What to do

1. **Confirm the project name.** If `$1` is provided, use it. Otherwise ask the user for a short name (e.g. "naturvardsverket-v1"). Use it for both the folder name and the client-facing references throughout.

2. **Parse optional flags from the rest of the invocation:**
   - `--input-dir <path>` → store as `input_dir` in `state.json` and write the same value under `interviews` in `.persona-config.md`.
   - `--baseline <path>` → store as `baseline_path` in `state.json` and write under `compare-baseline` in `.persona-config.md`.
   - `--auto` → set `mode: "auto"` in `state.json` and `process.mode: auto` in `.persona-config.md`.
   - `--run-all` → implies `--auto`; remember to hand off to the `run-pipeline` skill at the end (see step 9).
   Both path flags are optional. If absent, defaults apply (interviews under `personas-project/<project>/01-interviews/`, no baseline set). The analyst can add either flag's value later by editing `.persona-config.md` — the next skill run picks them up.

   **If `--auto` or `--run-all` is set, skip the interactive questions in steps 4, 5b, and 6** — apply the documented defaults (language `sv`, methodology `cooper`, brand `antrop-brand`, unless overridden by flags or an existing `.persona-config.md`) and record them. An autonomous run has no one to answer prompts; the choices are logged in `09-auto/auto-decisions.md` by `run-pipeline` instead.

3. **Auto-discover existing interviews in the input directory.** If `--input-dir` was set OR the analyst is starting from an existing folder of interviews, run a recursive `Glob` against the input dir for known extensions (`*.pdf`, `*.docx`, `*.md`, `*.txt`) and surface the file list to the analyst with:

   > "I found N interview-like files under `<path>`. Are these the interviews you want to analyse?"

   The discovery is recursive — `Glob` with pattern `**/*.{pdf,docx,doc,md,markdown,txt,text,rtf,vtt,srt,json,html,htm,csv}` so subfolder names like `intervjuer/pdf/`, `Transkriberingar/`, `intervjuer_af/`, `cleaned interviews/`, `Otter exports/` are all picked up automatically. Don't ask the analyst to specify the subfolder. Triage the hits into likely-interviews vs support-material (consent forms, guide, notes) before showing them — see `${CLAUDE_PLUGIN_ROOT}/references/input-ingestion.md`.

   If the list looks wrong (too many or too few), let the analyst narrow it via a glob pattern or by pointing at a different subfolder. **Do not assume `01-interviews/` is the only valid location**, and don't assume a fixed file type — analysts arrive with `.vtt`/`.srt` caption exports, Otter/Teams `.json`, `.rtf`, legacy `.doc`, and concatenated single-file transcripts. The full format + awkward-structure contract is in `references/input-ingestion.md`.

4. **Ask three setup questions with `AskUserQuestion`** before scaffolding. These three answers cascade through every later step, so capture them up front and write them into `state.json`:

   - **Output language for analysis and client deliverables.** Default `sv` (Swedish). Options: `sv`, `en`, `bilingual` (sv analysis + en client deliverable), `other` (analyst types the language code — e.g. `nb`, `da`, `de`). Quotes always stay in their source language; this controls the analytical writing and the client-facing artefacts.
   - **Persona methodology.** Default `cooper`. Options: `cooper`, `jobs-to-be-done`, `lightweight-archetypes`. The choice cascades into `frame-and-cluster` and `generate-archetypes`.
   - **Brand profile for the design step.** Default `antrop-brand` (the spec at `skills/design-archetypes/references/antrop-design-spec.md`). Options: `antrop-brand`, `client-brand` (analyst will supply a `client-brand.md` later), `generic` (no brand styling, plain typography).

   Write all three answers into the new project's `state.json` and into `.persona-config.md`. Confirm to the user that they can change these later by editing `.persona-config.md` — the next skill run will pick up the new values.

5. **Create the folder structure** at `personas-project/<project-name>/`:

   ```
   personas-project/<project-name>/
   ├── state.json          # pipeline state (managed by every skill)
   ├── .persona-config.md  # optional: project-local config (copy from settings/local.md.example)
   ├── effektmål.md        # project effect goals — input to Cooper prioritisation (P4)
   ├── project-brief.md    # one-page brief — scope, constraints, success criteria (P4)
   ├── 00-brief/           # research brief, interview guide, deeper background
   ├── 01-interviews/      # raw + cleaned transcripts (default; overridable via --input-dir)
   ├── 02-themes/          # output of analyse-themes
   ├── 03-framework/       # behavioural variables + clusters + plot + behavioural-variables.xlsx
   ├── 04-archetypes/      # Cooper archetypes (text) + optional baseline-comparison.md
   ├── 05-validation/      # audit findings + polished audit report
   ├── 06-design/          # designed persona cards (HTML + PDF) + design-handoff/
   ├── 07-polish/          # language-polish diff log (required step — second pass on Swedish)
   ├── 08-package/         # final client bundle
   └── 09-auto/            # auto-mode decision log + MORNING-REVIEW.md (created only on autonomous runs)
   ```

   Initialise `state.json` with every step set to `pending`. Include the optional fields from step 2 when set (`input_dir`, `baseline_path`). Schema in `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md`.

   Scaffold `effektmål.md` and `project-brief.md` as empty templates with comments showing the format the analyst should fill in (1–3 effect goals; brief covering scope/constraints/success). If the analyst answers the prompts in step 5b below, populate them then; otherwise leave them as templates — `generate-archetypes` will ask before composing.

   If the user wants to override additional defaults (anonymisation policy specifics, illustration library path, model overrides for sub-agents), they can edit `.persona-config.md`. The three core choices (language, methodology, brand) are already captured in step 4.

5b. **Optionally collect effect goals + project brief now.** Use `AskUserQuestion` to offer:

   - "Vill du skriva in projektets **effektmål** och en kort **brief** nu? (rekommenderat — driver Cooper-prioriteringen av primary persona)" → if yes, prompt for each. Write to `effektmål.md` and `project-brief.md`. If the analyst prefers to skip, the scaffolded template stays empty and `generate-archetypes` will ask later.

   The effect goals format is plain markdown — 1–3 measurable goals as a bullet list. Example:
   ```
   # Effektmål — <project>

   - Öka konverteringen för förstagångsbokare med 15 % under 2026
   - Minska tid till första lyckade ärende från 8 → 4 minuter
   - Höja NPS bland nya kunder från 22 → 35
   ```

   The project brief is one paragraph covering: deliverable, audience, scope, constraints, what counts as success.

6. **Ask the user where they want to start.** The pipeline supports entering at any step — they may already have cleaned transcripts, or already have themes, or be coming back to design a previously generated set of archetypes.

   Orient the analyst first: the pipeline has **eight required steps for quality** plus **two optional side-branches** (and the `run-pipeline` orchestrator for unattended runs).

   **Required for quality (don't skip):**
   - Step 1 · Clean a raw interview transcript — `clean-interview` (skippable only if transcripts are already cleaned + anonymised by hand)
   - Step 2 · Run a thematic analysis on cleaned transcripts — `analyse-themes` (**required** even though Cooper's original method skips this; the variable-selection downstream is only as good as the themes)
   - Step 3 · Build a behavioural-variable framework and cluster participants — `frame-and-cluster`
   - Step 4 · Generate Cooper archetypes from locked clusters — `generate-archetypes`
   - Step 5 · Validate existing archetypes against the source — `validate-archetypes` (the safety net that catches fabrication)
   - Step 6 · Design Antrop-branded persona cards from validated archetypes — `design-archetypes`
   - Step 7 · Second-pass language polish over deliverables — `polish-language` (Sonnet-based Swedish polish over Opus drafts)
   - Step 8 · Package the full project as a client deliverable — `package-for-client`

   **Optional side-branches (offered but not required):**
   - Side-branch · Per-participant workshop interview cards — `interview-cards` (useful for workshop walls, doesn't affect persona quality)
   - Side-branch · Compare current archetypes against a previous deliverable — `compare-baseline` (defends new round against prior, or vice versa)
   - The optional side-branches are surfaced again at relevant moments during the process — you don't have to remember them up front.

   Use AskUserQuestion to let the analyst pick the starting step. List the eight required steps; mention the side-branches in the briefing text but don't fill option slots with them.

7. **Brief the user on the five cross-cutting principles** that every skill in this plugin follows (plus the two shared mechanics below). They are documented in `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md`. Read that file and surface the headline of each (don't dump the file in chat — summarise):

   - Don't infer — ask, or flag the gap
   - Strategic recommendations live in their own section
   - Surface heterogeneity, don't smooth it
   - Run the falsification step before declaring done
   - Methodology choice is the first question, not the default
   - Every step uses a five-beat checkpoint flow (read → propose → checkpoint → produce → falsify)
   - Output: working markdown + HTML artifact + (when relevant) docx/PDF for client

8. **Hand off to the chosen skill.** Invoke it with the project context. Do not start the next step's work yourself — invoke the actual skill so the user gets that skill's full checkpoint flow.

9. **If `--run-all` was set, skip steps 6–8's interactive hand-off and invoke the `run-pipeline` skill instead.** Pass the project context (name, `input_dir`, `baseline_path`, resolved language/methodology/brand). `run-pipeline` sets `mode: auto`, runs every required step in order, generates AI portraits and the print-PDF, packages the bundle, and writes `09-auto/MORNING-REVIEW.md`. Do not run the steps yourself — invoke `run-pipeline` so the orchestration and decision-logging happen in one place. This is the path a scheduled Cowork job takes.

## Tone

Match the **language the analyst picked in step 2**. If they picked `sv`, all your conversation in this command is in Swedish. If `en`, English. If `other`, match whatever they specified. Default to Swedish only if the analyst hasn't answered the language question yet. Don't dump the whole pipeline in front of them — orient briefly, then start the chosen step.

## What this command does NOT do

It does not produce any analytical content of its own. It is pure scaffolding + orientation. The pipeline skills do the work (and `run-pipeline` orchestrates them on an unattended run).
