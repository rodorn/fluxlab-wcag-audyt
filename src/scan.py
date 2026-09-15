"""Skanowanie URL przez pa11y z runnerem axe.

Jesli pa11y / Chrome sa dostepne, uruchamia:
    pa11y --runner axe --reporter json <url>
W przeciwnym razie zwraca realistyczny tryb demo (wbudowany wynik axe),
zeby caly pipeline (map -> report) dalo sie uruchomic bez zaleznosci.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScanResult:
    url: str
    issues: list[dict[str, Any]]
    demo: bool = False
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


# Wbudowany, realistyczny zestaw wynikow axe (tryb demo).
# Kody odpowiadaja rzeczywistym regulom axe-core.
DEMO_ISSUES: list[dict[str, Any]] = [
    {
        "code": "color-contrast",
        "type": "error",
        "typeCode": 1,
        "message": "Element has insufficient color contrast of 2.94 (foreground #9aa0a6, background #ffffff). Expected contrast ratio of 4.5:1.",
        "context": '<a class="nav-link" href="/oferta">Nasza oferta</a>',
        "selector": "header > nav > a.nav-link:nth-child(2)",
        "runnerExtras": {"impact": "serious"},
    },
    {
        "code": "color-contrast",
        "type": "error",
        "typeCode": 1,
        "message": "Element has insufficient color contrast of 3.1 (foreground #b0b0b0, background #f2f2f2). Expected contrast ratio of 4.5:1.",
        "context": '<p class="footer-note">Copyright 2026</p>',
        "selector": "footer > p.footer-note",
        "runnerExtras": {"impact": "serious"},
    },
    {
        "code": "image-alt",
        "type": "error",
        "typeCode": 1,
        "message": "Images must have alternate text.",
        "context": '<img src="/hero.jpg">',
        "selector": "main > section.hero > img",
        "runnerExtras": {"impact": "critical"},
    },
    {
        "code": "image-alt",
        "type": "error",
        "typeCode": 1,
        "message": "Images must have alternate text.",
        "context": '<img src="/logo-partner.png" class="partner">',
        "selector": "section.partners > img.partner:nth-child(3)",
        "runnerExtras": {"impact": "critical"},
    },
    {
        "code": "label",
        "type": "error",
        "typeCode": 1,
        "message": "Form elements must have labels.",
        "context": '<input type="email" name="email" placeholder="Twoj e-mail">',
        "selector": 'form.newsletter > input[name="email"]',
        "runnerExtras": {"impact": "critical"},
    },
    {
        "code": "link-name",
        "type": "error",
        "typeCode": 1,
        "message": "Links must have discernible text.",
        "context": '<a href="https://facebook.com/fluxlab"><i class="icon-fb"></i></a>',
        "selector": "footer > div.social > a:nth-child(1)",
        "runnerExtras": {"impact": "serious"},
    },
    {
        "code": "button-name",
        "type": "error",
        "typeCode": 1,
        "message": "Buttons must have discernible text.",
        "context": '<button class="menu-toggle"><span class="hamburger"></span></button>',
        "selector": "header > button.menu-toggle",
        "runnerExtras": {"impact": "critical"},
    },
    {
        "code": "aria-required-attr",
        "type": "error",
        "typeCode": 1,
        "message": "Required ARIA attributes must be provided (aria-checked missing on role=checkbox).",
        "context": '<div role="checkbox" tabindex="0">Zgoda marketingowa</div>',
        "selector": 'form.contact > div[role="checkbox"]',
        "runnerExtras": {"impact": "serious"},
    },
    {
        "code": "html-has-lang",
        "type": "error",
        "typeCode": 1,
        "message": "The <html> element must have a lang attribute.",
        "context": "<html>",
        "selector": "html",
        "runnerExtras": {"impact": "serious"},
    },
    {
        "code": "heading-order",
        "type": "warning",
        "typeCode": 2,
        "message": "Heading levels should only increase by one (h1 followed by h4).",
        "context": "<h4>Dlaczego my</h4>",
        "selector": "main > section.why > h4",
        "runnerExtras": {"impact": "moderate"},
    },
    {
        "code": "region",
        "type": "warning",
        "typeCode": 2,
        "message": "All page content should be contained by landmarks.",
        "context": '<div class="cookie-bar">Uzywamy cookies</div>',
        "selector": "body > div.cookie-bar",
        "runnerExtras": {"impact": "moderate"},
    },
]


def _pa11y_available() -> bool:
    return shutil.which("pa11y") is not None


def scan_url(url: str, timeout: int = 60, force_demo: bool = False) -> ScanResult:
    """Skanuje pojedynczy URL. Fallback do trybu demo gdy pa11y niedostepne."""
    if force_demo or not _pa11y_available():
        return ScanResult(
            url=url,
            issues=[dict(i) for i in DEMO_ISSUES],
            demo=True,
            meta={
                "reason": "pa11y niedostepne" if not force_demo else "wymuszony demo"
            },
        )
    try:
        proc = subprocess.run(
            ["pa11y", "--runner", "axe", "--reporter", "json", url],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        # pa11y zwraca kod !=0 gdy sa bledy dostepnosci, ale stdout ma JSON.
        stdout = proc.stdout.strip()
        if not stdout:
            return ScanResult(
                url=url, issues=[], error=proc.stderr.strip() or "pusty wynik pa11y"
            )
        issues = json.loads(stdout)
        return ScanResult(url=url, issues=issues, demo=False)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return ScanResult(url=url, issues=[], error=f"{type(exc).__name__}: {exc}")


def scan_urls(
    urls: list[str], throttle: float = 1.0, force_demo: bool = False
) -> list[ScanResult]:
    """Skanuje liste URL z throttlingiem miedzy zadaniami."""
    results: list[ScanResult] = []
    for idx, url in enumerate(urls):
        if idx > 0 and throttle > 0:
            time.sleep(throttle)
        results.append(scan_url(url, force_demo=force_demo))
    return results
