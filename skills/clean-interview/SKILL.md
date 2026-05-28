---
name: clean-interview
description: "Clean, anonymise, and convert a raw interview transcript into analysis-ready markdown. Handles .pdf / .docx / .md / .txt input transparently. Use when the analyst wants to prepare transcripts for thematic analysis or upload raw interview files."
metadata:
  version: 1.1.0
  pipeline-step: 1
  works-on: persona-research
  triggers:
    - "städa intervju"
    - "anonymisera transkript"
    - "rensa intervju"
    - "rensa transkript inför analys"
    - "rensa utskriften"
    - "clean interview"
    - "prepare transcript"
    - "GDPR-anonymisering"
    - "gör intervjun klar för analys"
    - "kan du fixa den här intervjun"
    - "make this transcript safe to analyse"
    - "depersonalise this"
    - "förbered intervju för analys"
    - "remove names from transcript"
---

# Clean interview

Turn a raw interview transcript into a clean, anonymised, analysis-ready document. One transcript at a time.

This is step 1 of 8 in the antrop-personas pipeline. The output of this skill becomes the input to `analyse-themes`.

## Pipeline state

This skill is step `1-clean-interview` in the eight-step pipeline. At its **Read** beat it loads `personas-project/<project>/state.json` and:

- **Required-before:** —. If a required step's status is not `completed` (or explicitly `skipped`), halt with the graceful-fail message from `${CLAUDE_PLUGIN_ROOT}/references/pipeline-state.md` and direct the analyst to the right earlier skill.
- **Config override:** if `personas-project/<project>/.persona-config.md` exists, apply its overrides for language, methodology, anonymisation policy, and brand. Otherwise use the plugin defaults documented in `${CLAUDE_PLUGIN_ROOT}/settings/local.md.example`.

At its **Produce** beat it updates `state.json` for this step (status `completed`, completion timestamp, key counts, output paths). Write atomically (write to `.state.json.tmp`, rename) so a crashed write doesn't corrupt the file. If the Falsify beat surfaces issues the analyst wants to redo, mark `needs_rework` instead of `completed`.

## What this skill does

- Removes filler ("um", "ja precis", "liksom") when meaningless; keeps it when emotionally loaded
- Anonymises direct identifiers (names, employer, exact age, exact address) and the riskier indirect ones (rare role + city + life-event combinations that could re-identify)
- Corrects transcription errors flagged by the user, leaving uncertain words marked `[?]`
- Surfaces every non-trivial judgement call in a summary the user reviews before the file is saved

It does **not** summarise, collapse, or bullet-point the content. The cleaned document preserves dialogue order and substance.

## Inputs

- One raw transcript (`.pdf`, `.docx`, `.txt`, `.md`, or paste in chat)
- Optional: an `--input-dir <path>` override (read from `state.json` / `.persona-config.md`) pointing at the directory the analyst keeps interviews in
- Optional: a project anonymisation policy (city carve-outs, redaction conventions). Default policy is the one developed for Naturvårdsverket v1 — see `references/anonymisation-policy.md`
- Optional: corrections the user flagged in the raw transcript ("fix the speaker label at 00:10:01")

## Auto-discovery of raw interviews (A1)

At the **Read** beat:

1. Read `state.json.input_dir`. If set, use it as the search root. Otherwise default to `personas-project/<project>/01-interviews/`.
2. Run `Glob` recursively for **all supported extensions** against the root:
   `**/*.{pdf,docx,doc,md,markdown,txt,text,rtf,vtt,srt,json,html,htm,csv}`. **Don't** assume any specific subfolder name — projects in the wild use `intervjuer/pdf/`, `Transkriberingar/`, `intervjuer_af/`, `cleaned interviews/`, `transcripts/`, `råmaterial/`, `Otter exports/`, `Teams recordings/`, and others. Pick up whatever's there. See `${CLAUDE_PLUGIN_ROOT}/references/input-ingestion.md` for the full format + structure contract.
3. **Triage the hits before showing them.** Auto-discovery is greedy on purpose, so a raw folder usually contains non-interview files too (consent forms, the interview guide, moderator notes, a brief, screenshots-as-PDF, `~$`-locked Office temp files, `.DS_Store`). Apply the classification heuristics in `references/input-ingestion.md` § "Telling interviews from noise" and split the hits into **likely interviews** / **probably not** / **unsure**. Never silently drop a file — surface the split.
4. Surface the discovered+triaged list with one-line metadata (filename, extension, byte size, modified-at, and your interview/not/unsure guess) and ask the analyst:

   > "I found N files under `<input_dir>`. I think M are interviews (listed), K are probably support material (consent forms, guide, notes), and J I'm unsure about. Clean the M? Adjust the selection?"

5. If the analyst says "yes but only some", let them narrow by glob pattern or by hand-picking. If they say "wrong folder", let them point at a different one — update `state.json.input_dir` accordingly. Handle the awkward structures (one file containing all interviews, one participant split across several files, mixed already-cleaned + raw) per `references/input-ingestion.md` § "Awkward structures".

## Working format and format-agnostic input (A2)

**All working files in this pipeline are `.md`** — cheap to read, cheap to write, diff-friendly, easy for the next skill to ingest. Word and PDF only exist at the edges:

- Raw input can be `.pdf`, `.docx`, `.doc`, `.rtf`, `.txt`, `.md`, `.vtt`/`.srt` (caption/auto-transcript exports), `.json` (Otter/Whisper/Teams transcript exports), `.html`, or `.csv` — this skill detects the format and converts as needed. See `${CLAUDE_PLUGIN_ROOT}/references/input-ingestion.md` for the full per-format contract.
- The cleaned working file is **always** `.md` under `personas-project/<project>/01-interviews/`
- A `.docx` mirror of the cleaned file is produced **only** if the user explicitly asks for one to share outside the project

Reasoning: a 90-minute interview can be ~12k tokens as `.md` and 3–5× that as a parsed `.docx`. Every downstream skill (`analyse-themes`, `frame-and-cluster`, `generate-archetypes`, `validate-archetypes`) re-reads these files repeatedly. Keeping them as `.md` is the single biggest token saving in the pipeline.

### Input-detection step (run before the five-beat flow)

For every file picked up by auto-discovery, dispatch on extension:

```bash
# Resolve input format and convert to <id>-raw.md under 01-interviews/

case "${INPUT_FILE,,}" in
  *.md)
    cp "$INPUT_FILE" "01-interviews/<id>-raw.md"   # no conversion needed
    ;;
  *.txt)
    cp "$INPUT_FILE" "01-interviews/<id>-raw.md"   # plain text — rename to .md
    ;;
  *.docx)
    python3 -c "
from docx import Document
doc = Document('$INPUT_FILE')
for p in doc.paragraphs:
    print(p.text)
" > "01-interviews/<id>-raw.md"
    ;;
  *.doc)
    # Legacy binary Word. No pure-Python reader; use a converter if present.
    if command -v textutil >/dev/null; then           # macOS
      textutil -convert txt -stdout "$INPUT_FILE" > "01-interviews/<id>-raw.md"
    elif command -v antiword >/dev/null; then          # Linux
      antiword "$INPUT_FILE" > "01-interviews/<id>-raw.md"
    elif command -v libreoffice >/dev/null; then
      base="$(basename "$INPUT_FILE")"; base="${base%.*}"; libreoffice --headless --convert-to txt:Text --outdir /tmp "$INPUT_FILE" && cat "/tmp/$base.txt" > "01-interviews/<id>-raw.md"
    else
      echo "Cannot read legacy .doc — ask the analyst to re-save as .docx, or install textutil/antiword/libreoffice" >&2; exit 1
    fi
    ;;
  *.rtf)
    python3 -c "
try:
    from striprtf.striprtf import rtf_to_text
    print(rtf_to_text(open('$INPUT_FILE', encoding='utf-8', errors='ignore').read()))
except ImportError:
    import re, sys
    t = open('$INPUT_FILE', encoding='utf-8', errors='ignore').read()
    t = re.sub(r'\\\\[a-z]+-?[0-9]* ?', '', t)   # strip control words
    t = re.sub(r'[{}]', '', t)
    print(t)
" > "01-interviews/<id>-raw.md"
    ;;
  *.vtt|*.srt)
    # Caption / auto-transcript export. Drop cue numbers, timestamps, WEBVTT header,
    # and collapse repeated speaker tags. Keep the spoken text in order.
    python3 -c "
import re, sys
lines = open('$INPUT_FILE', encoding='utf-8', errors='ignore').read().splitlines()
out = []
for ln in lines:
    s = ln.strip()
    if not s or s == 'WEBVTT' or s.isdigit(): continue
    if '-->' in s: continue                       # timestamp cue
    s = re.sub(r'<[^>]+>', '', s)                 # inline <v Speaker> tags
    out.append(s)
print('\n'.join(out))
" > "01-interviews/<id>-raw.md"
    ;;
  *.json)
    # Otter / Whisper / Teams / Zoom transcript JSON. Try the common shapes:
    # top-level 'segments'/'monologues'/'results', each with 'text'/'speaker'.
    python3 -c "
import json, sys
d = json.load(open('$INPUT_FILE', encoding='utf-8'))
def emit(seg):
    spk = seg.get('speaker') or seg.get('speaker_name') or seg.get('speaker_label')
    txt = seg.get('text') or seg.get('transcript') or seg.get('content') or ''
    print((f'{spk}: ' if spk else '') + txt.strip())
segs = d.get('segments') or d.get('monologues') or d.get('results') or (d if isinstance(d, list) else [])
if segs:
    for s in segs: emit(s)
else:
    print(json.dumps(d, ensure_ascii=False, indent=2))   # unknown shape — dump for manual triage
" > "01-interviews/<id>-raw.md"
    ;;
  *.html|*.htm)
    python3 -c "
import re, sys
t = open('$INPUT_FILE', encoding='utf-8', errors='ignore').read()
t = re.sub(r'(?is)<(script|style).*?</\1>', '', t)
t = re.sub(r'(?i)</(p|div|br|li|h[1-6]|tr)>', '\n', t)
t = re.sub(r'<[^>]+>', '', t)
import html; print(html.unescape(t))
" > "01-interviews/<id>-raw.md"
    ;;
  *.csv)
    # Some tools export transcripts as speaker,timestamp,text rows. Join the text column.
    python3 -c "
import csv, sys
rows = list(csv.reader(open('$INPUT_FILE', encoding='utf-8', errors='ignore')))
# Heuristic: find the column whose cells are longest on average = the text column.
if rows:
    ncol = max(len(r) for r in rows)
    body = rows[1:] if any(not c.replace('.','').isdigit() for c in rows[0]) else rows
    avg = [sum(len(r[i]) for r in body if i < len(r))/max(1,len(body)) for i in range(ncol)]
    ti = avg.index(max(avg))
    for r in body:
        if ti < len(r) and r[ti].strip(): print(r[ti].strip())
" > "01-interviews/<id>-raw.md"
    ;;
  *.pdf)
    # Preferred: pypdf (text-layer extraction). pdfplumber is a fallback for messy PDFs.
    python3 -c "
import pypdf
r = pypdf.PdfReader('$INPUT_FILE')
for page in r.pages:
    print(page.extract_text() or '')
    print()
" > "01-interviews/<id>-raw.md"
    # If the PDF is image-only (scanned), the above produces an empty file.
    # In that case, surface a "this PDF appears to be scanned — OCR required" warning
    # and ask the analyst whether to run OCR (ocrmypdf, tesseract) before continuing.
    ;;
  *)
    echo "Unrecognised format. Supported: pdf, docx, doc, rtf, txt, md, vtt, srt, json, html, csv." >&2
    echo "You can also paste the transcript directly into chat and I'll ingest it." >&2
    exit 1
    ;;
esac
```

These snippets are illustrative — the point is the **dispatch contract**, not the exact code. After any conversion, **sanity-check the output is non-empty and looks like dialogue** (has speaker turns or sentence structure). An empty or garbage result means the wrong extractor (scanned PDF, unusual JSON shape, binary `.doc` with no converter) — surface that to the analyst rather than feeding empty text downstream. Keep speaker labels, timestamps, and paragraph breaks. **Do not** convert via `mammoth → html → md` chains — they introduce noise. Save the converted raw next to the cleaned file so the user can compare if needed.

**Dependencies.** `python-docx` and `pypdf` (required). Soft/optional, only for the formats that need them: `striprtf` (`.rtf` — there's a regex fallback if absent), and a system `.doc` converter (`textutil` on macOS / `antiword` / `libreoffice`). `.vtt`/`.srt`/`.json`/`.html`/`.csv`/`.txt`/`.md` need no extra library. If a needed converter is missing, ask the analyst to install it or to re-save / paste the transcript — never convert silently to empty. See `${CLAUDE_PLUGIN_ROOT}/references/input-ingestion.md` and `DEPENDENCIES.md`.

## The five-beat checkpoint flow

Every skill in this plugin uses the same beats. Don't skip any.

### 1. Read
Open the raw transcript (after `.docx` → `.md` conversion if needed). Note: speaker labels, timestamps, total length, language, presence of any pre-flagged corrections.

### 2. Propose
Produce a short brief for the user (in chat, not as a file yet) covering:

- Detected language and length
- The anonymisation calls you intend to make (every name, every location, every employer) as a list — one line each
- Every transcription correction you intend to apply, with the timestamp and the proposed text
- Any indirect-identifier judgements you want to make (e.g. "this combination of role + neighbourhood + study programme could re-identify — propose redacting study programme to `[study]`")

### 3. Checkpoint
Ask the user to approve, edit, or reject before you write anything. The user owns every redaction decision.

**Auto-mode for headless / batch runs.** When the parent invokes `clean-interview` with `auto_mode: true` (typically because the pipeline is processing N interviews unattended), the Propose+Checkpoint beats collapse into a *batch proposal*: write the per-interview proposal to `01-interviews/cleaning-proposals/<id>-proposal.md` rather than surfacing in chat, apply the policy from `.persona-config.md` § anonymisation deterministically, and proceed to Produce. The resulting `<id>-cleaning-summary.md` is the audit trail and replaces interactive approval. Auto-mode is NOT a strict-checkpoint bypass — it is a transcript-handling policy. It applies only when (a) `.persona-config.md` § anonymisation has an explicit `policy` set (not `custom`) and (b) the parent's prompt includes `auto_mode: true`. If either is absent, fall back to the interactive Propose+Checkpoint flow above.

Sub-agents launched from this skill (`interview-reader`) inherit `auto_mode` via the prompt — see `agents/interview-reader.md` § "Bypassing parent-skill checkpoints". Sub-agents never hold their own analyst-approval gates.

### 4. Produce
Write the cleaned transcript to `personas-project/01-interviews/<interview-id>-cleaned.md`. Use the cleaning conventions in `references/cleaning-conventions.md`. Save a parallel `<interview-id>-cleaning-summary.md` next to it listing every change made, with rationale.

### 5. Falsify
Run a self-check before declaring done:

- Open the cleaned file. Confirm: no real names slipped through; no Stockholm-internal location was over-redacted (the carve-out is load-bearing — see pitfalls below); no section was summarised or bulleted; the file reads in the original interview order
- Run a grep against the redaction list — every committed redaction should appear in the cleaned file *only* in its redacted form
- Open the cleaning-summary.md and confirm every judgement call is logged

If any check fails, fix and re-check. Don't ship a transcript with an unaudited redaction.

## Pitfalls — what went wrong on Naturvårdsverket v1

Read these before writing.

### Pitfall · Inferring an age bracket from context
On NV v1, Claude back-calculated an age bracket from a Fridays-for-Future reference ("participant was 17–18 during FFF → around 24–25 in 2026") and set the header to "25–34" as if it were a stated fact. **Don't.** Header metadata only gets populated from an explicit statement. Otherwise leave it blank or mark `[?]`, and flag the inference in the summary so the user can decide.

### Pitfall · Mechanically applying "redact to [city]" when the carve-out is the point
The Naturvårdsverket project's anonymisation policy carves out *Stockholm-internal* neighbourhoods, streets, and the city itself — they are research-relevant. Only locations *outside* Stockholm get redacted. A mechanical anonymisation pass would collapse the carve-out and over-redact. Surface the rule as an explicit per-location decision in your proposal; don't bury it in a generic pass.

### Pitfall · "Tidying up" at the end of a long context
The temptation at the end of a long cleaning pass is to bullet-point, summarise, or drop tangents. **Never.** The brief is explicit: preserve dialogue in interview order, keep repetition, keep tangents. Bulleting is a structural lie about a conversation.

### Pitfall · Asymmetric risk on filler words
Stripping too much filler erases voice. Leaving too much makes the transcript unreadable. The default is *keep*. When in doubt, mark `[pause]` rather than delete.

### Pitfall · Silent fixes
Every non-trivial fix — a corrected word, an indirect-identifier redaction, a speaker-label correction — must appear in the cleaning-summary.md. A clean file with no audit trail is worse than a dirty file the user can see.

## Headless auto-scan mode (E3 · cleaning-summary even when skipped)

The analyst may legitimately skip `clean-interview` — interviews already cleaned by hand, or a quick exploratory pass on raw text. **The pipeline still wants an auditable record of what PII was present in the source material**, so when a downstream skill (`analyse-themes`, `frame-and-cluster`, `validate-archetypes`, `package-for-client`) detects that `state.json.steps.clean-interview.status == "skipped"` AND no `auto-anonymisation-summary.md` exists yet, it MUST invoke this auto-scan mode before doing its own work.

Auto-scan mode does **not** modify the interview files. It only produces a documentation artefact.

### What it does

1. Iterate every file in the input directory.
2. Run lightweight PII detection: regex + named-entity recognition heuristics on:
   - **Direct identifiers** — proper names (capitalised non-first-word tokens that pass an NER `PER` check), email-like patterns, phone-like patterns, exact addresses (`<street> <number>`), employer-name patterns
   - **Indirect identifiers** — uncommon role + city + life-event combinations using the indirect-identifier framework from `references/anonymisation-policy.md`
   - **Financial values** — `\d+ ?(kr|kronor|SEK|euro|EUR|\$|USD)` and similar
   - **Health / sensitive-category mentions** — diagnoses, medications, religion, sexuality (these are flagged but never auto-redacted — only the analyst decides)
3. Write `personas-project/<project>/01-interviews/auto-anonymisation-summary.md` with:
   - Header explaining that this is a passive scan (no edits applied)
   - Per-file table of detected PII (type, snippet, line, severity)
   - A "what's NOT in this scan" disclosure: things this heuristic cannot detect (nicknames, implied identifiers, voice-style fingerprints, demographic combinations the regex doesn't catch)
   - Recommendation block — "if these interviews are going to a client deliverable, run `/antrop-personas:clean-interview` over them first"
4. Update `state.json.steps.clean-interview` to record `auto_scan_completed_at` and `output: 01-interviews/auto-anonymisation-summary.md` so the trace appears in the final package's cover document.

### When to invoke

Downstream skills check at their Read beat:

```python
state = load_state()
if state['steps']['clean-interview']['status'] == 'skipped':
    summary_path = '01-interviews/auto-anonymisation-summary.md'
    if not exists(summary_path):
        invoke('clean-interview', mode='auto-scan')
```

This is silent if the summary already exists — only one auto-scan per project unless explicitly re-run.

## References

- `references/anonymisation-policy.md` — Default Antrop anonymisation policy (Stockholm carve-out, indirect-identifier framework, redaction tokens). **Load via `Read` before the Propose beat.** If unreadable in the runtime environment (cache miss, packaging issue), use the *Fallback inline policy* below.
- `references/cleaning-conventions.md` — File format, `[?]` and `[pause]` and `[city]` tokens, speaker labels, timestamp handling. **Same fallback rule.**
- `../../references/cross-cutting-principles.md` — The five principles all skills follow

### Fallback inline policy (used only if `references/` cannot be opened)

If `Read('references/anonymisation-policy.md')` returns "no such file" (broken plugin install, cache miss):

- Direct identifiers always redacted: real names → `[Name]`, employer → `[Employer]`, exact ages without explicit statement → blank, email/phone/address → `[contact]`, children/partner names → `[child]` / `[partner]`.
- Indirect identifiers: combinations of rare-role + rare-neighbourhood + rare-life-event re-identify multiplicatively — generalise the rarer element.
- Stockholm-internal neighbourhoods, streets, and the city itself → KEEP (research-relevant). Locations outside Stockholm → `[city]`.
- Always log every indirect-identifier judgement in `<id>-cleaning-summary.md`.

If `Read('references/cleaning-conventions.md')` returns "no such file":

- Output is markdown with `**Interviewer:**` / `**Respondent:**` speaker labels, blank line between turns, `[00:HH:MM:SS]` timestamps at natural breaks, `[?]` / `[pause]` / `[unclear]` / `[laughter]` for editor's marks. Keep filler unless it's pure verbal noise.

After surfacing this fallback in the Propose beat, ask the analyst whether to (a) proceed with the inline policy or (b) halt and reinstall the plugin so the full references are available.

## Output

- `personas-project/<project>/01-interviews/<id>-cleaned.md` — the cleaned transcript
- `personas-project/<project>/01-interviews/<id>-cleaning-summary.md` — what was changed and why
- `personas-project/<project>/01-interviews/auto-anonymisation-summary.md` — produced by **headless auto-scan mode** when clean-interview is skipped but downstream skills want an audit trail
- Optional: a docx mirror of the cleaned file if the user wants to share it outside the project

## Offer the workshop-card side-branch

After all interviews are cleaned, mention the optional `interview-cards` side-branch to the analyst before they move on to step 2 (analyse-themes):

> "Klart — alla N intervjuer städade. Innan vi går till tematisk analys: vill du att jag producerar **arbets-workshop-kort** för varje deltagare? Det är en sidogren som kör direkt på de städade intervjuerna — användbart om personerna ska sitta uppe på en workshop-vägg, men det påverkar inte personas-kvaliteten. Säg **ja** för att köra `/antrop-personas:interview-cards`, eller **fortsätt** för att gå direkt till `analyse-themes`."

The default is **fortsätt** (don't run). Mentioning the option once here ensures the analyst knows it exists without forcing it.
