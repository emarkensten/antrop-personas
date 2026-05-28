# Audit delegation pattern — heavy reading via subagent

For projects with >5 archetypes or >10 interviews, the traceability check involves a lot of reading. Delegate to a subagent so the parent's context stays clear for synthesis.

## When to delegate

- 10+ interviews to cross-check against 4+ archetypes → delegate
- Composite reading + negative case + orphan check → delegate (this is what we did on NV v1)
- Spot-check or single-archetype review → do inline, no agent

## The prompt template

Use `Agent` with `general-purpose` subagent type. The prompt should be self-contained — the subagent does not see the parent conversation.

```
You are doing a qualitative-research validity audit.

ARTEFACT UNDER AUDIT: <path to archetypes.md>
GROUND TRUTH: 13 cleaned interviews at <paths>
TRIANGULATION ONLY: <path to themes.md>

THE ARCHETYPES AND THEIR COMPOSITE MEMBERSHIP:
- Anna (PRIMARY) — IP02, IP04
- Maja (PRIMARY) — IP01, IP07, IP11
- [etc.]

WHAT YOU MUST PRODUCE — write to <path>/audit-findings.md as you go.

For each archetype, run these checks:
1. TRACEABILITY — every claim → verbatim source quote. Verdict: GROUNDED, THIN, OVER-REACH, UNGROUNDED.
2. NEGATIVE CASE ANALYSIS — hunt composite members' interviews for evidence contradicting the archetype.
3. COMPOSITE COHERENCE — variance within the composite that the archetype smooths over.

Then cross-cutting:
4. COVERAGE / ORPHANS
5. DISTINCTIVENESS (pairs)
6. TRIANGULATION VS THEMES
7. SATURATION

REPORTING RULES
- Quote interviews verbatim with interview-id. Never invent a quote.
- "Could not find supporting evidence" is a legitimate finding.
- Be specific. Cite line numbers / interview IDs.
- Length: 3,000–6,000 words.
- End with a 200-word executive summary.

Return a 250-word response summarising what you wrote.
```

## What to do with the agent's output

1. Read `audit-findings.md` end-to-end
2. Spot-check 3–5 of the most consequential findings against the source (the agent's summary describes what it intended to do, not necessarily what it did)
3. Synthesise into the polished docx report — that's the human-judgement layer

The agent does the reading. The audit's voice and severity-ranking is yours.
