"""Generacja raportu audytu WCAG 2.2: HTML (+ PDF gdy dostepne narzedzie)."""

from __future__ import annotations

import html
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .map_wcag import Finding, summarize

FLUXLAB_URL = "https://fluxlab.pl"

_PRIORITY_BADGE = {
    "P1": ("#b00020", "Krytyczny"),
    "P2": ("#b26a00", "Wysoki"),
    "P3": ("#4a6a00", "Sredni"),
}


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def build_html(
    findings: list[Finding],
    urls: list[str],
    demo: bool,
    generated_at: str | None = None,
) -> str:
    stats = summarize(findings)
    ts = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    demo_banner = (
        '<div class="demo">TRYB DEMO: wynik na wbudowanym przykladzie axe '
        "(pa11y/Chrome niedostepne). Po podpieciu pa11y raport bazuje na realnym skanie.</div>"
        if demo
        else ""
    )

    rows = []
    for f in findings:
        color, label = _PRIORITY_BADGE.get(f.priority, ("#555", f.priority))
        sels = "<br>".join(_esc(s) for s in f.selectors[:5])
        if len(f.selectors) > 5:
            sels += f"<br><em>... i {len(f.selectors) - 5} wiecej</em>"
        rows.append(
            f"""<tr>
  <td><strong>{_esc(f.wcag)}</strong><br><span class="crit">{_esc(f.name)}</span></td>
  <td class="center">{_esc(f.level)}</td>
  <td class="center">{_esc(f.en301549)}</td>
  <td class="center">{f.count}</td>
  <td class="center"><span class="badge" style="background:{color}">{label} ({_esc(f.priority)})</span></td>
  <td><code>{_esc(f.code)}</code></td>
  <td class="sel">{sels}</td>
</tr>"""
        )

    recs = []
    for f in findings:
        color, label = _PRIORITY_BADGE.get(f.priority, ("#555", f.priority))
        recs.append(
            f"""<div class="rec">
  <h3><span class="badge" style="background:{color}">{_esc(f.priority)}</span>
      WCAG {_esc(f.wcag)} {_esc(f.name)} <span class="lvl">({_esc(f.level)})</span></h3>
  <p class="msg">{_esc(f.message)}</p>
  <div class="fix">{f.fix}</div>
</div>"""
        )

    url_list = "".join(f"<li>{_esc(u)}</li>" for u in urls)

    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audyt dostepnosci WCAG 2.2</title>
<style>
  :root {{ --fx:#0b5fff; --ink:#1a1a1a; --muted:#5a5a5a; --line:#e2e2e2; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif; color:var(--ink);
         margin:0; padding:40px; max-width:1100px; margin:0 auto; line-height:1.5; }}
  h1 {{ font-size:26px; margin:0 0 4px; }}
  h2 {{ font-size:20px; margin-top:36px; border-bottom:2px solid var(--fx); padding-bottom:6px; }}
  .brand {{ color:var(--fx); font-weight:700; }}
  .meta {{ color:var(--muted); font-size:13px; margin-bottom:20px; }}
  .demo {{ background:#fff3cd; border:1px solid #ffe08a; padding:10px 14px; border-radius:8px;
          font-size:13px; margin:16px 0; }}
  .cards {{ display:flex; gap:14px; flex-wrap:wrap; margin:20px 0; }}
  .card {{ flex:1; min-width:150px; background:#f7f9ff; border:1px solid var(--line);
          border-radius:10px; padding:16px; }}
  .card .num {{ font-size:30px; font-weight:800; }}
  .card .lbl {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.4px; }}
  .risk {{ background:#fff5f5; border:1px solid #ffd0d0; border-radius:10px; padding:18px 20px;
          margin:20px 0; }}
  .risk h2 {{ border:0; margin-top:0; color:#b00020; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:12px; }}
  th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
  th {{ background:#f2f5ff; }}
  td.center {{ text-align:center; white-space:nowrap; }}
  td.sel {{ font-family:monospace; font-size:11px; color:#333; }}
  .crit {{ color:var(--muted); font-size:12px; }}
  .badge {{ color:#fff; padding:2px 8px; border-radius:20px; font-size:11px; white-space:nowrap; }}
  .rec {{ border-left:4px solid var(--fx); background:#fafbff; padding:12px 16px; margin:14px 0;
         border-radius:0 8px 8px 0; }}
  .rec h3 {{ margin:0 0 6px; font-size:15px; }}
  .rec .msg {{ color:var(--muted); font-size:13px; margin:4px 0; }}
  .rec .fix {{ font-size:13px; background:#fff; border:1px solid var(--line); border-radius:6px;
             padding:8px 10px; }}
  .lvl {{ color:var(--muted); font-weight:400; font-size:13px; }}
  code {{ background:#eef1f7; padding:1px 5px; border-radius:4px; font-size:12px; }}
  footer {{ margin-top:50px; padding-top:16px; border-top:1px solid var(--line);
           color:var(--muted); font-size:13px; }}
  footer a {{ color:var(--fx); text-decoration:none; }}
</style>
</head>
<body>
<h1>Audyt dostepnosci cyfrowej WCAG 2.2</h1>
<div class="meta">Przygotowal <span class="brand">FluxLab</span> | Wygenerowano: {_esc(ts)}</div>
{demo_banner}

<h2>Streszczenie dla zarzadu</h2>
<p>Przeskanowano {len(urls)} adres(ow) URL wobec kryteriow <strong>WCAG 2.2 (poziom A i AA)</strong>
oraz normy <strong>EN 301 549</strong>, ktore stanowia podstawe zgodnosci z Europejskim Aktem o
Dostepnosci (EAA) i polska ustawa wdrazajaca (obowiazek od 28 czerwca 2025 r. dla podmiotow
komercyjnych, m.in. e-commerce, bankowosc, uslugi online).</p>
<p>Wykryto <strong>{stats["total_issues"]}</strong> niezgodnosci obejmujacych
<strong>{stats["criteria_failed"]}</strong> kryteriow sukcesu. W tym
<strong>{stats["p1"]}</strong> o priorytecie krytycznym (P1) blokujacych korzystanie z serwisu
przez osoby z niepelnosprawnosciami.</p>

<div class="cards">
  <div class="card"><div class="num">{stats["total_issues"]}</div><div class="lbl">Niezgodnosci ogolem</div></div>
  <div class="card"><div class="num" style="color:#b00020">{stats["p1"]}</div><div class="lbl">Priorytet P1</div></div>
  <div class="card"><div class="num" style="color:#b26a00">{stats["p2"]}</div><div class="lbl">Priorytet P2</div></div>
  <div class="card"><div class="num">{stats["criteria_failed"]}</div><div class="lbl">Kryteria WCAG</div></div>
</div>

<div class="risk">
  <h2>Ryzyko prawne i finansowe</h2>
  <p>Niezgodnosc z EAA / ustawa o dostepnosci grozi karami administracyjnymi. W polskim porzadku
  prawnym kary za naruszenie moga siegnac <strong>do 10% rocznego obrotu</strong> podmiotu,
  a organ moze nakazac wstrzymanie swiadczenia uslugi. Poza sankcja to takze ryzyko
  reputacyjne i realna utrata klientow, ktorzy nie moga sfinalizowac zakupu.</p>
</div>

<h2>Skanowane adresy</h2>
<ul>{url_list}</ul>

<h2>Tabela niezgodnosci</h2>
<table>
<thead><tr>
  <th>Kryterium WCAG 2.2</th><th>Poziom</th><th>EN 301 549</th><th>Liczba</th>
  <th>Priorytet</th><th>Kod axe</th><th>Selektory (probka)</th>
</tr></thead>
<tbody>
{"".join(rows) if rows else '<tr><td colspan="7">Brak wykrytych niezgodnosci.</td></tr>'}
</tbody>
</table>

<h2>Rekomendacje napraw</h2>
{"".join(recs) if recs else "<p>Brak rekomendacji, serwis nie wykazal bledow.</p>"}

<footer>
  Raport przygotowany przez <span class="brand">FluxLab</span> |
  <a href="{FLUXLAB_URL}">{FLUXLAB_URL}</a><br>
  Audyt automatyczny axe-core pokrywa czesc kryteriow WCAG. Pelna zgodnosc wymaga
  rowniez weryfikacji recznej (nawigacja klawiatura, czytnik ekranu, kontekst tresci).
</footer>
</body>
</html>"""


def _html_to_pdf(html_path: Path) -> Path | None:
    """Konwersja HTML->PDF gdy dostepne narzedzie. Zwraca sciezke PDF lub None."""
    html_path = html_path.resolve()
    pdf_path = html_path.with_suffix(".pdf")
    # Priorytet: wkhtmltopdf, potem chrome/chromium headless.
    if shutil.which("wkhtmltopdf"):
        cmd = [
            "wkhtmltopdf",
            "--enable-local-file-access",
            str(html_path),
            str(pdf_path),
        ]
    else:
        chrome = (
            shutil.which("chromium")
            or shutil.which("google-chrome-stable")
            or shutil.which("google-chrome")
            or shutil.which("chromium-browser")
        )
        if not chrome:
            return None
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=90, check=True)
        return pdf_path if pdf_path.exists() else None
    except (subprocess.SubprocessError, OSError):
        return None


def generate_report(
    findings: list[Finding],
    urls: list[str],
    demo: bool,
    out_dir: str | Path = "raporty",
    basename: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Zapisuje raport HTML (+ PDF gdy sie da). Zwraca sciezki i statystyki."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name = basename or f"audyt-wcag-{stamp}"
    html_path = out / f"{name}.html"

    html_content = build_html(findings, urls, demo, generated_at=generated_at)
    html_path.write_text(html_content, encoding="utf-8")

    pdf_path = _html_to_pdf(html_path)

    return {
        "html": str(html_path.resolve()),
        "pdf": str(pdf_path.resolve()) if pdf_path else None,
        "stats": summarize(findings),
    }
