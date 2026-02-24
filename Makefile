# Makefile لتطبيق مصحف المدينة

.PHONY: help install uninstall run build-appimage clean venv test

# المتغيرات
PYTHON := python3
VENV_DIR := venv
APP_NAME := mushaf-madinah

help:
	@echo "📖 مصحف المدينة - أوامر البناء"
	@echo ""
	@echo "الأوامر المتاحة:"
	@echo "  make venv         إنشاء البيئة الافتراضية"
	@echo "  make install      تثبيت التطبيق على النظام (يتطلب sudo)"
	@echo "  make uninstall    إلغاء تثبيت التطبيق (يتطلب sudo)"
	@echo "  make run          تشغيل التطبيق"
	@echo "  make build        بناء التطبيق"
	@echo "  make appimage     بناء AppImage"
	@echo "  make clean        تنظيف الملفات المؤقتة"
	@echo "  make test         تشغيل الاختبارات"

venv:
	@echo "📦 إنشاء البيئة الافتراضية..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

install:
	@echo "📦 تثبيت التطبيق..."
	@sudo ./install.sh

uninstall:
	@echo "🗑️  إلغاء التثبيت..."
	@sudo ./uninstall.sh

run:
	@echo "🚀 تشغيل التطبيق..."
	@if [ -d "$(VENV_DIR)" ]; then \
		source $(VENV_DIR)/bin/activate && $(PYTHON) src/main.py; \
	else \
		$(PYTHON) src/main.py; \
	fi

build:
	@echo "🔨 بناء التطبيق..."
	@if [ ! -d "$(VENV_DIR)" ]; then $(MAKE) venv; fi
	source $(VENV_DIR)/bin/activate && pyinstaller --clean --noconfirm \
		--name "Mushaf-Madinah" \
		--windowed \
		--onefile \
		--add-data "MushafMadinaHafsGreen1441HQ.pdf:." \
		--icon="assets/icon.png" \
		src/main.py

appimage:
	@echo "📦 بناء AppImage..."
	cd build-AppImage && ./build.sh

clean:
	@echo "🧹 تنظيف الملفات..."
	rm -rf build/ dist/ __pycache__/ *.egg-info/
	rm -rf $(VENV_DIR)/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

test:
	@echo "🧪 تشغيل الاختبارات..."
	@echo "✓ لا توجد اختبارات حالياً"
