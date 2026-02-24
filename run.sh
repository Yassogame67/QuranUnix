#!/bin/bash
# سكريبت تشغيل سريع لتطبيق Quran Unix

# التحقق من وجود البيئة الافتراضية
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# تشغيل التطبيق
python3 src/main.py "$@"
