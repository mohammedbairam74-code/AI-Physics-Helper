# AI Physics Helper Android

نسخة Android (WebView shell) فوق الـ FastAPI backend الحالي.

## التشغيل
1. شغّل الـ backend على سيرفر يمكن للتابلت الوصول إليه.
2. افتح التطبيق واضغط ⚙ ثم ضع عنوان الخادم مثل `http://192.168.1.10:8000`.
3. لا تضع `OPENAI_API_KEY` داخل التطبيق. المفتاح يبقى على الـ backend.

## البناء
افتح المجلد في Android Studio ثم Build > Build APK(s).

## ملاحظة
بيئة البناء الحالية لا تحتوي Android SDK/Gradle، لذلك لم يتم الادعاء بإنتاج APK هنا. ملفات المشروع جاهزة للبناء.
