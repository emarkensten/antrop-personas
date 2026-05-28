# Pitfalls extracted from prior Naturvårdsverket project sessions

These are concrete moments from three earlier Claude chats in this project where the user had to course-correct, where Claude inferred instead of asked, or where the deliverable needed rework. They feed warnings into the SKILL.md files for the UX-research plugin.

Where a pitfall is supported by silence rather than direct correction (a single-turn session where the user did not push back), it is marked **[risk]** rather than **[observed]**. The audit findings document `audit_findings.md` is treated as user-equivalent ground truth where it contradicts what Claude produced earlier.

---

## clean-interview (session: Interview 01 transcript cleaning)

The session ran in a single user turn with a very detailed brief. Claude followed the brief and produced the cleaned transcript without push-back. The pitfalls here are mostly *latent* risks the brief had to anticipate explicitly, plus a few judgement calls Claude made that the user might or might not have endorsed.

### Pitfall: Inferring an age bracket from a context clue
- **What Claude did**: Set the Age bracket header to "25–34" by reasoning from a Fridays-for-Future reference ("participant referenced being 17–18 during Fridays for Future, placing her around 24–25 in 2026").
- **What the user wanted**: The brief said "[e.g. 25–34]" — i.e. fill in if known. It didn't authorise Claude to back-calculate from circumstantial evidence.
- **Lesson**: For header metadata (age, household type, dates), only populate from a value that is *explicitly* stated by the participant. If you have to triangulate, flag the inference in the summary and leave the field blank or marked `[?]`. Do not present a derived value as a known fact. [risk]
- **Skill**: clean-interview

### Pitfall: Treating "redact to [city]" mechanically when a Stockholm-vs-not distinction is at the heart of the brief
- **What Claude did**: Replaced Örebro with `[city]`, kept Hornsgatan and Södermalm because they are inside Stockholm.
- **What the user wanted**: The brief explicitly carves out "neighbourhoods, streets, cities outside Stockholm". Claude got this right — flag is the inverse: a future run could easily collapse the carve-out and over-redact Stockholm-internal locations, which are research-relevant.
- **Lesson**: The Stockholm carve-out is load-bearing. Surface it as an explicit step ("decide for each location: inside Stockholm → keep, outside Stockholm → redact") rather than burying it inside a generic anonymisation pass. [observed — handled correctly, but a fragile point]
- **Skill**: clean-interview

### Pitfall: Stitching un-flagged corrections into the transcript
- **What Claude did**: Wrote "unravelled [?]" for the misheard "unravvled" — correctly using the `[?]` convention the brief specifies.
- **What the user wanted**: Same behaviour. Worth preserving: Claude listed the correction in the summary so the user could verify.
- **Lesson**: When applying transcription corrections, surface every non-trivial correction in the post-task summary, not just inside the document. The user reviewing the doc later can't tell what was changed without a diff. [observed — validated good move worth keeping]
- **Skill**: clean-interview

### Pitfall: Indirect-identifier redaction is the riskiest call and needs to be summarised, not buried
- **What Claude did**: Combined "specific master's programme + named university + Liljeholmen" into a redacted `master's at [university]` while keeping `[neighbourhood]` — and importantly, flagged this in the summary as a judgement call.
- **What the user wanted**: The brief explicitly says "use judgment — when in doubt, redact" and asks for indirect-identifier handling, but doesn't ask for an audit trail. Claude added one anyway, which is the right move.
- **Lesson**: Every indirect-identifier judgement must be listed in the summary with the rationale, so the user can override before the file goes anywhere else. Do this even if not asked. [observed — validated good move]
- **Skill**: clean-interview

### Pitfall: "Fix the speaker label error flagged in the transcript" requires reading the raw doc carefully, not just the brief
- **What Claude did**: Found the line at 00:10:01 that was wrongly attributed to "Interviewer" and re-attributed it to IP.
- **What the user wanted**: Exactly that — and called it out in the brief ("fix the speaker label error flagged in the transcript").
- **Lesson**: When the brief refers to "the X flagged in the transcript", treat that as a hard checklist item — open the raw doc, find the flag, fix the flag, name the fix in the summary. Don't fix it silently. [observed — validated good move]
- **Skill**: clean-interview

### Pitfall: The "do not summarise / do not collapse" rules sound obvious and are the most violated rules in transcript cleanup
- **What Claude did**: Preserved dialogue in interview order, kept repetitive material, did not bullet-point.
- **What the user wanted**: The brief has a whole "Never" block: "Summarise a section instead of transcribing it / Collapse answers into bullet points / Remove content that seems repetitive or tangential — keep it all".
- **Lesson**: When working long documents at the end of a context-heavy session, the default temptation is to "tidy up" — bullet points, condensed summaries, dropped tangents. The SKILL must hold the line with a *visible reminder before the writing step*, not just in the input brief. [risk]
- **Skill**: clean-interview

### Pitfall: Filler-word removal is judgement-heavy and easy to over-apply
- **What Claude did**: Applied the rule as stated — remove um/uh/like when meaningless, keep emotionally meaningful pauses.
- **What the user wanted**: That, plus implicit trust that Claude would not strip a participant's natural register in the name of "tidiness".
- **Lesson**: The risk profile is asymmetric. Stripping too much filler erases voice; leaving too much makes the transcript unreadable. Default toward keeping. When uncertain, mark `[pause]` rather than delete. The SKILL should call out this asymmetry explicitly. [risk]
- **Skill**: clean-interview

---

## analyse-themes, frame-and-cluster, generate-archetypes, validate-archetypes (session: Sustainable food thematic analysis)

This session is the longest and the most pitfall-rich. The user pushed back repeatedly. The audit findings document also catches a number of issues the user didn't catch in-session.

### Pitfall: Producing "behavioural variables" that are not behavioural
- **What Claude did**: Proposed six "behavioural variables" — locus of agency, practice mode, reasoning style, felt friction location, identity stance, social embeddedness — most of which are psychological drivers, not observable behaviours.
- **What the user said**: "are these really behaviours?"
- **Lesson**: When the user asks for *behavioural* variables, the test is "could you observe this in a shopping basket, a meal log, or a week of decisions?" If you'd need to interview the person to detect the variable, it's a psychological driver, not a behaviour — say so, and offer both layers explicitly. Don't dress a driver up as a behaviour. [observed — direct correction]
- **Skill**: frame-and-cluster

### Pitfall: Not committing to a methodology until asked
- **What Claude did**: Generated variables in a generic "real psychological tensions" frame without referencing any specific persona methodology.
- **What the user said**: "if we should do personas according to the cooper method what type of variables would you choose…"
- **Lesson**: At the start of an analyse-themes / frame-and-cluster flow, ask which persona methodology the user wants (Cooper, Pruitt & Adlin, jobs-to-be-done, archetype-only) — and let that drive the variable types. Don't default to a generic mix. The choice cascades through every later step. [observed — user had to invoke Cooper themselves]
- **Skill**: frame-and-cluster

### Pitfall: Recommending a count without being asked to pick one
- **What Claude did**: Initially produced six variables, then was told "pick a number of variables that you think is sufficient and choose the most important ones".
- **What the user said**: That direct instruction.
- **Lesson**: When you produce a long list of candidates, end with an explicit recommendation: "If you only want one set, I'd pick these seven — here's why". Don't make the user prompt twice for a recommendation. [observed]
- **Skill**: frame-and-cluster

### Pitfall: Failing the user's own falsification test
- **What Claude did**: Proposed "identity stance toward the sustainable label" as variable 7. When the user asked Claude to find the interview hardest to place on each scale, three of thirteen interviews resisted placement on variable 7 — IP03 on analytical grounds, IP05 and IP09 because they don't engage with the label as identity at all.
- **What the user said**: Designed the test explicitly: "if multiple interviews resist placement, the variable may be too abstract."
- **Lesson**: Before locking a variable framework, run the user's stated falsification test on yourself — map each participant to each scale, surface every hard-to-place case, and count. If more than one participant resists a scale, propose a re-cut before claiming the framework is ready. The user shouldn't have to be the one who runs the audit. [observed]
- **Skill**: frame-and-cluster, validate-archetypes

### Pitfall: Editing the wrong file
- **What Claude did**: Tried to update the framework by editing the older driver-only document, then had to backtrack: "Let me actually rewrite the framework doc properly — the file I just edited was the older driver-only framework, and the locked Cooper framework needs to be its own thing."
- **What the user said**: Nothing — Claude caught it itself.
- **Lesson**: When a deliverable has gone through multiple revisions and the variable framework has been reframed, the "framework document" might not be the file you remember. Re-read or list candidates before editing, and create a new versioned file when the underlying frame has materially changed. [observed — caught and recovered]
- **Skill**: frame-and-cluster

### Pitfall: Importing claims into archetypes that the source doesn't support
- **What Claude did**: Wrote that Anna's awareness-campaigns experience "compounds her guilt without reducing her load". The audit found this framing is not in either IP02 or IP04 — it's an importation. Same pattern hit Linn (the "not trusted as a source of social pull within networks" pain has no source-text support) and the "recognition as ambassador" need (none of IP05/IP09/IP12/IP13 articulates it; IP13 says the opposite).
- **What the audit said**: "OVER-REACH" — "The 'guilt-compounding' framing is imported, not present", and "The 'ambassador' framing comes from the clusters document's *strategic* recommendation, not from participant voice."
- **Lesson**: For every claim in a generated archetype — pains, needs, motivations, characteristic behaviours — there must be a verbatim or near-verbatim source quote. If you can't find one, either remove the claim or label it as a *strategic inference for designers*, not as a participant attribute. Strategic-recommendation language leaks into persona language easily and falsifies the persona. [observed via audit]
- **Skill**: generate-archetypes, validate-archetypes

### Pitfall: Flattening a heterogeneous composite by naming the variance once and ignoring it
- **What Claude did**: Built Maja from IP01 + IP07 + IP11 — three different mechanisms (money / self-regulation / postpartum bandwidth). The archetype writeup names the heterogeneity in one sentence ("each names a different constraint") and then proceeds as if they are one person.
- **What the audit said**: "the description then proceeds as if they are one person … the single biggest coherence weakness in the artefact."
- **Lesson**: When a composite spans more than one psychological mechanism, the archetype body must carry the variance throughout — at minimum a "variants" sub-section ("Maja-as-IP01 is class-resentful; Maja-as-IP07 is self-regulating; Maja-as-IP11 is in life-stage transition") rather than a single-paragraph acknowledgement. Otherwise the persona reads as fictional in a way the source doesn't support. [observed via audit]
- **Skill**: generate-archetypes

### Pitfall: Stitching quotes from different paragraphs without flagging
- **What Claude did**: Attributed quotes that stitched two sentences from different parts of the source (Maja, "I've made this deal with myself…" — two sentences from different parts of IP01; Anna, "My mental load is already maxed out…" — two phrases separated by an ellipsis in the source). Order was reversed for one IP04 quote.
- **What the audit said**: "MILDLY EDITED but faithful" — content true to source but the visible quotation marks promise verbatim.
- **Lesson**: When you stitch sentences into a single quote, mark the stitch with an ellipsis (…) and flag in the summary that quotes have been lightly edited for clarity. Never reverse sentence order silently. The quotation mark is a promise; respect it. [observed via audit]
- **Skill**: generate-archetypes, package-for-client

### Pitfall: Silently rewriting a participant's words to sharpen voice
- **What Claude did**: IP09's "I don't need to be told to care — I already care" was rewritten in the archetype as "Don't tell me to care — I already care" — a sharper, more imperative version of the same point.
- **What the audit said**: "MINOR PARAPHRASE — not strictly verbatim. Inversion sharpens IP09's voice but is an editor's hand on the quote."
- **Lesson**: Rhetorical sharpening of participant quotes is forbidden. If the original is less punchy than you'd like, choose a different quote — don't rewrite the existing one. Use the punchier version *only* as the archetype's own narrator-voice description, not inside quotation marks. [observed via audit]
- **Skill**: generate-archetypes, package-for-client

### Pitfall: Dropping orphan material that no archetype carries
- **What Claude did**: Generated four archetypes plus an outlier. The audit found five sample-wide orphans: legacy / intergenerational framing (IP11), successful-change pathways (IP05/IP09/IP12/IP13), anti-commercial suspicion (IP06), child-pushes-parent dynamic (IP04/IP12), IP07's mental-health framing of the value-action gap.
- **What the audit said**: The legacy orphan is "the most acute miss"; successful change pathways is "the most strategically actionable orphan".
- **Lesson**: After producing archetypes, run an explicit orphan check: for each participant, list which material in their interview is *not* represented in any archetype. Surface these as either (a) candidates for an additional archetype, (b) a strategic-recommendations note, or (c) a documented gap. Do not let orphan material disappear silently. [observed via audit]
- **Skill**: validate-archetypes

### Pitfall: Collapsing a participant into the nearest archetype when they don't fit
- **What Claude did**: Placed IP08 into the Continuity Keeper / Bengt archetype. The audit found Bengt is drawn as actively defensive (more like IP06) and IP08 is the quietest of the three — "silent already-doer, performs no-waste behaviour, refuses label without rancour."
- **What the audit said**: "Loose fit … IP08's silent-adopter register is captured at cluster level but flattened in the archetype."
- **Lesson**: When fitting participants to archetypes, the test isn't "where do they fit best" — it's "do they fit at all". If a participant's psychological register is materially different from the archetype's, flag them as a sub-variant or as a separate outlier (the way IP03 was correctly handled). [observed via audit]
- **Skill**: validate-archetypes, generate-archetypes

### Pitfall: Letting strategic recommendations leak into persona description
- **What Claude did**: Wrote Linn as someone who needs "recognition as ambassador and amplifier". The audit found this came from the *strategic recommendations layer* of the clusters document, not from any participant.
- **What the audit said**: OVER-REACH; "the framing comes from the clusters document's *strategic* recommendation, not from participant voice."
- **Lesson**: Keep a hard wall between (a) what participants say and do — which goes into the persona description — and (b) what designers should do about it — which goes into a separate strategic-implications section. Crossing the wall makes the persona look like it endorses your design recommendation. [observed via audit]
- **Skill**: generate-archetypes, package-for-client

### Pitfall: Producing themes that restate the research questions rather than cutting across them
- **What Claude did**: Was correctly held to the standard ("each one cuts across guide sections rather than restating one") and produced six themes that mostly do this — but Theme 3 and Theme 6 are partially prompted by specific guide sections, as Claude's own evaluation found.
- **What the user asked next**: To analyse which themes are emergent vs prompted.
- **Lesson**: For every theme, ask "which guide section produced this evidence?" If a single guide section produced most of the evidence, the theme is at risk of restating the question. Either re-anchor it on cross-section evidence or label it as a prompted finding. [observed]
- **Skill**: analyse-themes

### Pitfall: Reaching for visualisations before the analysis can support them
- **What Claude did**: When asked for both archetypes and a visual artifact, built both in parallel.
- **What the user wanted**: That's what was asked for — but two render iterations were needed to fix legend overflow and overlapping markers.
- **Lesson**: Visualisations have a craft layer (legend placement, marker overlap, edge-case handling) that needs at least one render-then-check cycle. Budget for it. The substantive insight should live in the document; the visual is for at-a-glance recognition, not for carrying the argument. [observed]
- **Skill**: generate-archetypes, package-for-client

### Pitfall: Handling edge cases by inventing a side-zone rather than asking
- **What Claude did**: For IP07 (oscillating between poles) and IP11 (in life-stage transition), created an "edge cases" zone to the right of the scale rather than plotting them on it.
- **What the user wanted**: Didn't object — and Claude flagged the choice in the summary.
- **Lesson**: This is a validated good move worth preserving. When data points genuinely don't sit on a scale, an explicit "edge cases" or "doesn't apply" zone preserves analytical honesty. The pitfall would be the opposite — forcing every point onto the scale to make the picture look clean. [observed — validated good move]
- **Skill**: frame-and-cluster, generate-archetypes

---

## design-archetypes (session: Word personas to Claude design)

The session is a single user turn — "how would you move from the word personas to claude design? a prompt and an attachment?" Claude gave a useful overview but the conversation never reached deliverable production. Pitfalls here are about the *meta* step where a researcher hands archetypes to a design phase.

### Pitfall: Offering many possible outputs without asking what the user is actually doing
- **What Claude did**: Listed four possible outputs — visual persona card, slide deck, design-handoff doc, design-critique — and asked the user at the end what they wanted.
- **What the user wanted**: Probably one specific thing; the conversation didn't continue, so we don't know which.
- **Lesson**: When a user asks "how would I do X", the first move is usually a clarifying question, not a menu. For design-archetypes, the menu has 4–6 plausible outputs that each imply a different process. Ask first ("what's the design output for — stakeholder buy-in, a designer's brief, or a workshop?"), then propose the right format. [observed pattern — but the user did seem to want a menu in this case]
- **Skill**: design-archetypes, package-for-client

### Pitfall: Suggesting "Figma-ready" without checking
- **What Claude did**: Listed "If you want a Figma-ready design spec…" as an option.
- **What the user wanted**: Unknown — but if a designer takes "Figma-ready" at face value, they will be disappointed. Claude can't produce a Figma file; it can produce a written spec that a designer transcribes into Figma.
- **Lesson**: Be precise about what "design-ready" means in this context. Output options for design-archetypes are: structured markdown / docx for handoff, HTML/SVG persona card that renders inline, slides for a stakeholder presentation. Not Figma files, not interactive prototypes. Set expectations honestly. [risk]
- **Skill**: design-archetypes, package-for-client

### Pitfall: Skipping the question of which archetypes to design for
- **What Claude did**: Treated "the personas" as a single bundle to be re-formatted.
- **What the user might have needed**: A persona set typically has primaries, secondaries, supplementals and negative personas (as the thematic-analysis session correctly produced — Anna and Maja as primary, Linn as supplemental, Bengt as negative). Different design outputs may serve only the primaries.
- **Lesson**: Before producing design-facing artifacts from a persona set, ask which personas are in scope. Negative personas in particular are usually *not* turned into design-ready cards — they live in the strategy document as constraints. Surface this distinction. [risk]
- **Skill**: design-archetypes, package-for-client

---

## Cross-cutting patterns

These recur across two or more sessions and are the highest-priority warnings for the plugin.

### Pattern 1: Inferring instead of asking
Claude repeatedly fills in values from context — an age bracket from a Fridays-for-Future reference, a "behavioural" framing when none was specified, an "ambassador" need that nobody articulated, a persona's pain that no participant named. The pattern: when a slot in the deliverable is empty, Claude reaches for a plausible value rather than flagging the gap or asking. The fix is structural: every SKILL.md must enumerate the slots that may *only* be filled from explicit source evidence, and the slots where strategic inference is permitted but must be labelled as such.

### Pattern 2: Strategic recommendations leaking into participant voice
The cleanest example is the "ambassador" need attributed to Linn, which comes from the clusters document's strategy section, not from any of IP05/IP09/IP12/IP13. The same mechanism produced the "guilt-compounding" framing in Anna. Once strategic-recommendation language has been written about a persona, it's easy to fold back in as if a participant said it. The plugin needs a hard wall: persona-description sections vs. design-implication sections must live in different documents, or at minimum in clearly labelled sections with different writing voice. Quote marks in the persona section are a contract — they must round-trip back to a verbatim transcript line.

### Pattern 3: Flattening heterogeneity
This shows up at every level: composites that span three different psychological mechanisms get one acknowledgement sentence and then proceed as if uniform; orphan material that doesn't fit any cluster disappears; participants who don't fit an archetype get squeezed into the closest one anyway. The plugin's clustering and archetype steps need an explicit *don't-fit* policy — surface variance, name sub-variants, keep orphans visible, treat single-participant outliers as legitimate (as IP03 was correctly handled). Composite tightness is a virtue only when the source supports it.

### Pattern 4: Skipping the falsification step the user would have asked for
In the analyse-themes session, Claude only ran an emergent-vs-prompted check after the user asked. Variable 7 only failed its test because the user designed the test. Quote-stitching only surfaced because the audit ran later. The pattern: Claude produces a confident artifact and waits for the user to test it. The plugin should bake the falsification steps in — every analyse-themes / frame-and-cluster / generate-archetypes flow should end with a *built-in* validation pass before the deliverable is presented, not after.

### Pattern 5: Choice of methodology assumed rather than asked
The thematic-analysis session ran for several turns of "behavioural variables" before the user invoked Cooper. Once Cooper was named, everything reframed. The same risk applies to thematic analysis (reflexive TA vs. framework analysis vs. grounded theory) and to archetype methodology (Cooper personas vs. jobs-to-be-done vs. lightweight archetypes). The plugin should ask the methodology question at the start of each step — explicitly, with options — rather than reach for a sensible default.
