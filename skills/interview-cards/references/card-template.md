# Interview-card field template

Default field set, based on the AMF Sparafasen card. **This template is the starting point** — every project edits it. Copy this file to `personas-project/<project>/card-template.md` to customise for one project.

## Fields

### Header

- **Card title** — fixed text in the top-left: `INTERVJUKORT <PROJECT-NAME>`. Project name is set by the analyst at card-time (defaults to whatever the analyst typed in `/antrop-personas:start-persona-project`).

### Portrait

- An AI-generated stipple/duotone portrait (when `photo-policy: ai-portrait`) OR a coloured disc with IP-id (when `initials-disc`). Lives top-left, below the title.

### Demographic block (right of portrait)

Standard demographic fields. Each field **only** populates from explicit statements in the interview — never inferred.

- **Avtalsområde / Domain segment** — the project-specific segment label. For AMF: pension domain (ITP/ITPK, SAF-LO, etc.). For another project: customer segment, role, business unit, whatever the project uses to slice respondents.
- **Ålder / Age** — only from explicit statement. If not stated, leave blank or `[?]`.
- **Löpnummer / Reference number** — the participant's IP-id or pseudonym (e.g. `1808-24`, `IP07`). Always populate.
- **Segment** — secondary segmentation (e.g. "Välbärgade" / "Affluent", "Frequent flyer", "Heavy user"). Project-specific. Leave blank if not segmented.
- **Civilstatus / Marital status** — only from explicit statement.
- **Sysselsättning / Occupation** — only from explicit statement.

### Quote block (top-right)

- **Bra citat / Key quotes** — 2–3 verbatim quotes from the interview. Each quote stays in source language. Choose quotes that:
  - reveal the participant's relationship to the research topic (not generic small-talk)
  - are short enough to read at A3 distance (one or two sentences max per quote)
  - are quoted verbatim, with no stitching unless marked with `…`

### Content columns

Three columns below the header block. Column widths can be tuned per project; default is left=narrow, middle=wide, right=narrow.

- **Left column — Intresse & kunnande / Interest & competence** — bullet points: what the participant knows about the topic, what they actively do, what their relationship to the domain is. Each bullet point must trace to verbatim source.
- **Middle column — Inställning, behov/problem & drivkrafter / Stance, needs/problems & drivers** — bullet points: what the participant cares about, what frustrates them, what motivates them, what they're trying to do. This is the largest column. Each bullet point must trace to verbatim source.
- **Right column — Skulle vara bättre om… / What would be better if…** — *participant-stated* wishes, not designer recommendations. Each bullet must trace to a verbatim quote where the participant articulates this wish. If the participant didn't articulate a wish, leave the field empty — don't fill it with designer-side ideas.

### Övrigt / Other (right column bottom)

- Free-text field for context the analyst wants on the card but doesn't fit the structured fields. Hobbies, occupation context, relevant life-events. Optional.

## Customising per project

For a non-pension project (or any project where the AMF fields don't fit), edit the labels and structure in a project-local copy:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/interview-cards/references/card-template.md \
   personas-project/<project>/card-template.md
# edit the project-local file
```

The skill reads the project-local file first if present, otherwise this default.

### Example: a transit-mobility project

- Domain segment → "Resmönster" (Mobility pattern)
- Segment → "Pendlare / Tillfällig / Långresenär"
- Civilstatus → drop (not relevant)
- Sysselsättning → drop (not relevant)
- Add: "Vanliga sträckor"
- Add: "Biljett-/app-vanor"

### Example: a B2B-product project

- Avtalsområde → "Roll" / "Funktion"
- Ålder → drop (replace with "Bransch-erfarenhet" if relevant)
- Civilstatus → drop
- Segment → "Företagsstorlek"
- Add: "Verktyg & system de använder"
- Add: "Beslutsmandat"

The point: the **structure is fixed** (header, portrait, demographics, quotes, three content columns), the **field labels and content** is project-specific.

## What NOT to do

- **Don't infer demographic fields.** Same rule as `clean-interview` — only explicit statements populate. The card's Age field is a fact, not an inference.
- **Don't sharpen quotes.** Same rule as `generate-archetypes` — pick a different verbatim quote if the chosen one doesn't fit.
- **Don't put designer recommendations in participant fields.** The "Skulle vara bättre om" field is for what the participant said they wanted, not what the design team thinks they need.
- **Don't break the indirect-identifier check.** A card combining several fields (occupation + neighbourhood + age + segment) can re-identify even without a name. Run the indirect-identifier check from `clean-interview/references/anonymisation-policy.md` before rendering.
