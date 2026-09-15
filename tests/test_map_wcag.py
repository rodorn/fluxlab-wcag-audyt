"""Testy mapowania axe -> WCAG 2.2 i logiki priorytetow."""

from src.map_wcag import AXE_TO_WCAG, map_issues, summarize
from src.scan import DEMO_ISSUES


def test_known_code_maps_to_wcag():
    findings = map_issues(
        [{"code": "image-alt", "runnerExtras": {"impact": "critical"}}]
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.wcag == "1.1.1"
    assert f.level == "A"
    assert f.en301549 == "9.1.1.1"


def test_unknown_code_falls_back():
    findings = map_issues([{"code": "totally-made-up-rule"}])
    assert len(findings) == 1
    assert findings[0].wcag == "4.1.1"
    assert findings[0].priority == "P3"


def test_grouping_counts_selectors():
    issues = [
        {
            "code": "image-alt",
            "selector": "img.a",
            "runnerExtras": {"impact": "critical"},
        },
        {
            "code": "image-alt",
            "selector": "img.b",
            "runnerExtras": {"impact": "critical"},
        },
    ]
    findings = map_issues(issues)
    assert len(findings) == 1
    assert findings[0].count == 2
    assert set(findings[0].selectors) == {"img.a", "img.b"}


def test_priority_escalated_by_critical_impact():
    # color-contrast bazowo P2, ale critical impact powinien podniesc do P1
    findings = map_issues(
        [{"code": "color-contrast", "runnerExtras": {"impact": "critical"}}]
    )
    assert findings[0].priority == "P1"


def test_priority_not_downgraded_by_low_impact():
    # image-alt bazowo P1; moderate impact nie moze go obnizyc
    findings = map_issues(
        [{"code": "image-alt", "runnerExtras": {"impact": "moderate"}}]
    )
    assert findings[0].priority == "P1"


def test_findings_sorted_by_priority():
    findings = map_issues([dict(i) for i in DEMO_ISSUES])
    priorities = [f.priority for f in findings]
    ranks = {"P1": 0, "P2": 1, "P3": 2}
    assert priorities == sorted(priorities, key=lambda p: ranks[p])


def test_summarize_totals():
    findings = map_issues([dict(i) for i in DEMO_ISSUES])
    stats = summarize(findings)
    assert stats["total_issues"] == len(DEMO_ISSUES)
    assert stats["p1"] + stats["p2"] + stats["p3"] == stats["total_issues"]
    assert stats["level_a"] + stats["level_aa"] == stats["total_issues"]


def test_all_mappings_have_required_fields():
    for code, m in AXE_TO_WCAG.items():
        assert m["level"] in ("A", "AA"), code
        assert m["priority"] in ("P1", "P2", "P3"), code
        assert m["en301549"].startswith("9."), code
        assert "<code>" in m["fix"], code
