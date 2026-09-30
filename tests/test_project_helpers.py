"""Tests for src/bayan/project.py — the helpers that make results traceable."""
import json

import pytest

from bayan.project import (
    choose_max_length,
    collect_notebook_results,
    emit_result,
    format_result_line,
    length_profile,
    normalize_answer,
    parse_result_lines,
    per_type_entity_report,
    qa_exact_and_f1,
    qa_report,
    reciprocal_rank_fusion,
    suggest_error_tag,
    taxonomy_summary,
    tune_null_threshold,
)


def test_result_line_round_trip_keeps_arabic(tmp_path):
    line = emit_result("demo", {"text": "بوابة", "value": 0.5}, reports_dir=tmp_path)
    assert line.startswith("BAYAN_RESULT::demo::")
    assert parse_result_lines("noise\n" + line + "\nmore")["demo"] == {"text": "بوابة", "value": 0.5}
    saved = json.loads((tmp_path / "demo.json").read_text(encoding="utf-8"))
    assert saved["text"] == "بوابة"


def test_result_name_is_restricted():
    with pytest.raises(ValueError):
        format_result_line("bad name", {})


def test_nan_becomes_null():
    assert '"x":null' in format_result_line("n", {"x": float("nan")})


def test_collect_reads_saved_outputs_with_provenance(tmp_path):
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# t"]},
            {"cell_type": "code", "execution_count": 3, "outputs": [
                {"output_type": "stream", "text": [format_result_line("a", {"v": 1}) + "\n"]}
            ]},
        ]
    }
    path = tmp_path / "03_x.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    found = collect_notebook_results(path)
    assert found["a"]["v"] == 1
    assert found["a"]["_provenance"] == {"notebook": "03_x.ipynb", "code_cell": 1, "execution_count": 3}


def test_source_text_alone_is_not_a_result(tmp_path):
    line = format_result_line("a", {"v": 1})
    notebook = {"cells": [{"cell_type": "code", "execution_count": None, "source": [line], "outputs": []}]}
    path = tmp_path / "n.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    assert collect_notebook_results(path) == {}


def test_length_profile_and_max_length_choice():
    profile = length_profile([5, 7, 9, 20], [2, 3, 3, 5], [8, 16, 32])
    assert profile["max_tokens"] == 20
    assert profile["truncation_rate"] == {"8": 0.5, "16": 0.25, "32": 0.0}
    # fertility excludes the two special tokens: (5-2)/2, (7-2)/3, (9-2)/3, (20-2)/5
    assert profile["mean_fertility"] == pytest.approx((1.5 + 5 / 3 + 7 / 3 + 3.6) / 4)
    assert choose_max_length([5, 7, 9, 20], [8, 16, 32])["max_length"] == 32
    assert choose_max_length([5, 7, 9, 20], [8, 16, 32], max_truncation_rate=0.25)["max_length"] == 16


def test_per_type_entity_report_is_strict():
    truth = [["B-ORG", "I-ORG", "O", "B-DATE"]]
    guess = [["B-ORG", "O", "O", "B-DATE"]]
    report = per_type_entity_report(truth, guess)
    assert report["per_type"]["DATE"]["f1"] == 1.0
    assert report["per_type"]["ORG"]["f1"] == 0.0
    assert report["overall"]["support"] == 2


def test_answer_normalisation_handles_arabic_and_articles():
    assert normalize_answer("بوابةُ الخدمات،") == "بوابة الخدمات"
    assert normalize_answer("إدارة") == normalize_answer("ادارة")
    assert normalize_answer("The appointments service.") == "appointments service"


def test_qa_scores_and_no_answer():
    assert qa_exact_and_f1("PDF", "PDF") == (1.0, 1.0)
    assert qa_exact_and_f1(None, None) == (1.0, 1.0)
    assert qa_exact_and_f1("PDF", None) == (0.0, 0.0)
    em, f1 = qa_exact_and_f1("عبر التطبيق", "عبر التطبيق أو مركز الاتصال")
    assert em == 0.0 and 0 < f1 < 1
    report = qa_report([
        {"prediction": "PDF", "gold": "PDF", "language": "en"},
        {"prediction": None, "gold": None, "language": "ar"},
        {"prediction": None, "gold": "صفحة طلباتي", "language": "ar"},
    ])
    assert report["overall"]["no_answer_accuracy"] == 1.0
    assert report["overall"]["false_abstentions"] == 1
    assert report["by_language"]["en"]["exact_match"] == 1.0


def test_null_threshold_uses_margins():
    result = tune_null_threshold([-3.0, -1.0, 2.0, 4.0], [True, True, False, False])
    assert result["validation_accuracy"] == 1.0
    assert -1.0 <= result["threshold"] < 2.0


def test_rrf_prefers_items_ranked_well_by_both():
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "c", "a"]])
    assert fused[0] == "b"
    assert reciprocal_rank_fusion([["x", "y"]], top_n=1) == ["x"]
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([["a"]], weights=[1.0, 2.0])


def test_error_tag_suggestions_are_transparent():
    assert suggest_error_tag({"text": "ما وصلني الرمز", "variant": "Gulf"})["taxonomy_tag"] == "dialect_gap"
    assert suggest_error_tag({"text": "The bus did not arrive on time"})["taxonomy_tag"] == "negation"
    assert suggest_error_tag({"text": "status please"})["taxonomy_tag"] == "hard_or_ambiguous"
    assert suggest_error_tag({"text": "x y z w"}, token_count=70, max_length=64)["taxonomy_tag"] == "truncation"
    summary = taxonomy_summary([
        {"example_id": "1", "taxonomy_tag": "negation", "text": "a", "task": "topic"},
        {"example_id": "2", "taxonomy_tag": "negation", "text": "b", "task": "sentiment"},
        {"example_id": "3", "taxonomy_tag": "dialect_gap", "text": "c", "task": "topic"},
    ])
    assert summary[0]["taxonomy_tag"] == "negation" and summary[0]["count"] == 2


def test_prepare_model_text_is_versioned_and_idempotent():
    from bayan.project import PREPROCESSING_VERSION, prepare_model_text

    assert PREPROCESSING_VERSION == "bayan-prep/1.0.0"
    raw = "الخـدمة   متأخرة، راسلني على test@example.com"
    once = prepare_model_text(raw, "ar")
    assert once == "الخدمة متأخرة، راسلني على [EMAIL]"
    assert prepare_model_text(once, "ar") == once
    assert prepare_model_text("Call 0551234567 now") == "Call [PHONE] now"
    # conservative profile keeps diacritics and alef forms for the model copy
    assert prepare_model_text("إِدارة") == "إِدارة"


def test_task_specific_error_tags():
    assert suggest_error_tag({"task": "ner"})["taxonomy_tag"] == "entity_boundary"
    assert suggest_error_tag({"task": "qa", "gold": None, "prediction": "x"})["taxonomy_tag"] == "hard_or_ambiguous"
    assert suggest_error_tag({"task": "qa", "gold": "PDF files", "prediction": "PDF"})["taxonomy_tag"] == "entity_boundary"
    assert suggest_error_tag({"task": "retrieval", "retrieval_mode": "cross_lingual", "text": "bus late"})["taxonomy_tag"] == "hard_or_ambiguous"
