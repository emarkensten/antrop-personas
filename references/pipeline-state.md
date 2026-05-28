# Pipeline state contract

Every skill in the antrop-personas plugin reads `personas-project/<project>/state.json` at the start of its **Read** beat and updates it at the end of its **Produce** beat.

The point: a skill should never silently assume an earlier step has run. If `validate-archetypes` is invoked but `archetypes.md` doesn't exist, the skill must fail clearly and direct the analyst to `generate-archetypes` first.

## Schema

```json
{
  "project_name": "naturvardsverket-v1",
  "created_at": "2026-05-12T09:30:00Z",
  "language": "sv",
  "methodology": {
    "thematic-analysis": "reflexive-ta",
    "personas": "cooper",
    "design": "antrop-brand"
  },
  "steps": {
    "clean-interview": {
      "status": "completed",
      "completed_at": "2026-05-12T11:20:00Z",
      "completed_count": 14,
      "outputs": ["01-interviews/IP01-cleaned.md", "01-interviews/IP02-cleaned.md", "..."]
    },
    "analyse-themes": {
      "status": "completed",
      "completed_at": "2026-05-13T15:45:00Z",
      "themes_count": 6,
      "methodology": "reflexive-ta",
      "outputs": ["02-themes/themes.md"]
    },
    "frame-and-cluster": {
      "status": "completed",
      "completed_at": "2026-05-14T17:10:00Z",
      "variables_count": 6,
      "clusters_count": 4,
      "outputs": [
        "03-framework/behavioural-variables.md",
        "03-framework/participant-mapping.md",
        "03-framework/participant-plot.svg"
      ]
    },
    "generate-archetypes": {
      "status": "completed",
      "completed_at": "2026-05-15T13:00:00Z",
      "archetypes_count": 4,
      "outputs": ["04-archetypes/archetypes.md"]
    },
    "validate-archetypes": {
      "status": "completed",
      "completed_at": "2026-05-16T11:30:00Z",
      "findings": { "critical": 1, "high": 3, "medium": 6, "low": 4 },
      "open_critical_findings": [
        { "id": "H22", "summary": "Possibly mis-attributed IP2 quote in Hanna's night-train cabin need" }
      ],
      "outputs": [
        "05-validation/audit-findings.md",
        "05-validation/Validity Audit — Naturvardsverket v1.docx"
      ]
    },
    "design-archetypes": {
      "status": "completed",
      "completed_at": "2026-05-17T16:20:00Z",
      "cards_count": 4,
      "outputs": [
        "06-design/persona-cards.html",
        "06-design/Persona Cards v1.pdf"
      ]
    },
    "polish-language": {
      "status": "completed",
      "completed_at": "2026-05-17T17:40:00Z",
      "polished_files": 5,
      "outputs": [
        "07-polish/polish-diff.md"
      ]
    },
    "package-for-client": {
      "status": "pending",
      "outputs": []
    }
  },
  "warnings": [
    "Saturation caveat from analyse-themes: new themes still emerging in last 2 interviews"
  ]
}
```

## Status values

- `pending` — the step has not been run yet
- `in_progress` — the step is currently running (one skill at a time per project)
- `completed` — the step finished cleanly
- `needs_rework` — the step finished but the analyst flagged it for redo (e.g. after audit findings)
- `skipped` — the analyst explicitly decided not to run this step (e.g. skipping design because the deliverable is text-only)

## Required-before contract

Each skill declares which steps must be `completed` (or `skipped`) before it runs:

| Skill | Required-before |
|-------|------------------|
| `clean-interview` | — (entry point) |
| `interview-cards` *(side-branch, optional)* | `clean-interview` with ≥1 completed interview. Side-branch — does not block any downstream step. |
| `analyse-themes` | `clean-interview` (with `completed_count ≥ 3`, OR `skipped` with auto-scan summary). **Required** — even though Cooper's original method skips thematic analysis, in practice every team needs the "what behavioural mechanic do these interviews surface?" pass before variables can be sensibly chosen. Skipping it means `frame-and-cluster` invents variables from sample-wide intuition rather than from grounded themes, which is the #1 reason persona projects produce variables that "aren't really behaviours". |
| `frame-and-cluster` | `analyse-themes` |
| `generate-archetypes` | `frame-and-cluster` (analyst has signed off the Excel checkpoint, B2/I1) |
| `compare-baseline` *(side-branch, optional)* | `generate-archetypes`. Side-branch — does not block any downstream step. Can be invoked anytime after archetypes exist. |
| `validate-archetypes` | `generate-archetypes` (analyst has signed off the post-Produce checkpoint, I1) |
| `design-archetypes` | `validate-archetypes`. If `validate-archetypes.open_critical_findings` is non-empty, the skill MUST surface every open finding to the analyst at its Read beat and require explicit "fortsätt även med <N> öppna CRITICAL-fynd" / "proceed despite N open critical findings" before rendering. No quiet warning. |
| `polish-language` | `design-archetypes` (HTML + portraits must exist). **Required for quality** — Opus 4.8's Swedish prose reads as machine-translated at the polish stage; this Sonnet-based pass catches anglicisms and "translation-y" phrasings before client delivery. |
| `package-for-client` | `polish-language` (or `design-archetypes` if `polish-language.status == "skipped"`) |

## Graceful-fail message template

If a required step is missing or not `completed`, halt with:

```
This step needs `<required-step>` to be complete first.

Current state of `<required-step>`: <status>.

Run `/antrop-personas:<required-step>` (or describe what you want to do — the
plugin will pick the right skill) before invoking this one.
```

If the analyst really wants to skip-ahead (e.g. they have hand-written archetypes and want to jump straight to design), they can mark a step as `skipped` in `state.json` by hand. Skills accept `skipped` as valid input but surface a warning.

## How state is updated

- **Read beat:** load `state.json`. If absent, treat all steps as `pending`. Check required-before contract. Halt if unsatisfied.
- **Checkpoint beat:** mark this step `in_progress` once the analyst approves the proposal.
- **Produce beat:** on successful completion, update the step's entry: `status: completed`, `completed_at`, key counts, output paths. Write `state.json` atomically (write to `.state.json.tmp`, then rename).
- **Falsify beat:** if the self-check fails and the analyst decides to redo, mark the step `needs_rework` instead of `completed`.

State files are line-diff-friendly JSON (one key per line, no compaction) so the analyst can hand-edit if they want.

## Auto-cleaning-summary contract (E3)

When `steps.clean-interview.status == "skipped"` AND no `01-interviews/auto-anonymisation-summary.md` exists yet, the next downstream skill to run (`analyse-themes`, `frame-and-cluster`, `validate-archetypes`, or `package-for-client`) MUST invoke `clean-interview` in headless `mode=auto-scan` before doing its own work. The auto-scan does not modify the interview files — it only writes the documentation artefact `auto-anonymisation-summary.md` and updates `state.json.steps.clean-interview.auto_scan_completed_at`.

This is a soft requirement: the downstream skill doesn't halt if the scan fails (e.g. PII-detection dependencies missing), but it must surface the gap in its proposal beat so the analyst sees the absence of an audit trail before client deliverables go out.

## Side-branch skills

Some skills are side-branches — they don't sit on the main pipeline path but produce useful artefacts from intermediate state:

- `interview-cards` — runs off cleaned interviews, produces per-participant workshop cards (does not block any downstream main-path step)
- `compare-baseline` — runs after `generate-archetypes`, compares current archetypes against a prior persona deliverable (set via `--baseline` on `start-persona-project`, or invoked standalone with a path argument). Output `04-archetypes/baseline-comparison.md` + HTML side-by-side artefact

Side-branch skills do not appear in the required-before table above. They can be invoked at any time the analyst wants, given the relevant prerequisites are in place.

## Optional state fields (v0.9.0-rc4)

```json
{
  "input_dir": "/Users/.../shared-drive/intervjuer/pdf",
  "baseline_path": "/Users/.../old-personas/Beteendeprofiler 9 oktober 2018.pdf",
  "portrait_seed": 47831,
  "steps": {
    "clean-interview": {
      "status": "skipped",
      "auto_scan_completed_at": "2026-05-28T08:14:00Z",
      "outputs": ["01-interviews/auto-anonymisation-summary.md"]
    },
    "compare-baseline": {
      "status": "completed",
      "completed_at": "2026-05-28T11:00:00Z",
      "baseline_source": "/Users/.../old-personas/Beteendeprofiler 9 oktober 2018.pdf",
      "outputs": ["04-archetypes/baseline-comparison.md"]
    }
  }
}
```

- `input_dir` — directory containing raw interviews (A3). Set via `--input-dir` at `start-persona-project`. All skills that read interviews use this path before falling back to `personas-project/<project>/01-interviews/`.
- `baseline_path` — pointer to a previous persona deliverable for comparison (F2). Used by `compare-baseline`.
- `portrait_seed` — integer seed for batch-consistent AI portraits (D2). Generated lazily on first `card-renderer` run, reused thereafter.
- `open_critical_findings` — list of unresolved CRITICAL audit findings, written by `validate-archetypes` at its Produce beat. Each entry is `{ "id": "H<n>", "summary": "<one-line>" }`. `design-archetypes` reads this at its Read beat and gates rendering on explicit analyst sign-off when non-empty. Cleared by the analyst (or by re-running the audit after fixes) — set to `[]` once resolved.
- `effect_goals_path` — relative path to `effektmål.md` (P4). Read by `generate-archetypes` to drive Cooper primary-persona prioritisation.
- `project_brief_path` — relative path to `project-brief.md` (P4). Same use as above.
- `has_customer_persona` — boolean, written by `generate-archetypes` at its Produce beat when a CUSTOMER archetype was included. `design-archetypes` reads this to know whether to render the customer-role banner.
- `has_served_persona` — boolean, same logic for SERVED archetypes.

## Example: validate-archetypes with no archetypes yet

```
Analyst: "är personas trovärdiga?"

[validate-archetypes triggers; reads state.json; finds generate-archetypes.status = "pending"]

Claude:
This step needs `generate-archetypes` to be complete first.

Current state of `generate-archetypes`: pending.

Run `/antrop-personas:generate-archetypes` (or just say "generera arketyper från
klustren") before invoking this one.
```

No silent failure. No half-produced audit on missing input.
