---
name: validate-archetypes
description: "Run a seven-check validity audit on archetypes against the underlying interviews — traceability, coverage, distinctiveness, negative cases, triangulation, saturation. Outputs audit-findings.md + polished docx + HTML traceability heatmap. Supports --depth=fast for time-pressured passes."
metadata:
  version: 1.1.0
  pipeline-step: 5
  works-on: persona-research
  triggers:
    - "validera arketyper"
    - "granska personas"
    - "kvalitetssäkra arketyper"
    - "audit personas"
    - "spårbarhet personas"
    - "stress-testa arketyper"
    - "validate the archetypes"
    - "are these archetypes well-grounded"
    - "är personas trovärdiga"
    - "håller personas"
    - "håller arketyperna"
    - "är de här arketyperna verkligen förankrade"
    - "kan jag lita på dessa personas"
    - "do these personas actually hold up"
    - "fact-check the personas"
    - "är personas grundade"
---

# Validate archetypes

Run a seven-check validity audit on a set of archetypes against the underlying interviews and themes. Output: a structured audit report with verdicts per claim, identified orphans, distinctiveness pairs checked, and severity-ranked recommendations.

This is step 5 of 8. Input: archetypes.md, themes.md, cleaned interviews. Output: a docx audit report + an HTML traceability heatmap. Feeds `design-archetypes` only after issues are addressed (or accepted as known limitations).

## Pipeline state

This skill is step `5-validate-archetypes` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `generate-archetypes`. If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

**`open_critical_findings` field (H22-fix).** After audit-runner completes, scan the findings table for every claim with severity `CRITICAL` whose status is not `resolved`. Write the list to `state.json.steps.validate-archetypes.open_critical_findings` as `[{ "id": "<H-id>", "summary": "<one-line>" }]`. This is what `design-archetypes` reads at its Read beat to gate rendering — without this field being populated, design proceeds quietly past unresolved criticals (the SJ Återförsäljare 2026-05-28 failure mode).

## What this skill does

Runs seven validity checks, each operationalised against the source material:

1. **Traceability** — every claim → verbatim source quote, with verdict (GROUNDED / THIN / OVER-REACH / UNGROUNDED)
2. **Verbatim quote integrity** — every attributed quote checked word-by-word (VERIFIED / MILDLY EDITED / MINOR PARAPHRASE / FABRICATED)
3. **Negative case analysis** — composite members' interviews searched for evidence that *contradicts* the archetype
4. **Composite coherence** — does the archetype acknowledge or smooth over meaningful variance within its composite?
5. **Coverage / orphans** — material in the data no archetype represents
6. **Distinctiveness** — pairs of archetypes at risk of collapsing into each other, checked against the source
7. **Triangulation + saturation** — theme anchors verified; themes not represented surfaced; new material in late interviews flagged

## Inputs

- `personas-project/04-archetypes/archetypes.md`
- `personas-project/02-themes/themes.md`
- All cleaned interviews
- The participant-mapping document (for context, not audit)

## The five-beat checkpoint flow

### 1. Read
Open archetypes.md. List every distinct claim per archetype (life-sketch facts, driving forces, pains, needs, theme anchors, attributed quotes). Open themes.md and all interviews.

### 2. Propose
Tell the user: which of the seven checks you'll run (default: all seven), and at what depth. For very thorough audits, recommend delegating the heavy reading to a subagent — see `references/audit-delegation-pattern.md`.

### 3. Checkpoint
The user approves the audit scope. Skipping checks is fine for time-pressured passes — just say which.

### 4. Produce
Two deliverables:

- `personas-project/05-validation/audit-findings.md` — the working audit document, with per-archetype findings and cross-cutting findings
- A polished docx report at `personas-project/05-validation/Validity Audit — <project>.docx` with: executive summary, method, per-archetype findings tables (claim / verdict / evidence), cross-cutting findings, severity-ranked recommendations, limitations
- HTML artifact: traceability heatmap — rows are archetypes, columns are claim categories, cells are coloured by verdict; click-to-expand evidence per cell

Use the structure in `references/audit-report-structure.md`.

### 5. Falsify
Verify the audit against its own source:

- Spot-check that every quote attributed in the report appears in the named interview
- Spot-check that no claim has crept into the report without grounding
- Confirm the executive summary is consistent with the per-archetype findings

A self-checked audit is the only kind worth reading.

## The seven checks — operational rules

### Traceability
For every claim in each archetype, find at least one supporting quote in the composite members' interviews. Verdicts:

- **GROUNDED** — clear verbatim support
- **THIN** — only one weak or oblique fragment supports it
- **OVER-REACH** — claim goes meaningfully beyond what the source says
- **UNGROUNDED** — no supporting evidence in any composite member's interview

### Verbatim quote integrity
For every quote the archetype attributes to a participant:

- **VERIFIED** — exactly matches the source word-for-word
- **MILDLY EDITED** — stitched from non-adjacent sentences of the same source but content faithful (note the stitch)
- **MINOR PARAPHRASE** — meaning preserved but wording changed (e.g. "I don't need to be told" → "Don't tell me")
- **FABRICATED** — doesn't appear in the source. Highest-severity finding.

### Negative case analysis
For each archetype, actively search composite members' interviews for evidence that contradicts its defining traits. Quote the contradicting evidence with interview-id.

### Composite coherence
The composite collapses 2–4 different people into one persona. Name the most important variance within the composite — places where the members really aren't the same person psychologically. Does the archetype description acknowledge this variance or smooth it over?

### Coverage / orphans
For each of the N participants, is the archetype they're assigned to a good fit for that interview? What parts of any participant's interview does the archetype not represent? List the most significant orphan material sample-wide.

### Distinctiveness
Take pairs of archetypes at risk of collapsing (e.g. "both are values-intact-behaviour-failing"). For each pair, name the claimed differences and verify they are real in the source data, not just rhetorical.

### Triangulation + saturation
- Are the theme anchors accurate? (do composite members actually exhibit the anchored themes?)
- Are there themes in themes.md that NO archetype represents?
- Look at the last 2–3 interviews: are new themes still emerging at the end of the sample? If yes, surface as a saturation caveat.

## Pitfalls — what went wrong on NV v1

### Pitfall · Trusting your own pre-validation
On NV v1 the audit caught fabrications and over-reaches that the user hadn't noticed in real time. The point of running the audit is to find what you missed. Don't pre-conclude — read the actual interview text against every claim.

### Pitfall · Spot-checking rather than full check
Doing 2–3 claims per archetype isn't an audit, it's a tasting. The full traceability table is the deliverable. If the sample is large, delegate heavy reading to a subagent (see `references/audit-delegation-pattern.md`).

### Pitfall · Burying the worst finding in the middle of the report
Lead with the most consequential weakness. On NV v1: composite over-smoothing in Maja was the biggest issue and deserved to be the first thing in the executive summary.

### Pitfall · Audit produces "all good" verdicts
If every claim is GROUNDED, you weren't trying hard enough. The seven checks exist specifically to surface what's wrong. An audit that finds nothing is rarely an audit that's been run.

## Delegation

After the checkpoint (step 3) is approved, delegate the actual audit run to `audit-runner` (opus). It enumerates claims, dispatches `interview-reader` (haiku) per composite member with `task: quotes-for-claim` for samples ≥10 interviews, runs the seven checks, severity-ranks the findings, and writes `audit-findings.md`, `audit-heatmap.json`, and `audit-summary.md`. You then assemble the polished docx, render the heatmap HTML artifact, and present to the user.

- `${CLAUDE_PLUGIN_ROOT}/agents/audit-runner.md` — runs the full seven-check audit
- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` — parallel claim-evidence reader

## References

- `references/audit-report-structure.md` — Section-by-section structure of the docx report
- `references/audit-delegation-pattern.md` — How to delegate heavy interview reading to a subagent for large samples
- `references/seven-checks-quickref.md` — One-page summary of all seven checks for quick recall
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/05-validation/audit-findings.md` — working audit document
- `personas-project/05-validation/Validity Audit — <project>.docx` — polished client report
- HTML traceability heatmap rendered in chat
