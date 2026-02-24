#!/usr/bin/env python3
"""
دوال مساعدة لتطبيق مصحف المدينة
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List


def find_pdf_file(filename: str) -> Optional[str]:
    """
    البحث عن ملف PDF في عدة مواقع محتملة
    
    Args:
        filename: اسم ملف PDF
        
    Returns:
        المسار الكامل للملف أو None إذا لم يوجد
    """
    possible_paths = [
        filename,
        Path(__file__).parent.parent / filename,
        Path(sys.executable).parent / filename,
        Path.cwd() / filename,
        Path.home() / ".local" / "share" / "mushaf-madinah" / filename,
        "/usr/share/mushaf-madinah" / Path(filename),
        "/opt/mushaf-madinah" / Path(filename),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    return None


def get_config_dir() -> Path:
    """
    الحصول على مجلد الإعدادات
    
    Returns:
        مسار مجلد الإعدادات
    """
    config_dir = Path.home() / ".config" / "mushaf-madinah"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_dir() -> Path:
    """
    الحصول على مجلد التخزين المؤقت
    
    Returns:
        مسار مجلد التخزين المؤقت
    """
    cache_dir = Path.home() / ".cache" / "mushaf-madinah"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def format_page_number(page: int, total: int) -> str:
    """
    تنسيق رقم الصفحة للعرض
    
    Args:
        page: رقم الصفحة الحالية
        total: إجمالي عدد الصفحات
        
    Returns:
        نص منسق
    """
    return f"الصفحة: {page} / {total}"


def format_zoom_percent(zoom: float) -> str:
    """
    تنسيق نسبة التكبير
    
    Args:
        zoom: نسبة التكبير
        
    Returns:
        نص منسج
    """
    return f"{int(zoom * 100)}%"


def get_surah_by_page(page_num: int, surahs: List[Tuple]) -> str:
    """
    الحصول على اسم السورة من رقم الصفحة
    
    Args:
        page_num: رقم الصفحة
        surahs: قائمة السور
        
    Returns:
        اسم السورة
    """
    for num, name, page, verses in reversed(surahs):
        if page_num >= page:
            return f"سورة {name}"
    return ""


def get_surah_index_by_page(page_num: int, surahs: List[Tuple]) -> int:
    """
    الحصول على فهرس السورة من رقم الصفحة
    
    Args:
        page_num: رقم الصفحة
        surahs: قائمة السور
        
    Returns:
        فهرس السورة
    """
    for i, (num, name, page, verses) in enumerate(surahs):
        if page_num >= page:
            if i == len(surahs) - 1 or page_num < surahs[i + 1][2]:
                return i
    return 0


def arabic_to_english_numbers(text: str) -> str:
    """
    تحويل الأرقام العربية إلى إنجليزية
    
    Args:
        text: النص العربي
        
    Returns:
        النص مع أرقام إنجليزية
    """
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    
    for arabic, english in zip(arabic_nums, english_nums):
        text = text.replace(arabic, english)
    
    return text


def normalize_arabic_text(text: str) -> str:
    """
    توحيد النص العربي للبحث
    
    Args:
        text: النص المراد توحيده
        
    Returns:
        النص الموحد
    """
    # إزالة التشكيل
    tashkeel = "ًٌٍَُِّْ"
    for char in tashkeel:
        text = text.replace(char, "")
    
    # توحيد أشكال الألف
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    
    # توحيد أشكال الهاء
    text = text.replace("ة", "ه")
    
    return text.lower().strip()


def is_dark_mode_preferred() -> bool:
    """
    التحقق مما إذا كان المستخدم يفضل الوضع الليلي
    
    Returns:
        True إذا كان يفضل الوضع الليلي
    """
    # التحقق من متغير البيئة
    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    
    # بعض بيئات سطح المكتب تدعم الوضع الليلي
    if "gnome" in desktop_env or "kde" in desktop_env:
        # يمكن إضافة منطق أكثر تعقيداً هنا
        pass
    
    return False


def get_app_version() -> str:
    """
    الحصول على إصدار التطبيق
    
    Returns:
        رقم الإصدار
    """
    try:
        from config import APP_VERSION
        return APP_VERSION
    except ImportError:
        return "1.0.0"


def resource_path(relative_path: str) -> str:
    """
    الحصول على المسار المطلق للموارد
    يعمل مع PyInstaller والتشغيل العادي
    
    Args:
        relative_path: المسار النسبي
        
    Returns:
        المسار المطلق
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    
    return os.path.join(os.path.dirname(__file__), relative_path)
