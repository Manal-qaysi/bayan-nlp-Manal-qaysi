# DECISIONS — Bayan

> يُولَّد من `docs_src/DECISIONS.md.j2`. الأدلة الرقمية منقولة آليًا من مخرجات الدفاتر، والمصدر لكل قرار مذكور. القيمة المعلّمة بـ ⏳ تعني أن الدفتر المسؤول لم يُشغَّل بعد.
>
> **Owner:** Manal Qaysi · **Last rendered:** 2026-09-30 13:16 UTC

## Decision D-001 — Dataset split and leakage control

* **Date:** 2026-09-29 · **Gate:** A — Data and evaluation · **Status:** accepted · **Owner:** Manal Qaysi

### Context | السياق
مجموعة التصنيف ثنائية اللغة، وكثير من أمثلتها أزواج عربي/إنجليزي لنفس الحالة. إذا وقع طرفا الزوج في split مختلفين يحصل تسرّب.

### Options considered | البدائل
| Option | Benefit | Cost/risk | Evidence |
|---|---|---|---|
| A — Group-isolated fixed split | يمنع عبور الأزواج بين train/validation/test | أمثلة أقل استقلالًا | `group_overlap = 0`، `20` مجموعة |
| B — Row-level random split | سهل | تسرّب محتمل بين الأزواج | لم يُختر |

### Decision | القرار
أستخدم التقسيم المجمّد المعزول بالمجموعات: {'test': 8, 'train': 24, 'validation': 8}. لا أفتح test إلا بعد تثبيت الإعدادات على validation.

### Evidence | الدليل
* [دفتر 03](notebooks/03_text_classification.ipynb) → [`reports/nb03_classification.json`](reports/nb03_classification.json) (`split_report`) · data SHA-256 `c50de92fdab1aa36…`

### Consequences and rollback
* الأثر: تقييم منضبط. القيد: test فيه 8 أمثلة فقط، فعدم اليقين كبير.
* الرجوع: عند اكتشاف تسرّب أعيد بناء التقسيم من البيانات بإصدار جديد، وأسجّل data hash جديدًا.

---

## Decision D-002 — Tokenizer and maximum sequence length

* **Date:** 2026-09-30 · **Gate:** A — Text preparation · **Status:** accepted · **Owner:** Manal Qaysi

### Context | السياق
التقييم السابق خصم لأن `MAX_LENGTH = 64` كانت بلا قياس. الآن أقيس أطوال الرموز الفعلية لكل لغة بمرمّزين قبل الاختيار.

### Evidence table | الدليل المقاس ([دفتر 01](notebooks/01_text_processing_tokenization.ipynb))
| Tokenizer | Lang | n | fertility (tokens/word) | p95 tokens | max tokens | trunc@16 | trunc@32 | trunc@64 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| mbert | ar | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |
| mbert | en | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |
| distilmbert | ar | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |
| distilmbert | en | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN | ⏳ PENDING_RUN |

- QA (سؤال + سياق): أطول زوج = ⏳ PENDING_RUN رمزًا، ونسبة القطع عند 96 = ⏳ PENDING_RUN.
- في [دفتر 03](notebooks/03_text_classification.ipynb) أعدت القياس على train+validation بمرمّز النموذج نفسه، فكانت p95 = 15.0 والأقصى = 16.

### Options considered | البدائل
| Option | Benefit | Cost/risk |
|---|---|---|
| A — أصغر طول مرشح بلا قطع (قاعدة مقاسة) | لا يُفقد نص، وحشو أقل، وزمن أقل | النصوص الأطول مستقبلًا قد تُقطع؛ لذلك أعيد القياس عند تغيّر البيانات |
| B — 64 ثابتة | بسيطة | بلا دليل، وحشو زائد |
| C — بلا حد | لا قطع أبدًا | ذاكرة وزمن غير محدودين |

### Decision | القرار
- المرمّز: `distilbert/distilbert-base-multilingual-cased` (مطابق للنموذج).
- `MAX_LENGTH = 16` للتصنيف (smallest candidate with truncation <= 0.0)، وقد اقترح دفتر 01 القيمة ⏳ PENDING_RUN على كل نصوص المشروع. تُستخدم القيمة نفسها في الخدمة (08) عبر `bayan_training_meta.json`.
- QA: أُبقي `max_length=96` لأن القطع عندها ⏳ PENDING_RUN.

### Consequences and rollback
* الفحص يتكرر آليًا في 03 عند كل تشغيل. إذا ظهر قطع في بيانات جديدة ينتقل الاختيار إلى المرشح التالي.
* الرجوع: أعيد القيمة السابقة في `CANDIDATE_LENGTHS` وأعيد التدريب والتقييم.

---

## Decision D-003 — Arabic preprocessing profile

* **Date:** 2026-09-30 · **Gate:** A/C — Data preparation · **Status:** accepted · **Owner:** Manal Qaysi

### Context | السياق
المعالجة العدوانية قد تدمج كلمات مختلفة في المعنى، أما البحث فيستفيد من توحيد الأشكال.

### Options considered | البدائل
| Option | Use | Rules | Evidence |
|---|---|---|---|
| A — `bayan-prep/1.0.0` محافظ | نسخة النموذج في التصنيف والخدمة | NFC، إزالة التطويل، حجب البريد والجوال، توحيد المسافات؛ ويُحفظ التشكيل والألف والياء | idempotent: ⏳ PENDING_RUN؛ غيّر ⏳ PENDING_RUN نصًا من ⏳ PENDING_RUN |
| B — CAMeL `search` ⏳ PENDING_RUN | البحث الدلالي (corpus وquery) | ما سبق + إزالة التشكيل + توحيد الألف والألف المقصورة؛ وتبقى التاء المربوطة | الاختبارات الذهبية: ⏳ PENDING_RUN ناجحة ([دفتر 05](notebooks/05_arabic_nlp.ipynb)) + [`tests/test_my_arabic_golden.py`](tests/test_my_arabic_golden.py) |
| C — توحيد التاء المربوطة إلى هاء | — | — | مرفوض: يدمج «حالة/حاله» ويغيّر المعنى |

### Tokenizer evidence per variant ([دفتر 05](notebooks/05_arabic_nlp.ipynb))
| Tokenizer | Slice | fertility | max tokens |
|---|---|---:|---:|

### Decision | القرار
أستخدم A لنسخة النموذج، وB للبحث فقط، ويُطبَّق B على corpus وquery معًا. Arabizi يبقى في مسار مستقل بلا تحويل (المرشحون: ⏳ PENDING_RUN).

### Consequences and rollback
* نسخة العرض لا تتغير أبدًا. أي تغيير في القواعد يرفع الإصدار ويُعاد بسببه بناء الفهرس.
* الرجوع: أعيد الإصدار السابق وأعيد تشغيل الاختبارات الذهبية والتقييم.

---

## Decision D-004 — Task models, baselines and training

* **Date:** 2026-09-30 · **Gate:** B — Model quality · **Status:** accepted · **Owner:** Manal Qaysi

### Evidence | الدليل (frozen test، `MEASURED_SMOKE`)
| Head | Baseline (TF-IDF char + LinearSVC) | Transformer (DistilmBERT) | Training |
|---|---:|---:|---|
| topic Macro-F1 | 0.733 | 0.867 | partial_finetune_cpu، epoch 9 |
| sentiment Macro-F1 (observed labels) | 1.000 | 0.356 | epoch 6، 72 خطوة |
| NER strict entity F1 (test) | — | ⏳ PENDING_RUN | ⏳ PENDING_RUN خطوة |
| QA EM / F1 (test) | — | ⏳ PENDING_RUN / ⏳ PENDING_RUN | ⏳ PENDING_RUN خطوة |

### Decisions | القرارات
- **رأسان مستقلان** لـtopic وsentiment، لكل منهما label map خاصة، على التقسيم نفسه. أحتفظ بالـbaseline مرجعًا دائمًا.
- **NER:** يأخذ أول subword وسم الكلمة، وتأخذ الاستمرارات والرموز الخاصة `-100`. التقييم صارم على مستوى الكيان ولكل نوع.
- **QA:** رفعت خطوات التدريب من 1–3 إلى 20 كي يكون لـEM/F1 معنى. **سياسة عدم الإجابة:** أمتنع إذا كان `null_score − best_span_score > ⏳ PENDING_RUN` (⏳ PENDING_RUN).
- **قيد:** في sentiment تنقص validation فئة `positive` وتنقص test فئة `neutral`، لذلك يُحسب Macro-F1 على الفئات الملاحظة فقط.

### Consequences and rollback
* الرجوع: إذا لم يحقق Transformer الجودة أو الميزانية، أخدم الـbaseline وأسجّل ذلك قرارًا جديدًا.

---

## Decision D-005 — Semantic encoder, index, k and no-answer threshold

* **Date:** 2026-09-30 · **Gate:** C — Search · **Status:** accepted · **Owner:** Manal Qaysi

| Field | Value | Evidence |
|---|---|---|
| Encoder | `⏳ PENDING_RUN` (dim ⏳ PENDING_RUN) | [`reports/nb06_retrieval.json`](reports/nb06_retrieval.json) |
| Normalisation / index | L2 + `⏳ PENDING_RUN` (⏳ PENDING_RUN vectors) | manifest |
| k | ⏳ PENDING_RUN | — |
| No-answer threshold | ⏳ PENDING_RUN (validation فقط؛ دقتها ⏳ PENDING_RUN) | test: ⏳ PENDING_RUN |
| Re-ranker | `⏳ PENDING_RUN`: MRR@3 ⏳ PENDING_RUN → ⏳ PENDING_RUN، وp95 ⏳ PENDING_RUN ms | **⏳ PENDING_RUN** |

الرجوع: أي تغيير في النموذج أو الـprofile أو البيانات يستلزم إعادة بناء الفهرس، لأن الـmanifest يربطها معًا.

---

## Decision D-006 — Metrics, slices and error priorities

* **Date:** 2026-09-30 · **Gate:** C — Evaluation · **Status:** accepted · **Owner:** Manal Qaysi

- **المقاييس:** Macro-F1 للتصنيف (يعطي الفئات وزنًا متساويًا)، وstrict entity F1 لـNER، وEM/F1 ودقة عدم الإجابة لـQA، وRecall@3/MRR@3 ودقة no-answer للبحث.
- **عدم اليقين:** 95% bootstrap CI (2000 إعادة)، ومقارنة زوجية. لا أدّعي اتجاهًا ما لم تستبعد الفترة الصفر. Topic: الفرق ⏳ PENDING_RUN، والفترة [⏳ PENDING_RUN, ⏳ PENDING_RUN].
- **الشرائح:** اللغة (ar/en). أي شريحة n<10 تُوسم `SMALL_SLICE`.
- **أولويات الإصلاح** (من تصنيف أخطاء نماذجي في [دفتر 07](notebooks/07_evaluation_error_analysis.ipynb)، ومراجعته اليدوية: ⏳ PENDING_RUN):

---

## Decision D-007 — Performance budget

* **Date:** 2026-09-30 · **Gate:** D — Serving performance · **Status:** accepted (written **before** measuring project candidates) · **Owner:** Manal Qaysi

| Constraint | TARGET |
|---|---:|
| p95 model-only latency per workload call (8 validation texts, batch 4) | ≤ 100 ms |
| minimum throughput | ≥ 20 items/s |
| maximum quality tax (validation Macro-F1) | ≤ 0.02 |
| target device | Colab CPU, `CPUExecutionProvider` |

* **Provenance:** كُتبت هذه القيم في `BENCHMARKS.md` §2 وفي خلية الإعداد في دفتر 08، ورُفعت في commit قبل أول تشغيل لـ`PROJECT_MODE`. في الدفتر: `BUDGET_PROVENANCE = STUDENT_DEFINED_BEFORE_MEASUREMENT`.
* الرجوع: إذا لم يحقق أي مرشح الميزانية، أحتفظ بمرجع PyTorch FP32.

---

## Decision D-008 — ONNX / INT8 runtime adoption

* **Date:** 2026-09-30 · **Gate:** D — Runtime optimisation · **Status:** accepted · **Owner:** Manal Qaysi

| Candidate | p95 ms | items/s | parity (max abs Δ / agreement) | quality tax | budget met |
|---|---:|---:|---|---:|---|
| A — PyTorch FP32 | 366.95 | 31.6 | reference | 0 | reference |
| B — ONNX Runtime FP32 | 277.37 | 39.7 | 2.1457672119140625e-06 / 100% | 0.000 | ❌ |
| C — ONNX dynamic INT8 | 188.85 | 47.3 | 1.3766056299209595 / 50% | 0.565 | ❌ |

* **Decision:** **KEEP_PYTORCH_FP32**، أي أن الخدمة تعمل بـ`pytorch-fp32`. القاعدة مطبّقة آليًا في دفتر 08: INT8 إن حقق الميزانية كاملة، وإلا ONNX FP32 إن حققها، وإلا PyTorch FP32.
* **Rollback:** أعيد التصدير من artefact دفتر 03 المسجَّل (hash الحالة `7ce92da659de7da5…`). الأوزان وملفات ONNX تبقى خارج GitHub.

---

## Decision D-009 — Served artefact, preprocessing and label versions

* **Date:** 2026-09-30 · **Gate:** D — Ship · **Status:** accepted · **Owner:** Manal Qaysi

| Field | Value |
|---|---|
| model | `bayan-topic-distilmbert (notebook 03 artefact)` / `project-v1` |
| runtime | `pytorch-fp32` |
| preprocessing | `bayan-prep/1.0.0` (نفسه في التدريب، دفتر 03) |
| label map | {'0': 'digital_service', '1': 'health', '2': 'permit', '3': 'transport'} |
| artefact SHA-256 | `7ce92da659de7da567bd6770…` |
| canaries | مثالان من train بوسميهما الحقيقيين (لا يولّدهما النموذج بنفسه) |

---

## Decision D-010 — Measured extension: hybrid sparse + dense retrieval (RRF)

* **Date:** 2026-09-30 · **Gate:** T7 — Extension · **Status:** ⏳ PENDING_RUN · **Owner:** Manal Qaysi

* **Rule written before measuring:** أعتمده إذا تحققت ثلاثة شروط: ربح في MRR@3 على validation ≥ 0.05، وعدم انخفاض Recall@3 عبر اللغات، وزمن وسيط إضافي ≤ 5 ms.
* **Measured:** الربح ⏳ PENDING_RUN؛ عدم انخفاض Recall@3 عبر اللغات: ⏳ PENDING_RUN؛ الزمن الإضافي ⏳ PENDING_RUN ms. → **⏳ PENDING_RUN**.
* **Evidence:** [`reports/nb06_extension.json`](reports/nb06_extension.json).
* **Rollback:** الـbaseline (dense فقط) هو الافتراضي، والامتداد لا يغيّر الفهرس ولا العتبة.

---

## قرارات إلزامية قبل Gate E

- [x] tokenizer + max length — D-002
- [x] Arabic preprocessing profile — D-003
- [x] task model/baseline and split — D-001، D-004
- [x] semantic encoder/index/k/threshold — D-005
- [x] metric/slices/error priorities — D-006
- [x] performance budget — D-007
- [x] ONNX/INT8 adopt or reject — D-008
- [x] served artefact + preprocessing/label versions — D-009
