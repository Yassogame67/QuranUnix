#!/bin/bash
# سكريبت البدء السريع لتطبيق Quran Unix
# Quickstart script for Quran Unix

set -e

echo "🚀 بدء تشغيل Quran Unix..."
echo ""

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python 3.8 أو أحدث."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# التحقق من البيئة الافتراضية
if [ ! -d "venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية (venv)..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
echo "📂 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تثبيت/تحديث المتطلبات
echo "📥 تثبيت المتطلبات (PyQt6, PyMuPDF)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# التحقق من ملف PDF
if [ ! -f "MushafMadinaHafsGreen1441HQ.pdf" ]; then
    echo "⚠️  تحذير: ملف PDF غير موجود!"
    echo "   يرجى وضع ملف MushafMadinaHafsGreen1441HQ.pdf في مجلد المشروع"
    echo ""
fi

# تشغيل التطبيق
echo "🎯 تشغيل التطبيق..."
echo ""
python3 src/main.py
