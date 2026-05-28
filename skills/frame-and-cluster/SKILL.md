---
name: frame-and-cluster
description: "Build a behavioural-variable framework and cluster interviews into emergent groups. Outputs behavioural-variables.xlsx (primary artefact) + cluster plot. Use when the analyst has 4–7 themes and wants Cooper-style design variables and clusters."
metadata:
  version: 1.1.0
  pipeline-step: 3
  works-on: persona-research
  triggers:
    - "bygg ramverk"
    - "behavioural variables"
    - "kluster intervjuer"
    - "Cooper variables"
    - "skapa kluster"
    - "frame-and-cluster"
    - "plotta deltagare"
    - "build a behavioural variable framework"
    - "bygg en spelplan av beteenden"
    - "hur grupperar vi deltagarna"
    - "plot the participants"
    - "vad är likheterna och skillnaderna mellan dem"
    - "vilka beteendedimensioner skiljer dem åt"
    - "gruppera intervjuerna"
    - "segment the participants"
---

# Frame and cluster

Translate themes into a small set of behavioural variables, then plot each interview against them and let clusters emerge. The **primary working artefact is an Excel workbook** (`behavioural-variables.xlsx`) — three sheets, hand-editable by the analyst between this skill and `generate-archetypes`. The markdown documents are generated read-only views of the same data.

This is step 3 of 8. Input: themes.md from `analyse-themes` and the cleaned interviews. Output feeds `generate-archetypes`.

This skill enforces a **non-skippable analyst checkpoint after Produce** (B2 + I1): pipeline progress halts until the analyst opens the Excel, decides whether to adjust placements / clusters, and explicitly says "fortsätt" / "continue". This is the single most consequential analytical decision in the pipeline.

## Pipeline state

This skill is step `3-frame-and-cluster` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `analyse-themes`. If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Generates candidate behavioural variables (5–9) from the themes
- Pressure-tests each variable against the user's own falsification criterion: plot every interview, see which resist placement
- Drops abstract variables that fail the placement test
- Plots interviews on the locked variables and surfaces emergent clusters
- Produces a markdown framework document, a markdown participant-mapping document, and an interactive HTML plot

## Inputs

- `personas-project/02-themes/themes.md`
- All cleaned interviews in `personas-project/01-interviews/`
- Optional: persona-methodology choice (default: Cooper)

## The five-beat checkpoint flow

### 1. Read
Open themes.md. Open all cleaned interviews. Note the methodology if specified.

### 2. Propose
Tell the user:

- Which persona methodology you'll use (Cooper, jobs-to-be-done, lightweight archetypes). **Ask, don't default.**
- A *candidate* list of 6–9 behavioural variables, each with: name, what it measures, what each end of the scale looks like
- Which variables you're least sure about, and why

Each candidate variable must pass the **observable test**: could you tell where a participant sits on this scale from a meal log, a shopping basket, or a week of decisions? If you'd need to interview them again to know — it's a psychological driver, not a behaviour. Label the candidate accordingly. Either keep both layers (behavioural + driver) or pick one and say so.

### 3. Checkpoint
The user picks the methodology and approves (or revises) the candidate variables. Lock the set before plotting.

### 4. Produce

**Primary artefact: `personas-project/<project>/03-framework/behavioural-variables.xlsx`** (B1).

Three sheets, written with `openpyxl`:

- **Sheet 1 · Variables** — rows = variables. Columns: `id (V1..VN)`, `name`, `what_it_measures`, `low_end`, `mid`, `high_end`, `observable_test`, `does_not_capture`, `edge_cases_anticipated`, `status` (`active` / `dropped — reason`).
- **Sheet 2 · Placements** — rows = participants. Columns: `participant_id` (e.g. `IP01`, `1805-7`), then for each variable two columns: `V<n>_score` (1–5 integer; blank for edge cases) and `V<n>_evidence` (one verbatim quote with line/timestamp). Includes a final `notes` column for analyst comments.
- **Sheet 3 · Clusters** — rows = clusters. Columns: `cluster_id` (`C1`, `C2`, …), `name`, `members` (comma-separated participant ids), `V1_end_goal`, `pattern_summary` (one sentence describing the convergent behaviour across V2–V5), `outlier_warning` (text — note if the cluster has heterogeneous psychologies that downstream `generate-archetypes` must surface as sub-variants).

The Excel is the source of truth. The analyst is expected to open it, possibly adjust placements (e.g. "move IP05 from V4=5 → V4=4") and cluster memberships, then signal continue. Downstream skills (`generate-archetypes`, `validate-archetypes`, `compare-baseline`) re-read the xlsx — **not** any frozen markdown — at their Read beat.

**Generated read-only views (rendered from the xlsx, do not hand-edit):**

- `personas-project/<project>/03-framework/behavioural-variables.md` — markdown summary of Sheet 1, for `analyse-themes`-style scanning
- `personas-project/<project>/03-framework/participant-mapping.md` — markdown summary of Sheet 2, for grep-friendly traceability
- `personas-project/<project>/03-framework/clusters.md` — markdown summary of Sheet 3
- `personas-project/<project>/03-framework/participant-plot.svg` (also rendered as HTML artifact in chat) — the cluster plot, generated from Sheet-2 data, with edge-case zones for non-placeable points

Each markdown file begins with a banner: *"Generated from behavioural-variables.xlsx — do not hand-edit. Re-run `frame-and-cluster` after editing the Excel to refresh these views."*

Surface emergent clusters: groups of 2–4 participants who converge across the behavioural-spine variables (V2–V5 typically). Don't impose clusters; let them emerge.

#### How to write the Excel (reference snippet)

```python
from openpyxl import Workbook
wb = Workbook()
# Sheet 1
ws1 = wb.active
ws1.title = 'Variables'
ws1.append(['id', 'name', 'what_it_measures', 'low_end', 'mid', 'high_end',
            'observable_test', 'does_not_capture', 'edge_cases_anticipated', 'status'])
for v in variables:
    ws1.append([v.id, v.name, v.what_it_measures, v.low_end, v.mid, v.high_end,
                v.observable_test, v.does_not_capture, v.edge_cases_anticipated, v.status])

# Sheet 2
ws2 = wb.create_sheet('Placements')
header = ['participant_id'] + [f'{v.id}_{c}' for v in variables for c in ('score','evidence')] + ['notes']
ws2.append(header)
for p in participants:
    row = [p.id]
    for v in variables:
        row += [p.placements[v.id].score, p.placements[v.id].evidence]
    row.append(p.notes)
    ws2.append(row)

# Sheet 3
ws3 = wb.create_sheet('Clusters')
ws3.append(['cluster_id','name','members','V1_end_goal','pattern_summary','outlier_warning'])
for c in clusters:
    ws3.append([c.id, c.name, ', '.join(c.members), c.v1_end_goal,
                c.pattern_summary, c.outlier_warning])
wb.save('03-framework/behavioural-variables.xlsx')
```

### 4b. Checkpoint (B2 · non-skippable analyst pause)

After writing the Excel, **HALT** and tell the analyst:

> "Excel-filen ligger på `personas-project/<project>/03-framework/behavioural-variables.xlsx`. Öppna den nu — kolla att placeringarna stämmer, justera klustermedlemskap där du tycker det är fel, droppa variabler som inte håller. Säg sedan **fortsätt** för att gå vidare till `generate-archetypes`, eller säg **kör om** om du vill att jag omformulerar variabler från grunden."

In `interactive` mode, do **not** invoke `generate-archetypes` automatically — wait for explicit "fortsätt", "continue", "klar", "go", or equivalent. (In `mode: auto` the `run-pipeline` orchestrator advances to the next step; this skill still never invokes it itself.)

**B2 is on `require_analyst_approval_checkpoints` by default.** A session-level instruction such as "kör på defaultvärden utan frågor" / "run with defaults" does NOT bypass B2 — that phrase only overrides questions about data, methodology, language, and scope. The cluster review is an analytical decision only the analyst can make, so the skill halts here by default.

**Exception — `mode: auto`.** If `state.json.mode == "auto"` (or `.persona-config.md` sets `process.mode: auto`), do **not** halt. Lock the clusters as proposed, append a B2 entry to the auto-decision log (`09-auto/auto-decisions.md`) recording the variable set, the cluster table, and any placement-difficulty flags, print one `AUTO ▸ frame-and-cluster:B2 — locked N clusters as proposed` line, then update `state.json` with `status: completed` (the `run-pipeline` orchestrator advances to `generate-archetypes`). This is the deliberate, explicit authorisation described in `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)". The other explicit bypass is `process.skip-checkpoints: yes` (synthetic / test run — emits a loud warning and marks the run synthetic in `cover.md`). See also § "What `strict-checkpoints: yes` is **not** overridden by".

When the analyst signals continue, re-load the Excel, refresh the markdown views and the plot from the (possibly edited) data, then update `state.json` with `status: completed` and proceed.

### 5. Falsify
Run the **placement-difficulty test** before declaring done:

- For each variable, list every interview that resisted placement and why
- If more than one participant resists a given variable, the variable is too abstract — re-cut or drop it before locking
- Surface this audit at the bottom of behavioural-variables.md

Then a second check: do the emergent clusters share a coherent end-goal (V1)? If not, the cluster is behavioural noise, not a design target.

## Pitfalls — what went wrong on NV v1

### Pitfall · Producing variables that aren't behavioural
On NV v1 the first pass had six "variables" — locus of agency, practice mode, reasoning style — most were psychological drivers, not observable behaviours. The user pushed back: "are these really behaviours?" Apply the observable test before proposing.

### Pitfall · Not committing to a methodology until asked
The user had to invoke Cooper themselves. Don't wait — ask at the start.

### Pitfall · Failing the user's own falsification test
On NV v1 the user designed the falsification test ("if multiple interviews resist placement, the variable may be too abstract") and Claude only ran it when asked. Run it yourself, before claiming the framework is ready. This is what step 5 is for.

### Pitfall · Editing the wrong file
On NV v1 Claude tried to update the framework by editing an older driver-only document, then backtracked. When a deliverable has gone through multiple revisions, re-read or list candidates before editing. Create a new versioned file when the underlying frame has materially changed.

### Pitfall · Forcing every point onto the scale
IP07 (oscillating) and IP11 (in life-stage transition) genuinely don't sit on a single scale position. **Good move from NV v1: create an explicit "edge cases" or "doesn't apply" zone** rather than picking a least-bad placement. Preserve this — analytical honesty over a clean picture.

## Delegation

For samples ≥6 interviews, the per-participant placement evidence is heavy reading. Dispatch one `interview-reader` (haiku) per candidate-variable × participant pair with `task: quotes-for-variable`. Run in parallel. Each returns a placement proposal + 2–5 supporting quotes + any contradicting quotes. Aggregate into `participant-mapping.md` yourself — placement decisions are an analyst call; the agent only surfaces evidence.

- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` — parallel placement-evidence reader

### Scaling: 30+ interviews

For large samples the participant-mapping table won't fit in a single rendered HTML plot, and the cross-variable placement work explodes (N × M = 30 × 7 = 210 placements). Pattern:

1. **Throttle.** Cap concurrent `interview-reader` calls at the `max-parallel-readers` value from `.persona-config.md` (default 6) so the host doesn't get rate-limited.
2. **Sub-cluster first, then aggregate.** Run frame-and-cluster on a stratified sub-sample of 8–12 interviews first. Use the resulting locked framework as the input variable set for the full-sample placement run — don't re-derive variables on the full sample.
3. **Place in batches.** Run placement on the remaining interviews in batches of 8–12. Each batch produces its own slice of `participant-mapping.md`. Concatenate at the end.
4. **Cluster plot at scale.** For the HTML plot, switch from per-point hover-detail to a heatmap (rows = participants, columns = variables, colour = position on scale). Reserve the scatter plot only for the V2–V5 behavioural spine.
5. **Saturation check at scale.** With 30+ interviews you have more statistical power to detect themes emerging late. Apply the saturation check (last 5–10% of interviews) more carefully than on a small sample.

## References

- `references/variable-template.md` — Format for each variable entry (name, what it measures, both ends, what it doesn't capture)
- `references/cooper-method-notes.md` — How Cooper variables differ from jobs-to-be-done variables, when to choose which
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/<project>/03-framework/behavioural-variables.xlsx` — **primary artefact**, hand-editable, three sheets
- `personas-project/<project>/03-framework/behavioural-variables.md` — generated read-only view of Sheet 1
- `personas-project/<project>/03-framework/participant-mapping.md` — generated read-only view of Sheet 2
- `personas-project/<project>/03-framework/clusters.md` — generated read-only view of Sheet 3
- `personas-project/<project>/03-framework/participant-plot.svg` (also rendered as HTML artifact in chat) — generated from Sheet 2 data

## Dependencies

- `openpyxl` (new) — for writing the xlsx. List in `DEPENDENCIES.md`. Install via `pip install openpyxl` if missing.
