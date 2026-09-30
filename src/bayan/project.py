"""Project-level helpers for Manal Qaysi's Bayan repository.

These helpers are shared by the nine notebooks and by
``scripts/collect_results.py``. They exist so that every number that appears
in the reports can be traced back to one executed notebook cell:

1. a notebook cell calls :func:`emit_result`, which prints one line
   ``BAYAN_RESULT::<name>::<json>`` into the saved notebook output;
2. ``scripts/collect_results.py`` reads the *saved* notebooks, extracts those
   lines, writes ``reports/<name>.json`` and renders the root documents.

Nothing here downloads a model; the functions are small, deterministic and
unit-tested in ``tests/test_project_helpers.py``.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Hashable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any
import hashlib
import json
import math
import re
import string
import subprocess

from .ner_alignment import bio_entities
from .preprocessing import build_text_record

RESULT_PREFIX = "BAYAN_RESULT::"

# One versioned preprocessing contract used by notebooks 01, 03 and 08 (train
# and serve). Conservative: NFC, tatweel removal, email/Saudi-mobile masking,
# whitespace cleanup; diacritics, alef forms and ya are preserved.
PREPROCESSING_VERSION = "bayan-prep/1.0.0"


def detect_language(text: str) -> str:
    """'ar' when the text contains Arabic letters, otherwise 'en'."""

    return "ar" if any("؀" <= char <= "ۿ" for char in str(text)) else "en"


def prepare_model_text(text: str, language: str = "auto") -> str:
    """Model copy of ``text`` under ``PREPROCESSING_VERSION`` (display copy untouched)."""

    if language not in {"ar", "en"}:
        language = detect_language(text)
    return build_text_record(text, language=language).model_text
_RESULT_LINE = re.compile(r"BAYAN_RESULT::([A-Za-z0-9_.-]+)::(\{.*\})\s*$")


# ---------------------------------------------------------------------------
# Traceable results
# ---------------------------------------------------------------------------

def json_safe(value: Any) -> Any:
    """Convert numpy/pathlib values into plain JSON values (NaN -> None)."""

    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        items = sorted(value, key=str) if isinstance(value, set) else value
        return [json_safe(item) for item in items]
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "item") and callable(value.item) and not isinstance(value, (str, bytes)):
        try:
            value = value.item()
        except (TypeError, ValueError):
            return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def format_result_line(name: str, payload: Mapping[str, Any]) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("result name may contain letters, digits, dot, dash and underscore only")
    body = json.dumps(json_safe(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{RESULT_PREFIX}{name}::{body}"


def emit_result(
    name: str,
    payload: Mapping[str, Any],
    *,
    reports_dir: str | Path | None = "reports",
) -> str:
    """Print a machine-readable result line and optionally save it as JSON."""

    line = format_result_line(name, payload)
    print(line)
    if reports_dir is not None:
        directory = Path(reports_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{name}.json").write_text(
            json.dumps(json_safe(payload), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return line


def parse_result_lines(text: str) -> dict[str, dict[str, Any]]:
    """Return every ``BAYAN_RESULT`` payload found in ``text`` (last one wins)."""

    results: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        match = _RESULT_LINE.search(line.strip())
        if match:
            results[match.group(1)] = json.loads(match.group(2))
    return results


def _output_text(output: Mapping[str, Any]) -> str:
    def join(value: Any) -> str:
        return "".join(value) if isinstance(value, list) else str(value or "")

    parts = [join(output.get("text"))]
    data = output.get("data") or {}
    parts.append(join(data.get("text/plain")))
    return "\n".join(parts)


def collect_notebook_results(path: str | Path) -> dict[str, dict[str, Any]]:
    """Extract results from the *saved outputs* of an executed notebook.

    Each payload gains a ``_provenance`` block naming the notebook, the code
    cell number and its execution count, so a reviewer can open the cell.
    """

    path = Path(path)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    found: dict[str, dict[str, Any]] = {}
    code_index = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        code_index += 1
        text = "\n".join(_output_text(output) for output in cell.get("outputs", []))
        for name, payload in parse_result_lines(text).items():
            payload = dict(payload)
            payload["_provenance"] = {
                "notebook": path.name,
                "code_cell": code_index,
                "execution_count": cell.get("execution_count"),
            }
            found[name] = payload
    return found


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def data_hashes(data_dir: str | Path) -> dict[str, str]:
    """SHA-256 of every file directly inside ``data_dir`` (sorted by name)."""

    directory = Path(data_dir)
    return {
        item.name: sha256_file(item)
        for item in sorted(directory.iterdir())
        if item.is_file()
    }


def git_head(repo_dir: str | Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------------------
# Tokenisation evidence (T1)
# ---------------------------------------------------------------------------

def _percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("values must not be empty")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def length_profile(
    token_lengths: Sequence[int],
    word_lengths: Sequence[int],
    candidates: Sequence[int],
    *,
    special_tokens: int = 2,
) -> dict[str, Any]:
    """Fertility, length percentiles and truncation rate per candidate.

    ``token_lengths`` must include special tokens (what the model receives,
    so truncation is judged on the real input length); fertility excludes the
    ``special_tokens`` ([CLS]/[SEP]) and divides by whitespace words.
    """

    if not token_lengths or len(token_lengths) != len(word_lengths):
        raise ValueError("token_lengths and word_lengths must be paired and non-empty")
    if any(words <= 0 for words in word_lengths):
        raise ValueError("every text needs at least one word")
    fertility_values = [
        max(0, tokens - special_tokens) / words
        for tokens, words in zip(token_lengths, word_lengths)
    ]
    return {
        "n": len(token_lengths),
        "mean_fertility": sum(fertility_values) / len(fertility_values),
        "p50_tokens": _percentile(token_lengths, 50),
        "p95_tokens": _percentile(token_lengths, 95),
        "max_tokens": int(max(token_lengths)),
        "truncation_rate": {
            str(int(limit)): sum(length > limit for length in token_lengths) / len(token_lengths)
            for limit in candidates
        },
    }


def choose_max_length(
    token_lengths: Sequence[int],
    candidates: Sequence[int],
    *,
    max_truncation_rate: float = 0.0,
) -> dict[str, Any]:
    """Smallest candidate whose truncation rate is within the tolerance."""

    if not candidates:
        raise ValueError("candidates must not be empty")
    ordered = sorted(int(value) for value in candidates)
    for limit in ordered:
        rate = sum(length > limit for length in token_lengths) / len(token_lengths)
        if rate <= max_truncation_rate:
            return {"max_length": limit, "truncation_rate": rate, "rule": f"smallest candidate with truncation <= {max_truncation_rate}"}
    limit = ordered[-1]
    rate = sum(length > limit for length in token_lengths) / len(token_lengths)
    return {"max_length": limit, "truncation_rate": rate, "rule": "largest candidate; tolerance not met"}


# ---------------------------------------------------------------------------
# NER (T3)
# ---------------------------------------------------------------------------

def per_type_entity_report(
    true_sequences: Sequence[Sequence[str]],
    predicted_sequences: Sequence[Sequence[str]],
) -> dict[str, Any]:
    """Strict entity-level P/R/F1 overall (micro) and per entity type."""

    if len(true_sequences) != len(predicted_sequences):
        raise ValueError("true and predicted sequence counts must match")
    gold: set[tuple[int, str, int, int]] = set()
    predicted: set[tuple[int, str, int, int]] = set()
    for sequence_id, (truth, guess) in enumerate(zip(true_sequences, predicted_sequences)):
        if len(truth) != len(guess):
            raise ValueError("tag sequence lengths must match")
        gold |= {(sequence_id, *span) for span in bio_entities(truth)}
        predicted |= {(sequence_id, *span) for span in bio_entities(guess)}

    def prf(g: set, p: set) -> dict[str, float | int]:
        tp, fp, fn = len(g & p), len(p - g), len(g - p)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {"precision": precision, "recall": recall, "f1": f1, "support": len(g), "predicted": len(p)}

    types = sorted({item[1] for item in gold | predicted})
    return {
        "overall": prf(gold, predicted),
        "per_type": {
            entity_type: prf(
                {item for item in gold if item[1] == entity_type},
                {item for item in predicted if item[1] == entity_type},
            )
            for entity_type in types
        },
    }


# ---------------------------------------------------------------------------
# Extractive QA (T3)
# ---------------------------------------------------------------------------

_AR_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
_PUNCT = set(string.punctuation) | set("،؛؟«»…“”‘’")
_EN_ARTICLES = re.compile(r"\b(a|an|the)\b")


def normalize_answer(text: str | None) -> str:
    """SQuAD-style normalisation extended with light Arabic folding."""

    if text is None:
        return ""
    text = str(text).lower().replace("ـ", "")
    text = _AR_DIACRITICS.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = "".join(" " if char in _PUNCT else char for char in text)
    text = _EN_ARTICLES.sub(" ", text)
    return " ".join(text.split())


def qa_exact_and_f1(prediction: str | None, gold: str | None) -> tuple[float, float]:
    """EM and token F1 for one pair. ``None`` means "no answer"."""

    if gold is None or prediction is None:
        both_null = float(gold is None and prediction is None)
        return both_null, both_null
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    exact = float(pred_tokens == gold_tokens)
    common = Counter(pred_tokens) & Counter(gold_tokens)
    overlap = sum(common.values())
    if overlap == 0:
        return exact, 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return exact, 2 * precision * recall / (precision + recall)


def qa_report(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate EM/F1 plus separate has-answer and no-answer behaviour.

    Each row needs ``prediction`` and ``gold`` (either may be ``None``) and
    optionally ``language``.
    """

    if not rows:
        raise ValueError("rows must not be empty")

    def summarise(subset: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        scores = [qa_exact_and_f1(row["prediction"], row["gold"]) for row in subset]
        has = [(row, score) for row, score in zip(subset, scores) if row["gold"] is not None]
        null = [row for row in subset if row["gold"] is None]
        return {
            "n": len(subset),
            "exact_match": sum(score[0] for score in scores) / len(scores),
            "f1": sum(score[1] for score in scores) / len(scores),
            "has_answer_n": len(has),
            "has_answer_f1": (sum(score[1] for _, score in has) / len(has)) if has else None,
            "no_answer_n": len(null),
            "no_answer_accuracy": (sum(row["prediction"] is None for row in null) / len(null)) if null else None,
            "false_abstentions": sum(row["prediction"] is None for row, _ in has),
        }

    report = {"overall": summarise(rows), "by_language": {}}
    languages = sorted({str(row.get("language", "unknown")) for row in rows})
    for language in languages:
        report["by_language"][language] = summarise(
            [row for row in rows if str(row.get("language", "unknown")) == language]
        )
    return report


def tune_null_threshold(
    margins: Sequence[float],
    has_answer: Sequence[bool],
) -> dict[str, float]:
    """Pick the null-score margin threshold on *validation* examples only.

    ``margin = null_score - best_span_score``; the model abstains when
    ``margin > threshold``. The threshold maximising answer/no-answer accuracy
    is chosen, ties broken towards the smaller (more willing to answer) value.
    """

    if not margins or len(margins) != len(has_answer):
        raise ValueError("margins and has_answer must be paired and non-empty")
    finite = sorted({float(m) for m in margins if math.isfinite(float(m))})
    candidates = [0.0]
    if finite:
        candidates += [finite[0] - 1e-6, finite[-1] + 1e-6]
        candidates += [(a + b) / 2 for a, b in zip(finite, finite[1:])]
    best = None
    for threshold in sorted(set(candidates)):
        correct = sum(
            (not (float(m) > threshold)) == bool(label)
            for m, label in zip(margins, has_answer)
        )
        accuracy = correct / len(margins)
        if best is None or accuracy > best[0]:
            best = (accuracy, threshold)
    return {"threshold": float(best[1]), "validation_accuracy": float(best[0])}


# ---------------------------------------------------------------------------
# Retrieval extension (T7): hybrid sparse + dense with reciprocal rank fusion
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[Hashable]],
    *,
    k: int = 60,
    weights: Sequence[float] | None = None,
    top_n: int | None = None,
) -> list[Hashable]:
    """Fuse several ranked id lists: score(d) = sum_i w_i / (k + rank_i(d))."""

    if not rankings:
        raise ValueError("at least one ranking is required")
    if k < 1:
        raise ValueError("k must be positive")
    weights = list(weights) if weights is not None else [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("weights must match rankings")
    scores: dict[Hashable, float] = defaultdict(float)
    first_seen: dict[Hashable, tuple[int, int]] = {}
    for ranking_index, (ranking, weight) in enumerate(zip(rankings, weights)):
        for rank, item in enumerate(ranking, start=1):
            scores[item] += weight / (k + rank)
            first_seen.setdefault(item, (rank, ranking_index))
    fused = sorted(scores, key=lambda item: (-scores[item], first_seen[item]))
    return fused[:top_n] if top_n else fused


# ---------------------------------------------------------------------------
# Error taxonomy (T5)
# ---------------------------------------------------------------------------

NEGATION_CUES = {"لم", "لن", "لا", "ما", "مو", "مب", "not", "no", "never", "cannot", "can't", "didn't", "doesn't", "isn't", "wasn't"}


def suggest_error_tag(
    row: Mapping[str, Any],
    *,
    token_count: int | None = None,
    max_length: int | None = None,
) -> dict[str, str]:
    """Transparent *suggestion* of a taxonomy tag for one wrong prediction.

    The suggestion must be read and confirmed (or changed) by a person; the
    notebook records whether that manual review happened.
    """

    task = str(row.get("task", ""))
    if task == "ner":
        return {"taxonomy_tag": "entity_boundary", "rationale": "gold and predicted BIO spans differ (strict match)"}
    if task == "qa":
        if row.get("gold") is None and row.get("prediction") is not None:
            return {"taxonomy_tag": "hard_or_ambiguous", "rationale": "answered an unanswerable question; no unanswerable training/validation examples"}
        if row.get("prediction") is None:
            return {"taxonomy_tag": "hard_or_ambiguous", "rationale": "abstained on an answerable question"}
        return {"taxonomy_tag": "entity_boundary", "rationale": "extracted span boundaries differ from the gold answer"}
    if task == "retrieval":
        if row.get("error_kind") == "answered_no_answer_query":
            return {"taxonomy_tag": "hard_or_ambiguous", "rationale": "best score above the frozen threshold for a query without a relevant case"}
        if row.get("retrieval_mode") == "cross_lingual":
            return {"taxonomy_tag": "hard_or_ambiguous", "rationale": "cross-lingual query: the relevant case is written in the other language"}

    text = str(row.get("text", ""))
    words = text.split()
    lowered = {word.strip("?.!،؟").lower() for word in words}
    if token_count is not None and max_length is not None and token_count > max_length:
        return {"taxonomy_tag": "truncation", "rationale": f"{token_count} tokens > max_length {max_length}"}
    if str(row.get("variant", "")) in {"Gulf", "Arabizi"}:
        return {"taxonomy_tag": "dialect_gap", "rationale": f"{row.get('variant')} wording; training data is mostly MSA/English"}
    if lowered & NEGATION_CUES:
        return {"taxonomy_tag": "negation", "rationale": "negation cue present: " + ", ".join(sorted(lowered & NEGATION_CUES))}
    if len(words) <= 3:
        return {"taxonomy_tag": "hard_or_ambiguous", "rationale": "very short request without an explicit topic noun"}
    return {
        "taxonomy_tag": "class_confusion",
        "rationale": f"{row.get('gold', row.get('topic'))} predicted as {row.get('prediction')}",
    }


def taxonomy_summary(tagged: Sequence[Mapping[str, Any]], *, example_chars: int = 60) -> list[dict[str, Any]]:
    """Counts per tag with one short example and the ids for traceability."""

    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in tagged:
        groups[str(row["taxonomy_tag"])].append(row)
    summary = []
    for tag, rows in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        example = str(rows[0].get("text", ""))
        summary.append({
            "taxonomy_tag": tag,
            "count": len(rows),
            "example_ids": [str(row.get("example_id")) for row in rows],
            "example": example[:example_chars] + ("…" if len(example) > example_chars else ""),
            "tasks": sorted({str(row.get("task", "")) for row in rows}),
        })
    return summary


def iter_errors(rows: Iterable[Mapping[str, Any]], *, gold_key: str = "gold", pred_key: str = "prediction") -> list[Mapping[str, Any]]:
    return [row for row in rows if row[gold_key] != row[pred_key]]
