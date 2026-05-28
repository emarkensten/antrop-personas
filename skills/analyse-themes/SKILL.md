---
name: analyse-themes
description: "Run an inductive thematic analysis across cleaned interview transcripts. Output: 4–7 themes that cut across multiple interviews and surface a behavioural mechanic, tension, or contradiction — not a topic. Use when ≥3 cleaned transcripts are present."
metadata:
  version: "1.1.0"
  pipeline-step: "2"
  works-on: persona-research
  triggers: "tematisk analys, thematic analysis, hitta teman, extrahera teman, kategorisera intervjuer, analysera intervjuer, what themes emerge from these interviews, kör en tematisk analys på, synthesise themes, kan du syntetisera vad folk sa, kan du köra en analys på intervjuerna, vad återkommer i materialet, vad säger folk egentligen, summarise the patterns across these interviews, find the patterns, what are people actually saying, vilka mönster finns, code these interviews"
---

# Analyse themes

Run an inductive thematic analysis across cleaned interview transcripts. Output: 4–7 themes that cut across multiple interviews and surface a behavioural mechanic, tension, or contradiction — not a topic.

This is step 2 of 8. Input is the output of `clean-interview`. Output feeds `frame-and-cluster`.

**Required for quality.** Cooper's original method skips this step and goes directly from interviews to behavioural variables. In practice, *teams who skip thematic analysis produce variables that aren't really behaviours* — they produce psychological drivers, topics, or analyst-imposed dimensions. The themes are where the data tells you what mechanism to vary on. Don't skip even if you're under time pressure; if you're truly time-constrained, run with `methodology: framework-analysis` and `depth: holistic` (faster than reflexive TA) but run it.

## Pipeline state

This skill is step `2-analyse-themes` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `clean-interview` (with at least 3 completed cleaned interviews). If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Reads all cleaned transcripts in scope
- Asks the user which thematic-analysis methodology to use (default: inductive Braun & Clarke reflexive TA)
- Codes inductively from what participants actually said, not from the interview-guide structure
- Pressure-tests every theme against the user's research questions and against the data itself
- Surfaces themes as a working markdown document + an HTML artifact the user can browse

It does **not** generate personas, archetypes, or how-might-we statements at this step. Those come later. Themes first.

## Inputs

- Cleaned interview transcripts in `personas-project/01-interviews/`
- The research brief (impact goals, research questions) if available
- The interview guide if available — used to run the emergent-vs-prompted check

## The five-beat checkpoint flow

### 1. Read
Open every cleaned transcript. Count, note language, note interview structure. Open the research brief if present.

### 2. Propose
Tell the user:

- Which methodology you plan to use (Braun & Clarke reflexive TA, framework analysis, grounded theory, IPA). **Ask, don't default** — the choice cascades. If the user has no preference, recommend reflexive TA for behavioural-research projects and explain the trade-off in one sentence.
- The depth of coding (line-by-line vs paragraph-level vs holistic)
- Whether to report themes as universal (10+ interviews) or high-intensity (felt strongly by a subgroup)
- Whether to attempt cross-cutting tensions in addition to themes

### 3. Checkpoint
User approves the analytical frame before you start coding.

### 4. Produce

Two deliverables:

- `personas-project/02-themes/themes.md` — the working analytical document: each theme has a core insight, where/when it surfaces, evidence (verbatim quotes with interview-ids), prevalence
- An HTML artifact rendered inline — one card per theme, with click-to-expand evidence, cross-tagged to participants

**Delegate heavy reading to subagents.** For samples ≥4 interviews:

1. Dispatch one `interview-reader` (haiku) per cleaned interview with `task: digest` — run them in parallel. Each returns a structured digest with candidate themes and notable quotes. Cheap, fast, parallelisable.
2. Once digests are collected, delegate cross-interview synthesis to `thematic-analyser` (sonnet) with the digest paths, the methodology, and the depth approved at the checkpoint. It writes `themes.md` and runs both self-checks before returning.
3. Read the returned themes.md, decide whether to accept the dropped-themes note from the agent's hand-off, and render the HTML artifact yourself in chat (one card per theme).

For small samples (<4 interviews), produce inline — the overhead isn't worth it.

Use the format in `references/theme-template.md`.

### Scaling: 30+ interviews

For large samples the cross-interview synthesis won't fit in a single `thematic-analyser` call. Batch:

1. **Batch the digests** into chunks of 8–12 interviews each. Use a sensible split — chronological, by interview-guide variant, or by sampling stratum.
2. **Per-batch synthesis.** Dispatch one `thematic-analyser` per batch with `target_theme_count: 4–6`. Each returns a per-batch `themes-batch-N.md`.
3. **Cross-batch merge.** Dispatch a final `thematic-analyser` (or do this yourself if the per-batch theme count is small) that reads only the per-batch theme files (not the underlying interviews) and consolidates into the final 4–7 themes. Keep verbatim quotes from the per-batch files — do not re-quote from interviews at this stage; the per-batch synthesiser has already done the verbatim verification.
4. **Final self-check.** Re-run the emergent-vs-prompted and restating-the-question checks against the consolidated themes. Spot-check three random quotes against the original interviews.

This pattern keeps each agent under its context budget while preserving the verbatim-source chain.

### 5. Falsify
Run **two mandatory checks** before declaring done. These are not optional follow-ups — they are part of the deliverable.

**Emergent vs prompted check.** For each theme, ask: did this surface unprompted from participants, or did a single guide section produce most of the evidence? Mark each theme `EMERGENT` or `PARTIALLY PROMPTED`. If a theme is mostly prompted, either re-anchor it on cross-section evidence or label it as a prompted finding.

**Restating-the-question check.** For each theme, ask: does this restate the research question, or does it cut across it? If it restates, it isn't a theme — it's a topic.

Both checks belong inside themes.md, in an Evaluation section at the bottom.

## Pitfalls — what went wrong on NV v1

### Pitfall · Producing themes that quietly restate the research questions
Theme 3 ("saturation point") and Theme 6 ("three voices") on NV v1 were partially prompted by specific guide sections. The substantive finding survived the prompt — but the volume of evidence was inflated by the guide. The audit caught this; the user shouldn't have to. Always run the emergent-vs-prompted check yourself.

### Pitfall · Reaching for visualisation before the analysis can support it
Beautiful theme cards don't fix shallow themes. Get the substantive analysis right first; render second.

### Pitfall · Defaulting to a generic methodology
On NV v1 the user had to invoke Cooper themselves several turns in. For thematic analysis, the same risk: don't default. Ask. Different methodologies produce materially different deliverables.

### Pitfall · Quoting non-verbatim
Every quote in themes.md must be verbatim from the cleaned transcript, with interview-id. If you can't find a clean verbatim, find a different quote. Do not paraphrase inside quotation marks.

## Delegation

- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` — first-pass reader, one per interview, parallelised
- `${CLAUDE_PLUGIN_ROOT}/agents/thematic-analyser.md` — cross-interview synthesis with both self-checks

## References

- `references/theme-template.md` — Template for each theme entry, with the eight required fields
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/02-themes/themes.md` — the working themes document
- HTML artifact rendered in chat (one card per theme)
- Optional: docx mirror for client review
