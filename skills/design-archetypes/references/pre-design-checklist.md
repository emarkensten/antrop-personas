# Pre-design briefing checklist (from Claude design's own reflection)

This is what Claude design said it would have needed BEFORE starting the persona-design step on this project. It is the missing input that, when not provided, forced rewrites and inference. Encode this as a mandatory pre-design checkpoint in the `design-archetypes` skill — the user must answer these eight questions before any visual is rendered. The single most important one is #2.

## The eight things to lock down upfront

### 1. Format
- Page size and orientation (e.g. A3 landscape)
- One persona per page, or several?
- Web view, print, both?
- → Decide A3 canvas from start; skip web-to-print rewrite.

### 2. Image aesthetic — THE MOST CRITICAL
**Default since v0.9.0-rc4 (D1b): `ai-photo`** — realistic but generic AI-generated portraits via `gemini-image-gen`, with consistency locked across the series by `references/portrait-style.md`. This produces a uniform, photojournalistic look that pairs cleanly with Antrop's typography and accent palette.

Other valid options:
- `stipple` — Antrop's hand-drawn stipple illustration library (or stipple-style AI). Use when the brand context strongly favours non-photographic imagery.
- `illustration` — Antrop's hand-drawn illustrations (non-stipple).
- `animal` — animal portraits as personas (project-specific design choice).

**`initials-disc` is ONLY a fallback** when AI generation fails. Never an upfront choice.

**Forbidden under every setting:**
- ❌ Geometric stick figures
- ❌ Empty silhouettes / vector outlines
- ❌ Abstract geometric placeholders
- ❌ Stock-photo placeholders
- ❌ Photorealistic likenesses of *real* people

When choosing other than `ai-photo`, decide BEFORE prompting:
- Duotone (dark blue/turquoise, or wine-red/light pink)?
- Halftone / grain overlay to match stippling feel?
- Cropped into an organic wave-mask (like the cover photo in the keynote template)?

Without this decision → it reads as stock.

### 3. Consistency rules across the persona set
If a single image deviates the whole series looks Unsplash-scraped. **The default brief in `references/portrait-style.md` locks these — review and override only if the project needs something else:**
- Same framing (half-bust by default)
- Same lighting (soft window light from upper-left)
- Same eye contact (looking just past camera)
- Same colour grade (~15% desaturated, low-saturation accent wash per persona)
- Same lens feel (85mm equivalent, f/2.0)
- Same prompt template + seed across the series

### 4. Per-persona character brief
For each persona: gender, ethnicity, body type, clothing, environment.
- Text alone implies (Anna 38 → woman; Bengt 58 → man) but inference is not instruction.
- Composites: should Maja (student/freelancer/parent) be depicted as one specific person or intentionally ambiguous?

### 5. Ethics
- Are the personas based on real interview subjects? → consent considerations for AI-generated likenesses.
- Footer disclaimer ("AI-genererat porträtt — inte en riktig person") is good form, especially in public-sector work.

### 6. Language
- Swedish or English throughout? Mixing is the failure mode.
- For real client delivery to a Swedish public agency: consistent Swedish (the source quotes are translated from Swedish interviews anyway).

### 7. Print specifications
- Bleed (3 mm around)?
- CMYK or RGB?
- Colour profile (FOGRA39 / ISOcoated_v2 for Swedish print)?
- Single-sided A3, or A3 spreads on A2 sheets?

### 8. Usage
- Workshop wall? Hand-out around the table? PDF in email?
- A3 on a wall can take less text; A3 in hand tolerates more.
- → Controls typography scale.

## How to use this in the skill

Make `design-archetypes` REFUSE to render until all eight are answered. Pre-fill defaults from a project config if available (most Antrop projects: A3 landscape, stipple illustrations not photos, Swedish, CMYK FOGRA39, hand-out + PDF). The user only needs to deviate from defaults, not re-decide every time.

If only one can be answered upfront, demand #2 (image aesthetic). All other typography, colour balance, white space follow from that decision.
