# Hand-off prompt — testing antrop-personas v0.11.5-rc4 in a fresh chat

Copy-paste the prompt below into a fresh Cowork session that has the `Claude personas/` folder mounted.

## Test strategy

This is a **production-realism test** on real interview material. The plugin will be run to validate:

- structural features work on real, messy data (state.json, agent-dispatch, eight-question briefing, batch-scaling, graceful-fail)
- falsification beats catch real problems (emergent-vs-prompted, traceability, composite coherence)
- the final deliverable is presentable on its own merits

### Two comparison modes

The exact test depends on what other artefacts are in `Claude personas/`:

**Mode A — no comparison baseline.** Only `cleaned interviews/` is present. The new Claude runs the full pipeline, reports the deliverable's quality on its own merits, and verdicts each step against the structural checks in section 5 of the prompt.

**Mode B — manual-personas baseline (preferred when available).** Both `cleaned interviews/` AND a `manual-personas/` folder are present, containing personas that were originally created by a human analyst for the same project (not by AI). This is a **human-quality benchmark** — a much stronger validation than AI-vs-AI. The new Claude runs the full pipeline, then in step 5d (after `generate-archetypes`) does a structured comparison:

- which clusters does the plugin find vs. which the human analyst found?
- are there primaries the human had that the plugin missed?
- are there primaries the plugin found that the human didn't?
- where the plugin and the human disagree on a composite, whose call is more defensible against the source?

The plugin doesn't have to match the human exactly. It has to be *defensible against the source*. The point isn't conformance — it's whether the plugin's output stands up to expert scrutiny.

**Earlier NV v1 baseline (Validity Audit + NV personas.pdf) — ignore if present.** Those were AI-generated from AI-generated interviews; comparing AI plugin output to them is a closed loop with no validation value.

## Folder layout in `Claude personas/`

```
Claude personas/
├── antrop-personas-0.11.5-rc4.plugin    # the installable
├── plugin-source/                       # editable source (for tweaks)
├── Exempeldata/                         # sample projects to test against
│   ├── AMF with manual personas/        # ← Mode B candidate: has manual personas
│   ├── Byggkatalogen/
│   ├── Naturvårdsverket AI-generated interviews/   # ← ignore: closed AI loop
│   └── SJ Återförsäljare/
├── HANDOFF_TO_NEW_CHAT.md
├── REBUILD.md
└── VALIDATION_REPORT.md
```

## Picking a project to test against

The new Claude should pick **one** project from `Exempeldata/` and test against it. Recommended order:

1. **AMF with manual personas** — Mode B. The folder should contain cleaned interviews AND a `manual-personas/` subfolder with human-made persona artefacts. This is the strongest validation — the plugin's output gets compared against an expert human's, with both judged against the source.
2. **SJ Återförsäljare** / **Byggkatalogen** — Mode A. Run the pipeline, report on its own merits. Pick one (don't run both — too much work for one test).
3. **Naturvårdsverket AI-generated interviews** — **skip**. The interviews are AI-generated; the baseline (if present) is AI-generated; testing the plugin on this material is a closed loop and tells us nothing. Only use this if you specifically want to verify the plugin doesn't crash on edge-case input.

## Expected files inside the chosen project folder

| File / folder inside the project | Required for | If missing |
|----------------------------------|--------------|------------|
| `cleaned interviews/` (≥5 `.docx` files) | Steps 5b–5g | Stop — these are the substrate |
| `raw interviews/` (1–2 `.docx` files) | Step 5a only — testing `clean-interview` | Skip 5a, do 5b–5g, note in report |
| `manual-personas/` | Mode B — comparison against human-made personas | Run in Mode A; note in report |

If files are at the project root rather than in named subfolders (raw `.docx` mixed with cleaned `.docx`), tell the analyst before starting — the structure mismatch is itself a finding worth surfacing.

At the top level, also expect:

| File | Required for | If missing |
|------|--------------|------------|
| `antrop-personas-0.11.5-rc4.plugin` | Installing the plugin | Stop |
| `plugin-source/` | Manifest/agent/setting reads | Stop |
| `VALIDATION_REPORT.md` | Context | Stop |
| `REBUILD.md` | Only if fixes are made | Skip silently |

---

## Prompt

```
I want to do an end-to-end production test of the antrop-personas plugin
v0.11.5-rc4. Everything you need is in the Claude personas folder — that's
your only mount.

Goal: validate the plugin works correctly on real interview material.

Comparison mode — check before starting:

- If `manual-personas/` exists in the folder: Mode B. There are personas
  a human analyst made for the same interviews. Run the pipeline, then
  do a structured comparison in step 5d. The point is not conformance —
  it's whether the plugin's output stands up against the source as well
  as the human's did.
- If only `cleaned interviews/` exists: Mode A. Run the pipeline, report
  on the deliverable's own merits.
- Ignore any `Validity Audit — Behavioural Archetypes.docx` or
  `NV personas.pdf` if present — those are AI-generated and not useful
  as a baseline.

Before starting:

- Read VALIDATION_REPORT.md and REBUILD.md for context
- Ask me which project in Exempeldata/ to test against, unless I already
  named one. Recommended: AMF with manual personas (Mode B). Avoid
  Naturvårdsverket AI-generated interviews (closed AI loop).
- Inside the chosen project folder: confirm `cleaned interviews/` exists
  with ≥5 .docx files. If not, stop and tell me which are missing.
- Confirm the .plugin file is at the Claude personas/ root. If not, stop.

Additional test for the new 8th skill (interview-cards):

After step 5g (package-for-client), run an extra step 5h:
  - Trigger interview-cards with the phrase "gör intervjukort till
    workshopen för dem alla" or similar
  - Verify it triggers the right skill (not design-archetypes or
    clean-interview)
  - Verify the pre-render briefing happens (scope, field set, photo
    policy, language)
  - Pick `ai-portrait` and let gemini-image-gen produce stipple avatars
  - Verify the A3 cards render and live in
    `personas-project/<project>/01-interviews/cards/`
  - Spot-check 3 cards: each field traces to verbatim source, no
    inferred demographics, no designer recs in "Skulle vara bättre om"
    field, indirect-identifier check passed

Procedure:

1. Install antrop-personas-0.11.5-rc4.plugin if it isn't already active.
   Confirm /antrop-personas:start-persona-project is available.

2. Run /antrop-personas:start-persona-project <project-name> to scaffold
   a new project (pick a sensible folder name). Verify:
   - state.json was created with every step set to pending
   - .persona-config.md was offered or created
   - the command asked three setup questions before scaffolding:
     output language, persona methodology, brand profile
   - the answers are written into state.json (look for top-level
     `language`, `methodology`, and `brand` keys)
   - the command's conversation continues in the language the analyst
     picked — no English drift if the user picked Swedish

   Pick `en` deliberately at this prompt to verify the language
   propagates: every subsequent skill's analytical writing should be in
   English, quotes stay in source language. Or pick `sv` to verify the
   default path. Note which you picked in the test report.

3. Trigger-fire-rate test (do not skip):
   Test each of these natural phrases and verify the right skill triggers.
   Stop and report any miss:
     - "kan du städa intervju 03?" → expect clean-interview
     - "kan du syntetisera vad folk sa?" → expect analyse-themes
     - "hur grupperar vi deltagarna?" → expect frame-and-cluster
     - "skriv ihop arketyperna" → expect generate-archetypes
     - "håller personas?" → expect validate-archetypes
     - "gör dem snygga som persona-kort" → expect design-archetypes
     - "ihop till slutleverans" → expect package-for-client

4. Pipeline-state graceful-fail test:
   From the scaffolded-but-empty project, try to invoke validate-archetypes.
   Expect a graceful fail with the message pointing to generate-archetypes
   first. Confirm no half-output is produced. Confirm state.json is not
   corrupted.

5. End-to-end run on the real interview material in cleaned interviews/:

   a. (Optional, only if raw interviews/ exists) clean-interview on one
      raw transcript. Verify: docx → md conversion happens up front;
      cleaning-summary.md lists every redaction; the anonymisation
      policy in .persona-config.md is honoured. If raw interviews/ is
      missing, skip and note in the report.

   b. analyse-themes on the cleaned interviews. Verify:
      - methodology is ASKED, not defaulted
      - sub-agents (interview-reader, thematic-analyser) actually fire
      - 4–7 themes produced
      - Evaluation section has emergent-vs-prompted + restating-question
        for each theme
      - quotes are verbatim (spot-check 3 against source)

   c. frame-and-cluster. Verify:
      - persona methodology is ASKED, not defaulted (Cooper vs JTBD vs
        lightweight)
      - placement-difficulty test runs automatically
      - edge-case zone exists for any non-placeable interviews
      - emergent clusters share a coherent V1 end-goal

   d. generate-archetypes. Verify:
      - archetype-drafter (opus) is dispatched
      - Strategic-implications section is SEPARATE from persona voice
      - Sub-variants section exists where composites span multiple
        mechanisms
      - every claim ties to a verbatim quote (spot-check 3)
      - no fabricated quotes (spot-check 3)

      MODE B (if manual-personas/ exists): after the plugin produces
      its archetypes.md, do a structured comparison against the manual
      personas. For each manual persona, find the plugin's closest
      analogue (or "no analogue"). For each plugin persona, find the
      manual's closest analogue (or "new"). For every pair: name 1–2
      meaningful differences and verdict each (PLUGIN-DEFENSIBLE /
      MANUAL-DEFENSIBLE / BOTH-DEFENSIBLE / NEITHER-DEFENSIBLE).
      Defensibility is checked against the source interviews, not
      against either author's preference. Write this comparison as
      manual-vs-plugin-comparison.md in the project folder.

   e. validate-archetypes. Verify:
      - audit-runner (opus) runs and dispatches interview-reader for
        sample ≥10 interviews
      - all 7 checks complete: traceability, verbatim integrity, negative
        cases, composite coherence, coverage/orphans, distinctiveness,
        triangulation+saturation
      - findings are severity-ranked
      - the audit does NOT produce "all good" verdicts (if it does,
        question whether the audit was actually run)

   f. design-archetypes. Verify:
      - all 8 pre-design questions are asked
      - card-renderer (sonnet) produces A3 landscape HTML + PDF
      - per-archetype accent colour from antrop-design-spec.md §3 is
        applied
      - negative persona has all three special-treatment features (light
        yellow surface, strategy banner in mono on navy, "Design around"
        pill)
      - typography rules from §4 are honoured (TT Norms Black for names,
        Playfair Italic ONLY for role-tagline and pull-quote, Martian
        Mono for label voice)
      - quotes on cards match archetypes.md verbatim
      - language is consistent (no Swedish/English mid-deliverable mix)

   g. package-for-client. Verify:
      - cover surfaces the top audit findings (don't bury them)
      - bundle order matches the documented structure
      - no sandbox or Anthropic-internal paths leak into any document

6. Report:
   For each step a–g:
     - did the output appear in the expected path?
     - did state.json update correctly?
     - did self-checks run automatically (not requiring user prompt)?

   Plus:
     - Trigger MISSes from step 3
     - Graceful-fail behaviour from step 4
     - Language consistency: did all analytical writing stay in the
       language picked in step 2? Note any drift.
     - MODE B only — manual-vs-plugin comparison: count of
       PLUGIN-DEFENSIBLE / MANUAL-DEFENSIBLE / BOTH / NEITHER pairs.
       Lead with the most consequential pair.
     - Most significant issue found (worst-finding-first, like the audit)
     - Final verdict: ready for v1.0.0, or what still needs fixing

   Save the report as TEST_REPORT_<date>.md in Claude personas/.
```

---

## What to do with the results

- **If the report says "ready for v1.0.0"** — edit `plugin-source/.claude-plugin/plugin.json` and `plugin-source/.claude-plugin/marketplace.json`, bump version to `1.0.0`, then follow `REBUILD.md` to repack as `antrop-personas-1.0.0.plugin`.
- **If the report finds issues** — open them in `VALIDATION_REPORT.md` under "What is still open", fix in `plugin-source/`, bump the version, repack, and re-run.

## Why a fresh chat

This session loaded the plugin's skills at session start. That means:
- Trigger fire-rates can't be tested cleanly — the skills are already on; what we want is to see if a natural phrase in a new session causes them to fire
- Agent invocations are different from a fresh install
- The token budget for parallel `interview-reader` calls is reduced

A fresh chat is the difference between "structurally complete" (where v0.11.5-rc4 is) and "actually works in production" (where v1.0.0 needs to be).
