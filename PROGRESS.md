# PROGRESS — Bayan Gates A–E

- **Student GitHub:** `Manal-qaysi`
- **Repository:** https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi
- **Last updated:** 2026-09-30 12:26 UTC (rendered by `scripts/collect_results.py`)

لا توضع علامة ✅ قبل وجود رابط commit أو تقرير أو اختبار قابل للفحص؛ الحالات أدناه تُحسب آليًا من وجود نتائج الدفاتر المنفّذة.

| Gate | Status | Required evidence | Commit/report links | Blocker/next action |
|---|---|---|---|---|
| A — ingest | 🟨 IN_PROGRESS | preprocessing tests + tokenizer decision | [nb01](reports/nb01_tokenization.json) · [nb05](reports/nb05_arabic.json) · `tests/test_my_arabic_golden.py` · D-002/D-003 | run + save notebooks 01 and 05 |
| B — tasks | 🟨 IN_PROGRESS | classification + NER + QA evidence | [nb03](reports/nb03_classification.json) · [nb04](reports/nb04_ner_qa.json) · D-004 | run + save notebooks 03 and 04 |
| C — search & truth | 🟨 IN_PROGRESS | search metrics + slices + taxonomy | [nb06](reports/nb06_retrieval.json) · [nb07](reports/nb07_evaluation.json) · `EVALUATION_REPORT.md` | run + save notebooks 06 then 07 |
| D — ship | 🟨 IN_PROGRESS | project benchmark + API tests + canaries | [nb08](reports/nb08_benchmark.json) · `BENCHMARKS.md` · D-007/D-008 | run notebook 08 in PROJECT_MODE after 03 |
| E — submit | 🟨 IN_PROGRESS | validator + demo + release tag | `reports/preflight.json` · `PRESENTATION.md` | validator + preflight, then tag `submission-v1.0` |

Status values: `⬜ NOT_STARTED`, `🟨 IN_PROGRESS`, `✅ PASSED`, `🟥 BLOCKED`.

## Runtime/run-all evidence

| Notebook | Clean run saved (commit date) | Core marker | Colab / GitHub link | run from repo commit |
|---|---|---|---|---|
| 00 | ⏳ PENDING_RUN | `BAYAN_ENV_READY = True` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/00_runtime_doctor.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/00_runtime_doctor.ipynb) | `—` |
| 01 | ⏳ PENDING_RUN | `DAY1_NOTEBOOK1_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/01_text_processing_tokenization.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/01_text_processing_tokenization.ipynb) | `—` |
| 02 | ⏳ PENDING_RUN | `DAY1_NOTEBOOK2_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/02_attention_transformers.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/02_attention_transformers.ipynb) | `—` |
| 03 | ⏳ PENDING_RUN | `DAY2_NOTEBOOK3_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/03_text_classification.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/03_text_classification.ipynb) | `—` |
| 04 | ⏳ PENDING_RUN | `DAY2_NOTEBOOK4_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/04_ner_and_qa.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/04_ner_and_qa.ipynb) | `—` |
| 05 | ⏳ PENDING_RUN | `DAY3_NOTEBOOK5_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/05_arabic_nlp.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/05_arabic_nlp.ipynb) | `—` |
| 06 | ⏳ PENDING_RUN | `DAY3_NOTEBOOK6_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/06_semantic_search.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/06_semantic_search.ipynb) | `—` |
| 07 | ⏳ PENDING_RUN | `DAY3_NOTEBOOK7_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/07_evaluation_error_analysis.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/07_evaluation_error_analysis.ipynb) | `—` |
| 08 | ⏳ PENDING_RUN | `DAY4_NOTEBOOK8_CORE=PASS` | [Colab](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/08_optimization_serving.ipynb) · [GitHub](https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/08_optimization_serving.ipynb) | `—` |

## Final release

- Final commit: الـcommit الذي يشير إليه `submission-v1.0` (يُطبع بخلية الفحص النهائية في `docs/learner-workflow` للدورة: `FINAL_COMMIT_SHA`).
- Release/tag `submission-v1.0`: https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi/releases/tag/submission-v1.0
- Validator pre-tag report: `reports/submission_validation.json`
- Validator `--require-tag` report: `reports/preflight.json` (بعد إنشاء الوسم)
- Private-window visibility check: يُفحص يدويًا بفتح المستودع وروابط Colab في نافذة خاصة قبل التسليم.
- Remaining limitation: عينات صغيرة اصطناعية (انظري `EVALUATION_REPORT.md` §9).
