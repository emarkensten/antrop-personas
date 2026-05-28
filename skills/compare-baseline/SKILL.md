---
name: compare-baseline
description: "Compare the current persona archetypes against a previous deliverable (Mode B baseline). Reads the prior PDF / docx / markdown / zip and the current archetypes.md, identifies 1–2 meaningful differences per pair, and verdict-grades each pair against the source interviews. Use when the analyst wants to validate the new round against a prior round, or to defend either version on the source material."
metadata:
  version: "1.0.0"
  pipeline-step: "4b"
  works-on: persona-research
  side-branch: "true"
  triggers: "jämför med tidigare personor, jämför med tidigare personas, validera mot gamla personerna, Mode B-jämförelse, Mode B comparison, compare to previous personas, compare with the old personas, matcha mot existerande personor, ställ mot förra omgången, jämför mot baseline, compare-baseline, baseline comparison, hur står sig dessa mot förra, is this an improvement over last time"
---

# Compare baseline

Side-branch skill. Compare the current Cooper archetypes against a prior persona deliverable, **using the source interviews as the arbiter** rather than analyst preference. Produces a verdict-graded side-by-side comparison the analyst can take into a stakeholder conversation about whether to adopt the new round, defend the old round, or build something that combines both.

This is **step 4b** in the pipeline — it sits beside `generate-archetypes` as a side-branch and does not block any downstream main-path step. Invoke it any time after `generate-archetypes` is `completed`.

## When to use

- `state.json.baseline_path` was set at project start via `--baseline` on `start-persona-project`, and `generate-archetypes` just finished — the parent skill surfaces a prompt asking "want to compare to baseline now?"
- The analyst says "jämför med förra rundans personor" / "compare to the old personas" any time after archetypes exist
- The analyst points at an arbitrary previous deliverable: "jämför mot `<path>`"

## Pipeline state

This skill is step `4b-compare-baseline` in the pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `generate-archetypes` must be `completed` (or `needs_rework` with an existing archetypes.md). If not, halt with the graceful-fail message and direct the analyst to run `generate-archetypes` first.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides.
- Side-branch — does **not** advance any main-path status field on completion. Records its own outputs under `state.json.steps.compare-baseline`.

At its **Produce** beat it updates `state.json.steps.compare-baseline` (status `completed`, `completed_at`, `baseline_source`, output paths). Atomic write as per the pipeline-state contract.

## What this skill does

- Reads the baseline deliverable (PDF / docx / markdown folder / zip)
- Extracts the baseline personas: name, role (primary / supplemental / negative / outlier if surfaceable), driving forces, pains, needs, attributed quotes
- Reads the current `04-archetypes/archetypes.md`
- Pairs the baseline and current personas (by best-fit semantic match — the analyst can override the pairing at the checkpoint)
- For each pair: identifies 1–2 meaningful differences (not "different wording" — different *claims*)
- Verdict-grades each pair against the source interviews:
  - **PLUGIN-DEFENSIBLE** — the current version is grounded in the source where it differs; the baseline isn't
  - **MANUAL-DEFENSIBLE** — the baseline is grounded where it differs; the current version isn't
  - **BOTH** — both versions are defensible against the source; the difference is interpretive
  - **NEITHER** — neither version is grounded where they differ; both are inferences
- Lists personas present in one round but not the other, with a one-line explanation of what they cover

## Inputs

- `personas-project/<project>/04-archetypes/archetypes.md` (current)
- `state.json.baseline_path` — pointer to the baseline deliverable (or an explicit arg from the analyst)
- All cleaned interviews under `state.json.input_dir`
- Optional: `themes.md` and `behavioural-variables.xlsx` for context

## Baseline format support

This skill handles four input shapes:

| Format | Extraction strategy |
|--------|---------------------|
| `.pdf` | `pypdf` text extraction; for multi-column persona-card layouts, fall back to `pdfplumber` |
| `.docx` | `python-docx`; pull paragraphs + tables |
| `.md` folder | Glob recursively for `*.md`; treat each top-level `# Persona` heading as a persona |
| `.zip` | Unzip to a temp directory and recurse |

If extraction fails (scanned PDF, image-based docx), halt and tell the analyst the baseline needs to be re-formatted before comparison can run. **Do not infer baseline personas from filenames alone** — the comparison must be against actual content.

## The five-beat checkpoint flow

### 1. Read

- Resolve `baseline_path` (from CLI arg, `state.json`, or analyst input)
- Detect format and extract baseline personas
- Open `04-archetypes/archetypes.md`
- Open the cleaned interviews under `input_dir`

### 2. Propose

Tell the analyst:

- Number of baseline personas extracted, with names + roles
- Number of current archetypes
- Proposed pairing (e.g. "Baseline 'Anna' ↔ Current 'Hanna'; Baseline 'Bengt' ↔ Current 'Bengt' (same name); Baseline 'Maja' has no current pair; Current 'Sara' has no baseline pair")
- The 1–2 differences you flagged per pair, in one-line form
- Which verdicts you're confident in vs which need the analyst to disambiguate

Surface uncertainty explicitly. If the pairing is wrong, the analyst overrides at the checkpoint.

### 3. Checkpoint

Analyst approves (or edits) the pairing, the differences, and the verdict-rationale rubric. Lock the rubric before producing the full report.

### 4. Produce

Two deliverables:

- `personas-project/<project>/04-archetypes/baseline-comparison.md` — the working comparison document, with:
  - Executive summary (3–5 sentences) — overall verdict on the round-over-round change
  - **Per-pair tables.** Columns: `field` (sketch / driving forces / pains / needs / themes / quote), `baseline` (text), `current` (text), `verdict`, `evidence` (one-line citation to the source interview where the verdict was decided). One table per pair.
  - **Orphans.** Baseline personas without a current pair, current archetypes without a baseline pair. Short rationale per orphan.
  - **What changed at the framework level.** If the variable set or cluster boundaries shifted between rounds, surface this — it's often the underlying reason persona-level claims differ.
  - **What did NOT change.** Areas of strong agreement between rounds. These are the load-bearing findings.

- HTML artifact rendered in chat — interactive side-by-side table with click-to-expand per cell. Filter by verdict. Sort by severity (UNGROUNDED first, then OVER-REACH).

### 5. Falsify

Self-check before declaring done:

- For each `PLUGIN-DEFENSIBLE` and `MANUAL-DEFENSIBLE` verdict, **re-verify** the citing interview text actually supports the claim. The whole skill exists to be the arbiter; sloppy verdicts here are worse than not running the skill at all.
- For each `NEITHER`, confirm both versions really lack grounding (not just that you couldn't find it quickly).
- For pairings the analyst overrode, confirm the override's evidence appears in the report.
- Confirm no quote attributed in the report is paraphrased.

## Pitfalls

### Pitfall · Pairing on names alone
If the baseline has "Anna" and the current has "Hanna", same-letter shortcut pairing is tempting. **Pair on behavioural fit, not name.** The cleanest test: do their core driving forces and primary pain align? If not, they aren't pairs.

### Pitfall · Letting analyst preference drive verdicts
The analyst may have a strong opinion about which round is better. **The verdict comes from the source interviews, not the analyst's gut.** If the analyst wants to defend a version that doesn't actually round-trip to source, the verdict is `MANUAL-DEFENSIBLE: NO` and the report says so plainly.

### Pitfall · Comparing rendered docs instead of underlying personas
A baseline PDF has typography, layout, design language that aren't part of the persona. **Comparison is on the persona content, not the design.** A baseline that looks better but says the same things isn't a meaningfully different persona.

### Pitfall · Calling stylistic differences "meaningful"
"Anna is described as 'tired' in v1 and 'over-extended' in v2" is a stylistic difference, not a claim difference. Meaningful differences change what the persona implies designers should do.

### Pitfall · Anchoring on the baseline's strategic recommendations
Baselines often fold strategic recommendations into the persona body (the wall the plugin enforces). When comparing, separate "what the persona says" from "what the team recommended around it" — the comparison is on the former.

## Delegation

For large baselines (10+ personas) or large source samples, delegate per-pair verdicting to `interview-reader` (haiku) calls in parallel. Each reader gets:

- The pair's baseline-text and current-text for one field (e.g. `pains`)
- The composite members' interviews
- Task: `task: verdict-pair-field`
- Returns: verdict + citation

Aggregate verdicts yourself — the call across pairs and fields is a judgement, not a haiku-grade reading.

- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` — parallel verdict-evidence reader

## References

- `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` — The five principles (verbatim-source, strategic wall, heterogeneity, falsification, methodology-first)
- `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` — side-branch contract

## Output

- `personas-project/<project>/04-archetypes/baseline-comparison.md` — working comparison
- HTML artifact rendered in chat
- `state.json.steps.compare-baseline` updated with `status`, `completed_at`, `baseline_source`, output paths

## Dependencies

- `pypdf` (also used by `clean-interview` for PDF input — A2)
- `pdfplumber` (recommended fallback for multi-column PDF persona cards) — list as recommended in `DEPENDENCIES.md`
- `python-docx` (already required)
