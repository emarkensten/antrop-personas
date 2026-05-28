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

# Quote pattern: attributed quote followed by interview-id on next line / same paragraph.
# Matches markdown blockquotes ('> "..." — IP02') and inline ('"..." — IP02').
QUOTE_PATTERN = re.compile(
    r'["“]([^"“”]{8,})["”]\s*[—–-]\s*(?:INTERVIEW\s*|IP)?\s*(?P<id>\d{1,3}[A-Z]?|[A-Z]+\d+)',
    re.IGNORECASE,
)

# Loose-match threshold: how many consecutive normalised characters must match.
LOOSE_MATCH_MIN_RUN = 20


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
    if longest >= LOOSE_MATCH_MIN_RUN // 4:
        return "MINOR_PARAPHRASE"

    return "FABRICATED"


def extract_quotes(text: str) -> Iterable[tuple[str, str, int]]:
    """Yield (quote_text, interview_id, line_number)."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in QUOTE_PATTERN.finditer(line):
            yield m.group(1).strip(), m.group("id").strip().upper(), lineno


def find_interview_file(interviews_dir: Path, ip_id: str) -> Path | None:
    # Try several naming conventions: IP02-cleaned.md, IP2-cleaned.md, 02-cleaned.md
    numeric = re.sub(r"[^0-9]", "", ip_id) or ip_id
    candidates = [
        interviews_dir / f"IP{numeric}-cleaned.md",
        interviews_dir / f"IP{numeric.zfill(2)}-cleaned.md",
        interviews_dir / f"{ip_id}-cleaned.md",
        interviews_dir / f"interview-{numeric}-cleaned.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fall back to glob
    for p in interviews_dir.glob(f"*{numeric}*cleaned*.md"):
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
