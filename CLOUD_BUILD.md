# بناء APK من التابلت فقط

المشروع يحتوي على GitHub Actions جاهز لبناء APK تلقائيًا.

1. أنشئ مستودع GitHub جديد باسم `AI-Physics-Helper`.
2. ارفع **محتويات هذا المجلد** إلى المستودع، وليس ملف ZIP نفسه.
3. افتح تبويب **Actions**.
4. شغّل workflow باسم **Build Android APK**.
5. بعد نجاح البناء افتح الـworkflow run ثم قسم **Artifacts**.
6. نزّل `AI-Physics-Helper-debug` وفك ضغطه.
7. ستجد `app-debug.apk`، افتحه على التابلت واضغط تثبيت.

ملاحظة أمنية: لا تضع مفتاح OpenAI داخل تطبيق Android. التطبيق يحتاج عنوان الـBackend فقط، والمفتاح يبقى على الخادم.
