#!/bin/bash
# سكريبت تثبيت تطبيق Quran Unix على النظام
# Installation script for Quran Unix

set -e

echo "📦 تثبيت Quran Unix..."

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

# إنشاء مجلد التثبيت
echo "📁 إنشاء مجلد التثبيت..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$ICON_DIR"

# نسخ الملفات
echo "📂 نسخ الملفات..."
cp -r src "$INSTALL_DIR/"
cp -r assets "$INSTALL_DIR/"

if [ -f "MushafMadinaHafsGreen1441HQ.pdf" ]; then
    cp "MushafMadinaHafsGreen1441HQ.pdf" "$INSTALL_DIR/"
fi

cp requirements.txt "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/"
cp LICENSE "$INSTALL_DIR/"

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
python3 -m pip install -r requirements.txt --quiet

# إنشاء سكريبت التشغيل
echo "⚙️ إنشاء سكريبت التشغيل..."
cat > "$BIN_DIR/$APP_NAME" << 'EOF'
#!/bin/bash
cd /opt/quran-unix
python3 src/main.py "$@"
EOF

chmod +x "$BIN_DIR/$APP_NAME"

# نسخ الأيقونة
if [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$ICON_DIR/$APP_NAME.png"
fi

# نسخ ملف desktop
if [ -f "quran-unix.desktop" ]; then
    cp "quran-unix.desktop" "$DESKTOP_DIR/"
elif [ -f "mushaf-madinah.desktop" ]; then
    cp "mushaf-madinah.desktop" "$DESKTOP_DIR/quran-unix.desktop"
    # تحديث الاسم داخل ملف desktop
    sed -i 's/Name=مصحف المدينة/Name=Quran Unix/g' "$DESKTOP_DIR/quran-unix.desktop"
    sed -i 's/Exec=mushaf-madinah/Exec=quran-unix/g' "$DESKTOP_DIR/quran-unix.desktop"
    sed -i 's/Icon=mushaf-madinah/Icon=quran-unix/g' "$DESKTOP_DIR/quran-unix.desktop"
fi

# تحديث قاعدة بيانات الأيقونات
update-icon-caches /usr/share/icons/hicolor/ 2>/dev/null || true

# تحديث قاعدة بيانات desktop
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "✅ تم التثبيت بنجاح!"
echo ""
echo "🚀 يمكنك تشغيل التطبيق بإحدى الطرق التالية:"
echo "   - من قائمة التطبيقات: Quran Unix"
echo "   - من الطرفية: quran-unix"
echo ""
echo "🗑️  لإلغاء التثبيت، قم بتشغيل: sudo ./uninstall.sh"
