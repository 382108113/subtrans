"""
SubTrans - 实时字幕翻译工具
主程序入口
"""
import sys
import time
from threading import Thread, Event
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

# 子模块
from subtrans.ui.overlay import OverlayWindow
from subtrans.ui.selection import SelectionWindow
from subtrans.ocr.recognizer import get_recognizer
from subtrans.translator.ollama_translator import get_ollama_translator, OllamaTranslator
from subtrans.translator.offline_translator import detect_language
from subtrans.capture.screen_capture import capture_screen
from subtrans.capture.window_capture import get_window_list, capture_window, get_window_by_name
from subtrans.utils.hotkeys import get_hotkey_manager
from subtrans.asr.audio_capture import AudioCapture
from subtrans.asr.speech_recognizer import get_speech_recognizer
from subtrans.asr.streaming_recognizer import get_streaming_recognizer
from subtrans import config


class SubTransApp(QObject):
    """SubTrans 应用主类"""
    translation_done = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 连接翻译完成信号
        self.translation_done.connect(self._on_translation_done)

        # UI 组件
        self.overlay = OverlayWindow()
        self.selection_window: Optional[SelectionWindow] = None

        # 翻译组件 - 使用 Ollama
        self.recognizer = get_recognizer()
        self.translator = get_ollama_translator(config.TRANSLATION_MODEL)

        # 语音识别组件
        self.audio_capture = AudioCapture()
        self.speech_recognizer = get_speech_recognizer()

        # 状态
        self.is_translating = False
        self.capture_rect = None
        self.capture_thread: Optional[Thread] = None
        self.stop_capture = Event()

        # 快捷键 (传入 app 以便在主线程执行回调)
        self.hotkey_manager = get_hotkey_manager(self.app)
        self._setup_hotkeys()

        # 系统托盘
        self._setup_tray()

        # 预加载翻译模型
        self._preload_model()

    def _setup_hotkeys(self):
        """设置全局快捷键"""
        self.hotkey_manager.register(config.HOTKEY_SELECT_REGION, self.start_selection)
        self.hotkey_manager.register(config.HOTKEY_TOGGLE_OVERLAY, self.toggle_overlay)
        self.hotkey_manager.register(config.HOTKEY_SPEECH_MODE, self.start_speech_recognition)
        self.hotkey_manager.register(config.HOTKEY_OCR_MODE, self.start_selection)  # OCR reuse selection
        self.hotkey_manager.start()

    def _setup_tray(self):
        """设置系统托盘"""
        self.tray = QSystemTrayIcon()

        # 创建托盘菜单
        menu = QMenu()

        select_action = QAction("选择区域翻译 (⌃⌥2)", self.app)
        select_action.triggered.connect(self.start_selection)

        window_action = QAction("选择窗口翻译 (⌃⌥3)", self.app)
        window_action.triggered.connect(self.start_window_selection)

        speech_action = QAction("语音识别翻译 (⌃⌥5)", self.app)
        speech_action.triggered.connect(self.start_speech_recognition)

        toggle_action = QAction("显示/隐藏悬浮窗 (⌃⌥4)", self.app)
        toggle_action.triggered.connect(self.toggle_overlay)

        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.quit)

        menu.addAction(select_action)
        menu.addAction(window_action)
        menu.addAction(speech_action)
        menu.addAction(toggle_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.setToolTip("SubTrans - 实时字幕翻译")

        # 点击托盘图标显示悬浮窗
        self.tray.activated.connect(lambda reason: self.toggle_overlay() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)

        self.tray.show()

    def _preload_model(self):
        """预加载翻译模型"""
        def _load():
            try:
                self.translator.load_model('zh')
            except Exception as e:
                print(f"Model preload error: {e}")

        thread = Thread(target=_load)
        thread.daemon = True
        thread.start()

    def start_selection(self):
        """开始屏幕选区"""
        if self.is_translating:
            self.stop_translation()

        # 创建选区窗口
        self.selection_window = SelectionWindow()
        self.selection_window.selection_made.connect(self.on_selection_made)

    def on_selection_made(self, rect):
        """选区完成回调"""
        self.capture_rect = rect
        self.start_translation()

    def start_window_selection(self):
        """开始窗口选择"""
        windows = get_window_list()

        if not windows:
            msg = QMessageBox()
            msg.setWindowTitle("SubTrans")
            msg.setText("未找到可捕获的窗口")
            msg.exec()
            return

        # 显示窗口列表让用户选择
        # 简化处理：直接选择最前面的窗口
        if windows:
            # 选择 Steam、VLC、Chrome 等常见应用
            target = get_window_by_name('VLC') or get_window_by_name('Chrome') or \
                     get_window_by_name('Safari') or get_window_by_name('YouTube') or \
                     get_window_by_name('Netflix')

            if target:
                self.capture_window(target.window_id)
            else:
                # 使用第一个窗口
                self.capture_window(windows[0].window_id)

    def capture_window(self, window_id: int):
        """捕获指定窗口"""
        self.is_translating = True
        self.stop_capture.clear()
        self.overlay.show()

        def _capture_loop():
            while not self.stop_capture.is_set():
                img = capture_window(window_id)
                if img:
                    self.process_image(img)
                time.sleep(1.5)

        self.capture_thread = Thread(target=_capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def start_translation(self):
        """开始实时翻译"""
        if self.capture_rect is None:
            print("[DEBUG] start_translation: capture_rect is None!")
            return

        print(f"[DEBUG] start_translation: rect={self.capture_rect}")
        self.is_translating = True
        self.stop_capture.clear()
        self.overlay.raise_()  # 确保悬浮窗置顶
        self.overlay.show()

        def _capture_loop():
            last_text = ""
            last_translate_time = 0
            translate_interval = 2.5  # 翻译间隔（秒），避免太频繁

            while not self.stop_capture.is_set():
                img = capture_screen(self.capture_rect)
                if img:
                    text = self.recognizer.recognize(img)
                    current_time = time.time()
                    # 文字变化且距离上次翻译已过足够时间
                    if text and text != last_text and (current_time - last_translate_time) > translate_interval:
                        last_text = text
                        last_translate_time = current_time
                        self.translate_and_display(text)
                        print(f"[DEBUG] OCR: {text[:50]}...")
                time.sleep(0.5)  # 捕获间隔（秒）

        self.capture_thread = Thread(target=_capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def process_image(self, img):
        """处理捕获的图片"""
        text = self.recognizer.recognize(img)
        if text:
            self.translate_and_display(text)

    def translate_and_display(self, text: str):
        """翻译并显示"""
        def _translate():
            # 检测语言
            source_lang = detect_language(text)

            # 翻译成中文（可配置）
            translation = self.translator.translate(text, target_lang='zh', source_lang=source_lang)

            # 发送信号更新 UI
            self.translation_done.emit(text, translation)

        thread = Thread(target=_translate)
        thread.daemon = True
        thread.start()

    def start_speech_recognition(self):
        """开始语音识别翻译"""
        # 如果正在翻译，先停止
        if self.is_translating:
            self.stop_translation()

        print("[DEBUG] 开始语音识别翻译模式 (实时流式)")
        self.is_translating = True
        self.stop_capture.clear()
        self.overlay.raise_()
        self.overlay.show()

        # 使用流式语音识别器
        self.streaming_recognizer = get_streaming_recognizer()
        self.streaming_recognizer.load_models()

        # 开始录音
        self.audio_capture.start()

        def audio_provider():
            """持续提供音频数据"""
            while not self.stop_capture.is_set():
                chunk = self.audio_capture.read_chunk()
                if chunk:
                    yield chunk
                time.sleep(0.1)

        def on_transcript(text):
            """识别结果回调"""
            if text:
                print(f"[STREAM] 识别: {text[:50]}...")
                self.translate_and_display(text)

        # 启动流式识别
        self.streaming_thread = Thread(
            target=lambda: self.streaming_recognizer.recognize_streaming(
                audio_callback=lambda: self.audio_capture.read_chunk(),
                result_callback=on_transcript
            )
        )
        self.streaming_thread.daemon = True
        self.streaming_thread.start()

    def _on_translation_done(self, original, translation):
        """翻译完成回调"""
        self.overlay.update_text(original, translation)

    def stop_translation(self):
        """停止翻译"""
        self.is_translating = False
        self.stop_capture.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            self.capture_thread = None
        # 停止流式识别
        if hasattr(self, 'streaming_recognizer') and self.streaming_recognizer:
            self.streaming_recognizer.stop()
        if hasattr(self, 'streaming_thread') and self.streaming_thread:
            self.streaming_thread.join(timeout=2)
        # 停止录音
        if hasattr(self, 'audio_capture') and self.audio_capture:
            self.audio_capture.stop()

    def toggle_overlay(self):
        """切换悬浮窗显示"""
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

    def quit(self):
        """退出应用"""
        self.stop_translation()
        self.hotkey_manager.stop()
        self.app.quit()

    def run(self):
        """运行应用"""
        # 显示初始提示
        msg = QMessageBox()
        msg.setWindowTitle("SubTrans")
        msg.setText(
            "SubTrans 已启动！\n\n"
            "快捷键：\n"
            "⌃⌥2 - 选择区域翻译\n"
            "⌃⌥3 - 选择窗口翻译\n"
            "⌃⌥4 - 显示/隐藏悬浮窗\n"
            "⌃⌥5 - 语音识别翻译\n\n"
            "点击托盘图标也可以操作。"
        )
        msg.exec()

        # 隐藏悬浮窗初始状态
        self.overlay.hide()

        sys.exit(self.app.exec())


def main():
    app = SubTransApp()
    app.run()


if __name__ == '__main__':
    main()
