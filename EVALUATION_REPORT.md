# تقرير تقييم بيان | Bayan Evaluation Report

> يُولَّد من `docs_src/EVALUATION_REPORT.md.j2`. كل رقم منقول آليًا من مخرجات دفاتري المنفّذة. مصدر كل نتيجة (الدفتر والخلية والـcommit) موجود في [`reports/results_index.json`](reports/results_index.json).

## 1. نطاق التقرير

* تاريخ آخر توليد: `2026-09-30 13:16 UTC`
* commit SHA الذي شُغّلت منه الدفاتر (قيمة `repo_sha` المسجّلة داخل كل دفتر):
  * `00_runtime_doctor.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `01_text_processing_tokenization.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `02_attention_transformers.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `03_text_classification.ipynb` → run from `5d83b7de5efb`، وحُفظ في commit `76720f008555` (2026-09-30)
  * `04_ner_and_qa.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `05_arabic_nlp.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `06_semantic_search.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `07_evaluation_error_analysis.ipynb` → run from `⏳ PENDING_RUN`، وحُفظ في commit `5d83b7de5efb` (2026-09-30)
  * `08_optimization_serving.ipynb` → run from `76720f008555`، وحُفظ في commit `51ce661e3408` (2026-09-30)
* runtime/device: Python ⏳ PENDING_RUN / `⏳ PENDING_RUN` (GPU: ⏳ PENDING_RUN)
* data version/hash (SHA-256، أول 16 خانة):
  * `data/sample/bayan_day1_sample.csv` — `904a5e1e860f23ac`
  * `data/sample/bayan_day2_classification.csv` — `c50de92fdab1aa36`
  * `data/sample/bayan_day2_ner.jsonl` — `ab413f0941656abf`
  * `data/sample/bayan_day2_qa.json` — `4e894757b74d09df`
  * `data/sample/bayan_day3_arabic.csv` — `0a3346b6177d0c0b`
  * `data/sample/bayan_day3_cases.csv` — `322867b54d1f6f35`
  * `data/sample/bayan_day3_predictions.csv` — `63b4df9dab076880`
  * `data/sample/bayan_day3_queries.jsonl` — `f80ebd8b25c37b33`
* preprocessing profile/version/backend: `bayan-prep/1.0.0` (نسخة النموذج، Python) · `search ⏳ PENDING_RUN` بـ`⏳ PENDING_RUN` (البحث)
* model/checkpoint IDs: TF-IDF char_wb + LinearSVC (baseline) · `distilbert/distilbert-base-multilingual-cased` (topic, sentiment, NER, QA) · `⏳ PENDING_RUN` + `⏳ PENDING_RUN` (search)
* نوع الأرقام: `MEASURED_SMOKE` — قياس فعلي من تشغيلي، على عينات الدورة الاصطناعية الصغيرة.

## 2. العقود قبل القياس

| العقد | الدليل | الحالة |
|---|---|---|
| لا PII حقيقية | البيانات اصطناعية، وحجب البريد والجوال في `bayan-prep/1.0.0`، وفحص الخصوصية الآلي في `scripts/collect_results.py` | PASS |
| train/validation/test بلا leakage | `group_overlap = 0` · {'test': 8, 'train': 24, 'validation': 8} | PASS |
| tokenizer/model متطابقان | مرمّز DistilmBERT مع نموذجه؛ `MAX_LENGTH=16` مقاسة (D-002) | PASS |
| Arabic profile متطابقة في train/index/query/serve | `bayan-prep/1.0.0` في 03 و08؛ و`search` على corpus وquery في 06 | ⏳ PENDING_RUN |
| corpus/query embeddings مطبّعة L2 | assertions في دفتر 06، و`normalization = ⏳ PENDING_RUN` | ⏳ PENDING_RUN |
| frozen test لم يُستخدم في tuning | الحقبة والعتبات من validation فقط؛ وtest يُقرأ مرة واحدة | PASS |

## 3. نتائج المهام (frozen test)

| المهمة | المقياس الرئيس | النتيجة | 95% CI (bootstrap 2000) | مجموعة القياس |
|---|---|---:|---|---|
| Topic — Transformer | Macro-F1 | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, n=⏳ PENDING_RUN |
| Topic — baseline | Macro-F1 | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, n=⏳ PENDING_RUN |
| Sentiment — Transformer | Macro-F1 (observed labels) | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, n=⏳ PENDING_RUN |
| Sentiment — baseline | Macro-F1 (observed labels) | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, n=⏳ PENDING_RUN |
| NER | strict entity F1 (P / R) | ⏳ PENDING_RUN (⏳ PENDING_RUN / ⏳ PENDING_RUN) | n صغير جدًا؛ لا CI | test: ⏳ PENDING_RUN gold entities |
| QA | EM / F1 | ⏳ PENDING_RUN / ⏳ PENDING_RUN | n صغير جدًا؛ لا CI | test, n=⏳ PENDING_RUN |
| QA no-answer | accuracy | ⏳ PENDING_RUN | — | ⏳ PENDING_RUN unanswerable |
| Retrieval (dense) | Recall@3 | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, ⏳ PENDING_RUN answerable |
| Retrieval (dense) | MRR@3 | ⏳ PENDING_RUN | [⏳ PENDING_RUN, ⏳ PENDING_RUN] | test, ⏳ PENDING_RUN answerable |
| Retrieval no-answer | accuracy (frozen threshold) | ⏳ PENDING_RUN | — | test |

**NER per entity type (test):**

| Type | P | R | F1 | support |
|---|---:|---:|---:|---:|

## 4. شرائح التقييم

| المهمة | الشريحة | n | Macro-F1 | 95% CI | التحذير/التفسير |
|---|---|--:|---:|---|---|
| classification | `variant=Gulf` (topic, dialect comparison, notebook 05) | ⏳ PENDING_RUN | DistilmBERT ⏳ PENDING_RUN · CAMeLBERT-DA ⏳ PENDING_RUN | — | 4 أمثلة فقط؛ وصفي |

كل الشرائح صغيرة جدًا (`SMALL_SLICE` تعني n<10). الفترات تبيّن أن الفرق بين العربية والإنجليزية لا يمكن الحكم عليه من هذه العينة.

## 5. مقارنة الإصدارات

* Model A: `TF-IDF char_wb (3–5) + LinearSVC`
* Model B: `distilbert/distilbert-base-multilingual-cased` (partial_finetune_cpu)
* observed difference B−A (topic, test): **⏳ PENDING_RUN** Macro-F1
* paired 95% CI: [⏳ PENDING_RUN, ⏳ PENDING_RUN] — directional claim supported: **⏳ PENDING_RUN**
* sentiment B−A: ⏳ PENDING_RUN [⏳ PENDING_RUN, ⏳ PENDING_RUN]
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
| directional (no-answer must abstain: QA test) | ⏳ PENDING_RUN cases | ⏳ PENDING_RUN | — |
| minimum functionality (service) | AR 200 · EN 200 · empty 422 · unsupported language 422 · too long 422 | 100% | — |

## 7. تحليل الأخطاء

* المصدر: أخطاء **validation** الفعلية من كل المهام.
* عدد الأخطاء المقروءة يدويًا: `⏳ PENDING_RUN` — تمت المراجعة اليدوية للتصنيف: **⏳ PENDING_RUN**
* رابط worksheet داخل المستودع: [`reports/nb07_evaluation.json`](reports/nb07_evaluation.json) (`errors`)، وخلية «✍️ مراجعتي اليدوية» في [دفتر 07](notebooks/07_evaluation_error_analysis.ipynb).

| taxonomy tag | count | أمثلة (IDs) | مثال آمن مختصر | المهام |
|---|---:|---|---|---|

**الأخطاء نفسها:**

| split | task | id | text | gold → prediction | tag | why |
|---|---|---|---|---|---|---|

## 8. الإصلاحات الثلاثة ذات الأولوية

| الأولوية | الفئة | الدليل | الإجراء | metric/slice المتوقع | الكلفة | اختبار عدم الرجوع |
|---:|---|---|---|---|---|---|

## 9. ما الذي لا تثبته النتائج؟

* حجم test صغير جدًا (n=8 للتصنيف)، والفترات واسعة، فلا تعميم على بيانات إنتاجية.
* البيانات اصطناعية تعليمية، ولا تمثل تنوع النصوص الواقعية.
* الخليجية ممثلة بأمثلة قليلة، واللهجات الأخرى وArabizi غير مقاسة.
* في sentiment تنقص validation فئة `positive` وتنقص test فئة `neutral`، فالمقياس لا يغطي كل الفئات في كل split.
* NER وQA قيسا على عدد قليل جدًا من الجمل. EM/F1 هنا تدل على سلامة المسار لا على جودة عامة.
* قياسات الزمن من Colab CPU مشترك، وتختلف بين الجلسات.
* بذرة واحدة فقط (42)، ولا توجد تقديرات من تشغيلات متكررة.

## 10. خلاصة للإدارة

على test المجمّد (8 أمثلة) حقق رأس الموضوع في DistilmBERT Macro-F1 = ⏳ PENDING_RUN مقابل ⏳ PENDING_RUN للـbaseline، والفرق الزوجي ⏳ PENDING_RUN (لا يدعم ادعاءً اتجاهيًا). أكثر فئات الخطأ تكرارًا: `⏳ PENDING_RUN`، والإصلاح الأول: ⏳ PENDING_RUN. الخدمة تعمل بـ`pytorch-fp32` وفق ميزانية مكتوبة مسبقًا (انظري [`BENCHMARKS.md`](BENCHMARKS.md)). النظام مناسب للتعلم والعرض، ولا يصلح لاتخاذ قرارات عن أشخاص.
