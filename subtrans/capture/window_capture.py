"""
窗口捕获 - 使用 PyObjC 调用 macOS CGWindowList API
"""
import subprocess
import json
from dataclasses import dataclass
from typing import List, Optional

try:
    import AppKit
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False


@dataclass
class WindowInfo:
    window_id: int
    owner_name: str
    window_name: str
    bounds: dict


def get_window_list() -> List[WindowInfo]:
    """获取当前所有窗口列表"""
    if not HAS_APPKIT:
        return []

    windows = []

    # 使用 CGWindowListCopyWindowInfo 获取窗口列表
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOption

        options = kCGWindowListOption | 0x2  # kCGWindowListExcludeOnScreenWindows
        window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

        for window in window_list:
            try:
                window_id = window.get('kCGWindowNumber', 0)
                owner = window.get('kCGWindowOwnerName', '')
                name = window.get('kCGWindowName', '')
                bounds = window.get('kCGWindowBounds', {})

                # 过滤掉系统窗口
                if owner and bounds.get('Width', 0) > 50 and bounds.get('Height', 0) > 50:
                    windows.append(WindowInfo(
                        window_id=window_id,
                        owner_name=owner,
                        window_name=name,
                        bounds=bounds
                    ))
            except Exception:
                continue
    except Exception as e:
        print(f"Error getting window list: {e}")

    return windows


def capture_window(window_id: int) -> Optional[bytes]:
    """捕获指定窗口的画面"""
    if not HAS_APPKIT:
        return None

    try:
        from AppKit import NSScreen
        from Quartz import CGWindowID, CGWindowImageBounds, CGWindowListCreateImage

        # 捕获指定窗口
        image = CGWindowListCreateImage(
            ((0, 0), (0, 0)),
            0,
            window_id,
            0x2 | 0x4  # kCGWindowImageBounds | kCGWindowImageBestResolution
        )

        if image is None:
            return None

        # 将 CGImage 转换为 PNG 数据
        from AppKit import NSImage, NSBitmapImageRep
        import Foundation

        ns_image = NSImage.alloc().initWithCGImage_size_(image, (0, 0))
        if ns_image is None:
            return None

        # 转换为 PNG
        rep = NSBitmapImageRep.imageRepWithData_(ns_image.TIFFRepresentation())
        if rep is None:
            return None

        png_data = rep.representationUsingType_properties_(
            NSBitmapImageRep.PNGCompressionFactor
        )
        return png_data

    except Exception as e:
        print(f"Error capturing window: {e}")
        return None


def get_window_by_name(owner_name: str = None, window_name: str = None) -> Optional[WindowInfo]:
    """根据名称查找窗口"""
    windows = get_window_list()
    for window in windows:
        if owner_name and owner_name.lower() in window.owner_name.lower():
            if window_name is None or (window.window_name and window_name.lower() in window.window_name.lower()):
                return window
    return None
