# DATA CARD — Bayan

> يُولَّد من `docs_src/DATA_CARD.md.j2`. البصمات محسوبة من ملفات `data/sample/` نفسها.

## Dataset identity

* Name/version: Bayan course sample datasets (8 files، مأخوذة كما هي من مادة الدورة، دون تعديل)
* Source/creator: [bayan-applied-nlp-course](https://github.com/almiyead-rgb/bayan-applied-nlp-course) — `data/sample/` (ميعاد المري)
* License/permission: للاستخدام التعليمي ضمن الدورة؛ لا توجد رخصة عامة منفصلة
* Intended educational task: معالجة وترميز، وتصنيف topic/sentiment، وNER، وQA استخراجي، وبحث دلالي ثنائي اللغة، وتقييم

| File | Purpose | Rows | SHA-256 (first 16) |
|---|---|---:|---|
| `bayan_day1_sample.csv` | preprocessing/tokenisation texts | 12 | `904a5e1e860f23ac` |
| `bayan_day2_classification.csv` | topic + sentiment | 40 | `c50de92fdab1aa36` |
| `bayan_day2_ner.jsonl` | NER (BIO) | 12 | `ab413f0941656abf` |
| `bayan_day2_qa.json` | extractive QA (+ no-answer) | 10 | `4e894757b74d09df` |
| `bayan_day3_arabic.csv` | Arabic variants (MSA/Gulf/Arabizi) | 20 | `0a3346b6177d0c0b` |
| `bayan_day3_cases.csv` | search corpus | 24 | `322867b54d1f6f35` |
| `bayan_day3_queries.jsonl` | search queries (+ no-answer) | 18 | `f80ebd8b25c37b33` |
| `bayan_day3_predictions.csv` | COURSE_FIXTURE for the evaluation lab only | 36 | `63b4df9dab076880` |

> ملاحظة: كانت أسماء الملفات في النسخة السابقة من مستودعي مختلفة (مثل `sample data/bayan_Qa.json`). أعدتها إلى أسمائها الأصلية تحت `data/sample/`، والمحتوى لم يتغير (البصمات أعلاه).

## Composition (classification)

| Split | Rows | Arabic | English | Groups | Notes |
|---|---:|---:|---:|---:|---|
| train | 24 | 12 | 12 | 12 | تدريب |
| validation | 8 | 4 | 4 | 4 | اختيار الحقبة والعتبات. sentiment فيه `neutral`=6 و`negative`=2 فقط |
| frozen test | 8 | 4 | 4 | 4 | يُقرأ مرة واحدة. sentiment فيه `negative`=6 و`positive`=2 فقط |

**Total:** 40 rows، و⏳ PENDING_RUN groups، و`group_overlap = ⏳ PENDING_RUN` (مقيس في دفتر 03).

## Fields and labels

| Field/label | Meaning | Allowed values | Missing-value rule |
|---|---|---|---|
| `example_id` | معرّف فريد | `F-001` … `F-040` | Required |
| `group_id` | مجموعة تمنع عبور الأزواج بين splits | — | Required |
| `split` | الجزء | `train`, `validation`, `test` | Required |
| `language` | اللغة | `ar`, `en` | Required |
| `text` | النص (نسخة العرض) | Arabic/English | Required |
| `topic` | الهدف الرئيس | `digital_service`, `health`, `permit`, `transport` | Required |
| `sentiment` | الهدف الثاني (رأس مستقل) | `positive`, `negative`, `neutral` | Required |
| NER tags | BIO | `SERVICE`, `LOCATION`, `DATE`, `REF_NUM`, `ORG` | Required per token |
| QA `answer_text` | مقطع من السياق أو `null` | string / null | `null` = no answer |

## Collection/generation

مجموعة اصطناعية تعليمية صغيرة كتبتها المدربة لمادة الدورة، عن سيناريوهات خدمية (خدمات رقمية، تصاريح، صحة، نقل). لا تحتوي أشخاصًا أو حالات أو بيانات شخصية حقيقية. أمثلة البريد والجوال في الاختبارات مصطنعة لاختبار الحجب.

## Cleaning and preprocessing

* Display copy rule: `display_text` تبقى كما وصلت، وتُستخدم للعرض والتقييم اليدوي.
* PII masking rule: حجب البريد → `[EMAIL]` والجوال السعودي → `[PHONE]` قبل أي معالجة للنموذج.
* Arabic profile/version: `bayan-prep/1.0.0` لنسخة النموذج (NFC، إزالة التطويل، توحيد المسافات، والحفاظ على التشكيل والألف). و`search` ⏳ PENDING_RUN بـCAMeL Tools للبحث (D-003).
* Deduplication/grouping: الأزواج العربية/الإنجليزية في `group_id` واحد وsplit واحد.
* Filtering/exclusions: Arabizi لا يدخل التصنيف، ويُعلَّم بقاعدة شفافة فقط.

## Split and leakage controls

* Split method/seed: تقسيم ثابت من ملف البيانات؛ البذرة 42 للتدريب.
* Group isolation evidence: `group_overlap = ⏳ PENDING_RUN` ([`reports/nb03_classification.json`](reports/nb03_classification.json)).
* Near-duplicate audit: الأزواج ثنائية اللغة مجمّعة بـ`group_id`.
* Frozen-test access: test يُقرأ مرة واحدة بعد تثبيت الإعدادات. الدفاتر شُغّلت من commit `⏳ PENDING_RUN`.

## Known gaps and risks

* Dialects/Arabizi: الخليجية 9 أمثلة فقط في ملف اللهجات؛ اللهجات الأخرى غائبة؛ Arabizi مثالان.
* Class balance: الموضوعات متوازنة (10 لكل موضوع)، أما المشاعر فغير متوازنة بين splits.
* Synthetic-to-real gap: جمل قصيرة ونظيفة، والنصوص الواقعية أطول وأكثر فوضى.
* Annotation ambiguity: بعض الجمل القصيرة تحتمل أكثر من موضوع (انظري تصنيف الأخطاء).
* Small slices/uncertainty: validation وtest فيهما 8 أمثلة لكل منهما، فعدم اليقين كبير.
* Misuse/privacy risk: لا يُستخدم لاتخاذ قرارات عن أشخاص حقيقيين.

## Permitted and prohibited use

* Permitted: تجارب تعليمية في المعالجة والترميز والتصنيف وNER وQA والبحث والتقييم.
* Prohibited/high-risk: الإنتاج، وتنميط الأشخاص، وتقديم النتائج دليلًا على أداء واقعي.
* Human review: مطلوبة قبل أي استخدام خارج التعلم.

## Maintenance

* Owner/contact: Manal Qaysi — عبر Issues في https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi
* Change/version policy: أي تعديل في البيانات يغيّر البصمات أعلاه، ويُسجَّل قرارًا جديدًا في `DECISIONS.md`.
* Rebuild triggers: تغيّر البيانات أو التسميات أو التقسيم أو إصدار المعالجة أو الـcheckpoint يستلزم إعادة التدريب والفهرسة والتقييم.
