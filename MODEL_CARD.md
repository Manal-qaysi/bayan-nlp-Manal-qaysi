# بطاقة نموذج بيان | Bayan Model Card

> يُولَّد من `docs_src/MODEL_CARD.md.j2`؛ النتائج من [`reports/`](reports/).

## Model details

* Name/version: `Bayan Topic Classifier v1` (+ Sentiment head v1، وNER وQA heads للتجربة)
* Base checkpoint: `distilbert/distilbert-base-multilingual-cased`
* Task: `Multilingual (AR/EN) topic classification` — 4 labels: digital_service, health, permit, transport
* Training: `partial_finetune_cpu`، seed 42، selected epoch 9، `MAX_LENGTH=16`
* License/source: رخصة base checkpoint كما في [بطاقته](https://huggingface.co/distilbert/distilbert-base-multilingual-cased)؛ والرؤوس مدرّبة في مشروع تعليمي
* Trained from commit: `5d83b7de5efb` · state SHA-256 `7ce92da659de7da5…`
* Served runtime: `pytorch-fp32` (D-008)
* Owner/contact role: Manal Qaysi (`Manal-qaysi`) — Applied NLP trainee

## Intended use

* الاستخدام المقصود: فرز ملاحظات خدمية عربية (فصحى وخليجية) وإنجليزية قصيرة إلى أربعة موضوعات، مع مراجعة بشرية لكل مخرج، لأغراض تعليمية وتجريبية.
* المستخدمون المقصودون: المتدربون والمدربة والمراجعون في سياق الدورة.
* خارج النطاق: الاستخدام الإنتاجي، والقرارات عن أشخاص حقيقيين، والتنميط (profiling)، وأي قرار عالي المخاطر، والنصوص الطويلة، وArabizi، واللهجات غير الخليجية.

## Data and preprocessing

* Dataset ID/version: `data/sample/bayan_day2_classification.csv` — SHA-256 `c50de92fdab1aa36…`
* Languages/variants: Arabic (MSA) + English؛ وقيس الخليجي منفصلًا في دفتر 05
* Split strategy: {'test': 8, 'train': 24, 'validation': 8}، 20 groups، `group_overlap = 0`
* PII policy: بيانات اصطناعية، مع حجب البريد والجوال السعودي في نسخة النموذج. نسخة العرض تبقى كما هي، ولا تُنشر إن احتوت PII
* Preprocessing profile/version/backend: `bayan-prep/1.0.0` (`src/bayan/project.py`، Python)، مطابق في التدريب والخدمة
* Tokenizer/embedding model: مرمّز DistilmBERT نفسه

## Evaluation

| metric/slice | n | result | uncertainty (95% bootstrap) | evidence file |
|---|-:|---:|---|---|
| Topic Macro-F1 — frozen test | ⏳ PENDING_RUN | **⏳ PENDING_RUN** | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) |
| Topic accuracy — frozen test | 8 | 0.875 | — | [`reports/nb03_classification.json`](reports/nb03_classification.json) |
| Sentiment Macro-F1 (observed labels) — test | ⏳ PENDING_RUN | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) |
| Topic Macro-F1 — Gulf test (notebook 05, DistilmBERT) | ⏳ PENDING_RUN | ⏳ PENDING_RUN | 4 أمثلة؛ وصفي | [`reports/nb05_arabic.json`](reports/nb05_arabic.json) |

**Baseline reference:** TF-IDF char_wb + LinearSVC → topic Macro-F1 = ⏳ PENDING_RUN على test نفسه. الفرق الزوجي ⏳ PENDING_RUN، ويدعم ادعاءً اتجاهيًا: ⏳ PENDING_RUN.

## Behavioural checks

| capability | pass rate | known failure |
|---|---:|---|
| Invariance (punctuation, spaces, tatweel, diacritic, lowercase) | 52/56 (93%) | انظري EVALUATION_REPORT §6 |
| Service contract (AR/EN 200؛ empty, unsupported language, >1000 chars → 422) | 5/5 | — |
| Startup canaries (gold labels of two training examples) | 2 PASS | — |

## Limitations and risks

1. test فيه **8 أمثلة** فقط، والفترات واسعة جدًا. النتيجة لا تمثل الأداء الإنتاجي.
2. البيانات اصطناعية تعليمية، والخليجية ممثلة بأمثلة قليلة، وArabizi واللهجات الأخرى غائبة.
3. تدريب قصير ببذرة واحدة، وعلى CPU تُحدَّث آخر طبقة فقط. الأخطاء الأكثر تكرارًا: `⏳ PENDING_RUN` (EVALUATION_REPORT §7).

## Ethical and privacy notes

* البيانات لا تمثل أشخاصًا أو حالات حقيقية.
* حجب PII محدود بالبريد والجوال السعودي، وليس كاشفًا شاملًا.
* لا يُستخدم النموذج لاتخاذ قرار عن شخص أو لتنميطه. كل مخرج يراجعه إنسان.
* الأوزان لا تُنشر في GitHub، وتبقى في Drive خاص.

## Reproduction

1. افتحي [notebook 03](https://colab.research.google.com/github/Manal-qaysi/bayan-nlp-Manal-qaysi/blob/main/notebooks/03_text_classification.ipynb) ثم **Runtime → Restart session and run all** (يحفظ النموذج في `MyDrive/bayan/model-v1`).
2. runtime/device: Colab (`cpu`)، والإصدارات في `requirements-day2.txt`.
3. من commit: `5d83b7de5efb`، البذرة 42.
4. قارني مع: topic test Macro-F1 = 0.867. قد تختلف قليلًا بين GPU وCPU لأن نمط التدريب مختلف.
