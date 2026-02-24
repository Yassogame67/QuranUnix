#!/usr/bin/env python3
"""
اختبارات بسيطة لتطبيق مصحف المدينة
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """اختبار استيراد المكتبات"""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QPixmap
        import fitz
        print("✓ جميع المكتبات مستوردة بنجاح")
        return True
    except ImportError as e:
        print(f"✗ خطأ في استيراد المكتبات: {e}")
        return False

def test_surah_data():
    """اختبار بيانات السور"""
    try:
        from main import SURAHS
        assert len(SURAHS) == 114, "يجب أن يكون هناك 114 سورة"
        assert SURAHS[0][1] == "الفاتحة", "السورة الأولى يجب أن تكون الفاتحة"
        assert SURAHS[-1][1] == "الناس", "السورة الأخيرة يجب أن تكون الناس"
        print("✓ بيانات السور صحيحة")
        return True
    except Exception as e:
        print(f"✗ خطأ في بيانات السور: {e}")
        return False

def test_pdf_exists():
    """اختبار وجود ملف PDF"""
    pdf_paths = [
        "MushafMadinaHafsGreen1441HQ.pdf",
        os.path.join(os.path.dirname(__file__), "MushafMadinaHafsGreen1441HQ.pdf"),
    ]
    
    for path in pdf_paths:
        if os.path.exists(path):
            print(f"✓ ملف PDF موجود: {path}")
            return True
    
    print("⚠ ملف PDF غير موجود - ستحتاج إلى وضعه يدوياً")
    return True  # لا نعتبر هذا خطأً

def main():
    """الدالة الرئيسية للاختبارات"""
    print("🧪 تشغيل اختبارات تطبيق مصحف المدينة...")
    print("-" * 50)
    
    tests = [
        test_imports,
        test_surah_data,
        test_pdf_exists,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("-" * 50)
    passed = sum(results)
    total = len(results)
    print(f"النتيجة: {passed}/{total} اختبارات ناجحة")
    
    if passed == total:
        print("✅ جميع الاختبارات ناجحة!")
        return 0
    else:
        print("❌ بعض الاختبارات فشلت")
        return 1

if __name__ == "__main__":
    sys.exit(main())
