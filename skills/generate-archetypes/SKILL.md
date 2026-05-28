---
name: generate-archetypes
description: "Turn locked clusters into Cooper-style behavioural archetypes — bullets AND a narrative (≥200 words) per archetype. Reads behavioural-variables.xlsx from frame-and-cluster. Enforces a non-skippable analyst checkpoint after Produce."
metadata:
  version: 1.1.0
  pipeline-step: 4
  works-on: persona-research
  triggers:
    - "generera arketyper"
    - "skapa personas"
    - "bygg arketyper"
    - "Cooper-personas"
    - "ta fram personas"
    - "generate archetypes"
    - "build personas from clusters"
    - "compose archetypes from clusters"
    - "bygg ihop personerna"
    - "skriv ihop arketyperna"
    - "gör om klustren till personas"
    - "draft the personas now"
    - "write up the archetypes"
    - "create user personas"
---

# Generate archetypes

Build Cooper-style behavioural archetypes from locked clusters. Each archetype is a composite — name, age, life-context sketch, driving forces, key pains, key needs, anchoring themes, and one or two illustrative verbatim quotes.

This is step 4 of 8. Input: clusters and the locked variable framework. Output feeds `validate-archetypes` and `design-archetypes`.

## Pipeline state

This skill is step `4-generate-archetypes` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `frame-and-cluster`. If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Asks how many archetypes to produce and how to designate them (primary / supplemental / negative / outlier)
- For each cluster, drafts an archetype following Cooper conventions
- Pulls verbatim quotes from the composite members' interviews — never paraphrasing
- Names heterogeneity within each composite explicitly, rather than smoothing it
- Surfaces strategic-recommendation language in a separate section, never folded back as participant voice

## Inputs

- **`personas-project/<project>/03-framework/behavioural-variables.xlsx`** — primary source. Read all three sheets (Variables / Placements / Clusters). The xlsx is the ground truth after the analyst's checkpoint; the markdown views in `03-framework/` are derived and may be stale.
- All cleaned interviews under the project's `input-dir` (default `01-interviews/`)
- Optional: `02-themes/themes.md` (used to anchor each archetype to themes)
- Optional: `state.json.baseline_path` — if set, the plugin will surface a "want to run compare-baseline now?" prompt after this skill completes

### Reading the Excel

```python
from openpyxl import load_workbook
wb = load_workbook('03-framework/behavioural-variables.xlsx', data_only=True)
variables  = list(wb['Variables'].iter_rows(min_row=2, values_only=True))
placements = list(wb['Placements'].iter_rows(min_row=2, values_only=True))
clusters   = list(wb['Clusters'].iter_rows(min_row=2, values_only=True))
```

If the xlsx is missing but the markdown views exist, halt and ask the analyst to re-run `frame-and-cluster` — the markdown views aren't authoritative.

## The five-beat checkpoint flow

### 1. Read
Open the framework, the participant-mapping, and the cleaned interviews of each cluster's members.

### 2. Propose

#### 2a · Gather prioritisation inputs (P4-fix)

Before composing archetypes, the skill needs the project's *effect goals* and *brief* — those drive the Cooper prioritisation decision (one PRIMARY per product). At the start of the Propose beat:

1. Look for `personas-project/<project>/effektmål.md` (or `effect-goals.md`). If present, read it.
2. Look for `personas-project/<project>/project-brief.md`. If present, read it.
3. Look in `.persona-config.md` for `project.effect-goals` and `project.brief-path` fields.

If neither file nor config field is present, **HALT and ask the analyst** before continuing:

> "Innan vi väljer primary persona behöver jag två inputs som styr prioriteringen:
>
> 1. **Effektmål** — vilken förändring vill projektet driva? (t.ex. 'öka konverteringen för förstagångsbokare', 'minska tid till första lyckade ärende', 'höja NPS bland nya kunder'). 1–3 mätbara mål räcker.
> 2. **Projektbrief** — kort beskrivning: vem är leveransen för, vilka är scope och constraints, vad räknas som framgång?
>
> Skriv direkt här så sparar jag dem i `effektmål.md` och `project-brief.md` under projektet, eller säg **'hoppa över'** om du vill att jag väljer primary persona enbart från intervjudatan (då sänks kvaliteten på prioriteringen — Cooper's rule är att effektmål driver primary-valet)."

When the analyst answers, write the inputs to `personas-project/<project>/effektmål.md` and `project-brief.md` so they survive across sessions. They're plain markdown; the analyst can edit later.

If the analyst says "hoppa över", proceed but flag in archetypes.md that prioritisation was made on data alone, no project context — this is documented as a known limitation in the audit and cover.

#### 2b · Scan for customer-persona context (P1-customer)

Before proposing the persona lineup, scan `themes.md` and a sample of cleaned interviews for B2B / buyer-≠-user signals (see `references/cooper-archetype-template.md` § "Detecting B2B / customer-persona context"). Look for: procurement language, decision-maker mentions, IT-chef / inköp / sponsor archetypes in the data, "för våra kunder/medarbetare" phrasing.

If 2+ signals appear, include in the Propose surface:

> "Intervjudatan har <N> signaler på B2B-/upphandlings-kontext: <signals>. Vill du att jag inkluderar en **CUSTOMER persona** (köpare ≠ användare — t.ex. IT-chefen / upphandlingsenheten med fokus på upphandling, integration, governance, TCO)? Default: **nej** om det är osäkert — säg **ja** för att lägga till."

If fewer than 2 signals, **do not** mention customer personas — it would be fabrication in a B2C context.

#### 2c · Propose the lineup

Tell the user:

- **Prioritisation rationale** — given the effect goals and brief, which cluster's End goals most directly enable those effect goals? That cluster gets PRIMARY (exactly one). One sentence per other archetype on its assigned Cooper role (secondary / supplemental / customer / served / negative / outlier).
- How many archetypes you'll produce, with the Cooper role for each (default mix: 1 primary, 0–2 secondary, 0–2 supplemental, optionally 1 customer / 1 served / 1 negative / 1 outlier)
- The composite membership for each archetype (e.g. "Anna = IP02 + IP04")
- Heterogeneity within each composite — where the members are *not* the same person psychologically, and how you'll surface it
- Which themes from themes.md each archetype will anchor to
- One representative verbatim quote per archetype (you'll add more during production)
- **Goal-hierarchy preview** — for each archetype, one example Life goal / Experience goal / End goal trio from the source material, so the analyst can see what Cooper's three-tier model looks like for this project before drafting.

### 3. Checkpoint
The user approves the archetype line-up before drafting. This is where you catch composites that try to merge incompatible psychologies (see pitfalls).

### 4. Produce
Two deliverables:

- `personas-project/<project>/04-archetypes/archetypes.md` — the working archetype document with the full Cooper template per archetype (see `references/cooper-archetype-template.md`). **Includes the `narrative` field (≥ 200 words of running prose) per archetype** (C1).
- HTML artifact — one card per archetype, with composite-from line in mono, goals + pains columns, theme chips, verbatim quote at the bottom, and a collapsible "Narrative" panel under the bullets.

Cooper template per archetype:
- **Name + age** (a composite name and age, never a real participant's). **Demographic claims (age, occupation, civil status, location) are verified against the cleaned interview itself (E1) — not against `participant-mapping.md` or analyst notes.** If a fact isn't in the cleaned IP*.md, mark it `[ålder ej angiven]` / `[inferred from context]` and surface in the hand-off.
- **Composite from** — explicit list of source interview IDs and one-line participant sketches
- **Sketch** — 2–3 sentences of life context
- **Core driving forces** — goal-level motivations
- **Key pains** — felt frustrations and barriers
- **Key needs** — what would actually move them
- **Anchoring themes** — which themes from themes.md define this archetype
- **Sub-variants** — if the composite spans materially different psychologies, name them as sub-variants here
- **Narrative** — 3–6 paragraphs of running prose, ≥ 200 words, anchored in the **same** verbatim citations as the bullets. This is what fills the back of the A3 card in design-archetypes. The bullets exist to summarise this prose — not the other way around.
- **Verbatim source map for the narrative** — one line per narrative paragraph naming the interview-id(s) and line/timestamp the paragraph leans on. Audit-readable, not card-rendered.
- **In their own words** — 1–2 verbatim quotes with interview-id attribution
- **Strategic implications** — separate section, never folded into pains/needs/quotes

### 4b. Checkpoint (I1 · non-skippable analyst pause)

After writing `archetypes.md`, **HALT** before proceeding. Surface to the analyst:

- the full archetype list with name + age + composite + tagline
- count of `[inferred]` flags per archetype
- count of orphan-material items
- top 3 risks the audit (`validate-archetypes`) is most likely to flag

Then ask:

> "Arketyperna ligger i `04-archetypes/archetypes.md`. Öppna den, läs igenom narrative-prosan, justera namn / sub-variants / orphan-noteringar om du vill. Säg sedan **fortsätt** för att gå vidare (default = `validate-archetypes`). Säg **kör om** om du vill att jag drar om kompositionen. Säg **jämför** om du vill köra `compare-baseline` mot en tidigare leverans innan validation."

**I1 is on `require_analyst_approval_checkpoints` by default.** A session-level instruction such as "kör på defaultvärden utan frågor" / "run with defaults" does NOT bypass I1 — that phrase only overrides questions about data, methodology, language, and scope. Composing archetypes is an analyst-owned analytical decision; the audit (`validate-archetypes`) cannot stand in for it. The skill MUST halt here even when the parent context is auto-mode. The only way to bypass is `process.skip-checkpoints: yes` in `.persona-config.md`, which emits a loud warning and marks the run as synthetic. See `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "What `strict-checkpoints: yes` is **not** overridden by".

If `state.json.baseline_path` is set AND `compare-baseline` hasn't been run on the current archetypes yet, also surface:

> "Tidigare baseline finns på `<state.json.baseline_path>`. Vill du köra `compare-baseline` nu? (default = ja, men du kan säga `hoppa över`)"

### 5. Falsify
Run a **traceability self-check** before declaring done — every claim in each archetype must trace to a verbatim source. Specifically:

- For each pain, need, goal, frustration → find at least one supporting quote in a composite member's interview
- For every attributed quote → verify it appears verbatim in the interview. No stitching across paragraphs without ellipses. No silent paraphrasing.
- Flag any claim you can't ground as `[inferred — not in source]` or remove it

**Quote verification — run the grep-based checker, don't self-attest.** The historical failure mode (NV v1 self-check + SJ Återförsäljare 2026-05-28 retro) is that self-attested falsification passes claims it shouldn't — the model marks its own quotes "verbatim" without re-reading the source. The skill MUST run `references/verify-quotes.py` against the just-written `archetypes.md` and surface the report at the I1 checkpoint:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/generate-archetypes/references/verify-quotes.py" \
  --archetypes personas-project/<project>/04-archetypes/archetypes.md \
  --interviews-dir personas-project/<project>/01-interviews/ \
  --report     personas-project/<project>/04-archetypes/quote-verification.md
```

The script:
- extracts every attributed quote (`"…" — IP02` and markdown blockquote variants)
- looks up the named interview file in the interviews dir
- assigns each quote a verdict (`VERIFIED` / `MILDLY_EDITED` / `MINOR_PARAPHRASE` / `FABRICATED` / `INTERVIEW_NOT_FOUND` / `TOO_SHORT_TO_AUDIT`)
- writes `04-archetypes/quote-verification.md` with the full table and a worst-verdict summary
- exits 0 if every quote is `VERIFIED` (or `TOO_SHORT_TO_AUDIT`), 1 otherwise

If the script reports anything worse than `VERIFIED`, fix the offending quotes (replace with a verbatim quote, or mark the stitch with `…`) and re-run before reaching the I1 checkpoint. **Do not** present clean-looking archetypes to the analyst when the verifier disagrees — the verifier's report is the ground truth, not the model's self-attestation.

This is no longer "soft validation". The full seven-check audit still happens in `validate-archetypes`, but quote verbatimness is mechanically verified here so the audit doesn't have to re-discover obvious lapses.

## Pitfalls — what went wrong on NV v1

### Pitfall · Importing claims that no source supports
On NV v1, "Anna's awareness campaigns compound her guilt" was imported — neither IP02 nor IP04 says it. Same with "Linn needs recognition as ambassador" — no composite member articulates it; IP13 explicitly says the opposite. **Rule:** every pain, need, goal must round-trip to a verbatim source quote in a composite member. If you can't find one, the claim doesn't go in.

### Pitfall · Strategic-recommendation language leaking into participant voice
On NV v1, "ambassador" came from the strategy section of the clusters document and got folded into Linn's needs as if a participant had said it. **Rule:** strategic recommendations live in a separate section ("Strategic implications") at the bottom of each archetype, never inside the persona description.

### Pitfall · Flattening heterogeneous composites
On NV v1, Maja merged IP01 (class resentment), IP07 (self-regulation), IP11 (legacy framing) — three meaningfully different psychologies. The archetype named the heterogeneity in one sentence and then wrote as if Maja were one person. **Rule:** if the composite spans more than one mechanism, add an explicit "Sub-variants" section ("Maja-as-IP01 is class-resentful; Maja-as-IP07 is self-regulating; Maja-as-IP11 is in life-stage transition"). Don't smooth.

### Pitfall · Sharpening participant quotes
On NV v1, IP09's "I don't need to be told to care" was rewritten in the archetype as "Don't tell me to care" — sharper, more imperative, same meaning. **The quotation mark is a promise.** If the original isn't punchy enough, pick a different quote or use the punchier version in the narrator-voice description (without quotation marks). Never rewrite inside quotation marks.

### Pitfall · Stitching quotes silently
On NV v1, two attributed quotes stitched non-adjacent sentences from the same source. **Rule:** if you stitch, mark with `…` and flag in the production summary. Never reverse sentence order silently.

### Pitfall · Squeezing participants into the nearest archetype
On NV v1, IP08 (quiet silent-adopter) was placed in Bengt (active defender) and partially flattened. **Rule:** the test isn't "where do they fit best" — it's "do they fit at all". A misfit participant gets a sub-variant, an outlier note, or no placement — not a forced fit.

### Pitfall · Skipping orphan material
On NV v1, the legacy register (IP11), the anti-commercial register (IP06), the successful-change pathways (IP05/09/12/13) all disappeared in the archetypes. These will be caught in `validate-archetypes`, but try to catch them here too: after drafting, list any major material in the interviews that no archetype carries. Either add an archetype, add a sub-variant, or note it explicitly as a documented gap.

## Delegation

After the checkpoint (step 3) is approved, delegate the actual drafting to `archetype-drafter` (opus). The drafter reads the framework, mapping, themes and composite members' interviews, drafts each archetype following the Cooper template, runs the traceability self-check, and returns a hand-off listing every `[inferred]` flag and every orphan-material item. You then review the hand-off with the user before declaring the step complete.

For sample-wide quote-pulls before drafting, dispatch parallel `interview-reader` (haiku) calls with `task: quotes-for-claim` to surface evidence the drafter then composes from.

- `${CLAUDE_PLUGIN_ROOT}/agents/archetype-drafter.md` — composes Cooper archetypes with traceability self-check
- `${CLAUDE_PLUGIN_ROOT}/agents/interview-reader.md` — parallel verbatim-evidence reader

## References

- `references/cooper-archetype-template.md` — Full Cooper persona template with every required field
- `references/verify-quotes.py` — Grep-based verbatim verification, run at every Falsify beat
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/04-archetypes/archetypes.md`
- HTML artifact rendered in chat (one card per archetype, with verbatim quotes)
- Optional: docx mirror for client review
