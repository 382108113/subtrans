"""
屏幕选区工具
"""
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class SelectionWindow(QWidget):
    selection_made = pyqtSignal(QRect)  # 选区完成信号

    def __init__(self):
        super().__init__()
        self.start_point = None
        self.end_point = None
        self.is_selecting = False
        self.init_ui()

    def init_ui(self):
        # 全屏透明窗口
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # 获取主屏幕几何
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        else:
            self.setGeometry(0, 0, 1920, 1080)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 半透明遮罩
        if not self.is_selecting:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
            # 显示提示文字
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 20))
            painter.drawText(
                self.rect().center() - QPoint(200, 10),
                "拖拽选择翻译区域，按 ESC 取消"
            )
            return

        # 绘制选区边框
        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point).normalized()

            # 暗色遮罩
            painter.fillRect(self.rect(), QColor(0, 0, 0, 60))

            # 清除选区内的遮罩（让选区完全可见）
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.white)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # 黄色醒目边框
            pen = QPen(QColor(255, 230, 0), 3)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

            # 虚线内部边框
            pen_dash = QPen(QColor(79, 195, 247), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_dash)
            painter.drawRect(rect.adjusted(2, 2, -3, -3))

            # 尺寸和位置提示
            size_text = f"选区: {rect.width()} × {rect.height()} | 位置: ({rect.x()}, {rect.y()})"
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 14))

            # 在选区上方显示文字
            text_rect = QRect(rect.x(), rect.y() - 35, rect.width(), 30)
            if text_rect.y() < 0:
                text_rect.moveTop(rect.bottom() + 5)

            painter.fillRect(text_rect, QColor(0, 0, 0, 150))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, size_text)

            # 角落标记
            corner_size = 10
            painter.setPen(QPen(QColor(255, 230, 0), 2))
            # 左上角
            painter.drawLine(rect.x(), rect.y(), rect.x() + corner_size, rect.y())
            painter.drawLine(rect.x(), rect.y(), rect.x(), rect.y() + corner_size)
            # 右上角
            painter.drawLine(rect.x() + rect.width(), rect.y(), rect.x() + rect.width() - corner_size, rect.y())
            painter.drawLine(rect.x() + rect.width(), rect.y(), rect.x() + rect.width(), rect.y() + corner_size)
            # 左下角
            painter.drawLine(rect.x(), rect.y() + rect.height(), rect.x() + corner_size, rect.y() + rect.height())
            painter.drawLine(rect.x(), rect.y() + rect.height(), rect.x(), rect.y() + rect.height() - corner_size)
            # 右下角
            painter.drawLine(rect.x() + rect.width(), rect.y() + rect.height(), rect.x() + rect.width() - corner_size, rect.y() + rect.height())
            painter.drawLine(rect.x() + rect.width(), rect.y() + rect.height(), rect.x() + rect.width(), rect.y() + rect.height() - corner_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.position().toPoint()
            rect = QRect(self.start_point, self.end_point).normalized()

            # 忽略太小的选区
            if rect.width() > 20 and rect.height() > 10:
                self.selection_made.emit(rect)

            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
