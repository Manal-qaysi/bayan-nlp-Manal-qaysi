# STUDENT PROFILE | ملف المتدرب

استخدم المعلومات اللازمة للتقييم فقط. لا تضف رقم هوية أو هاتفًا أو عنوانًا أو token أو بيانات حساسة.

- Display name | الاسم للعرض: Manal Qaysi — منال قيسي
- GitHub username: Manal-qaysi
- Public repository: https://github.com/Manal-qaysi/bayan-nlp-Manal-qaysi
- Learning lane completed: Core / Explore / Distinction — Distinction
- Starting level (self-described): beginner / intermediate / specialist — beginner

## My contribution | مساهمتي

- **ملف كتبته بنفسي:** [`my_work/nlp3.py`](my_work/nlp3.py). هو سكربت Colab يجمع عمل اليوم الأول: فحص البيئة، ومعالجة النص بنسختين مع حجب البريد والجوال، والترميز بـWordPiece، وfertility وtruncation، والانتباه المقيَّس مع الأقنعة وmulti-head، وتدقيق معاملات checkpointين.
- **قرار اتخذته:** ميزانية الأداء في [`BENCHMARKS.md`](BENCHMARKS.md) §2 (p95 ≤ 100 ms، ≥ 20 عنصر/ث، أثر جودة ≤ 0.02 على CPU)، وكتبتها قبل قياس أي مرشح.
- **تشغيل ومراجعة:** شغّلت الدفاتر التسعة على Colab وحفظت مخرجاتها، وراجعت تصنيف أخطاء نماذجي في دفتر 07. الأدلة في [`reports/results_index.json`](reports/results_index.json).

## One skill I can now demonstrate

شرح وتنفيذ مسار كامل من المعالجة إلى التقييم: عقد نسختين للنص، واختيار `MAX_LENGTH` من قياس fertility وtruncation، ومحاذاة BIO على أول subword، ومقطع QA مقيَّد مع عتبة عدم الإجابة، وبحث FAISS مطبّع L2 مع قياس Recall/MRR، وقراءة bootstrap CI قبل أي ادعاء بالتفوق.

## One limitation I understand

مجموعة test فيها 8 أمثلة فقط، فخطأ واحد يغيّر Macro-F1 بأكثر من 0.1، وفترة الثقة الزوجية بين Transformer والـbaseline غالبًا تشمل الصفر. لذلك لا أستطيع أن أقول إن نموذجًا «أفضل» من آخر. أقصى ما أقوله إن المسار يعمل، وإن الفرق المرصود لا تدعمه العينة إحصائيًا. البيانات أيضًا اصطناعية، والخليجية فيها قليلة.

## Integrity declaration | إقرار النزاهة

- [ لا] أفهم كل كود وقرار أسلمه ويمكنني شرحه.
- [نعم ] نسبت المصادر والمكتبات والنماذج والبيانات إلى أصحابها.
- [ نعم] لم أستخدم بيانات شخصية أو أسرارًا.
- [نعم ] لم أغيّر test labels أو validator للحصول على PASS.

Signature/display name: Manal Qaysi  
Date: 2026-09-30
