#!/usr/bin/env python3
"""
render-pdf.py — Convert persona-cards.html → Persona Cards v1.pdf.

Fallback ladder (J1):
    1. Chromium / Google Chrome --headless --print-to-pdf       (best fidelity)
    2. Playwright (Chromium engine, Python)                     (same engine, programmatic)
    3. WeasyPrint                                                (Python-only, no browser)

Runs in the design-archetypes parent context, where the user's mounted skills
directory is reachable. The card-renderer subagent sometimes cannot reach
chromium in its sandbox — that's why this lives at the parent level.

Usage:
    python3 render-pdf.py \
        --html  personas-project/<project>/06-design/persona-cards.html \
        --pdf   "personas-project/<project>/06-design/Persona Cards v1.pdf"
"""

from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def try_chromium(html: Path, pdf: Path) -> bool:
    for binary in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(binary)
        if not path:
            continue
        cmd = [
            path,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}",
            html.resolve().as_uri(),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            if pdf.exists() and pdf.stat().st_size > 4096:
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return False


def try_playwright(html: Path, pdf: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html.resolve().as_uri())
            page.emulate_media(media="print")
            page.pdf(
                path=str(pdf),
                format="A3",
                landscape=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                print_background=True,
            )
            browser.close()
        return pdf.exists() and pdf.stat().st_size > 4096
    except Exception as e:
        print(f"playwright failed: {e}", file=sys.stderr)
        return False


def try_weasyprint(html: Path, pdf: Path) -> bool:
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        return False
    try:
        HTML(filename=str(html)).write_pdf(str(pdf))
        return pdf.exists() and pdf.stat().st_size > 4096
    except Exception as e:
        print(f"weasyprint failed: {e}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, type=Path)
    ap.add_argument("--pdf", required=True, type=Path)
    args = ap.parse_args()

    if not args.html.exists():
        print(f"input HTML not found: {args.html}", file=sys.stderr)
        return 2

    args.pdf.parent.mkdir(parents=True, exist_ok=True)

    for label, fn in (
        ("chromium", try_chromium),
        ("playwright", try_playwright),
        ("weasyprint", try_weasyprint),
    ):
        if fn(args.html, args.pdf):
            print(f"rendered via {label}: {args.pdf}")
            return 0

    print(
        "PDF generation failed via all three engines (chromium / playwright / weasyprint).\n"
        "Install one of:\n"
        "  • Chromium or Google Chrome (system binary)\n"
        "  • pip install playwright && playwright install chromium\n"
        "  • pip install weasyprint\n"
        "The HTML at",
        args.html,
        "is still openable in a browser; the analyst can print to PDF manually as a last resort.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
