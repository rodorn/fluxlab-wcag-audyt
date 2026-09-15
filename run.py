#!/usr/bin/env python3
"""Pipeline audytu WCAG 2.2: scan (lub demo) -> map -> report.

Uzycie:
    python run.py                          # tryb demo na przykladzie
    python run.py https://example.com ...  # skan URL (pa11y+axe jesli dostepne)
    python run.py --demo https://x.pl      # wymus demo mimo pa11y
"""

from __future__ import annotations

import argparse
import sys

from src.map_wcag import map_issues
from src.report import generate_report
from src.scan import scan_urls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audyt dostepnosci WCAG 2.2 by FluxLab"
    )
    parser.add_argument("urls", nargs="*", help="Adresy URL do skanu")
    parser.add_argument("--demo", action="store_true", help="Wymus tryb demo")
    parser.add_argument(
        "--throttle", type=float, default=1.0, help="Przerwa miedzy skanami (s)"
    )
    parser.add_argument("--out", default="raporty", help="Katalog wyjsciowy raportu")
    args = parser.parse_args(argv)

    urls = args.urls or ["https://fluxlab.pl (przyklad demo)"]
    force_demo = args.demo or not args.urls

    print(f"[1/3] Skanowanie {len(urls)} URL (demo={force_demo}) ...")
    results = scan_urls(urls, throttle=args.throttle, force_demo=force_demo)

    all_issues = []
    demo_used = False
    for r in results:
        if r.error:
            print(f"  ! blad dla {r.url}: {r.error}", file=sys.stderr)
        demo_used = demo_used or r.demo
        all_issues.extend(r.issues)
    print(f"      zebrano {len(all_issues)} surowych issues (demo={demo_used})")

    print("[2/3] Mapowanie axe -> WCAG 2.2 / EN 301 549 ...")
    findings = map_issues(all_issues)
    print(f"      zmapowano {len(findings)} kryteriow")

    print("[3/3] Generacja raportu ...")
    out = generate_report(findings, urls, demo=demo_used, out_dir=args.out)

    print("\n=== RAPORT GOTOWY ===")
    print(f"  HTML: {out['html']}")
    print(f"  PDF : {out['pdf'] or '(brak narzedzia PDF, tylko HTML)'}")
    print(f"  Statystyki: {out['stats']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
