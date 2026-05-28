# Plugin dependencies

The antrop-personas plugin invokes other skills and Python libraries at specific pipeline steps. None of these are bundled — they must be available in the host (Cowork, Claude Code, Claude.ai) at runtime.

If a hard dependency is missing, the depending step **must fail clearly** with the message in the "graceful-fail" column. Do not silently degrade — the analyst loses trust in the deliverable when output quality drops without warning.

## Required Python libraries

| Library | Used by | What for | Install |
|---------|---------|----------|---------|
| `python-docx` | `clean-interview`, `analyse-themes`, `validate-archetypes`, `package-for-client` | Reading raw .docx interview transcripts (A2) + writing client-facing docx reports | `pip install python-docx` |
| `pypdf` | `clean-interview` (A2 — `.pdf` input), `compare-baseline` (F1 — baseline extraction) | Text-layer extraction from PDF inputs | `pip install pypdf` |
| `openpyxl` | `frame-and-cluster` (B1 — primary artefact `behavioural-variables.xlsx`), `generate-archetypes` (reads the xlsx), `validate-archetypes` (reads the xlsx) | Writing and reading the behavioural-variables workbook with three sheets | `pip install openpyxl` |

## Recommended Python libraries (soft dependency)

| Library | Used by | What for | Behaviour if missing |
|---------|---------|----------|----------------------|
| `pdfplumber` | `compare-baseline` | Multi-column PDF persona-card extraction when `pypdf` fails | Falls back to `pypdf` text extraction. Surface a warning if extraction returns very little content per page. |
| `weasyprint` | `card-renderer` (J1 fallback) | PDF rendering from HTML when headless-browser CLI is unavailable in the agent's environment | First-choice PDF rendering is via headless chromium (Bash). If unavailable, fall back to WeasyPrint; if both fail, hand PDF generation back to the parent skill explicitly with a `pdf_generation_blocked` flag. |
| `tesseract` / `ocrmypdf` | `clean-interview` (A2 — scanned PDFs) | OCR for image-only PDFs | Ask the analyst whether to install + OCR, or convert by hand. Don't auto-OCR. |
| `striprtf` | `clean-interview` (`.rtf` input) | Clean RTF→text extraction | Regex control-word strip fallback (lossier). |
| `textutil` (macOS) / `antiword` / `libreoffice` | `clean-interview` (legacy `.doc` input) | Read binary `.doc` | Ask the analyst to re-save as `.docx` or paste the text. |

`.vtt` / `.srt` (caption exports), `.json` (Otter/Whisper/Teams transcript exports), `.html`, `.csv`, `.txt`, `.md` need **no extra library** — they're handled with the standard library. See `references/input-ingestion.md` for the full per-format ingestion contract.

## Required skills (hard dependency)

| Depending skill | Required skill | Used for | Graceful-fail message |
|-----------------|----------------|----------|------------------------|
| `clean-interview` | `docx` | Producing the optional `.docx` mirror of the cleaned transcript when the analyst asks to share outside the project | "Docx export requires the `docx` skill. The cleaned `.md` file is ready — install `docx` to also produce a Word mirror." |
| `analyse-themes` | `docx` | Producing the client-facing themes report when requested | "Themes report as `.docx` requires the `docx` skill. The working `themes.md` is complete — install `docx` to generate the client report." |
| `validate-archetypes` | `docx` | Producing the polished `Validity Audit — <project>.docx` | "Validity audit as `.docx` requires the `docx` skill. The working `audit-findings.md` is complete — install `docx` to generate the client-facing audit." |
| `package-for-client` | `docx` | Producing the `Cover.docx` and the per-artefact docx files in the bundle | "Bundle assembly requires the `docx` skill — the cover and per-section reports cannot be produced without it." |
| `frame-and-cluster` | `xlsx` (skill) OR `openpyxl` (library) | Writing the primary artefact `behavioural-variables.xlsx` | "Excel artefact requires either the `xlsx` skill or `openpyxl`. Install one before re-running `frame-and-cluster`." |

## Recommended skills (soft dependency)

| Depending skill | Recommended skill | Used for | Behaviour if missing |
|-----------------|-------------------|----------|----------------------|
| `design-archetypes` / `interview-cards` | `gemini-image-gen` | Generating AI-photo portraits (D1b default policy) | Falls back to `initials-disc`. Surface a warning. **Never** falls through to stick figures or geometric placeholders. |
| `design-archetypes` | `canvas-design` (D1, **optional enhancement only**) | An extra automated polish loop on top of the already-print-ready render | **Not required.** The bundled template + `render-pdf.py` (Chrome/Chromium → Playwright → WeasyPrint) produce the complete, consistent A3 deliverable on their own. `canvas-design` is consulted only when the analyst opts in with `use-canvas-design: yes` AND it happens to be installed; otherwise the bundled render is the final output. Default `use-canvas-design: no`. |
| `compare-baseline` | `xlsx` | Producing the comparison docx if the analyst asks for one | Falls back to writing only the markdown + HTML artefact. |
| `analyse-themes`, `frame-and-cluster`, `validate-archetypes`, `generate-archetypes`, `polish-language` | Sub-agents (see `agents/` — `interview-reader`, `thematic-analyser`, `archetype-drafter`, `audit-runner`, `card-renderer`, `language-polisher`) | Parallel heavy reading for samples ≥4 interviews; `polish-language` delegates to `language-polisher` | Runs inline if sub-agents aren't available — slower and more context-heavy. Surface in chat that the run will be slower without sub-agent support. |

## gemini-image-gen — current model (M2-image)

Portraits should be generated with the **current best** Gemini image model. As of
2026-05 (per the `google-genai` SDK docs, verified by a live run):

- **`gemini-3-pro-image`** (Nano Banana Pro — Gemini 3 Pro Image) — highest
  fidelity, "Thinking", supports `image_size` 1K/2K/4K + aspect-ratio control.
  **Preferred for client-facing persona portraits** (quality over cost). The
  `gemini-3-pro-image-preview` alias also works. Generate at `image_size: "2K"`,
  `aspect_ratio: "4:5"` (matches `portrait-style.md` and the portrait disc).
- `gemini-2.5-flash-image` (Nano Banana) — cheaper/faster fallback for high volume.

There is **no `gemini-3.5-flash` image model** — that name does not exist; don't
pin it. Google rotates these, so re-check the live `google-genai` docs / model
list before a run rather than trusting any pinned string. A minimal known-good
call (used to generate the SJ Återförsäljare portraits):

```python
from google import genai
from google.genai import types
from io import BytesIO; from PIL import Image
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
resp = client.models.generate_content(
    model="gemini-3-pro-image",
    contents=open("prompt-<name>.txt").read(),
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(aspect_ratio="4:5", image_size="2K")))
for part in resp.parts:
    if getattr(part, "inline_data", None):
        Image.open(BytesIO(part.inline_data.data)).convert("RGB").save("<name>.jpg", quality=92)
```

If the `gemini-image-gen` skill pins an older model, update it to `gemini-3-pro-image`.

## gemini-image-gen ESM-resolution note (J2)

`gemini-image-gen` uses ESM with a hard-coded `import "@google/genai"` that doesn't resolve when the script is invoked from outside its own `node_modules/`.

The plugin handles this in two ways:

1. **Per-invocation:** `card-renderer` and `interview-cards` set `NODE_PATH` to the gemini-image-gen skill's directory before invoking the script:

   ```bash
   GEMINI_SKILL_DIR="$(claude plugin-skill-path gemini-image-gen)"
   NODE_PATH="$GEMINI_SKILL_DIR/node_modules" node "$GEMINI_SKILL_DIR/generate_image.mjs" \
     --prompt="..." --output="output_dir/portraits/<id>.jpg" --seed=$portrait_seed
   ```

2. **Fallback ladder (D1b):** if the above still fails (network, quota, ESM resolution error), the renderer drops to `initials-disc` instead of stick figures. The error is surfaced in chat with the exact failure reason so the analyst can debug.

If `gemini-image-gen` is updated upstream to ship with bundled deps or to support a `require()`-friendly entry, the per-invocation `NODE_PATH` dance can be removed.

## Per-agent model overrides

Skills can override the default model per sub-agent via `.persona-config.md`:

```
delegation:
  audit-runner-model: opus           # default opus
  archetype-drafter-model: opus      # default opus
  thematic-analyser-model: opus      # default opus
  card-renderer-model: sonnet        # default sonnet
  language-polisher-model: sonnet    # default sonnet
  interview-reader-model: haiku      # default haiku
```

Down-grading saves cost. Up-grading is rarely justified — the defaults are tuned per agent's task type. Document the override in the project's cover document so the deliverable is reproducible.

## How each skill enforces this

In each affected SKILL.md, the **Read** beat checks for the required dependency by attempting to import / invoke the skill at the start. If absent and required, the skill halts with the graceful-fail message above before any heavy work. If absent and recommended-only, the skill warns and proceeds in fallback mode.

The intent: the analyst always knows what's happening, and a missing optional dependency never silently produces a lower-quality artefact.

## How to check what's available

```bash
# In Claude Code / Cowork
claude plugin list                            # list installed plugins
python3 -c "import openpyxl, pypdf; print('ok')"  # check Python deps
```

If a skill is needed but not installed, install the relevant plugin first (`docx`, `xlsx` are part of `anthropic-skills`; `gemini-image-gen` and `canvas-design` are typically already available in Cowork sessions).
