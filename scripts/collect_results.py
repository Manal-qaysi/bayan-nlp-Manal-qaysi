#!/usr/bin/env python3
"""Collect measured results from the executed notebooks and render the reports.

Usage (from the repository root, after running and saving notebooks 00-08):

    python scripts/collect_results.py            # render; missing results show as ⏳ PENDING_RUN
    python scripts/collect_results.py --strict   # fail if any notebook result is missing

What it does, in order:
1. reads the *saved outputs* of ``notebooks/*.ipynb`` and extracts every
   ``BAYAN_RESULT::<name>::<json>`` line (source code alone is never enough);
2. writes ``reports/<name>.json`` plus ``reports/results_index.json`` (which
   notebook, which code cell, which repository commit produced each result);
3. renders the root documents from ``docs_src/*.md.j2``;
4. runs the test-suite and a small privacy scan, then writes
   ``PROJECT_SUMMARY.json`` with ``tests_passed`` / ``privacy_check`` set from
   those checks rather than typed by hand.

No number in the root documents is typed manually: every value comes from a
notebook output through this script.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bayan.project import collect_notebook_results, data_hashes, git_head  # noqa: E402

OWNER = "Manal-qaysi"
REPO = "bayan-nlp-Manal-qaysi"
REPO_URL = f"https://github.com/{OWNER}/{REPO}"
NOTEBOOKS = [
    ("00_runtime_doctor.ipynb", "runtime doctor", "environment", "nb00_runtime", "BAYAN_ENV_READY = True"),
    ("01_text_processing_tokenization.ipynb", "text processing / tokenisation", "Gate A · T1", "nb01_tokenization", "DAY1_NOTEBOOK1_CORE=PASS"),
    ("02_attention_transformers.ipynb", "attention / transformers", "T2", "nb02_attention", "DAY1_NOTEBOOK2_CORE=PASS"),
    ("03_text_classification.ipynb", "topic + sentiment classification", "Gate B · T3", "nb03_classification", "DAY2_NOTEBOOK3_CORE=PASS"),
    ("04_ner_and_qa.ipynb", "NER and extractive QA", "Gate B · T3", "nb04_ner_qa", "DAY2_NOTEBOOK4_CORE=PASS"),
    ("05_arabic_nlp.ipynb", "Arabic NLP (CAMeL profile)", "Gate C · T1", "nb05_arabic", "DAY3_NOTEBOOK5_CORE=PASS"),
    ("06_semantic_search.ipynb", "semantic search + extension", "Gate C · T4/T7", "nb06_retrieval", "DAY3_NOTEBOOK6_CORE=PASS"),
    ("07_evaluation_error_analysis.ipynb", "evaluation / error analysis", "Gate C · T5", "nb07_evaluation", "DAY3_NOTEBOOK7_CORE=PASS"),
    ("08_optimization_serving.ipynb", "optimisation / serving", "Gate D · T6", "nb08_benchmark", "DAY4_NOTEBOOK8_CORE=PASS"),
]
EXPECTED_RESULTS = [item[3] for item in NOTEBOOKS] + ["nb06_extension"]
RENDERED = [
    "README.md", "DECISIONS.md", "BENCHMARKS.md", "EVALUATION_REPORT.md",
    "MODEL_CARD.md", "DATA_CARD.md", "PROGRESS.md", "PRESENTATION.md",
]
PENDING_TEXT = "⏳ PENDING_RUN"


class Pending:
    """Stand-in for a result that does not exist yet (non-strict mode)."""

    def __str__(self) -> str:
        return PENDING_TEXT

    __repr__ = __str__

    def __bool__(self) -> bool:
        return False

    def __iter__(self):
        return iter(())

    def __len__(self) -> int:
        return 0

    def __getitem__(self, key: Any) -> "Pending":
        return self

    def __getattr__(self, name: str) -> "Pending":
        if name.startswith("__"):
            raise AttributeError(name)
        return self

    def items(self):
        return []

    def get(self, key: Any, default: Any = None) -> "Pending":
        return self


PENDING = Pending()


MISSING_FIELDS: list[str] = []


def lookup(results: dict[str, Any], path: str, strict: bool) -> Any:
    """Resolve ``nbXX_name.a.b`` in the collected results.

    * notebook result not collected yet  -> PENDING (``--strict`` refuses earlier);
    * a field that is legitimately null   -> None (rendered as "—");
    * a field absent from an existing result -> None, and reported at the end so
      template/notebook mismatches never pass silently.
    """

    head, _, rest = path.partition(".")
    if head not in results:
        return PENDING
    value: Any = results[head]
    for part in rest.split(".") if rest else []:
        if value is None:
            return None
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        else:
            MISSING_FIELDS.append(path)
            return None
    return value


# ---------------------------------------------------------------- formatting

def _num(value: Any, spec: str) -> str:
    if isinstance(value, Pending):
        return PENDING_TEXT
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return format(value, spec)
    return str(value)


def f3(value: Any) -> str:
    return _num(value, ".3f")


def f2(value: Any) -> str:
    return _num(value, ".2f")


def f1(value: Any) -> str:
    return _num(value, ".1f")


def pct(value: Any) -> str:
    return _num(value, ".0%")


def signed(value: Any) -> str:
    return _num(value, "+.3f")


def ci(value: Any) -> str:
    if isinstance(value, Pending) or not isinstance(value, dict):
        return PENDING_TEXT
    return f"{value['estimate']:.3f} [{value['ci_low']:.3f}, {value['ci_high']:.3f}]"


def short(value: Any, n: int = 12) -> str:
    if isinstance(value, Pending) or value is None:
        return str(value) if value is not None else "—"
    return str(value)[:n]


def yesno(value: Any) -> str:
    if isinstance(value, Pending):
        return PENDING_TEXT
    return "✅" if value else "❌"


def lst(value: Any, sep: str = ", ") -> str:
    if isinstance(value, Pending):
        return PENDING_TEXT
    if value is None:
        return "—"
    if isinstance(value, (list, tuple)):
        return sep.join(str(item) for item in value) if value else "—"
    return str(value)


def is_pending(value: Any) -> bool:
    return isinstance(value, Pending)


# ---------------------------------------------------------------- git helpers

def _git(*args: str) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True,
                                       stderr=subprocess.DEVNULL, timeout=15).strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def notebook_commit(name: str) -> dict[str, str | None]:
    line = _git("log", "-1", "--format=%H %cs", "--", f"notebooks/{name}")
    if not line:
        return {"sha": None, "date": None}
    sha, date = line.split()
    return {"sha": sha, "date": date}


# ---------------------------------------------------------------- checks

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?966|0)?5\d{8}(?!\d)")
SYNTHETIC_ALLOWED = {
    "learner@example.org", "test@example.com", "user@example.com", "name@example.com",
    "0551234567", "0512345678", "0501234567", "0555555555", "0500000000",
    "noreply@anthropic.com",
}
SCAN_SUFFIXES = {".md", ".py", ".ipynb", ".json", ".jsonl", ".csv", ".yml", ".yaml", ".txt"}


def privacy_scan() -> dict[str, Any]:
    findings = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if "artifacts" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in (EMAIL_RE, PHONE_RE):
            for match in pattern.finditer(text):
                token = match.group(0)
                if token in SYNTHETIC_ALLOWED or re.search(r"@example\.(com|org|net|invalid)$", token):
                    continue
                findings.append({"file": path.relative_to(ROOT).as_posix(), "match": token[:3] + "…"})
    return {"passed": not findings, "findings": findings[:20],
            "scope": "email / Saudi-mobile patterns outside the documented synthetic examples"}


def run_tests() -> dict[str, Any]:
    try:
        import pytest  # noqa: F401
    except ImportError:
        return {"passed": False, "summary": "pytest not installed; run: pip install pytest"}
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")}, timeout=600,
    )
    tail = (completed.stdout.strip().splitlines() or [""])[-1]
    return {"passed": completed.returncode == 0, "summary": tail}


# ---------------------------------------------------------------- main

def collect() -> tuple[dict[str, Any], dict[str, Any]]:
    results: dict[str, Any] = {}
    for name, *_ in NOTEBOOKS:
        path = ROOT / "notebooks" / name
        if path.is_file():
            results.update(collect_notebook_results(path))
    index = {
        name: {
            **payload.get("_provenance", {}),
            "repo_sha": payload.get("repo_sha"),
            "saved_in_commit": notebook_commit(payload.get("_provenance", {}).get("notebook", "")),
        }
        for name, payload in sorted(results.items())
    }
    return results, index


def render(results: dict[str, Any], index: dict[str, Any], strict: bool) -> list[str]:
    try:
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("jinja2 is required: pip install jinja2") from exc

    env = Environment(loader=FileSystemLoader(str(ROOT / "docs_src")), undefined=StrictUndefined,
                      keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True,
                      finalize=lambda value: "—" if value is None else value)
    env.filters.update(f3=f3, f2=f2, f1=f1, pct=pct, signed=signed, ci=ci, short=short, yesno=yesno, lst=lst)
    notebooks = []
    for name, purpose, gate, result_name, marker in NOTEBOOKS:
        commit = notebook_commit(name)
        notebooks.append({
            "name": name, "purpose": purpose, "gate": gate, "result": result_name, "marker": marker,
            "colab": f"https://colab.research.google.com/github/{OWNER}/{REPO}/blob/main/notebooks/{name}",
            "github": f"{REPO_URL}/blob/main/notebooks/{name}",
            "ran": result_name in results,
            "commit_sha": commit["sha"], "commit_date": commit["date"],
        })
    context = {
        "R": results, "INDEX": index, "NOTEBOOKS": notebooks,
        "OWNER": OWNER, "REPO": REPO, "REPO_URL": REPO_URL, "PENDING": PENDING_TEXT,
        "DATA_SHA256": data_hashes(ROOT / "data" / "sample"),
        "rendered_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "all_ran": all(name in results for name in EXPECTED_RESULTS),
        "v": lambda path: lookup(results, path, strict),
        "is_pending": is_pending,
    }
    written = []
    for output in RENDERED:
        text = env.get_template(output + ".j2").render(**context)
        (ROOT / output).write_text(text, encoding="utf-8")
        written.append(output)
    return written


def write_reports(results: dict[str, Any], index: dict[str, Any]) -> None:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    for name, payload in results.items():
        (reports / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (reports / "results_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    samples = ROOT / "sample_outputs"
    samples.mkdir(exist_ok=True)
    if "nb08_benchmark" in results:
        tests = results["nb08_benchmark"]["service"]["tests"]
        sample = {
            "source": "notebooks/08_optimization_serving.ipynb (FastAPI TestClient, synthetic inputs)",
            "arabic_request": {"text": "الخدمة واضحة", "language": "ar"},
            "arabic_prediction": tests.get("arabic_prediction"),
            "english_request": {"text": "The service is clear", "language": "en"},
            "english_prediction": tests.get("english_prediction"),
            "rejected_inputs": {k: tests.get(k) for k in ["empty_rejected", "unsupported_language_rejected", "too_long_rejected"]},
        }
        (samples / "service_examples.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if "nb04_ner_qa" in results:
        qa = results["nb04_ner_qa"]["qa"]["predictions"]
        (samples / "qa_examples.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if "nb06_extension" in results:
        rankings = results["nb06_extension"]["test"]
        (samples / "search_examples.json").write_text(json.dumps(
            {"dense": rankings["dense"]["rankings"], "hybrid": rankings["hybrid"]["rankings"]},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(results: dict[str, Any], tests: dict[str, Any], privacy: dict[str, Any]) -> None:
    extension = results.get("nb06_extension", {})
    summary = {
        "student_github": OWNER,
        "repository_url": REPO_URL,
        "languages": ["ar", "en"],
        "tasks": ["classification", "sentiment", "ner", "qa", "semantic_search"],
        "extension": {
            "name": "Hybrid sparse+dense retrieval with reciprocal rank fusion (RRF) over the FAISS baseline",
            "evidence": "reports/nb06_extension.json",
            "decision": extension.get("decision", PENDING_TEXT),
        },
        "benchmark_mode": "PROJECT_ARTIFACT",
        "final_tag": "submission-v1.0",
        "privacy_check": bool(privacy["passed"]),
        "tests_passed": bool(tests["passed"]),
        "checks": {"tests": tests, "privacy": privacy,
                   "results_collected": sorted(results), "results_missing": [n for n in EXPECTED_RESULTS if n not in results]},
    }
    (ROOT / "PROJECT_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="fail when any notebook result is missing")
    parser.add_argument("--skip-tests", action="store_true", help="do not run pytest (tests_passed stays false)")
    args = parser.parse_args()

    results, index = collect()
    missing = [name for name in EXPECTED_RESULTS if name not in results]
    print("results found:", ", ".join(sorted(results)) or "none")
    if missing:
        print("results missing:", ", ".join(missing))
        if args.strict:
            print("STRICT: run and save the missing notebooks first.")
            return 1
    write_reports(results, index)
    written = render(results, index, strict=args.strict)
    print("rendered:", ", ".join(written))
    tests = {"passed": False, "summary": "skipped"} if args.skip_tests else run_tests()
    privacy = privacy_scan()
    write_summary(results, tests, privacy)
    print("tests:", tests["summary"], "| privacy scan:", "PASS" if privacy["passed"] else privacy["findings"])
    if MISSING_FIELDS:
        print("WARNING fields absent from collected results:", sorted(set(MISSING_FIELDS)))
    print("repository HEAD:", git_head(ROOT))
    status = "COMPLETE" if not missing and not MISSING_FIELDS and tests["passed"] and privacy["passed"] else "INCOMPLETE"
    print(f"BAYAN_RESULTS={status}")
    return 0 if status == "COMPLETE" or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
