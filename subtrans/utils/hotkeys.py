"""
全局快捷键管理
"""
from typing import Callable, Optional
from pynput import keyboard
from threading import Thread
import time


class GlobalHotkeyManager:
    """全局快捷键管理器"""

    def __init__(self, app=None):
        self.hotkeys: dict = {}
        self.listener: Optional[keyboard.Listener] = None
        self.current_keys: set = set()
        self._running = False
        self._app = app  # Qt app instance

    def register(self, key_combination: str, callback: Callable):
        """注册快捷键"""
        self.hotkeys[key_combination.lower()] = callback

    def unregister(self, key_combination: str):
        """取消注册快捷键"""
        self.hotkeys.pop(key_combination.lower(), None)

    def start(self):
        """启动监听"""
        if self._running:
            return

        self._running = True

        def on_press(key):
            try:
                key_name = self._get_key_name(key)
                if key_name:
                    self.current_keys.add(key_name)
                    self._check_hotkeys()
            except Exception as e:
                print(f"Hotkey press error: {e}")

        def on_release(key):
            try:
                key_name = self._get_key_name(key)
                if key_name:
                    self.current_keys.discard(key_name)
            except Exception as e:
                print(f"Hotkey release error: {e}")

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def stop(self):
        """停止监听"""
        self._running = False
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _get_key_name(self, key) -> Optional[str]:
        """获取键名称"""
        key_map = {
            keyboard.Key.cmd: 'cmd',
            keyboard.Key.ctrl: 'ctrl',
            keyboard.Key.alt: 'alt',
            keyboard.Key.shift: 'shift',
            keyboard.Key.esc: 'esc',
            keyboard.Key.space: 'space',
            keyboard.Key.enter: 'enter',
            keyboard.Key.tab: 'tab',
            keyboard.Key.f1: 'f1',
            keyboard.Key.f2: 'f2',
            keyboard.Key.f3: 'f3',
            keyboard.Key.f4: 'f4',
            keyboard.Key.f5: 'f5',
            keyboard.Key.f6: 'f6',
            keyboard.Key.f7: 'f7',
            keyboard.Key.f8: 'f8',
            keyboard.Key.f9: 'f9',
            keyboard.Key.f10: 'f10',
            keyboard.Key.f11: 'f11',
            keyboard.Key.f12: 'f12',
        }

        if key in key_map:
            return key_map[key]

        try:
            if hasattr(key, 'char'):
                return key.char.lower()
            elif hasattr(key, 'vk'):
                vk = key.vk
                if 65 <= vk <= 90:
                    return chr(vk).lower()
                if 48 <= vk <= 57:
                    return chr(vk)
        except:
            pass

        return None

    def _check_hotkeys(self):
        """检查是否有快捷键被触发"""
        active_keys = self.current_keys.copy()

        for combo, callback in self.hotkeys.items():
            parts = set(combo.split('+'))
            if parts.issubset(active_keys):
                # 使用 QTimer.singleShot 确保在主线程执行
                try:
                    from PyQt6.QtCore import QTimer
                    if self._app:
                        QTimer.singleShot(0, callback)
                    else:
                        callback()
                except Exception as e:
                    print(f"Hotkey callback error: {e}")


# 全局实例
_hotkey_manager: Optional[GlobalHotkeyManager] = None


def get_hotkey_manager(app=None) -> GlobalHotkeyManager:
    """获取全局快捷键管理器"""
    global _hotkey_manager
    if _hotkey_manager is None:
        _hotkey_manager = GlobalHotkeyManager(app)
    return _hotkey_manager
