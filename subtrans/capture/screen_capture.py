"""
屏幕区域截图
"""
import mss
import numpy as np
from PIL import Image
from PyQt6.QtCore import QRect
from typing import Optional


def capture_screen(rect: QRect) -> Optional[Image.Image]:
    """截取屏幕指定区域"""
    try:
        with mss.mss() as sct:
            # mss 使用 (left, top, right, bottom) 格式
            monitor = {
                "left": rect.left(),
                "top": rect.top(),
                "width": rect.width(),
                "height": rect.height()
            }

            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            return img
    except Exception as e:
        print(f"Screen capture error: {e}")
        return None


def capture_screen_full() -> Optional[Image.Image]:
    """截取整个屏幕"""
    try:
        with mss.mss() as sct:
            # 截取主屏幕
            monitor = sct.monitors[1]  # 索引1是主屏幕
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img
    except Exception as e:
        print(f"Full screen capture error: {e}")
        return None


def save_screenshot(img: Image.Image, filepath: str) -> bool:
    """保存截图到文件"""
    try:
        img.save(filepath)
        return True
    except Exception as e:
        print(f"Save screenshot error: {e}")
        return False
