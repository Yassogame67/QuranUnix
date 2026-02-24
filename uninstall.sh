#!/bin/bash
# سكريبت إلغاء تثبيت تطبيق Quran Unix
# Uninstallation script for Quran Unix

set -e

echo "🗑️  إلغاء تثبيت Quran Unix..."

# التحقق من الصلاحيات
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️ يرجى تشغيل السكريبت بصلاحيات root (sudo)"
    exit 1
fi

# المتغيرات
APP_NAME="quran-unix"
INSTALL_DIR="/opt/$APP_NAME"
BIN_DIR="/usr/bin"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="/usr/share/applications"

# حذف الملفات
echo "🗑️  حذف الملفات..."

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "   ✓ حذف مجلد التثبيت"
fi

if [ -f "$BIN_DIR/$APP_NAME" ]; then
    rm "$BIN_DIR/$APP_NAME"
    echo "   ✓ حذف سكريبت التشغيل"
fi

if [ -f "$ICON_DIR/$APP_NAME.png" ]; then
    rm "$ICON_DIR/$APP_NAME.png"
    echo "   ✓ حذف الأيقونة"
fi

if [ -f "$DESKTOP_DIR/$APP_NAME.desktop" ]; then
    rm "$DESKTOP_DIR/$APP_NAME.desktop"
    echo "   ✓ حذف ملف desktop"
fi

# تحديث قواعد البيانات
update-icon-caches /usr/share/icons/hicolor/ 2>/dev/null || true
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo "✅ تم إلغاء التثبيت بنجاح!"
