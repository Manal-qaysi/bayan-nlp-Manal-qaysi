"""The root reports must contain measured values, not pending markers.

This test fails on purpose until every notebook has been run, saved to GitHub
and collected with ``python scripts/collect_results.py``.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERED = [
    "README.md", "DECISIONS.md", "BENCHMARKS.md", "EVALUATION_REPORT.md",
    "MODEL_CARD.md", "DATA_CARD.md", "PROGRESS.md", "PRESENTATION.md",
]


def test_root_reports_have_no_pending_results():
    pending = [name for name in RENDERED if "PENDING_RUN" in (ROOT / name).read_text(encoding="utf-8")]
    assert not pending, (
        "Run and save the notebooks, then `python scripts/collect_results.py`. Still pending: " + ", ".join(pending)
    )


def test_every_reported_result_has_provenance():
    import json

    index = json.loads((ROOT / "reports" / "results_index.json").read_text(encoding="utf-8"))
    assert index, "no collected results"
    for name, entry in index.items():
        assert entry.get("notebook") and entry.get("code_cell") and entry.get("execution_count"), name
        assert entry.get("repo_sha"), f"{name}: notebook was not run from a repository commit"
