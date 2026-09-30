# PRESENTATION — Bayan | عرض بيان

**GitHub username / معرف المتدرب:** `Manal-qaysi` — منال قيسي

خمس دقائق + دقيقتان للتحقق الفردي؛ خمسة أقسام. كل مثال أدناه من تشغيلي المحفوظ في المستودع (لا تشغيل أثناء العرض).

## 1. Problem and user | المشكلة والمستخدم

- **المستخدم:** موظف فرز ومتابعة لملاحظات خدمية تصل بالعربية (فصحى/خليجية) والإنجليزية.
- **المدخل:** نص قصير (≤ 1000 حرف) + لغة `ar`/`en`/`auto`.
- **ما يفعله:** موضوع + مشاعر، كيانات، إجابة من نص إجراء أو امتناع، وبحث عن حالة سابقة مشابهة ولو بلغة أخرى.
- **ما لا يدّعيه:** لا قرارات عن أشخاص، لا إنتاج، لا Arabizi، لا لهجات غير خليجية؛ البيانات اصطناعية.

## 2. Architecture | المعمارية

- المخطط في [`README.md#architecture--المعمارية`](README.md#architecture--المعمارية): display copy → `bayan-prep/1.0.0` (حجب PII) → رؤوس DistilmBERT (topic/sentiment/NER/QA) + فرع البحث (CAMeL `search` → MiniLM متعدد اللغات L2 → FAISS → re-rank / RRF) → استجابة تحمل model/runtime/preprocessing version.
- اختياراتي الفعلية: `MAX_LENGTH=⏳ PENDING_RUN` مقاسة (D-002)، profile محافظ للنموذج وبحثي للفهرس (D-003)، runtime الخدمة `⏳ PENDING_RUN` (D-008).

## 3. Demonstration | التطبيق

- **Arabic example + output evidence:** `"الخدمة واضحة"` → `⏳ PENDING_RUN` (confidence ⏳ PENDING_RUN) — [`sample_outputs/service_examples.json`](sample_outputs/service_examples.json)، خلية TestClient في [دفتر 08](notebooks/08_optimization_serving.ipynb).
- **English example + output evidence:** `"The service is clear"` → `⏳ PENDING_RUN` (confidence ⏳ PENDING_RUN).
- **Extraction / search:** NER على test: F1 = ⏳ PENDING_RUN؛ بحث عبر اللغات: [`sample_outputs/search_examples.json`](sample_outputs/search_examples.json) (ترتيب dense مقابل hybrid لكل استعلام test).
- **No-answer / invalid-input case:** أسئلة QA بلا إجابة في test — دقة الامتناع ⏳ PENDING_RUN ([`sample_outputs/qa_examples.json`](sample_outputs/qa_examples.json))؛ استعلامات بحث بلا حالة مطابقة — دقة ⏳ PENDING_RUN؛ مدخل فارغ / لغة غير مدعومة / أطول من 1000 حرف → HTTP ⏳ PENDING_RUN / ⏳ PENDING_RUN / ⏳ PENDING_RUN.
- **Saved fallback from the same submission:** الدفاتر المحفوظة بمخرجاتها في `notebooks/` + `sample_outputs/` من التشغيل نفسه.

## 4. Measured evidence | الدليل المقاس

- **Quality metric, data split and report:** topic Macro-F1 على frozen test (n=⏳ PENDING_RUN) = ⏳ PENDING_RUN مقابل baseline ⏳ PENDING_RUN — [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) §3، [`reports/nb07_evaluation.json`](reports/nb07_evaluation.json).
- **Performance metric, environment and report:** p95 model-only على workload validation (8 نصوص، batch 4، Colab CPU): PyTorch ⏳ PENDING_RUN ms → ONNX FP32 ⏳ PENDING_RUN ms (×⏳ PENDING_RUN)، أثر الجودة ⏳ PENDING_RUN — [`BENCHMARKS.md`](BENCHMARKS.md).
- **Measurement label and limits:** `MEASURED_SMOKE` للجودة و`MEASURED` (PROJECT_ARTIFACT) للأداء؛ n صغير، CPU مشترك، بذرة واحدة.

## 5. Decision and ownership | القرار والمساهمة

- **My change / measured extension and file:** بحث هجين sparse+dense (RRF) — [`reports/nb06_extension.json`](reports/nb06_extension.json)، [دفتر 06](notebooks/06_semantic_search.ipynb).
- **Baseline, benefit/cost and limitation:** baseline = dense فقط؛ MRR@3 (validation) ⏳ PENDING_RUN → ⏳ PENDING_RUN، +⏳ PENDING_RUN ms؛ القرار **⏳ PENDING_RUN** بقاعدة مكتوبة قبل القياس؛ القيد: 10 استعلامات validation.
- **One code decision I can explain:** اختيار `MAX_LENGTH` في دفتر 03 = أصغر طول مرشح بلا قطع على train+validation (`choose_max_length` في `src/bayan/project.py`) — وسأجرّب أمامك تغيير نص (مثل إضافة تطويل أو تشكيل) وأبيّن أثره على التنبؤ وعلى invariance tests.
- **Known error I would not deploy yet:** `⏳ PENDING_RUN` — الإصلاح المقترح: ⏳ PENDING_RUN.
