# Cleaning conventions

The cleaned transcript should be markdown, easy to grep, easy for downstream skills to parse.

## File header

```
# Interview <NN> — cleaned

- **Interview ID**: IP<NN>
- **Date**: YYYY-MM-DD
- **Length**: ~MM minutes
- **Age bracket**: 25–34 *(only if stated)*
- **Household**: single / couple / family-with-children / shared housing *(only if stated)*
- **Cleaned by**: Claude (antrop-personas plugin v0.11.0-rc1)
- **Anonymisation policy**: default · v1
- **Summary of changes**: see `IP<NN>-cleaning-summary.md`
```

## Speaker labels

- `**Interviewer:**` and `**Respondent:**` (or `**IP:**`)
- Each turn on its own line, blank line between turns
- Don't merge consecutive turns from the same speaker — preserve the turn-taking shape

## Timestamps

- Keep `[00:10:01]` markers inline at natural break points
- If the raw transcript has them per-turn, keep them per-turn
- If the raw has them only at the start, add nothing

## Edits inside the text

- `[?]` — single-word uncertainty (transcriber heard "unravvled" → write "unravelled `[?]`")
- `[unclear]` — speech genuinely indecipherable; use sparingly
- `[pause]` — emotionally meaningful pause (the speaker is gathering themselves, not just breathing). Use only when context supports it; don't pepper.
- `[laughter]` / `[crosstalk]` / `[interrupted]` — non-verbal speech events worth preserving
- Square brackets are reserved for editor's marks and redaction tokens. Don't use them for anything else.

## Filler word policy

Default: keep. Remove only when:
- Pure verbal noise (`um, uh, uhh`) that adds no rhythm or emotion
- Repetitive throat-clearing at the start of a turn

Always keep:
- Hesitations before a sensitive statement
- Repeated phrases that mark thinking aloud
- "I mean" / "you know" / "like" when used as discourse markers (they carry voice)

## Section markers (optional)

If the interview clearly has phases (warm-up → main → close), add lightweight markers:

```
---
### Phase 2 — Definitions and experience
---
```

Don't bullet-point or restructure — markers are signposts, not summary.

## Never

- Summarise a section instead of transcribing it
- Collapse answers into bullet points
- Remove content that seems repetitive or tangential — keep it all
- Sanitise emotional language ("I was furious" stays "I was furious")
- Translate quotes silently if the interview is mixed-language — note the original language inline

## Summary file format

`IP<NN>-cleaning-summary.md`:

```
# Cleaning summary — IP<NN>

## Anonymisations applied
- "Anna Karlsson" → [Name] (direct identifier)
- "ICA på Hornsgatan" → [Employer] (direct identifier, store chain + street → identifying)
- "Örebro" → [city] (location outside Stockholm)
- "Södermalm" → KEPT (Stockholm-internal — research-relevant)

## Indirect-identifier judgements
- Specific master's programme + university name + neighbourhood combo would re-identify. Redacted programme to [study]; kept university name and neighbourhood per Stockholm carve-out.

## Transcription corrections
- 00:10:01 — speaker label was "Interviewer", changed to "Respondent" based on context
- 00:23:14 — "unravvled" corrected to "unravelled [?]"

## Filler/pause edits
- Removed ~14 instances of "uhm" with no apparent emotional weight
- Added [pause] at 00:18:30 (long pause before talking about job loss)

## Open questions for the user
- 00:31:02 — IP says "I work at a place that, well, you know" then names a Swedish company. Currently redacted to [Employer]; flag for user — could be left unredacted if the company is mentioned often in this sector.
```
