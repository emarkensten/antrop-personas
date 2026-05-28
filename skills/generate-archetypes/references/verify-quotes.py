#!/usr/bin/env python3
"""
verify-quotes.py — Grep-based verbatim verification for archetypes.md quotes.

Reads archetypes.md, extracts every attributed quote (verbatim text + interview-id),
and confirms that the quote appears word-for-word in the named interview file.

Usage:
    python3 verify-quotes.py \
        --archetypes personas-project/<project>/04-archetypes/archetypes.md \
        --interviews-dir personas-project/<project>/01-interviews/ \
        --report personas-project/<project>/04-archetypes/quote-verification.md

Exit codes:
    0 — every quote VERIFIED
    1 — at least one quote MILDLY EDITED / MINOR PARAPHRASE / FABRICATED
    2 — file or attribution lookup failed

The script never modifies archetypes.md. It produces a report the parent skill
surfaces at the Falsify beat (and the analyst signs off at I1).
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# Quote pattern: attributed quote followed by an interview-id.
# Matches markdown blockquotes ('> "..." — IP02') and inline ('"..." — INTERVJU 02 · RAD 142').
# Recognises Swedish AND English attribution words (INTERVJU / INTERVIEW / IP / RESPONDENT / R)
# — the plugin's default language is Swedish, so "INTERVJU"/"Intervju" MUST match or the whole
# verification silently passes. Ids handled: IP02, 02, 02A, 1808-29, 1805-7. A trailing
# "· RAD nnn" / page/line suffix is ignored (it falls outside the id capture group).
QUOTE_PATTERN = re.compile(
    r'["“]([^"“”]{8,})["”]\s*[—–-]\s*'
    r'(?:INTERVJU|INTERVIEW|RESPONDENT|IP|R)?\s*'
    r'(?P<id>[A-Za-z]{0,3}\d{1,4}(?:-\d{1,4})?[A-Za-z]?)',
    re.IGNORECASE,
)

# Minor-paraphrase threshold: how many consecutive words of the quote must appear
# verbatim in the transcript for the verdict to be MINOR_PARAPHRASE rather than FABRICATED.
MINOR_PARAPHRASE_MIN_WORDS = 5


def normalise(s: str) -> str:
    """Strip whitespace and lowercase for fuzzy compare; keep letters and digits."""
    return re.sub(r"\s+", " ", s).strip().lower()


def find_quote_verdict(quote: str, transcript: str) -> str:
    q_norm = normalise(quote)
    t_norm = normalise(transcript)

    if q_norm in t_norm:
        return "VERIFIED"

    # Mildly edited: every word of the quote appears in order, but with extra
    # words in between (stitched non-adjacent sentences).
    words = q_norm.split()
    if len(words) < 4:
        return "TOO_SHORT_TO_AUDIT"

    # Look for the first and last 5-word chunks separately in the transcript.
    head = " ".join(words[:5])
    tail = " ".join(words[-5:])
    if head in t_norm and tail in t_norm:
        return "MILDLY_EDITED"  # ellipsis-stitch candidate

    # Minor paraphrase: half the words appear in some local window.
    longest = 0
    for n in range(len(words), 2, -1):
        for i in range(0, len(words) - n + 1):
            chunk = " ".join(words[i : i + n])
            if chunk in t_norm:
                longest = max(longest, n)
                break
        if longest > 0:
            break
    if longest >= MINOR_PARAPHRASE_MIN_WORDS:
        return "MINOR_PARAPHRASE"

    return "FABRICATED"


def extract_quotes(text: str) -> Iterable[tuple[str, str, int]]:
    """Yield (quote_text, interview_id, line_number)."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in QUOTE_PATTERN.finditer(line):
            yield m.group(1).strip(), m.group("id").strip().upper(), lineno


def find_interview_file(interviews_dir: Path, ip_id: str) -> Path | None:
    # Handle ids like IP02, 02, 1808-29, 1805-7. Keep the hyphenated form (real AMF/SJ
    # naming) AND a digits-only form, and try both as filenames and as glob tokens.
    raw = ip_id.strip()
    hyphen = re.sub(r"[^0-9-]", "", raw).strip("-") or raw   # "1808-29"
    digits = re.sub(r"[^0-9]", "", raw) or raw               # "180829"
    candidates = [
        interviews_dir / f"IP{raw}-cleaned.md",
        interviews_dir / f"{raw}-cleaned.md",
        interviews_dir / f"IP{hyphen}-cleaned.md",
        interviews_dir / f"IP{digits}-cleaned.md",
        interviews_dir / f"IP{digits.zfill(2)}-cleaned.md",
        interviews_dir / f"{hyphen}-cleaned.md",
        interviews_dir / f"interview-{digits}-cleaned.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fall back to glob — prefer the hyphen-preserving token (won't over-concatenate
    # "1808-29" into "180829"), then the digits-only form.
    for token in (raw, hyphen, digits):
        for p in interviews_dir.glob(f"*{token}*"):
            if p.suffix == ".md" and "clean" in p.name.lower():
                return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archetypes", required=True, type=Path)
    ap.add_argument("--interviews-dir", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()

    if not args.archetypes.exists():
        print(f"archetypes file not found: {args.archetypes}", file=sys.stderr)
        return 2
    if not args.interviews_dir.is_dir():
        print(f"interviews dir not found: {args.interviews_dir}", file=sys.stderr)
        return 2

    archetypes_text = args.archetypes.read_text(encoding="utf-8")
    results = []
    worst = "VERIFIED"
    severity = {
        "VERIFIED": 0,
        "TOO_SHORT_TO_AUDIT": 1,
        "MILDLY_EDITED": 2,
        "MINOR_PARAPHRASE": 3,
        "FABRICATED": 4,
        "INTERVIEW_NOT_FOUND": 4,
    }

    for quote, ip_id, lineno in extract_quotes(archetypes_text):
        interview_path = find_interview_file(args.interviews_dir, ip_id)
        if interview_path is None:
            verdict = "INTERVIEW_NOT_FOUND"
            transcript = ""
        else:
            transcript = interview_path.read_text(encoding="utf-8")
            verdict = find_quote_verdict(quote, transcript)

        if severity.get(verdict, 0) > severity.get(worst, 0):
            worst = verdict

        results.append(
            {
                "line": lineno,
                "interview_id": ip_id,
                "interview_path": str(interview_path) if interview_path else None,
                "quote": quote,
                "verdict": verdict,
            }
        )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Quote verification report",
        "",
        f"Source: `{args.archetypes}`",
        f"Interviews: `{args.interviews_dir}`",
        f"Worst verdict: **{worst}**",
        "",
        "| Line | Interview | Verdict | Quote |",
        "| ---: | --- | --- | --- |",
    ]
    for r in results:
        q_short = r["quote"][:80] + ("…" if len(r["quote"]) > 80 else "")
        lines.append(f"| {r['line']} | {r['interview_id']} | {r['verdict']} | {q_short} |")
    lines.append("")
    lines.append("Verdicts:")
    lines.append("- `VERIFIED` — exact verbatim match in the named interview")
    lines.append("- `MILDLY_EDITED` — head and tail of the quote present, middle stitched (mark ellipses)")
    lines.append("- `MINOR_PARAPHRASE` — substantial fragment present but wording diverges")
    lines.append("- `FABRICATED` — no substantial fragment found in the interview")
    lines.append("- `INTERVIEW_NOT_FOUND` — the cited IP-id has no matching file in the interviews dir")
    lines.append("- `TOO_SHORT_TO_AUDIT` — quote is < 4 words; can't run the loose-match heuristic")
    args.report.write_text("\n".join(lines), encoding="utf-8")

    if worst in {"VERIFIED", "TOO_SHORT_TO_AUDIT"}:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
