"""Mapowanie kodow regul axe-core na kryteria WCAG 2.2 i EN 301 549.

Kazdy wpis:
  wcag      - numer kryterium sukcesu WCAG 2.2
  name      - nazwa kryterium
  level     - poziom zgodnosci (A / AA)
  en301549  - odnosnik do EN 301 549 (klauzula)
  priority  - P1 / P2 / P3 (P1 = blokuje uzytkownika, krytyczne)
  fix       - rekomendacja z fragmentem poprawnego kodu
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Finding:
    code: str
    wcag: str
    name: str
    level: str
    en301549: str
    priority: str
    impact: str
    count: int
    selectors: list[str]
    message: str
    fix: str


# Priorytet bazowy wg wagi kryterium; moze byc podniesiony przez impact axe.
AXE_TO_WCAG: dict[str, dict[str, Any]] = {
    "color-contrast": {
        "wcag": "1.4.3",
        "name": "Kontrast (minimalny)",
        "level": "AA",
        "en301549": "9.1.4.3",
        "priority": "P2",
        "fix": (
            "Zwieksz kontrast tekstu do min. 4.5:1 (3:1 dla duzego tekstu). "
            "Przyklad: <code>.nav-link { color: #1a1a1a; }</code> zamiast #9aa0a6."
        ),
    },
    "image-alt": {
        "wcag": "1.1.1",
        "name": "Tresc nietekstowa",
        "level": "A",
        "en301549": "9.1.1.1",
        "priority": "P1",
        "fix": (
            "Dodaj opisowy atrybut alt. Przyklad: "
            '<code>&lt;img src="/hero.jpg" alt="Zespol FluxLab przy pracy"&gt;</code>. '
            'Dla obrazow dekoracyjnych uzyj <code>alt=""</code>.'
        ),
    },
    "label": {
        "wcag": "3.3.2",
        "name": "Etykiety lub instrukcje",
        "level": "A",
        "en301549": "9.3.3.2",
        "priority": "P1",
        "fix": (
            "Powiaz pole z etykieta. Przyklad: "
            '<code>&lt;label for="email"&gt;E-mail&lt;/label&gt;'
            '&lt;input id="email" type="email" name="email"&gt;</code>. '
            "Placeholder nie zastepuje etykiety."
        ),
    },
    "link-name": {
        "wcag": "2.4.4",
        "name": "Cel linku (w kontekscie)",
        "level": "A",
        "en301549": "9.2.4.4",
        "priority": "P1",
        "fix": (
            "Zapewnij czytelna tresc linku. Przyklad: "
            '<code>&lt;a href="..." aria-label="Facebook FluxLab"&gt;'
            '&lt;i class="icon-fb" aria-hidden="true"&gt;&lt;/i&gt;&lt;/a&gt;</code>.'
        ),
    },
    "button-name": {
        "wcag": "4.1.2",
        "name": "Nazwa, rola, wartosc",
        "level": "A",
        "en301549": "9.4.1.2",
        "priority": "P1",
        "fix": (
            "Nadaj przyciskowi dostepna nazwe. Przyklad: "
            '<code>&lt;button class="menu-toggle" aria-label="Otworz menu"&gt;'
            '&lt;span class="hamburger" aria-hidden="true"&gt;&lt;/span&gt;&lt;/button&gt;</code>.'
        ),
    },
    "aria-required-attr": {
        "wcag": "4.1.2",
        "name": "Nazwa, rola, wartosc",
        "level": "A",
        "en301549": "9.4.1.2",
        "priority": "P2",
        "fix": (
            "Uzupelnij wymagane atrybuty ARIA lub uzyj natywnego elementu. Przyklad: "
            '<code>&lt;input type="checkbox" id="zgoda"&gt;'
            '&lt;label for="zgoda"&gt;Zgoda marketingowa&lt;/label&gt;</code>.'
        ),
    },
    "html-has-lang": {
        "wcag": "3.1.1",
        "name": "Jezyk strony",
        "level": "A",
        "en301549": "9.3.1.1",
        "priority": "P2",
        "fix": (
            'Ustaw jezyk dokumentu. Przyklad: <code>&lt;html lang="pl"&gt;</code>.'
        ),
    },
    "heading-order": {
        "wcag": "1.3.1",
        "name": "Informacje i relacje",
        "level": "A",
        "en301549": "9.1.3.1",
        "priority": "P3",
        "fix": (
            "Zachowaj logiczna hierarchie naglowkow (h1 -> h2 -> h3). "
            "Przyklad: zamien <code>&lt;h4&gt;</code> na <code>&lt;h2&gt;</code>."
        ),
    },
    "region": {
        "wcag": "1.3.1",
        "name": "Informacje i relacje",
        "level": "A",
        "en301549": "9.1.3.1",
        "priority": "P3",
        "fix": (
            "Umiesc tresc w znacznikach landmark. Przyklad: "
            '<code>&lt;aside class="cookie-bar" aria-label="Informacja o cookies"&gt;...&lt;/aside&gt;</code>.'
        ),
    },
    "focus-order-semantics": {
        "wcag": "2.4.3",
        "name": "Kolejnosc fokusu",
        "level": "A",
        "en301549": "9.2.4.3",
        "priority": "P2",
        "fix": (
            "Zapewnij logiczna kolejnosc fokusu i widoczny wskaznik. Przyklad: "
            "<code>:focus-visible { outline: 2px solid #005fcc; }</code>."
        ),
    },
}

# Fallback dla nieznanych kodow axe.
UNKNOWN = {
    "wcag": "4.1.1",
    "name": "Nieprzypisane kryterium (przeglad reczny)",
    "level": "A",
    "en301549": "9.4.1.1",
    "priority": "P3",
    "fix": "Kod reguly nie ma mapowania. Wymaga recznej weryfikacji audytora.",
}

# Podniesienie priorytetu na podstawie impact axe.
_IMPACT_RANK = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
_PRIORITY_RANK = {"P1": 0, "P2": 1, "P3": 2}
_RANK_PRIORITY = {0: "P1", 1: "P2", 2: "P3"}


def _selector(issue: dict[str, Any]) -> str:
    return issue.get("selector") or issue.get("context") or "(brak selektora)"


def _impact(issue: dict[str, Any]) -> str:
    extras = issue.get("runnerExtras") or {}
    return extras.get("impact") or (
        "critical" if issue.get("typeCode") == 1 else "moderate"
    )


def _resolve_priority(base_priority: str, impact: str) -> str:
    """Priorytet = mocniejszy z (bazowy kryterium, impact axe critical->P1)."""
    base_rank = _PRIORITY_RANK.get(base_priority, 2)
    impact_rank = min(_IMPACT_RANK.get(impact, 2), 2)
    return _RANK_PRIORITY[min(base_rank, impact_rank)]


def map_issues(issues: list[dict[str, Any]]) -> list[Finding]:
    """Agreguje surowe issues axe do zmapowanych Findings (grupowanie po kodzie)."""
    grouped: dict[str, dict[str, Any]] = {}
    for issue in issues:
        code = issue.get("code", "unknown")
        mapping = AXE_TO_WCAG.get(code, UNKNOWN)
        impact = _impact(issue)
        if code not in grouped:
            grouped[code] = {
                "mapping": mapping,
                "selectors": [],
                "message": issue.get("message", ""),
                "impacts": [],
            }
        grouped[code]["selectors"].append(_selector(issue))
        grouped[code]["impacts"].append(impact)

    findings: list[Finding] = []
    for code, data in grouped.items():
        m = data["mapping"]
        # najgorszy impact w grupie
        worst_impact = min(data["impacts"], key=lambda i: _IMPACT_RANK.get(i, 3))
        priority = _resolve_priority(m["priority"], worst_impact)
        findings.append(
            Finding(
                code=code,
                wcag=m["wcag"],
                name=m["name"],
                level=m["level"],
                en301549=m["en301549"],
                priority=priority,
                impact=worst_impact,
                count=len(data["selectors"]),
                selectors=data["selectors"],
                message=data["message"],
                fix=m["fix"],
            )
        )

    findings.sort(key=lambda f: (_PRIORITY_RANK.get(f.priority, 3), -f.count))
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    """Zwraca liczniki wg priorytetu i poziomu."""
    total = sum(f.count for f in findings)
    by_priority = {"P1": 0, "P2": 0, "P3": 0}
    by_level = {"A": 0, "AA": 0}
    for f in findings:
        by_priority[f.priority] = by_priority.get(f.priority, 0) + f.count
        by_level[f.level] = by_level.get(f.level, 0) + f.count
    return {
        "total_issues": total,
        "criteria_failed": len(findings),
        "p1": by_priority["P1"],
        "p2": by_priority["P2"],
        "p3": by_priority["P3"],
        "level_a": by_level["A"],
        "level_aa": by_level["AA"],
    }
