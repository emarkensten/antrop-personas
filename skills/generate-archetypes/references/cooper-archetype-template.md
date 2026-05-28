# Cooper archetype template

Every archetype in archetypes.md uses this template. Don't drop fields. Don't reorder.

## Format per archetype

```
## ARCHETYPE N · <ROLE>
### <Composite name>, <age> — The <descriptor>

**Composite from.** <Explicit source list — e.g. "IP02 (34, IT consultant, 2 young kids) and IP04 (41, project manager, 3 kids)">

**Sketch.** 2–3 sentences of life context. Show, don't summarise. Make the person legible enough to hold in someone's head.

**Life goals.** Long-horizon, identity-level — who this person wants to be over years ("vara en närvarande förälder", "vara respekterad som expert"). 1–3 short statements. These anchor strategic positioning but rarely drive a feature decision.

**Experience goals.** How the person wants to *feel* during interaction ("kompetent, inte dum", "lugn", "inte överbelastad", "litad på"). 1–3 short statements. These shape interaction quality, microcopy, error-handling — the texture of the experience.

**End goals.** What the person wants to accomplish through the product/service ("få en middag på bordet utan konflikt", "rapportera felet och bli klar", "veta att betalningen gått igenom"). 2–5 concrete statements. **End goals do the design work** — they are what features and flows have to deliver.

> Cooper's hierarchy: Life goals anchor strategy; Experience goals shape interaction; End goals drive features. Every claim still traces to a verbatim source quote.

**Key pains.** Felt frustrations and barriers. Each pain must trace to verbatim source material (see falsification check in generate-archetypes SKILL.md). Each pain a designer could *do something about*.

**Key needs.** What would actually move this person. Not "more awareness" — specific levers the source supports.

**Anchoring themes from the thematic analysis.** Theme N (short description), Theme M (short description). The themes that this archetype most directly expresses.

**Sub-variants.** [Only if the composite spans materially different psychologies — e.g. "Maja-as-IP01 is class-resentful; Maja-as-IP07 is self-regulating; Maja-as-IP11 is in life-stage transition"] Otherwise omit this section.

**Narrative.** [C1 — required.] 3–6 paragraphs of running prose, ≥ 200 words. Written in third-person, or in first-person if the project methodology calls for it. Describes the person in context — a day in their life, their relationship to the subject of the research, their life-history context, the felt texture of the tension the archetype embodies. Anchored in **the same verbatim citations** that the bullet fields use — every paragraph must round-trip to at least one quote in a composite member's interview. This is the field the bullets exist to summarise; it is what carries the persona on the **back of the A3 card** in workshops.

**Verbatim source map for the narrative.** [Internal aid, not rendered on the card.] One line per narrative paragraph listing the interview-id(s) and the line/timestamp the paragraph leans on. The audit (`validate-archetypes`) uses this to check the narrative against its sources.

**In their own words.**
> "Quote one verbatim." — Interview NN
>
> "Quote two verbatim." — Interview MM

**Strategic implications.** [Strictly separated from the persona description. This is what *designers should do about it*, not what the persona experiences. Optional — can also live in a separate strategy doc.]
```

## Role types — pick from this list per archetype

Cooper specifies six persona types. Use the right one for each archetype; don't default everyone to "primary".

- **PRIMARY · DESIGN TARGET** — the audience the work is for. **Exactly one** per product/service (Cooper's prioritisation rule — see below). If you can't pick one, the strategy is unclear and that's worth surfacing.
- **SECONDARY · ALSO DESIGN FOR** — also catered for, but won't get features tailored specifically for them at the expense of the primary. 0–2 per project.
- **SUPPLEMENTAL · CALIBRATION** — already there or otherwise not the focus, but the design must not condescend to / alienate them.
- **CUSTOMER · BUYS BUT DOESN'T USE** — *Conditional. Only include in B2B / multi-stakeholder / procured contexts where the buyer ≠ the user.* The classic case: IT-chefen / inköp / upphandlingsenheten who approves the spend but doesn't use the tool. The customer persona's goals are about *purchase justification, integration, total cost of ownership, governance* — not about the user task. If the project is B2C consumer or otherwise has buyer = user, **omit this type entirely**. See "Detecting B2B / customer-persona context" below.
- **SERVED · INDIRECT BENEFICIARY** — *Conditional. Only when the product affects someone who doesn't interact with it.* Patient when product is for nurse; pupil when product is for teacher; citizen when product is for caseworker. Omit when the user is also the beneficiary.
- **NEGATIVE · DESIGN AROUND** — explicitly not the work's target. Named so the strategy doesn't drift toward them and dilute the primary. Cooper's negative-persona logic.
- **OUTLIER · MARGIN NOTE** — n=1 in the sample, intellectually distinct enough to recognise. Worth carrying as a small supplemental note rather than merged into a nearby cluster.

## Detecting B2B / customer-persona context

At the Propose beat in `generate-archetypes`, scan themes.md and a sample of cleaned interviews for signals that the project has a buyer ≠ user gap. If two or more signals appear, *surface to the analyst* a recommendation to include a CUSTOMER archetype (don't add silently — the analyst decides).

Signals:
- Procurement / purchase / RFP / anbud / upphandling / inköp / avtal language
- Decision-makers / sponsors / beslutsfattare / godkännare distinct from end users
- IT-chef / CIO / finanschef / inköpschef approving spend
- "för våra kunder" / "för medarbetarna" / "for our employees" (the user is downstream of the buyer)
- Enterprise / organisation / public-sector / municipality as the contracting party
- Total cost of ownership / SLA / governance / compliance / integration as recurring topics

For pure B2C consumer products (Tinder, Spotify, a personal banking app where the consumer pays for themselves), customer = user; **do not** fabricate a customer persona just to fill the slot.

## Prioritisation rule — one primary per product

Cooper's rule: **exactly one PRIMARY** per product or service. The primary is the persona whose End goals the product must fulfil even at the cost of optimising for others. If you can serve the primary's End goals you can usually serve secondaries' too; the reverse is not true.

Inputs to the prioritisation decision (gathered at the Propose beat):

- **Effektmål / project effect goals** — what change does the project want to drive? ("öka konverteringen för förstagångsbokare", "minska tid till första lyckade ärende", "höja NPS bland nya kunder"). The primary is whoever most directly enables those goals.
- **Project brief** — scope, constraints, success criteria, who the deliverable is for.
- **Business stakes** — which segment is the strategic bet? (Sometimes the most-numerous segment isn't the primary — the *highest-stakes* segment is.)

The analyst owns this call; the skill surfaces the candidates and the trade-off, then locks the decision after analyst sign-off at the I1 checkpoint.

Output: archetypes.md has an explicit **Prioritisation rationale** block above the per-archetype sections — naming each persona's role and one sentence on why this primary, not another.

## Verbatim rule

Quotes attributed to a participant must be verbatim from the cleaned interview, with interview-id. The plugin's cross-cutting principle #1 applies: every claim → verbatim source, or remove it.

Three permitted edits to quotes (clearly flagged):
- Trimming with `…` to fit the card
- Stitching non-adjacent sentences from the same source with `…` and a flag in the production summary
- Translating from Swedish to English (with the original language noted, e.g. "— Interview 02, translated from Swedish")

Forbidden:
- Sharpening, rephrasing, or punching up
- Stitching across different interviews
- Reordering sentence within a quote silently

## What this document is NOT

It is not yet the designed persona card (that's `design-archetypes`). It is the *content* of the persona — text-only, working markdown the design step will lay out. Keep it plain and clean; the visual layer comes later.
