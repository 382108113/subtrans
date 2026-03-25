"""
透明悬浮翻译框
"""
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor


class OverlayWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()

    def init_ui(self):
        # 设置窗口属性：透明、无边框、始终在最前
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        # 确保置顶
        self.raise_()
        self.setFixedSize(400, 200)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 标题栏（可拖拽）
        title_bar = QHBoxLayout()
        title_label = QLabel("SubTrans 翻译")
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background-color: transparent;")

        spacer = QLabel("")
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(30, 20)
        minimize_btn.clicked.connect(self.hide)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 20)
        close_btn.clicked.connect(self.close_window)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,100,100,0.6);
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(255,100,100,0.8);
            }
        """)

        title_bar.addWidget(title_label)
        title_bar.addWidget(spacer)
        title_bar.addWidget(minimize_btn)
        title_bar.addWidget(close_btn)

        # 原文标签
        self.source_label = QLabel("等待识别...")
        self.source_label.setFont(QFont("Arial", 11))
        self.source_label.setStyleSheet("""
            color: #cccccc;
            background-color: rgba(30,30,30,0.85);
            padding: 8px;
            border-radius: 5px;
        """)
        self.source_label.setWordWrap(True)
        self.source_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # 译文标签
        self.translation_label = QLabel("译文将显示在这里")
        self.translation_label.setFont(QFont("Arial", 12))
        self.translation_label.setStyleSheet("""
            color: #4fc3f7;
            background-color: rgba(30,30,30,0.85);
            padding: 8px;
            border-radius: 5px;
        """)
        self.translation_label.setWordWrap(True)
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(title_bar)
        main_layout.addWidget(self.source_label, 1)
        main_layout.addWidget(self.translation_label, 1)

        self.setLayout(main_layout)

        # 样式
        self.setStyleSheet("""
            background-color: transparent;
        """)

        # 初始位置：屏幕右下角
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move(geo.width() - 420, geo.height() - 220)

    def update_text(self, source: str, translation: str):
        """更新显示的原文和译文"""
        self.source_label.setText(source if source else "未能识别到文字")
        self.translation_label.setText(translation if translation else "正在翻译...")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.close_window()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def close_window(self):
        self.hide()
        self.closed.emit()

    def show_at_position(self, x: int, y: int):
        """显示在指定位置附近"""
        self.move(x + 20, y + 20)
        self.show()
