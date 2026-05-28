# Input-ingestion contract

Analysts hand the plugin whatever they already have. The folder name, the file
formats, and the structure are **never** guaranteed to match the plugin's own
layout. This contract is how every skill that reads source material
(`clean-interview` primarily; `analyse-themes`, `frame-and-cluster`,
`validate-archetypes`, `interview-cards`, `compare-baseline` secondarily) copes
with real-world input without guessing silently.

The rule throughout: **be greedy on discovery, conservative on interpretation,
and never drop or fabricate silently.** When unsure, surface the ambiguity to
the analyst (or, in `mode: auto`, log the assumption to the auto-decision log).

## 1 · Where the files are (folder names + structure)

- Resolve the search root in this order: `state.json.input_dir` → the
  `--input-dir` flag → `personas-project/<project>/01-interviews/`.
- Discover **recursively** (`**/…`). Never assume `01-interviews/`. Real roots
  seen in the wild: `intervjuer/`, `Transkriberingar/`, `cleaned interviews/`,
  `transcripts/`, `råmaterial/`, `Otter exports/`, `Teams recordings/`,
  `Drive/Delning/…`, deeply nested date-stamped folders.
- If the root is a `.zip`, expand it to a temp dir and discover inside.
- Follow one level of obvious indirection: a folder that contains only more
  folders → recurse; a Google Drive `.gdoc`/`.gsheet` pointer file → tell the
  analyst it must be exported first (it has no local content).

## 2 · Supported formats (what each conversion does)

| Format | Handling | Library |
|--------|----------|---------|
| `.md` / `.markdown` / `.txt` / `.text` | copied as-is to `<id>-raw.md` | none |
| `.docx` | paragraph text via `python-docx` | python-docx (required) |
| `.doc` (legacy binary) | `textutil` (macOS) / `antiword` / `libreoffice` | system tool |
| `.rtf` | `striprtf`; regex control-word strip fallback | striprtf (optional) |
| `.pdf` | text layer via `pypdf`; `pdfplumber` for messy multi-column; OCR (`ocrmypdf`) only after asking, for scanned/image-only | pypdf (required) |
| `.vtt` / `.srt` | strip cue numbers + timestamps + `<v>` tags, keep spoken text | none |
| `.json` | Otter/Whisper/Teams/Zoom shapes — pull `segments[].text` + `speaker`; unknown shape → dump for manual triage | none |
| `.html` / `.htm` | strip script/style + tags, unescape entities | none |
| `.csv` | join the longest-average column (the text column) | none |

After **every** conversion, check the result is non-empty and reads like
dialogue (speaker turns, Q&A rhythm, or sentence structure). Empty/garbage means
the wrong extractor — surface it, don't pass empty text downstream. Handle BOM /
non-UTF-8 by reading with `errors="ignore"` and noting any lossy decode.

Anything outside this list: don't convert silently. Tell the analyst the format
isn't recognised and offer the fallback — re-save as `.docx`/`.txt`, or paste the
transcript straight into chat (always accepted).

## 3 · Telling interviews from noise

Auto-discovery is greedy, so a raw folder usually holds non-interview files too.
Classify each hit as **interview / probably-not / unsure** — never silently drop.

Signals it **is** an interview:
- dialogue structure: alternating speaker turns, `Intervjuare:` / `Moderator:` /
  `IP:` / `R:` labels, timestamps, or a question-then-long-answer rhythm;
- length: a real interview is rarely < ~1 kB of text;
- filename hints: `intervju`, `interview`, `transcript`, `IP\d`, `P\d`, `R\d`,
  `respondent`, a person's name, a date.

Signals it is **probably not** an interview (flag, don't clean):
- filename hints: `samtycke`/`consent`, `guide`/`gd`/`intervjuguide`, `brief`,
  `agenda`, `anteckningar`/`notes`, `mall`/`template`, `sammanfattning`/`summary`,
  `README`, `effektmål`, `kravprofil`;
- structure: a bullet list / form / slide export / spreadsheet of metadata;
- Office lock/temp files (`~$…`), `.DS_Store`, zero-byte files.

When unsure, put it in the **unsure** bucket and ask. In `mode: auto`, apply the
classification, log each decision to the auto-decision log, and proceed.

## 4 · Awkward structures

- **One file containing many interviews.** Detect repeated participant headers
  (`Intervju 1`, `Respondent 2`, `IP03`, `=== … ===`, a recurring name pattern,
  or large gaps). Split into per-participant `<id>-raw.md` files. If the split is
  ambiguous, show the proposed boundaries and ask before committing.
- **One participant split across several files** (`IP03-part1`, `IP03-del2`).
  Group by filename stem and concatenate in order into one `<id>-raw.md`.
- **Mixed already-cleaned + raw.** If a file already looks cleaned/anonymised
  (has a cleaning-summary sibling, `[city]`/`[namn]` redaction markers, or a
  `Cleaned by` header), treat it as *cleaned input* — don't re-clean; record it
  as `status: clean-skipped` and still run the PII auto-scan (E3) for the audit
  trail. Raw files go through the normal flow.
- **Non-interview support material** (guide, brief, consent) — never clean it,
  but offer to file the guide under `00-brief/` and the brief into
  `project-brief.md` if empty.

## 5 · Participant IDs from arbitrary filenames

Downstream skills (and `verify-quotes.py`) resolve quotes by interview id, so the
ids must be stable and traceable.

- Derive a canonical id per source: prefer an explicit id in the name
  (`IP02`, `P4`, `1805-7`, `Respondent 3`); otherwise assign sequential `IP01…`
  in discovery order.
- Write `01-interviews/id-map.md` mapping **original filename → assigned id →
  cleaned path**. This is the audit trail; never rename a source on disk without
  recording it here.
- Keep the assigned id consistent across `-raw.md`, `-cleaned.md`, and
  `-cleaning-summary.md`, and in `state.json.steps.clean-interview.outputs`.

## 6 · What to write back

- `01-interviews/<id>-raw.md` — converted raw (kept for comparison).
- `01-interviews/<id>-cleaned.md` — the working file every later skill reads.
- `01-interviews/id-map.md` — filename → id → path map.
- `state.json.steps.clean-interview` — `completed_count`, `outputs`, and (if any)
  a `support_files` list of the non-interview material that was set aside.

Downstream skills must read interviews via the resolved `input_dir` + the
`id-map.md`, not by assuming `IP\d\d-cleaned.md` names. If a skill can't find the
cleaned files it expects, it halts with the graceful-fail message from
`pipeline-state.md` — it never invents interviews.
