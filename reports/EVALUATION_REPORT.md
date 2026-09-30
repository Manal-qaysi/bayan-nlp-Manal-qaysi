# تقرير تقييم بيان | Bayan Evaluation Report

> يُولَّد من `docs_src/EVALUATION_REPORT.md.j2`. كل رقم منقول آليًا من مخرجات دفاتري المنفّذة. مصدر كل نتيجة (الدفتر والخلية والـcommit) موجود في [`reports/results_index.json`](reports/results_index.json).

## 1. نطاق التقرير

* تاريخ آخر توليد: `2026-09-30 14:29 UTC`
* commit SHA الذي شُغّلت منه الدفاتر (قيمة `repo_sha` المسجّلة داخل كل دفتر):
  * `00_runtime_doctor.ipynb` → run from `8fabb2a6026a`، وحُفظ في commit `898a347f5b50` (2026-09-30)
  * `01_text_processing_tokenization.ipynb` → run from `d37d08f8c2d7`، وحُفظ في commit `a6b51e3094ea` (2026-09-30)
  * `02_attention_transformers.ipynb` → run from `e7c5eb2da458`، وحُفظ في commit `7df70d391bb0` (2026-09-30)
  * `03_text_classification.ipynb` → run from `4f460cf65d41`، وحُفظ في commit `d1c65338bfbd` (2026-09-30)
  * `04_ner_and_qa.ipynb` → run from `d54ae98a11ca`، وحُفظ في commit `4e36e896d0b7` (2026-09-30)
  * `05_arabic_nlp.ipynb` → run from `2421d4194582`، وحُفظ في commit `97ffb56fece9` (2026-09-30)
  * `06_semantic_search.ipynb` → run from `7df70d391bb0`، وحُفظ في commit `03e1f481cd6c` (2026-09-30)
  * `07_evaluation_error_analysis.ipynb` → run from `03e1f481cd6c`، وحُفظ في commit `d37d08f8c2d7` (2026-09-30)
  * `08_optimization_serving.ipynb` → run from `76720f008555`، وحُفظ في commit `51ce661e3408` (2026-09-30)
* runtime/device: Python 3.13.15 / `cpu` (GPU: —)
* data version/hash (SHA-256، أول 16 خانة):
  * `data/sample/bayan_day1_sample.csv` — `904a5e1e860f23ac`
  * `data/sample/bayan_day2_classification.csv` — `c50de92fdab1aa36`
  * `data/sample/bayan_day2_ner.jsonl` — `ab413f0941656abf`
  * `data/sample/bayan_day2_qa.json` — `4e894757b74d09df`
  * `data/sample/bayan_day3_arabic.csv` — `0a3346b6177d0c0b`
  * `data/sample/bayan_day3_cases.csv` — `322867b54d1f6f35`
  * `data/sample/bayan_day3_predictions.csv` — `63b4df9dab076880`
  * `data/sample/bayan_day3_queries.jsonl` — `f80ebd8b25c37b33`
* preprocessing profile/version/backend: `bayan-prep/1.0.0` (نسخة النموذج، Python) · `search 1.0.0` بـ`camel-tools==1.6.0` (البحث)
* model/checkpoint IDs: TF-IDF char_wb + LinearSVC (baseline) · `distilbert/distilbert-base-multilingual-cased` (topic, sentiment, NER, QA) · `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` + `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (search)
* نوع الأرقام: `MEASURED_SMOKE` — قياس فعلي من تشغيلي، على عينات الدورة الاصطناعية الصغيرة.

## 2. العقود قبل القياس

| العقد | الدليل | الحالة |
|---|---|---|
| لا PII حقيقية | البيانات اصطناعية، وحجب البريد والجوال في `bayan-prep/1.0.0`، وفحص الخصوصية الآلي في `scripts/collect_results.py` | PASS |
| train/validation/test بلا leakage | `group_overlap = 0` · {'test': 8, 'train': 24, 'validation': 8} | PASS |
| tokenizer/model متطابقان | مرمّز DistilmBERT مع نموذجه؛ `MAX_LENGTH=16` مقاسة (D-002) | PASS |
| Arabic profile متطابقة في train/index/query/serve | `bayan-prep/1.0.0` في 03 و08؛ و`search` على corpus وquery في 06 | PASS |
| corpus/query embeddings مطبّعة L2 | assertions في دفتر 06، و`normalization = l2` | PASS |
| frozen test لم يُستخدم في tuning | الحقبة والعتبات من validation فقط؛ وtest يُقرأ مرة واحدة | PASS |

## 3. نتائج المهام (frozen test)

| المهمة | المقياس الرئيس | النتيجة | 95% CI (bootstrap 2000) | مجموعة القياس |
|---|---|---:|---|---|
| Topic — Transformer | Macro-F1 | 0.867 | [0.523, 1.000] | test, n=8 |
| Topic — baseline | Macro-F1 | 0.733 | [0.314, 1.000] | test, n=8 |
| Sentiment — Transformer | Macro-F1 (observed labels) | 0.356 | [0.095, 0.733] | test, n=8 |
| Sentiment — baseline | Macro-F1 (observed labels) | 1.000 | [1.000, 1.000] | test, n=8 |
| NER | strict entity F1 (P / R) | 0.571 (0.667 / 0.500) | n صغير جدًا؛ لا CI | test: 4 gold entities |
| QA | EM / F1 | 0.000 / 0.000 | n صغير جدًا؛ لا CI | test, n=2 |
| QA no-answer | accuracy | 0.000 | — | 2 unanswerable |
| Retrieval (dense) | Recall@3 | 1.000 | [1.000, 1.000] | test, 6 answerable |
| Retrieval (dense) | MRR@3 | 0.667 | [0.500, 0.833] | test, 6 answerable |
| Retrieval no-answer | accuracy (frozen threshold) | 1.000 | — | test |

**NER per entity type (test):**

| Type | P | R | F1 | support |
|---|---:|---:|---:|---:|
| DATE | 0.000 | 0.000 | 0.000 | 1 |
| LOCATION | 1.000 | 1.000 | 1.000 | 1 |
| ORG | 0.000 | 0.000 | 0.000 | 1 |
| SERVICE | 0.500 | 1.000 | 0.667 | 1 |

## 4. شرائح التقييم

| المهمة | الشريحة | n | Macro-F1 | 95% CI | التحذير/التفسير |
|---|---|--:|---:|---|---|
| topic | `ALL` | 8 | 0.867 | [0.500, 1.000] | SMALL_SLICE |
| topic | `language=ar` | 4 | 0.667 | [0.333, 1.000] | SMALL_SLICE |
| topic | `language=en` | 4 | 1.000 | [1.000, 1.000] | SMALL_SLICE |
| sentiment | `ALL` | 8 | 0.356 | [0.095, 0.733] | SMALL_SLICE |
| sentiment | `language=ar` | 4 | 0.167 | [0.000, 0.429] | SMALL_SLICE |
| sentiment | `language=en` | 4 | 0.600 | [0.200, 1.000] | SMALL_SLICE |
| retrieval | `language=ar` | 3 | MRR@3 0.500 · R@3 1.000 | — | SMALL_SLICE |
| retrieval | `language=en` | 3 | MRR@3 0.833 · R@3 1.000 | — | SMALL_SLICE |
| retrieval | `retrieval_mode=cross_lingual` | 2 | MRR@3 0.500 · R@3 1.000 | — | SMALL_SLICE |
| retrieval | `retrieval_mode=monolingual` | 4 | MRR@3 0.750 · R@3 1.000 | — | SMALL_SLICE |
| classification | `variant=Gulf` (topic, dialect comparison, notebook 05) | 4 | DistilmBERT 0.000 · CAMeLBERT-DA 0.667 | — | 4 أمثلة فقط؛ وصفي |

كل الشرائح صغيرة جدًا (`SMALL_SLICE` تعني n<10). الفترات تبيّن أن الفرق بين العربية والإنجليزية لا يمكن الحكم عليه من هذه العينة.

## 5. مقارنة الإصدارات

* Model A: `TF-IDF char_wb (3–5) + LinearSVC`
* Model B: `distilbert/distilbert-base-multilingual-cased` (partial_finetune_cpu)
* observed difference B−A (topic, test): **+0.133** Macro-F1
* paired 95% CI: [-0.386, +0.675] — directional claim supported: **❌**
* sentiment B−A: -0.644 [-0.905, -0.267]
* القرار المهني: إذا شملت الفترة الزوجية الصفر، لا أقول إن أحد النموذجين أفضل؛ أقول إن العينة (n=8) لا تدعم ادعاءً اتجاهيًا. أحتفظ بالـbaseline مرجعًا ومسار رجوع.

## 6. Behavioural tests

| النوع | passed/total | pass rate | فشل مهم |
|---|---:|---:|---|
| invariance (all perturbations, topic head) | 52/56 | 93% | انظري التفصيل أدناه |
| invariance — `diacritic` | 6/8 | 75% | يتغير التنبؤ مع تغيير شكلي |
| invariance — `double_spaces` | 16/16 | 100% | — |
| invariance — `lowercase` | 8/8 | 100% | — |
| invariance — `tatweel` | 8/8 | 100% | — |
| invariance — `trailing_punctuation` | 14/16 | 88% | يتغير التنبؤ مع تغيير شكلي |
| directional (no-answer must abstain: QA test) | 2 cases | 0% | النموذج يجيب عن أسئلة لا إجابة لها |
| minimum functionality (service) | AR 200 · EN 200 · empty 422 · unsupported language 422 · too long 422 | 100% | — |

## 7. تحليل الأخطاء

* المصدر: أخطاء **validation** الفعلية من كل المهام.
* عدد الأخطاء المقروءة يدويًا: `6` — تمت المراجعة اليدوية للتصنيف: **❌**
* رابط worksheet داخل المستودع: [`reports/nb07_evaluation.json`](reports/nb07_evaluation.json) (`errors`)، وخلية «✍️ مراجعتي اليدوية» في [دفتر 07](notebooks/07_evaluation_error_analysis.ipynb).

| taxonomy tag | count | أمثلة (IDs) | مثال آمن مختصر | المهام |
|---|---:|---|---|---|
| `class_confusion` | 3 | D-027:sentiment, D-037:sentiment, D-038:sentiment | أين أجد نتيجة الموعد الطبي | sentiment_classification |
| `entity_boundary` | 3 | NER-val-0, Q-007, Q-008 | Case BAYAN-302 belongs to the transport service | ner, qa |

**الأخطاء نفسها:**

| split | task | id | text | gold → prediction | tag | why |
|---|---|---|---|---|---|---|
| validation | sentiment_classification | D-027:sentiment | أين أجد نتيجة الموعد الطبي | neutral → negative | `class_confusion` | neutral predicted as negative |
| validation | sentiment_classification | D-037:sentiment | تغير وقت وصول الحافلة | neutral → negative | `class_confusion` | neutral predicted as negative |
| validation | sentiment_classification | D-038:sentiment | The bus arrival time has changed | neutral → negative | `class_confusion` | neutral predicted as negative |
| validation | ner | NER-val-0 | Case BAYAN-302 belongs to the transport service | O B-REF_NUM O O O B-SERVICE I-SERVICE → O B-REF_NUM O O O O O | `entity_boundary` | gold and predicted BIO spans differ (strict match) |
| validation | qa | Q-007 | كيف يمكن تقديم بلاغ النقل؟ | عبر التطبيق أو مركز الاتصال → بلاغ النقل عبر التطبيق | `entity_boundary` | extracted span boundaries differ from the gold answer |
| validation | qa | Q-008 | Which file format is required? | PDF → it documents must be uploaded | `entity_boundary` | extracted span boundaries differ from the gold answer |

## 8. الإصلاحات الثلاثة ذات الأولوية

| الأولوية | الفئة | الدليل | الإجراء | metric/slice المتوقع | الكلفة | اختبار عدم الرجوع |
|---:|---|---|---|---|---|---|
| 1 | `class_confusion` | 3 observed: D-027:sentiment, D-037:sentiment, D-038:sentiment | إضافة أمثلة contrastive للزوج المختلط ومراجعة دليل التسميات | macro-F1 للفئتين المختلطتين | منخفضة | paired bootstrap دون تراجع في بقية الشرائح |
| 2 | `entity_boundary` | 3 observed: NER-val-0, Q-007, Q-008 | توسيع أمثلة الكيانات متعددة الكلمات ومراجعة محاذاة I- للكلمات اللاحقة | strict entity F1 لكل نوع | متوسطة | اختبار حدود الكيان في tests/ |
| 3 | `dialect_gap` | not observed in this run; known risk from slices/data card | إضافة أمثلة خليجية مراجَعة لكل فئة في train (≥5 لكل فئة) وإعادة التدريب | Gulf-slice macro-F1 (دفتر 05) + شريحة language=ar | متوسطة | حالات خليجية ثابتة في behavioural tests + عدم انخفاض MSA |

## 9. ما الذي لا تثبته النتائج؟

* حجم test صغير جدًا (n=8 للتصنيف)، والفترات واسعة، فلا تعميم على بيانات إنتاجية.
* البيانات اصطناعية تعليمية، ولا تمثل تنوع النصوص الواقعية.
* الخليجية ممثلة بأمثلة قليلة، واللهجات الأخرى وArabizi غير مقاسة.
* في sentiment تنقص validation فئة `positive` وتنقص test فئة `neutral`، فالمقياس لا يغطي كل الفئات في كل split.
* NER وQA قيسا على عدد قليل جدًا من الجمل. EM/F1 هنا تدل على سلامة المسار لا على جودة عامة.
* قياسات الزمن من Colab CPU مشترك، وتختلف بين الجلسات.
* بذرة واحدة فقط (42)، ولا توجد تقديرات من تشغيلات متكررة.

## 10. خلاصة للإدارة

على test المجمّد (8 أمثلة) حقق رأس الموضوع في DistilmBERT Macro-F1 = 0.867 [0.523, 1.000] مقابل 0.733 [0.314, 1.000] للـbaseline، والفرق الزوجي +0.133 (لا يدعم ادعاءً اتجاهيًا). أكثر فئات الخطأ تكرارًا: `class_confusion`، والإصلاح الأول: إضافة أمثلة contrastive للزوج المختلط ومراجعة دليل التسميات. الخدمة تعمل بـ`pytorch-fp32` وفق ميزانية مكتوبة مسبقًا (انظري [`BENCHMARKS.md`](BENCHMARKS.md)). النظام مناسب للتعلم والعرض، ولا يصلح لاتخاذ قرارات عن أشخاص.
