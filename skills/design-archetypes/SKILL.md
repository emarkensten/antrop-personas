---
name: design-archetypes
description: "Turn validated archetypes into Antrop-branded persona cards — double-sided A3 (front = visual summary, back = narrative prose), AI-generated photo portraits with locked series style, design-handoff folder for designers / claude/design. Outputs PDF + HTML + raw-material handoff."
metadata:
  version: 1.1.0
  pipeline-step: 6
  works-on: persona-research
  triggers:
    - "designa personas"
    - "snygga personas"
    - "Antrop persona-kort"
    - "persona PDF"
    - "persona cards"
    - "make the archetypes look good"
    - "design the archetypes in our brand"
    - "persona one-pager"
    - "A3 personas"
    - "gör dem snygga"
    - "gör om dem till kort"
    - "snygg PDF av personas"
    - "make this presentable"
    - "produce the persona cards"
    - "rendera personas i brand"
    - "export personas to PDF"
---

# Design archetypes

Turn validated archetypes into Antrop-branded persona cards. A3 landscape, one card per persona, print-ready PDF + browsable HTML that mirrors the print version.

This is step 6 of 8. Input: validated archetypes from `validate-archetypes`. Output feeds `polish-language`, then `package-for-client`.

**Hard requirement before this skill runs:** read `references/antrop-design-spec.md` AND `references/pre-design-checklist.md` end-to-end. The brand spec is non-negotiable; the pre-design checklist is the eight questions that must be answered before any visual is rendered.

## Pipeline state

This skill is step `6-design-archetypes` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** `validate-archetypes`. If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Open CRITICAL gating (H22-fix).** Read `state.json.steps.validate-archetypes.open_critical_findings`. If the list is non-empty, **HALT** at the Read beat and surface to the analyst:

   > "⚠ Validate-archetypes reported **N open CRITICAL findings**. Designing on top of these means the cards may carry the same issues into the client deliverable:
   >
   > - H<id> — <summary>
   > - H<id> — <summary>
   >
   > Du kan: (a) säga **fortsätt även med <N> öppna CRITICAL-fynd** för att designa ändå (eskaleringen loggas i `06-design/README.md` och `package-for-client` cover-dokumentet), eller (b) köra `/antrop-personas:validate-archetypes` igen efter att ha åtgärdat fynden, eller (c) markera fynden som `resolved` för hand i `05-validation/audit-findings.md` och köra `validate-archetypes` om för att uppdatera state."

   In `interactive` mode, do **not** proceed past Read until the analyst signals explicit override or resolves the findings. A silent "warn and proceed" is not enough — that's how H22 leaked through on SJ Återförsäljare 2026-05-28.

   **Exception — `mode: auto`.** If `state.json.mode == "auto"`, do not halt (halting would defeat the unattended run). Instead: set `state.json.auto_review_required: true`, append the full open-CRITICAL list to the auto-decision log (`09-auto/auto-decisions.md`), and carry the banner **"⚠ AUTONOMOUS RUN — `<N>` open CRITICAL audit findings were NOT reviewed by an analyst. Review before any client use."** onto the inline preview, `06-design/README.md`, AND (via `auto_review_required`) the `package-for-client` cover. This keeps the H22 safety signal loud and unmissable for the morning review while still letting the run finish. Print one `AUTO ▸ design-archetypes:critical-gate — proceeding with N open CRITICAL findings (banner stamped)` line. See `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)".
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Walks the user through an eight-question pre-design briefing (format, image aesthetic, consistency rules, per-persona character, ethics, language, print specs, usage)
- Builds **double-sided** A3-landscape persona cards in Antrop's brand:
  - **Front (page 1)** — visual summary: name, AI photo portrait in tinted disc, tagline, goals + pains columns, theme chips, pull-quote band, optional audit badges
  - **Back (page 2)** — running narrative prose (≥ 200 words per persona) anchored in the same verbatim citations as the front
- Renders an HTML version (for iteration, with `@page` print CSS) and a PDF (for client delivery, 2 pages per archetype)
- Generates **AI-photo portraits by default** (D1b) via `gemini-image-gen` using the locked series brief in `references/portrait-style.md`. Fallback when generation fails: `initials-disc`. **Never** stick figures, geometric placeholders, or empty silhouettes.
- Routes the final render through the `canvas-design` skill (D1) when `use-canvas-design: yes` in `.persona-config.md` (default) — iterates 2–3 rounds: render → preview → polish
- Runs a preview-loop after first render (D3): shows one representative card in chat and asks "iterate on something specific, or OK?"
- Emits a `design-handoff/` folder (D4b) with raw material (text per persona, AI portraits, palette, typography spec, brief) so a designer or `claude/design` session can produce alternative formats
- Optionally renders **sub-variant mini-cards** (D5) at A5 size as satellites to the primary card, when `render-sub-variants: yes`
- Optionally renders an **Outliers card** (H1) listing edge-zone participants from `frame-and-cluster`, when `render-edge-cases: yes` (default)
- Reads `05-validation/audit-findings.md` and adds **audit badges** per card (THIN / OVER-REACH / UNGROUNDED on the relevant fields) unless `hide-audit-markers: yes` (E2)

## Inputs

- `personas-project/04-archetypes/archetypes.md` (validated)
- `personas-project/05-validation/audit-findings.md` (so you don't carry forward weaknesses the audit flagged)
- Optional: path to Antrop's illustration library (defaults: try `references/antrop-illustrations/` if present)
- Optional: project-level brand override (e.g. client wants their own colours)

## The five-beat checkpoint flow

### 1. Read
Open archetypes.md. Open audit-findings.md. Open `references/antrop-design-spec.md` and `references/pre-design-checklist.md` fully. Open the validated archetype list — confirm which archetypes are in scope for design (primaries, supplemental, negative, outlier — design decisions about which ones get cards happen here).

### 2. Propose — the eight-question pre-design briefing
**This is the single most important step in this skill.** On the Naturvårdsverket project, Claude design said the one thing it most wished it had upfront was the image aesthetic decision (#2). Without these eight answers, the work goes off-spec.

Walk the user through, with defaults pre-filled from `references/pre-design-checklist.md`:

1. **Format** — A3 landscape (default), double-sided (front + back), PDF + HTML
2. **Image aesthetic** — **`ai-photo` (default — D1b)**. Other options: `stipple` (Antrop illustration library), `illustration` (Antrop hand-drawn), `animal` (project-specific). **`initials-disc` only as fallback when AI generation fails.** Stick figures / geometric placeholders / empty silhouettes are forbidden under every setting. *This is still the most important question* — the analyst must explicitly approve the default or pick another option.
3. **Consistency rules** — read from `references/portrait-style.md` (D2 — framing / lighting / colour grade locked across the series, single seed)
4. **Per-persona character** — gender, ethnicity, body type, clothing, one specific detail — explicit per persona, not inferred from the name
5. **Ethics** — AI-portrait disclaimer in footer (default `yes`); consent check if real participants are depicted
6. **Language** — read from `state.json.language` (default Swedish for Antrop)
7. **Print specs** — read from `.persona-config.md` `brand-overrides.print-spec` (default `a3-landscape-fogra39`)
8. **Usage** — workshop wall, hand-out, PDF email (controls typography scale)

Additional decisions surfaced at this step (not part of the eight questions but checked here):

- `double-sided-cards` — `yes` (default) renders front + back. `no` renders front only.
- `render-sub-variants` — surface to analyst if any archetype in `archetypes.md` has a non-empty `Sub-variants` block.
- `render-edge-cases` — surface to analyst if `clusters.md` has edge-zone participants. Default `yes`.
- `hide-audit-markers` — `no` (default) shows audit badges; `yes` produces a clean client version. Ask the analyst which version they want; if they ask for both, render both.
- `emit-design-handoff` — `yes` (default) emits the `06-design/design-handoff/` folder. If the analyst is delivering only the PDF, set to `no`.

### 3. Checkpoint (D0 · non-skippable analyst pause)
The user confirms all eight answers + the additional decisions above. **Refuse to render until they're answered.** Defaults are fine, but the user must see the defaults and approve them.

**D0 is on `require_analyst_approval_checkpoints` by default.** A session-level instruction such as "kör på defaultvärden utan frågor" / "run with defaults" does NOT bypass D0 — image aesthetic (#2, marked "THE MOST CRITICAL") and per-persona character briefs (#4) cannot be auto-resolved without an analyst signal under normal interactive use. The skill surfaces all eight defaults and waits for explicit confirmation by default.

**Exception — `mode: auto`.** If `state.json.mode == "auto"` (or `.persona-config.md` sets `process.mode: auto`), do **not** wait. Apply the eight pre-design defaults from `${CLAUDE_PLUGIN_ROOT}/skills/design-archetypes/references/pre-design-checklist.md` (`photo-policy: ai-photo`, `palette: light`, `double-sided-cards: yes`, `card-front-columns: 3`, etc., as overridden by `.persona-config.md`), append a D0 entry to the auto-decision log (`09-auto/auto-decisions.md`) listing all eight answers used, print one `AUTO ▸ design-archetypes:D0 — applied 8 pre-design defaults` line, and proceed to Produce at **full** fidelity (portraits via `gemini-image-gen`, PDF rendered). This is the deliberate, explicit authorisation in `${CLAUDE_PLUGIN_ROOT}/references/cross-cutting-principles.md` § "`mode` (autonomous run)". The other explicit bypass is `process.skip-checkpoints: yes`.

In `mode: auto`, the rendered output and `06-design/README.md` carry an info note *"Pre-design briefing auto-applied — defaults logged in `09-auto/auto-decisions.md`"* (this is review-pending, not synthetic — full quality). If `skip-checkpoints: yes` is set instead and D0 is bypassed, the output must carry the stronger banner *"Pre-design briefing skipped — defaults applied"* on the inline preview, and `06-design/README.md` must note which defaults were applied without analyst review.

### 4. Produce

The deliverable is a small set of files plus an optional handoff folder. Defaults shown below; flags from `.persona-config.md` toggle individual outputs.

#### 4.1 · Card files (always emitted)

- `personas-project/<project>/06-design/persona-cards.html` — the master HTML. **Two `<section class="persona-card …">` blocks per archetype** when `double-sided-cards: yes` (default — C3): one with class `.front`, one with class `.back`. Self-contained, Antrop brand CSS variables, A3 landscape via `@page` rules, `page-break-after: always` on every section.
- `personas-project/<project>/06-design/Persona Cards v1.pdf` — printed PDF version. With double-sided + N archetypes, this PDF is 2N pages. **PDF generation runs in this parent skill's context after `card-renderer` returns** — see § 4.9 below. The renderer cannot reliably reach chromium / weasyprint in its sandbox (SJ Återförsäljare 2026-05-28 failure mode); parent does it.
- An inline HTML artifact rendered in chat (a representative card preview — front + back side-by-side — with a button to open the full file).

Layout details:
- **Front:** Apply `antrop-design-spec.md` §6 layout. Per-archetype colour assignment from §3 (primary → vinröd/mörkblå; supplemental → mörkgrön; negative → ljusgul with strategy banner; outlier → vit). Typography from §4 (display name, Playfair Italic for role-tagline + pull-quote, Martian Mono for label voice). AI photo portrait in the tinted disc; goals + pains columns; theme chips; pull-quote band.
- **Back (C3):** Same A3 surface, same accent colour, lighter weight. Single block of the **narrative prose** (≥ 200 words) from `archetypes.md` in the project's body type. A "Pull-quotes from the narrative" sidebar with 2–3 short verbatim citations and their interview-id attributions. Sub-variants summary if applicable. Page-number `2/2` per archetype.

Honour every rule in §9 ("things to never do"): no border-radius on the A3 page, no shadows, no emoji avatars, no Playfair under 18pt.

#### 4.2 · Portrait generation (D1b) — runs in the PARENT skill, not the renderer subagent

Default: **AI photo** via `gemini-image-gen`, using the locked brief in `references/portrait-style.md` (D2).

**Where this runs.** Portrait generation runs in **this parent skill's context**, *before* delegating to the `card-renderer` subagent. The parent has access to `gemini-image-gen` and the host's mounted skills directory; the `card-renderer` subagent runs in an isolated sandbox and frequently cannot reach those paths (this was the failure mode on SJ Återförsäljare 2026-05-28: the subagent's Linux sandbox could not see `/var/folders/.../skills/gemini-image-gen/`). The parent generates portraits first, writes them to `06-design/portraits/`, and passes the **file paths** to `card-renderer` in the delegation prompt.

The parent:

1. Reads `references/portrait-style.md` and every archetype's per-persona character brief from `archetypes.md`
2. Captures a project-level `portrait_seed` in `state.json` (random on first run, reused after)
3. Builds one prompt per archetype, substituting the per-persona fields into the locked template
4. Calls the `gemini-image-gen` skill in batch, expecting consistent output across the series
5. Saves portraits under `06-design/portraits/<archetype-slug>.jpg` (and `.png`) at ≥ 2048×2560
6. Writes a `06-design/portraits/manifest.json` mapping `archetype_id → portrait_path` so the renderer doesn't need to guess slugs
7. **On failure (gemini-image-gen ESM-resolution issue, J2; network outage; quota; or rejection)** — first retry once with a modified prompt; if still failing, write the prompt to `06-design/portraits/prompt-<archetype-slug>.txt` for manual runs and tell the renderer to use **`initials-disc`** for that archetype. **Never** stick figures, geometric outlines, or empty silhouettes.

The delegation prompt to `card-renderer` then includes `portraits_manifest_path`. If a path in the manifest is missing or empty, the renderer falls back to `initials-disc` for that archetype only.

If `photo-policy` is set to something other than `ai-photo` in `.persona-config.md`, follow that choice — but the fallback ladder is unchanged.

#### 4.3 · Sub-variant mini-cards (D5, conditional)

If `render-sub-variants: yes` AND any archetype has a non-empty `Sub-variants` block:

- Render each sub-variant as an A5 mini-card (half-A4 landscape) in the **same accent colour** as the parent archetype, with a smaller satellite-style header noting "Sub-variant of `<parent>`"
- Lay out on the wall as: primary card at A3 + N sub-variant mini-cards at A5 around it
- Add to `persona-cards.html` after the parent archetype's back-card, before the next archetype's front-card

#### 4.4 · Outliers / edge-cases card (H1, conditional)

If `render-edge-cases: yes` (default) AND `03-framework/clusters.md` has edge-zone participants:

- Render one A3 "Outliers" card after all primary archetypes
- One short paragraph per edge-case participant: IP-id, why they didn't fit any cluster, what their interview surfaces that no archetype carries
- Same brand language, but with `class="outlier"` (white surface, dark text — see `antrop-design-tokens.css`)

#### 4.5 · Audit-badges overlay (E2, conditional)

If `hide-audit-markers: no` (default):

- Read `personas-project/<project>/05-validation/audit-findings.md` (the working audit document from `validate-archetypes`)
- For every field on every card (sketch, driving forces, pains, needs, themes, quotes), if the audit's verdict is `THIN` / `OVER-REACH` / `UNGROUNDED`, add a small badge next to that field in the renderer's output:
  - `THIN` — yellow dot
  - `OVER-REACH` — orange dot
  - `UNGROUNDED` — red dot
- A legend at the bottom-right of every card explains what the dots mean

Also render a second pass `Persona Cards v1 — clean.pdf` with `hide-audit-markers: yes` for the client-facing version, if the analyst asked for both versions at the briefing.

#### 4.6 · Canvas-design routing (D1 — optional enhancement, OFF by default)

**The bundled template + `references/render-pdf.py` already produce a complete, print-ready, consistent A3 double-sided card** (all elements: photo, name, role tagline, behaviour dot-scales, drivkrafter + goal hierarchy, smärtor, behov, theme chips, pull-quote on the front; narrative + quote sidebar on the back). `canvas-design` is **not required** and is OFF by default (`use-canvas-design: no`). Do not block or degrade the deliverable when it is absent.

If `use-canvas-design: yes` AND the `canvas-design` skill is installed (pure opt-in enhancement):

- After the initial render, invoke `canvas-design` with the produced HTML and PDF
- Iterate 2–3 rounds: render → preview-in-chat → polish (typography, white space, rhythm, edge cases) → re-render
- Each round, show the analyst the new representative card and ask "iterate more, or OK?"
- Stop when the analyst says "klar" / "OK"

If `use-canvas-design: no` (default) **or** the skill isn't installed, the `render-pdf.py` output is the final deliverable — full stop, no warning needed.

#### 4.7 · Preview iteration loop (D3)

After the **first** rendered output (whether or not canvas-design is in the loop), show a preview of one representative card in chat as an inline HTML artifact and ask:

> "Här är ett representativt kort. Vill du iterera på något specifikt (typografi, illustration, layout, färgval, ordval), eller är detta OK?"

Iterate until the analyst says "klar" / "OK" / "räcker". Do **not** accept the first render as final.

#### 4.8 · Design-handoff folder (D4b, conditional)

If `emit-design-handoff: yes` (default), emit `personas-project/<project>/06-design/design-handoff/` with raw material a designer (mänsklig or `claude/design`) can take into any tool:

```
06-design/design-handoff/
├── README.md                   # brief to the designer (what's here, what to do, prompt for claude/design)
├── personas/
│   ├── 01-<name>.md            # all text per persona — name, tagline, drivkrafter, pains, behov, narrative, citat — IP-id sources anchored on every field
│   ├── 02-<name>.md
│   └── …
├── images/
│   ├── portraits/              # AI-generated portraits, 2K, JPG + PNG
│   ├── animals/                # if photo-policy = animal
│   └── plot.svg                # cluster plot as vector
├── color-palette.md            # per-archetype accent colours with HEX / RGB / CMYK
├── typography-spec.md          # font recommendations + open-source fallback stack (D4)
└── design-brief.md             # one-pager — what the personas are for, where they'll be used, who reads them
```

The folder is **format-neutral**: no HTML, no WeasyPrint-specific CSS, no plot script. Raw material only. The `README.md` includes a copy-paste prompt the analyst can hand to `claude/design`:

> "Use `06-design/design-handoff/` as raw material. Read `design-brief.md` first. Produce: [analyst's chosen alternative format, e.g. 'mobile-readable HTML', 'A4 portrait version', 'Figma file via XML import']."

#### 4.9 · PDF render (J1-fix) — runs in the parent skill

After `card-renderer` returns the HTML + per-card check-list, this skill renders the PDF locally. Card-renderer's sandbox often lacks chromium and weasyprint (SJ Återförsäljare 2026-05-28); the parent has broader tooling.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/design-archetypes/references/render-pdf.py" \
  --html "personas-project/<project>/06-design/persona-cards.html" \
  --pdf  "personas-project/<project>/06-design/Persona Cards v1.pdf"
```

The script tries three engines in order:

1. **Chromium / Google Chrome `--headless --print-to-pdf`** — best fidelity, matches the analyst's browser exactly
2. **Playwright (Chromium engine, Python)** — same engine, programmatic
3. **WeasyPrint** — Python-only fallback for hosts without a browser

If all three fail, surface to the analyst:

> "PDF-generering misslyckades med alla tre motorer. HTML-filen `06-design/persona-cards.html` är öppningsbar i webbläsare — välj 'Skriv ut → Spara som PDF', A3 landskap, marginaler: ingen. Installera alternativt en av: chromium, `pip install playwright && playwright install chromium`, eller `pip install weasyprint`."

Do **not** mark `state.json.steps.design-archetypes.outputs` as containing the PDF if it doesn't actually exist on disk. Honest failure beats false claim.

Run a second pass with the same script if the analyst requested both an audit-badged and a clean version:

```bash
python3 ".../render-pdf.py" \
  --html "06-design/persona-cards-clean.html" \
  --pdf  "06-design/Persona Cards v1 — clean.pdf"
```

### 5. Falsify
Before declaring done:

- Open the HTML, render at A3 in a browser, verify each card (front and back) is single-page, no overflow
- Print to PDF, verify colours and bleed; verify 2N pages with double-sided
- Check the negative persona has all three special-treatment features (light surface, strategy banner, "Design around" pill)
- Confirm quotes on the cards match the validated archetypes.md verbatim — no last-minute paraphrasing for visual fit
- **C3:** confirm every archetype's back card carries ≥ 200 words of narrative prose anchored in the same sources as the front
- **D1b:** confirm every portrait is either AI-generated or `initials-disc`. No stick figures, no empty silhouettes
- **D2:** confirm all portraits look like members of the same series (same framing, same lighting, same colour grade — only the per-persona character varies)
- **D4b:** confirm `design-handoff/README.md` exists and the copy-paste prompt is present
- **E2:** confirm audit badges appear on the version intended for the analyst (and not on the "clean" version, if both were requested)

## Pitfalls — what went wrong on NV v1

### Pitfall · Format declared after the fact
The session started with Claude designing for web scroll and rewrote to A3 print later. Lock the format in step 2.

### Pitfall · Image aesthetic decided by inference
With no instruction, AI portraits will clash with Antrop's stipple-illustration language. Always ask. The fall-back default is stipple illustrations, not photos.

### Pitfall · Mixing Swedish and English mid-deliverable
The defaults should be Swedish for any Antrop client deliverable. Don't drift to English in headings or labels because they sound punchier — the inconsistency is read as carelessness.

### Pitfall · "Figma-ready" promised but not delivered
We don't produce Figma files. We produce HTML + PDF, plus a structured markdown spec a designer can transcribe. Be honest about that in the briefing.

### Pitfall · Designing the negative persona to look like a primary
Bengt on NV v1 needs all three: light yellow surface (breaks from dark surfaces of primaries), strategy banner in mono on navy at the bottom, and "Design around" pill instead of "Design target". Without these the layout lies about the persona's role.

### Pitfall · Skipping the print spec
PDF that looks right on screen but prints with wrong colours wastes the workshop. Always ask CMYK vs RGB and bleed before exporting.

## Delegation

After the eight-question briefing is approved at the checkpoint, delegate the rendering to `card-renderer` (sonnet). The renderer reads the design spec, the template, the tokens CSS, picks or generates illustrations, populates the HTML, prints to PDF, and runs the per-card self-falsification (overflow, quote-match, negative-treatment, language). You review the returned per-card check-list before declaring the step complete.

- `${CLAUDE_PLUGIN_ROOT}/agents/card-renderer.md` — produces persona-cards.html + Persona Cards v1.pdf

## References

- `references/antrop-design-spec.md` — Full Antrop brand spec for persona cards (colours, typography, layout, illustration policy, things-to-never-do)
- `references/pre-design-checklist.md` — The eight questions to answer before rendering, with defaults
- `references/antrop-design-tokens.css` — CSS variables for the Antrop colours and **open-source font-fallback stack** (D4)
- `references/persona-card-template.html` — Self-contained HTML template with A3 print CSS — now with front + back layout (C3)
- `references/portrait-style.md` — Locked series brief for AI-photo portraits (D2)
- `references/render-pdf.py` — Three-engine PDF render (chromium → playwright → weasyprint). Runs in this parent skill's context after card-renderer returns
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

## Output

- `personas-project/<project>/06-design/persona-cards.html` — master HTML, double-sided front + back per archetype
- `personas-project/<project>/06-design/Persona Cards v1.pdf` — PDF version (2N pages with double-sided)
- `personas-project/<project>/06-design/Persona Cards v1 — clean.pdf` *(if audit-badges and "both versions" requested)*
- `personas-project/<project>/06-design/portraits/<id>.jpg` and `.png` (per archetype)
- `personas-project/<project>/06-design/design-handoff/` *(if `emit-design-handoff: yes`)*
- Inline HTML artifact preview in chat
