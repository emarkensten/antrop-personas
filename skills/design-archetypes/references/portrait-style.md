# Portrait style — locked brief for the persona-card series (D2)

This file is the source of truth for what every AI-generated portrait in a persona-card series should look like. The point of locking it is **batch consistency**: when the cards are hung next to each other on a workshop wall, all N portraits must read as members of the same series — not five different photoshoots stitched together.

`card-renderer` reads this file before generating any portrait. Override per-project by dropping a `portrait-style.md` next to `.persona-config.md` in the project folder; otherwise the defaults below apply.

---

## 1 · Composition (locked across the series)

- **Framing:** half-bust — top of head to mid-chest. Subject roughly centred, with ~10% headroom above the head.
- **Eye-line:** at camera height; subject looking just past the lens (not direct eye-contact, not in profile).
- **Body angle:** chest at 5–10° to the camera; not full-frontal, not full three-quarter.
- **Pose energy:** quiet, considered. Not smiling broadly. Not somber. A neutral resting expression with the suggestion of an in-progress thought.

## 2 · Lighting

- **Key light:** soft, diffuse, from the upper-left at ~45°. Window-light feel.
- **Fill:** gentle, opposite side, ~1.5 stops below key.
- **Background:** unlit; falls off into ~30% mid-grey or the persona's accent colour at low saturation.
- **Highlights:** softly clipped on the brow and cheekbone, never blown out. No specular catch-lights from ring-lights.

## 3 · Lens & rendering

- **Equivalent:** 85mm portrait lens, f/2.0 — narrow but not paper-thin depth of field. Eyes sharp, shirt-shoulder beginning to soften.
- **Aspect:** 4:5 portrait crop (so the disc-mask the cards use does not crop important content).
- **Resolution:** 2048 × 2560 minimum at generation time. Down-sample on render.

## 4 · Colour grade

- **Base palette:** desaturated by ~15%, with skin tones held to natural reference points.
- **Series tint:** each portrait gets a low-saturation wash in **the persona's accent colour** at ~8–10% opacity over the background and very lightly on the cooler areas of skin. The accent never dominates — it should read as "these portraits are all from the same shoot, with subtle accent washes per persona", not "this is a colour-graded portrait series".
- **Forbidden:** Instagram-style filter looks, heavy grain, sepia, monochrome.

## 5 · Background

- One of:
  - **Plain wash** — single-tone background in mid-grey or the persona's accent at low saturation
  - **Soft environmental** — out-of-focus interior suggestion (window, wall, plant) that doesn't telegraph profession
- **Forbidden:** branded environments (no specific cafés, offices, gyms, workplaces — the portrait should not over-determine the persona's job)

## 6 · Subject character (per-persona, varies by design)

`card-renderer` reads each archetype's `Per-persona character brief` (pre-design-checklist question 4) and fills in:

- Approximate apparent age (must round-trip to the archetype's stated age)
- Gender presentation
- Ethnicity
- Body type
- Clothing (everyday — avoid uniforms unless the archetype is occupation-defined)
- One small specific detail per person (wire-rim glasses, a scarf, a single earring) — to give the series variety within consistency

These vary per persona. Everything in §1–§5 does not.

## 7 · Seeded prompt template (D2)

`card-renderer` builds the gemini-image-gen prompt from this template, substituting the per-persona fields. Same seed across the series for maximum stylistic consistency:

```
Realistic photographic half-bust portrait, 85mm equivalent f/2.0, soft window
light from upper-left, gentle fill, quiet considered expression, looking just
past camera, ~10% headroom, 4:5 aspect.
Subject: <apparent_age> <gender_presentation> <ethnicity>, <body_type>,
wearing <clothing>, <one_specific_detail>.
Background: plain wash in <accent_color_low_sat>, soft falloff.
Style: photojournalistic, desaturated by ~15%, no filter look, no grain
overlay, no specular ring-light catch lights. Skin tones natural. Series
colour wash: <accent_color> at 8% opacity.
Seed: <project_seed>
```

`<project_seed>` is captured in `state.json` at first portrait generation and reused for every subsequent one in the same series.

## 8 · Forbidden under every project (D1b)

These are hard rules and **cannot** be overridden by analyst or operator:

- ❌ Geometric stick figures
- ❌ Empty silhouettes / vector outlines without a face
- ❌ Abstract geometric portraits
- ❌ Emoji avatars
- ❌ Generic stock-photo placeholders ("person 1.jpg")
- ❌ Photorealistic portraits of *real* people (likeness liability)

If `gemini-image-gen` fails for any reason, the fallback is **`initials-disc`** — a large accent-coloured disc with the participant id or initials in the persona's display typography. Never fall back to a stick figure.

## 9 · Acceptance test

When the N portraits are rendered, line them up side-by-side at A6 scale. The test:

> "If a stranger walked past, would they read these as members of the same series?"

If a single portrait looks different (warmer skin grade, different framing, harder light), it is wrong. Regenerate that one with the same seed and a tighter prompt — never regrade or composite afterwards.
