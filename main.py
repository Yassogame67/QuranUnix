#!/usr/bin/env python3
"""
Quran Unix - تطبيق قراءة القرآن الكريم
تطبيق بسيط وأنيق لقراءة القرآن الكريم بخط المصحف المدني
"""

import sys
import os
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QSplitter, QToolBar, QStatusBar, QLineEdit, QComboBox, QSpinBox,
    QFileDialog, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QSizePolicy, QMenu, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, QPoint, QEvent
from PyQt6.QtGui import (
    QPixmap, QImage, QIcon, QFont, QKeySequence, QShortcut, QAction,
    QPalette, QColor, QLinearGradient, QBrush, QFontDatabase, QCursor, QPainter, QKeyEvent
)
import fitz  # PyMuPDF

# إضافة مسار src للاستيراد
sys.path.append(os.path.dirname(__file__))
from config import SURAHS, LIGHT_THEME, DARK_THEME, KEYBOARD_SHORTCUTS, APP_NAME, APP_VERSION

def get_resource_path(relative_path):
    """الحصول على المسار الصحيح للملفات سواء في وضع التطوير أو بعد التجميع (AppImage/PyInstaller)"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a bundle, use the directory of the script
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # البحث عن الملف في عدة أماكن محتملة لضمان التوافق
    paths_to_check = [
        os.path.join(base_path, relative_path),
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), relative_path),
        os.path.join(os.getcwd(), relative_path)
    ]
    
    for p in paths_to_check:
        if os.path.exists(p):
            return p
            
    return os.path.join(base_path, relative_path)

class ArabicLineEdit(QLineEdit):
    """حقل إدخال ذكي يقوم بتحويل الحروف الإنجليزية إلى عربية تلقائياً عند الحاجة"""
    
    # قاموس تحويل الكيبورد من الإنجليزي إلى العربي (QWERTY to Arabic)
    EN_TO_AR_MAP = {
        'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف', 'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح', '[': 'ج', ']': 'د',
        'a': 'ش', 's': 'س', 'd': 'ي', 'f': 'ب', 'g': 'ل', 'h': 'ا', 'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'ك', "'": 'ط',
        'z': 'ئ', 'x': 'ء', 'c': 'ؤ', 'v': 'ر', 'b': 'لا', 'n': 'ى', 'm': 'ة', ',': 'و', '.': 'ز', '/': 'ظ',
        'Q': 'َ', 'W': 'ً', 'E': 'ُ', 'R': 'ٌ', 'T': 'لإ', 'Y': 'إ', 'U': '‘', 'I': '÷', 'O': '×', 'P': '؛', '{': '<', '}': '>',
        'A': 'ِ', 'S': 'ٍ', 'D': ']', 'F': '[', 'G': 'لأ', 'H': 'أ', 'J': 'ـ', 'K': '،', 'L': '/', ':': ':', '"': '"',
        'Z': '~', 'X': 'ْ', 'C': '{', 'V': '}', 'B': 'لآ', 'N': 'آ', 'M': '’', '<': ',', '>': '.', '?': '؟'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setPlaceholderText("🔍 ابحث عن سورة (اكتب بالعربي أو الإنجليزي)...")
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            super().keyPressEvent(event)
            return

        char = event.text()
        if char in self.EN_TO_AR_MAP:
            ar_char = self.EN_TO_AR_MAP[char]
            self.insert(ar_char)
            event.accept()
        else:
            super().keyPressEvent(event)

class PDFPageView(QGraphicsView):
    """عارض صفحات PDF مخصص مع تحسين التكبير"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | 
            QPainter.RenderHint.SmoothPixmapTransform |
            QPainter.RenderHint.TextAntialiasing
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = None
        self._zoom_factor = 1.0
        self.current_pixmap = None
        
    def set_page(self, pixmap: QPixmap):
        """عرض صفحة جديدة"""
        self.current_pixmap = pixmap
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.scene.addItem(self.pixmap_item)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self.update_view()
        
    def update_view(self):
        """تحديث العرض بناءً على مستوى التكبير"""
        if self.pixmap_item:
            self.resetTransform()
            self.scale(self._zoom_factor, self._zoom_factor)

    def wheelEvent(self, event):
        """التكبير/التصغير بعجلة الفأرة مع مفتاح Ctrl"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            if event.angleDelta().y() > 0:
                self.zoom_in(zoom_in_factor)
            else:
                self.zoom_out(zoom_out_factor)
            event.accept()
        else:
            super().wheelEvent(event)
            
    def zoom_in(self, factor=1.2):
        self._zoom_factor *= factor
        if self._zoom_factor > 5.0: self._zoom_factor = 5.0
        self.update_view()
        
    def zoom_out(self, factor=0.8):
        self._zoom_factor *= factor
        if self._zoom_factor < 0.1: self._zoom_factor = 0.1
        self.update_view()
        
    def zoom_reset(self):
        self._zoom_factor = 1.0
        self.update_view()
        
    def get_zoom(self) -> float:
        return self._zoom_factor

class SurahListWidget(QListWidget):
    """قائمة السور المخصصة"""
    surah_selected = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Amiri", 13))
        self.setSpacing(2)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.itemClicked.connect(self.on_item_clicked)
        self._setup_items()
        
    def _setup_items(self):
        for num, name, page in SURAHS:
            item = QListWidgetItem()
            item.setText(f"{name}  ({page})")
            item.setData(Qt.ItemDataRole.UserRole, (num, page))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.addItem(item)
            
    def on_item_clicked(self, item: QListWidgetItem):
        surah_num, page_num = item.data(Qt.ItemDataRole.UserRole)
        self.surah_selected.emit(surah_num, page_num)
        
    def search_surah(self, text: str):
        text = text.strip().lower()
        for i in range(self.count()):
            item = self.item(i)
            surah_name = SURAHS[i][1].lower()
            if text in surah_name or text in str(i+1):
                item.setHidden(False)
            else:
                item.setHidden(True)

class MushafViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1100, 750)
        
        self.pdf_document = None
        self.current_page_idx = 0
        self.is_dark_mode = False
        
        # استخدام الوظيفة الجديدة للحصول على مسار ملف الـ PDF بشكل صحيح
        self.pdf_path = get_resource_path("MushafMadinaHafsGreen1441HQ.pdf")
        
        self.config_dir = Path.home() / ".config" / "quran-unix"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_ui()
        self._setup_shortcuts()
        self.load_settings()
        self._apply_theme()
        self.load_pdf()
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("app-title")
        title_label.setFont(QFont("Amiri", 22, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        self.search_box = ArabicLineEdit()
        self.search_box.setFont(QFont("Amiri", 12))
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box.setFixedHeight(40)
        sidebar_layout.addWidget(self.search_box)
        
        self.surah_list = SurahListWidget()
        self.surah_list.surah_selected.connect(self.go_to_page)
        sidebar_layout.addWidget(self.surah_list)
        
        self.page_info = QLabel("الصفحة: -")
        self.page_info.setFont(QFont("Amiri", 12))
        self.page_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.page_info)
        
        self.splitter.addWidget(sidebar)
        
        # Viewer Area
        viewer_container = QFrame()
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFixedHeight(50)
        self.toolbar.setIconSize(QSize(24, 24))
        
        self.btn_prev = QPushButton("◀ السابق")
        self.btn_prev.setFixedWidth(80)
        self.btn_prev.clicked.connect(self.prev_page)
        
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 604)
        self.page_spin.setFixedWidth(70)
        self.page_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_spin.valueChanged.connect(self.on_page_spin_changed)
        
        self.btn_next = QPushButton("التالي ▶")
        self.btn_next.setFixedWidth(80)
        self.btn_next.clicked.connect(self.next_page)
        
        self.btn_zoom_in = QPushButton("➕")
        self.btn_zoom_in.setFixedWidth(40)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        
        self.btn_zoom_out = QPushButton("➖")
        self.btn_zoom_out.setFixedWidth(40)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        
        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setFixedWidth(40)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.toolbar.addWidget(self.btn_prev)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.page_spin)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_next)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.btn_zoom_out)
        self.toolbar.addWidget(self.btn_zoom_in)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_theme)
        
        viewer_layout.addWidget(self.toolbar)
        
        self.pdf_view = PDFPageView()
        viewer_layout.addWidget(self.pdf_view)
        
        self.splitter.addWidget(viewer_container)
        self.splitter.setStretchFactor(1, 1)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Right"), self, self.next_page)
        QShortcut(QKeySequence("Left"), self, self.prev_page)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.pdf_view.zoom_reset)

    def load_pdf(self):
        if not os.path.exists(self.pdf_path):
            QMessageBox.critical(self, "خطأ", f"لم يتم العثور على ملف الـ PDF في المسار:\n{self.pdf_path}")
            return
        
        try:
            self.pdf_document = fitz.open(self.pdf_path)
            self.page_spin.setRange(1, len(self.pdf_document))
            self.render_page()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل ملف الـ PDF:\n{str(e)}")

    def render_page(self):
        if not self.pdf_document: return
        
        page = self.pdf_document[self.current_page_idx]
        zoom = 2.0 
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        fmt = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        
        if self.is_dark_mode:
            qimg.invertPixels()
            
        self.pdf_view.set_page(QPixmap.fromImage(qimg))
        self.page_info.setText(f"الصفحة: {self.current_page_idx + 1} / {len(self.pdf_document)}")
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(self.current_page_idx + 1)
        self.page_spin.blockSignals(False)
        self.save_settings()

    def go_to_page(self, surah_num, page_num):
        self.current_page_idx = page_num - 1
        self.render_page()

    def next_page(self):
        if self.pdf_document and self.current_page_idx < len(self.pdf_document) - 1:
            self.current_page_idx += 1
            self.render_page()

    def prev_page(self):
        if self.pdf_document and self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.render_page()

    def on_page_spin_changed(self, value):
        self.current_page_idx = value - 1
        self.render_page()

    def on_search_changed(self, text):
        self.surah_list.search_surah(text)

    def zoom_in(self):
        self.pdf_view.zoom_in()

    def zoom_out(self):
        self.pdf_view.zoom_out()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.btn_theme.setText("☀️" if self.is_dark_mode else "🌙")
        self._apply_theme()
        self.render_page()

    def _apply_theme(self):
        theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        style = f"""
            QMainWindow {{ background-color: {theme['viewer_bg']}; }}
            QFrame#sidebar {{ 
                background-color: {theme['sidebar_bg']}; 
                border-right: 1px solid {theme['sidebar_border']};
            }}
            QLabel#app-title {{ color: {theme['title_color']}; margin-bottom: 10px; }}
            QLineEdit {{ 
                background-color: {theme['input_bg']}; 
                border: 1px solid {theme['input_border']};
                border-radius: 5px;
                padding: 5px;
                color: {theme['title_color']};
            }}
            QListWidget {{ 
                background-color: {theme['list_bg']}; 
                border: none;
                color: {theme['list_item_color']};
            }}
            QListWidget::item:selected {{ 
                background-color: {theme['list_item_selected']};
                color: {theme['title_color']};
                border-radius: 5px;
            }}
            QToolBar {{ 
                background-color: {theme['toolbar_bg']}; 
                border-bottom: 1px solid {theme['toolbar_border']};
                spacing: 10px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme['nav_btn_bg']};
                color: white;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['nav_btn_hover']};
            }}
            QSpinBox {{
                background-color: {theme['input_bg']};
                color: {theme['title_color']};
                border: 1px solid {theme['input_border']};
                border-radius: 4px;
            }}
        """
        self.setStyleSheet(style)

    def load_settings(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    self.current_page_idx = settings.get("last_page", 0)
                    self.is_dark_mode = settings.get("dark_mode", False)
                    self.btn_theme.setText("☀️" if self.is_dark_mode else "🌙")
            except: pass

    def save_settings(self):
        settings = {
            "last_page": self.current_page_idx,
            "dark_mode": self.is_dark_mode
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f)
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    font_path = get_resource_path(os.path.join("assets", "Amiri-Regular.ttf"))
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
        app.setFont(QFont("Amiri", 11))
    
    window = MushafViewer()
    window.show()
    sys.exit(app.exec())
