# BENCHMARKS — Bayan

> يُولَّد من `docs_src/BENCHMARKS.md.j2`. §2 (الميزانية) كُتب ورُفع **قبل** تشغيل أي مرشح للمشروع. الأقسام 3–8 منقولة آليًا من [دفتر 08](notebooks/08_optimization_serving.ipynb) → [`reports/nb08_benchmark.json`](reports/nb08_benchmark.json).

## 1. Claim boundary | حدود الادعاء

- Artefact role: `PROJECT_ARTIFACT` — رأس topic الذي درّبته في دفتر 03، وليس checkpoint مسار Systems Smoke.
- Result label: `MEASURED`
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

- **Commit/time proving budget existed before candidate:** هذه القيم مكتوبة في هذا الملف وفي خلية الإعداد في دفتر 08 منذ commit «perf: write performance budget before measuring candidates» بتاريخ 2026-09-30، وهو سابق لأول تشغيل لـ`PROJECT_MODE` (راجعي `git log -- BENCHMARKS.md docs_src/BENCHMARKS.md.j2`). في الدفتر: `BUDGET_PROVENANCE = STUDENT_DEFINED_BEFORE_MEASUREMENT`.

## 3. Reproduction contract

| Field | Value |
|---|---|
| Colab runtime / Python | Python 3.13.15 — `Linux-6.6.122+-x86_64-with-glibc2.39` |
| Device / provider | `cpu` / `CPUExecutionProvider` |
| Runtime doctor (notebook 00) | device=⏳ PENDING_RUN, GPU=⏳ PENDING_RUN, in_colab=⏳ PENDING_RUN |
| Library versions | torch 2.11.0+cpu · onnx 1.22.0 · onnxruntime 1.29.0 (pinned in `requirements-day4.txt`) |
| Model ID / revision / hash | `distilbert/distilbert-base-multilingual-cased` fine-tuned in notebook 03 (partial_finetune_cpu, epoch 9); state SHA-256 `7ce92da659de7da5…` |
| Trained from repository commit | `5d83b7de5efb` |
| Preprocessing version | `bayan-prep/1.0.0` (training = serving) |
| Label map version | digital_service, health, permit, transport (saved with the checkpoint config) |
| Workload path / hash | validation split of `data/sample/bayan_day2_classification.csv`، SHA-256 `9b07010d0e607282…` |
| Split | validation (candidate selection); frozen test not used here |
| Examples + AR/EN counts | 8 rows · languages ar, en |
| Length distribution | p50 11.0 · p95 14.649999999999999 · max 15 tokens; would truncate: 0 |
| Batch size | 4 |
| Padding / max length | dynamic padding per batch / `MAX_LENGTH=16` (measured, D-002) |
| Warm-up / repetitions | 5 / 30 |
| Measured boundary | `model_only_primary_and_pytorch_end_to_end_secondary` |
| Memory method | process RSS start and observed peak; approximate |

## 4. Controlled candidates

| ID | Runtime/precision | Only intended change | Artefact hash | Size MiB |
|---|---|---|---|---:|
| A | PyTorch FP32 reference | baseline | `7ce92da659de` | 516.2 |
| B | ONNX Runtime FP32 | runtime/export | `6cbf2dabbdd2` | 516.3 |
| C | ONNX Runtime dynamic INT8 | weight quantisation | `fc1d2eef8c58` | 129.4 |

INT8 status: available = True; error = —

## 5. Parity

| Comparison | max abs logits diff | mean abs diff | prediction agreement | Verdict |
|---|---:|---:|---:|---|
| A vs B | 2.1457672119140625e-06 | 7.185153663158417e-07 | 100% | PASS |
| A vs C | 1.3766056299209595 | 0.33087921142578125 | 50% | reported; INT8 is judged by quality tax, not bit-parity |

- **Tolerance chosen before inspection:** FP32: `max abs logits diff < 1e-3` و`prediction agreement = 1.0` (assertions في الدفتر). INT8: لا أطلب تطابق الـlogits، وأحكم عليه بأثر الجودة ≤ 0.02.
- **Rationale:** ONNX FP32 يجب أن يكون الحساب نفسه تقريبًا (فروق float فقط). أما INT8 فيغيّر الأوزان عمدًا، فالمهم أثره على Macro-F1.

## 6. Performance results (model-only, per workload call)

| ID | p50 ms | p95 ms | p99 ms | items/s | observed peak RSS MiB | speedup vs A (p95) |
|---|---:|---:|---:|---:|---:|---:|
| A | 230.48 | 366.95 | 375.12 | 31.6 | 1184.0 | 1.00× |
| B | 184.54 | 277.37 | 283.52 | 39.7 | 2324.2 | 1.32× |
| C | 179.02 | 188.85 | 197.31 | 47.3 | 2417.2 | — |

PyTorch end-to-end (tokenisation + model): p95 362.37 ms، 31.3 items/s.

## 7. Quality results

- Primary task metric: `macro_f1_validation_full_workload` (macro-F1 on the full validation workload, same examples for every candidate)
- Evaluation file/split: validation workload (n=8)

| ID | Task quality | Quality tax = A − candidate | Small-sample/CI note |
|---|---:|---:|---|
| A | 1.000 | 0 | n=8: خطأ واحد يغيّر Macro-F1 كثيرًا |
| B | 1.000 | 0.000 | الأمثلة نفسها |
| C | 0.435 | 0.565 | الأمثلة نفسها |

## 8. Budget verdict and decision

| Candidate | latency OK | throughput OK | quality OK | Overall |
|---|---|---|---|---|
| B | ❌ | ✅ | ✅ | ❌ |
| C | ❌ | ✅ | ❌ | ❌ |

- Selected runtime: `pytorch-fp32`
- Decision: **KEEP_PYTORCH_FP32**
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
- [x] Numbers are `MEASURED`, not copied references.
- [x] No weights, ONNX artefacts, cache, secrets, or PII committed (`.gitignore` + privacy scan in `scripts/collect_results.py`).
