# BENCHMARKS — Bayan

> يُولَّد من `docs_src/BENCHMARKS.md.j2`. §2 (الميزانية) كُتب ورُفع **قبل** تشغيل أي مرشح للمشروع. الأقسام 3–8 منقولة آليًا من [دفتر 08](notebooks/08_optimization_serving.ipynb) → [`reports/nb08_benchmark.json`](reports/nb08_benchmark.json).

## 1. Claim boundary | حدود الادعاء

- Artefact role: `⏳ PENDING_RUN` — رأس topic الذي درّبته في دفتر 03، وليس checkpoint مسار Systems Smoke.
- Result label: `⏳ PENDING_RUN`
- Task: Multilingual (AR/EN) topic text classification — 4 labels
- Author: Manal Qaysi
- لا تمثل هذه الأرقام خدمة إنتاجية. القياس على CPU في Colab، وعلى workload صغيرة ثابتة.

## 2. Performance budget — written before candidates

| Constraint | TARGET | Why this matters |
|---|---:|---|
| p95 model-only latency per workload call (8 texts, batch 4) | 100 ms | استجابة تفاعلية لموظف الفرز على CPU مجاني |
| minimum throughput | 20 items/s | فرز دفعة الملاحظات اليومية دون GPU |
| maximum quality tax | 0.02 macro-F1 | التحسين لا يستحق أن يُفقد أكثر من نقطتين من الجودة |
| target device | Colab CPU (`CPUExecutionProvider`) | بيئة قابلة لإعادة الإنتاج للجميع |

- **Commit/time proving budget existed before candidate:** هذه القيم مكتوبة في هذا الملف وفي خلية الإعداد في دفتر 08 منذ commit «perf: write performance budget before measuring candidates» بتاريخ 2026-09-30، وهو سابق لأول تشغيل لـ`PROJECT_MODE` (راجعي `git log -- BENCHMARKS.md docs_src/BENCHMARKS.md.j2`). في الدفتر: `BUDGET_PROVENANCE = ⏳ PENDING_RUN`.

## 3. Reproduction contract

| Field | Value |
|---|---|
| Colab runtime / Python | Python ⏳ PENDING_RUN — `⏳ PENDING_RUN` |
| Device / provider | `⏳ PENDING_RUN` / `⏳ PENDING_RUN` |
| Runtime doctor (notebook 00) | device=⏳ PENDING_RUN, GPU=⏳ PENDING_RUN, in_colab=⏳ PENDING_RUN |
| Library versions | torch ⏳ PENDING_RUN · onnx ⏳ PENDING_RUN · onnxruntime ⏳ PENDING_RUN (pinned in `requirements-day4.txt`) |
| Model ID / revision / hash | `distilbert/distilbert-base-multilingual-cased` fine-tuned in notebook 03 (⏳ PENDING_RUN, epoch ⏳ PENDING_RUN); state SHA-256 `⏳ PENDING_RUN…` |
| Trained from repository commit | `⏳ PENDING_RUN` |
| Preprocessing version | `⏳ PENDING_RUN` (training = serving) |
| Label map version | ⏳ PENDING_RUN (saved with the checkpoint config) |
| Workload path / hash | validation split of `data/sample/bayan_day2_classification.csv`، SHA-256 `⏳ PENDING_RUN…` |
| Split | validation (candidate selection); frozen test not used here |
| Examples + AR/EN counts | ⏳ PENDING_RUN rows · languages ⏳ PENDING_RUN |
| Length distribution | p50 ⏳ PENDING_RUN · p95 ⏳ PENDING_RUN · max ⏳ PENDING_RUN tokens; would truncate: ⏳ PENDING_RUN |
| Batch size | ⏳ PENDING_RUN |
| Padding / max length | dynamic padding per batch / `MAX_LENGTH=⏳ PENDING_RUN` (measured, D-002) |
| Warm-up / repetitions | ⏳ PENDING_RUN / ⏳ PENDING_RUN |
| Measured boundary | `⏳ PENDING_RUN` |
| Memory method | ⏳ PENDING_RUN |

## 4. Controlled candidates

| ID | Runtime/precision | Only intended change | Artefact hash | Size MiB |
|---|---|---|---|---:|
| A | PyTorch FP32 reference | baseline | `⏳ PENDING_RUN` | ⏳ PENDING_RUN |
| B | ONNX Runtime FP32 | runtime/export | `⏳ PENDING_RUN` | ⏳ PENDING_RUN |
| C | ONNX Runtime dynamic INT8 | weight quantisation | `⏳ PENDING_RUN` | ⏳ PENDING_RUN |

INT8 status: available = ⏳ PENDING_RUN; error = ⏳ PENDING_RUN

## 5. Parity

| Comparison | max abs logits diff | mean abs diff | prediction agreement | Verdict |
|---|---:|---:|---:|---|
| A vs B | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |
| A vs C | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | reported; INT8 is judged by quality tax, not bit-parity |

- **Tolerance chosen before inspection:** FP32: `max abs logits diff < 1e-3` و`prediction agreement = 1.0` (assertions في الدفتر). INT8: لا أطلب تطابق الـlogits، وأحكم عليه بأثر الجودة ≤ 0.02.
- **Rationale:** ONNX FP32 يجب أن يكون الحساب نفسه تقريبًا (فروق float فقط). أما INT8 فيغيّر الأوزان عمدًا، فالمهم أثره على Macro-F1.

## 6. Performance results (model-only, per workload call)

| ID | p50 ms | p95 ms | p99 ms | items/s | observed peak RSS MiB | speedup vs A (p95) |
|---|---:|---:|---:|---:|---:|---:|
| A | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | 1.00× |
| B | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN× |
| C | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | — |

PyTorch end-to-end (tokenisation + model): p95 ⏳ PENDING_RUN ms، ⏳ PENDING_RUN items/s.

## 7. Quality results

- Primary task metric: `⏳ PENDING_RUN` (macro-F1 on the full validation workload, same examples for every candidate)
- Evaluation file/split: validation workload (n=⏳ PENDING_RUN)

| ID | Task quality | Quality tax = A − candidate | Small-sample/CI note |
|---|---:|---:|---|
| A | ⏳ PENDING_RUN | 0 | n=⏳ PENDING_RUN: خطأ واحد يغيّر Macro-F1 كثيرًا |
| B | ⏳ PENDING_RUN | ⏳ PENDING_RUN | الأمثلة نفسها |
| C | ⏳ PENDING_RUN | ⏳ PENDING_RUN | الأمثلة نفسها |

## 8. Budget verdict and decision

| Candidate | latency OK | throughput OK | quality OK | Overall |
|---|---|---|---|---|
| B | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |
| C | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |

- Selected runtime: `⏳ PENDING_RUN`
- Decision: **⏳ PENDING_RUN**
- Evidence-based reason: القاعدة المكتوبة مسبقًا في دفتر 08: INT8 إن حقق الميزانية كاملة، وإلا ONNX FP32 إن حققها، وإلا PyTorch FP32. الجدول أعلاه يبيّن أي شرط تحقق.
- Known limitation/noise source: Colab CPU مشترك وزمنه يتذبذب بين الجلسات؛ الـworkload 8 نصوص قصيرة؛ ذاكرة RSS تقريبية للعملية كلها.
- FP32 rollback/reproduction path: أعيد تشغيل دفتر 03 (يحفظ artefact في Drive)، ثم دفتر 08. الأوزان وONNX لا تُرفع إلى GitHub.
- Generated JSON report: [`reports/nb08_benchmark.json`](reports/nb08_benchmark.json)

## 9. Reproduction commands

1. Run [notebook 03](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/03_text_classification.ipynb) (saves the fine-tuned model to `MyDrive/bayan/model-v1`).
2. Run [notebook 08](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/08_optimization_serving.ipynb) with **Runtime → Restart session and run all** (PROJECT_MODE=True).
3. Save notebook 08 to GitHub, then `python scripts/collect_results.py --strict`.

## 10. Integrity check

- [x] Budget predates candidate results (committed 2026-09-30, before the first PROJECT_MODE run).
- [x] Same workload/device/batch/boundary used (one workload list and one batch size in the notebook).
- [x] Warm-up excluded (`benchmark_callable` warm-up calls are not timed).
- [x] At least 30 measured repetitions.
- [x] p50/p95/p99 and throughput included.
- [x] Memory wording matches measurement method (process RSS, observed peak, approximate).
- [x] Quality tax uses the same examples.
- [x] Failed/slower candidates were not hidden (all three rows are shown, including INT8 errors).
- [ ] Numbers are `MEASURED`, not copied references.
- [x] No weights, ONNX artefacts, cache, secrets, or PII committed (`.gitignore` + privacy scan in `scripts/collect_results.py`).
