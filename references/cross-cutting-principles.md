# Cross-cutting principles for the antrop-personas plugin

These five rules apply to **every** skill in the plugin. They were extracted from concrete failures and successes in the Naturvårdsverket v1 project (2026), documented in `references/pitfalls-from-nv-v1.md`.

Whenever a skill is about to produce a non-trivial output, the skill instructions should remind Claude to check itself against these.

## 1 · Don't infer — ask, or flag the gap

When a slot in a deliverable is empty (age bracket, behavioural mechanism, a "pain" for a persona, a methodology choice), the default move is to fill it with a plausible value. Don't. Either ask the user, or flag the slot as `[inferred]` / `[not supported]` so the user sees that you guessed.

**The test:** would a verbatim source quote support this claim? If no, it doesn't go in.

## 2 · Strategic recommendations live in their own section

Persona attributes (pains, needs, goals) describe what participants said and did. Strategic recommendations describe what *designers should do about it*. Keep a hard wall between them.

**The failure mode:** strategic-recommendation language ("recognition as ambassador", "designs around them") gets folded back in as if a participant had said it. Once it crosses the wall, the persona looks like it endorses your strategy. It doesn't.

## 3 · Surface heterogeneity, don't smooth it

When a composite spans multiple psychological mechanisms (different constraints, different ages, different stances), the persona body must carry that variance — at minimum as named sub-variants. A one-sentence acknowledgement followed by single-voice description is not enough.

**The same rule applies to orphan material:** if a participant or a theme doesn't fit any cluster, name it as an outlier or as a sub-variant. Don't squeeze it into the nearest fit.

## 4 · Run the falsification step before declaring done

Every analysis step has a built-in test that the user shouldn't have to run for you:

- **analyse-themes** → emergent-vs-prompted check (which themes were participant-initiated, which were guide-section-initiated?)
- **frame-and-cluster** → placement-difficulty test (which interviews resist placement on which variables? if >1 resist a variable, the variable is too abstract)
- **generate-archetypes** → traceability check (every claim → verbatim source)
- **validate-archetypes** → orphan check (what material is in the data but not in any archetype?)

Bake these in. Don't ship deliverables and wait for the user to audit.

## 5 · Methodology choice is the first question, not the default

Don't reach for a generic mix. At the start of a step, ask which methodology the user wants:

- **analyse-themes** → reflexive TA, framework analysis, grounded theory?
- **frame-and-cluster** → Cooper, jobs-to-be-done, lightweight archetypes?
- **design-archetypes** → Antrop default brand, client's own brand, or generic?

The choice cascades through every later step. Wrong methodology, locked in early, is the most expensive mistake to fix.

---

## Checkpoint pattern (shared mechanic)

Every skill in this plugin operates on the same five-beat structure:

1. **Read** the input (raw transcript, themes, archetypes, etc.)
2. **Propose** what the output will be (variables to use, themes to extract, archetypes to draw) — surface it as a short summary, not a full deliverable
3. **Checkpoint** — pause and present the proposal to the user. The user approves, edits, or rejects before any heavy work proceeds.
4. **Produce** the output — markdown working file + HTML artifact for inspection
5. **Falsify** — run the step's built-in validation, surface any issues, *then* mark the step complete

If a skill skips beat 3 or 5, it has failed the plugin's contract. The analyst must own every step's decision and see every step's flaws.

## Output format convention

Each skill produces, by default:

- **One markdown working file** under `personas-project/<step>/` for the next skill to read and the user to edit by hand if they want
- **One HTML artifact** rendered inline in the chat for the analyst to inspect (filters, hover-detail, scannable)
- *Only when relevant* — one docx or PDF for client delivery (only `clean-interview`, `analyse-themes`, `validate-archetypes`, `design-archetypes`, `package-for-client`)

The working markdown is the source of truth. The HTML is for the analyst. The PDF/docx is for the client.

### Why .md is the working format (not .docx)

A 90-minute interview can be ~12k tokens as `.md` and 3–5× that as a parsed `.docx`. Every downstream skill re-reads these files repeatedly — `frame-and-cluster` reads all interviews, `validate-archetypes` reads them again, `package-for-client` reads them one more time. **Keeping working files as `.md` is the single biggest token saving in the pipeline.**

Therefore:
- Input may be `.docx` (transcripts often come that way)
- `clean-interview` converts to `.md` as its first action — see that skill's "Working format" section
- Every step after that reads and writes `.md`
- `.docx` and `.pdf` only appear at the edges, where the deliverable leaves the project

This applies whether or not the user mentions tokens. It's the default.

## Process flags (v0.9.0-rc4)

These flags are read from `.persona-config.md` `process` section at every skill's Read beat.

### `strict-checkpoints` (I1, default `yes`)

Three checkpoints in the pipeline are **non-skippable** by default (the *analyst-approval checkpoints*):

1. **After `frame-and-cluster` Produce** (B2) — the analyst must explicitly say "fortsätt" / "continue" after opening `behavioural-variables.xlsx` and reviewing/adjusting placements + cluster membership. This is the single most consequential analytical decision in the pipeline.
2. **After `generate-archetypes` Produce** (I1) — the analyst must explicitly say "fortsätt" / "continue" after reading the narrative prose, `[inferred]` flag counts, and audit-risk preview.
3. **Before `design-archetypes` Produce** (D0) — the eight-question pre-design briefing (especially #2 image aesthetic, marked "THE MOST CRITICAL"). The analyst must see and approve every default before any visual is rendered.

Other checkpoints (post-Propose at every skill) are enforced but recoverable — if the analyst skips them, the skill warns and re-surfaces the proposal.

### What `strict-checkpoints: yes` is **not** overridden by

A common failure mode is the analyst saying "kör på defaultvärden utan frågor" / "run with defaults, no questions" at the top of a session. **This phrase only overrides questions about data, methodology, language, and scope** — questions where the plugin would otherwise gather missing context. It does **not** override the three analyst-approval checkpoints above.

Concretely:
- ✅ Override: "What language is the project in?", "Which thematic-analysis methodology?", "Which interviews to include?", "Cooper vs JTBD?", "Anonymisation policy?".
- ❌ Do **not** override: B2 (cluster review), I1 (archetype review), D0 (pre-design briefing). These are the analyst's analytical decisions and cannot be auto-resolved by defaults — they require *the analyst*, not a default value.

Two explicit config settings — and only these two — bypass the three strict checkpoints. A casual session phrase never does:

- **`mode: auto`** — a deliberate, full-quality unattended run. The gates apply their documented default, log the decision to `09-auto/auto-decisions.md`, and proceed. Output is real and full-quality, stamped "autonomous run — analyst review pending". See § "`mode` (autonomous run)" below.
- **`skip-checkpoints: yes`** — a synthetic / test run. The gates are skipped *and* the work behind them is reduced; output is stamped synthetic. Use only for test/dev passes.

Setting either requires an explicit edit to `.persona-config.md` (or the equivalent `--auto` flag / `run-pipeline` invocation for `mode: auto`). There is no other way to bypass.

### `skip-checkpoints` (I1, default `no`)

Setting this to `yes` bypasses **even** the strict ones, for test / synthetic runs. Triggers a loud warning:

> "⚠ You have skipped critical analytical checkpoints (frame-and-cluster B2 + generate-archetypes I1 + design-archetypes D0). Deliverable quality may be reduced. Re-run with `skip-checkpoints: no` for client-quality output."

The warning is repeated in the final `cover.md` produced by `package-for-client` so the client sees that the run was synthetic.

### `require_analyst_approval_checkpoints` (override list)

`.persona-config.md` may set an explicit list under `process` to add or remove checkpoints from the strict-set:

```
require_analyst_approval_checkpoints:
  - frame-and-cluster:B2
  - generate-archetypes:I1
  - design-archetypes:D0
```

The default list is the three above. The analyst can add `validate-archetypes:V0` (gating before audit) or remove a checkpoint by hand-editing. Removing a checkpoint here does **not** generate a warning — it's an explicit analyst choice and the analyst is the only person who can do it.

### `dry-run` (I2, default `no`)

Setting this to `yes` runs every skill in preview mode:

| Skill | Dry-run behaviour |
|-------|-------------------|
| `clean-interview` | Process the first 2 interviews only; do not write cleaned files for the rest |
| `analyse-themes` | Process 8 of N interviews; produce 3 themes instead of 4–7 |
| `frame-and-cluster` | Plot 8 of N interviews; one Excel sheet only (Placements) |
| `generate-archetypes` | Produce bullets only; skip the narrative field (C1) |
| `validate-archetypes` | Run `--depth=fast` (traceability + composite-coherence + orphans only) |
| `design-archetypes` | Render 1 representative card (front + back); skip portraits batch generation |
| `interview-cards` | Render 3 representative cards instead of N |
| `compare-baseline` | Compare 2 pairs instead of all |
| `package-for-client` | Build the bundle structure but skip docx generation |

Use for iteration and prompt-debugging. **Always re-run with `dry-run: no` before delivering.** The skill surfaces a "this output was produced in dry-run mode" banner at the bottom of every artefact.

### `mode` (autonomous run) — `interactive` (default) | `auto`

This is the master switch for **unattended end-to-end runs** — the case where the analyst schedules the whole pipeline (e.g. in Claude Cowork) and wants finished, full-quality personas waiting in the morning, including AI portraits and the print-PDF, with no human in the loop.

`mode: auto` is a deliberate, explicit opt-in. It is **not** the same as either of the other two process flags, and the three must not be confused:

| Flag | What it means | Output quality | Stamp on deliverable |
|------|---------------|----------------|----------------------|
| `dry-run: yes` | Preview / prompt-debugging | **Reduced** (subset of interviews, bullets-only, 1 card, fast audit) | "produced in dry-run mode" |
| `skip-checkpoints: yes` | Synthetic / test data, skip the analytical work behind the gates | **Reduced / unreviewed** | "synthetic run — quality may be reduced" (also in `cover.md`) |
| `mode: auto` | **Real, full-quality run, executed unattended** | **Full** — every step runs at full depth, portraits + PDF generated | "autonomous run — analyst review pending" + a decision log |

**What `auto` does at each checkpoint.** Instead of pausing and waiting for the analyst, every skill at its Checkpoint beat:

1. Composes the same proposal it would have shown a human.
2. **Applies the documented default decision** (methodology from config, candidate variables as proposed, cluster memberships as computed, archetype line-up as drafted, the eight pre-design defaults from `pre-design-checklist.md`, `photo-policy: ai-photo`, etc.).
3. **Writes the proposal + the decision it took** to the auto-decision log (`09-auto/auto-decisions.md`, created on first auto step), with a timestamp and the skill/beat id.
4. Prints a single `AUTO ▸ <skill>:<beat> — <decision>` line to the chat and **proceeds** to Produce.

This applies to **every** checkpoint, including the three that are otherwise non-skippable (`frame-and-cluster` B2, `generate-archetypes` I1, `design-archetypes` D0). In `auto` mode those gates apply their default and log it rather than halting. This is exactly the "explicit, deliberate analyst choice" the strict-checkpoint rule reserves for config — see § "What `strict-checkpoints: yes` is **not** overridden by" below: the casual session phrase still does not bypass them; `mode: auto` (set in `.persona-config.md`, via `--auto` on `start-persona-project`, or by invoking the `run-pipeline` skill) does.

**Open CRITICAL audit findings under `auto`.** The `validate-archetypes` → `design-archetypes` gate does **not** halt in auto mode (halting would defeat the unattended run). Instead `design-archetypes` proceeds, and:

- records the open findings in `09-auto/auto-decisions.md`,
- stamps a loud, unmissable banner on the inline preview, on `06-design/README.md`, and on the `package-for-client` cover: **"⚠ AUTONOMOUS RUN — `<N>` open CRITICAL audit findings were NOT reviewed by an analyst. Review before any client use."**

This preserves the H22 safety signal (the SJ Återförsäljare 2026-05-28 failure mode) without blocking completion — the analyst sees it first thing when they review the morning output.

**Quality is NOT reduced in auto mode.** Every interview is read, the full variable set is built, narrative prose is written, the seven-check audit runs at full depth, portraits are generated via `gemini-image-gen` (with the `initials-disc` fallback only on generation failure — never stick figures), the PDF is rendered, the language-polish pass runs, and the full bundle is built. `auto` changes *who approves* (defaults, logged) — not *how much work happens*.

**Morning-review summary.** The final step (`package-for-client`, or `run-pipeline` if it drove the run) writes `09-auto/MORNING-REVIEW.md` at the top of the bundle: every auto-decision in order, every `[inferred]` slot, the audit finding counts, any open CRITICAL findings, and a one-line "what to check first". This is the analyst's entry point when they wake up.

**Falsification still runs.** `mode: auto` never skips beat 5. Every step's built-in self-check (emergent-vs-prompted, placement-difficulty, traceability via `verify-quotes.py`, orphan check) runs and its result is logged. Auto mode removes the human pause, not the safety net.

## Language

The plugin is language-flexible but **the choice must be made once, at project start, and held consistently through every later step**.

- **Default:** Swedish (`sv`). Antrop runs most projects with Swedish-speaking participants and Swedish-speaking clients.
- **Configurable:** the analyst picks the project language in `/antrop-personas:start-persona-project` (or by editing `state.json` / `.persona-config.md` before running the next step). Supported: `sv`, `en`, `bilingual` (Swedish analysis + English client deliverable), or `other` with a language code.
- **Hard rule — no drift.** Once the project language is set, every analytical document (themes.md, behavioural-variables.md, archetypes.md, audit-findings.md) and every client-facing artefact (cover, designed cards, audit docx) writes in that language. Mid-document language drift reads as carelessness.
- **Quotes stay in source language always.** Even when the project language is English, a Swedish-language interview's quotes stay in Swedish, with a translation in `()` on the line after if the client deliverable is English. Never translate inside quotation marks. Never paraphrase to fit a language.
- **Bilingual deliverables.** When the project is `bilingual`, the working markdown and HTML artefacts can stay in Swedish; only the client-facing PDF/docx is rendered in both languages (Swedish primary, English in italic under each section header).

Every skill reads the language setting from `state.json` at its Read beat. If `state.json` has no language set and no `.persona-config.md` exists, fall back to `sv` and surface a warning in the proposal asking the analyst to confirm.
