"""Testy generacji raportu z danych demo."""

from src.map_wcag import map_issues
from src.report import build_html, generate_report
from src.scan import DEMO_ISSUES, scan_urls


def test_build_html_contains_key_sections():
    findings = map_issues([dict(i) for i in DEMO_ISSUES])
    html = build_html(findings, ["https://example.com"], demo=True)
    assert "Streszczenie dla zarzadu" in html
    assert "10% rocznego obrotu" in html
    assert "EN 301 549" in html
    assert "https://fluxlab.pl" in html
    assert "TRYB DEMO" in html
    # kazde kryterium powinno pojawic sie w tabeli
    for f in findings:
        assert f.wcag in html


def test_build_html_escapes_content():
    findings = map_issues([{"code": "image-alt", "selector": "<script>x</script>"}])
    html = build_html(findings, ["u"], demo=True)
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_generate_report_writes_file(tmp_path):
    results = scan_urls(["https://demo.pl"], throttle=0, force_demo=True)
    issues = [i for r in results for i in r.issues]
    findings = map_issues(issues)
    out = generate_report(findings, ["https://demo.pl"], demo=True, out_dir=tmp_path)
    from pathlib import Path

    html_file = Path(out["html"])
    assert html_file.exists()
    assert html_file.stat().st_size > 1000
    assert out["stats"]["total_issues"] == len(DEMO_ISSUES)


def test_demo_scan_returns_issues():
    results = scan_urls(["https://x.pl"], throttle=0, force_demo=True)
    assert len(results) == 1
    assert results[0].demo is True
    assert len(results[0].issues) == len(DEMO_ISSUES)
    assert results[0].error is None
