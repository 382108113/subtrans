"""
SubTrans 配置文件
Configuration file for SubTrans
"""

# ============================================================
# 翻译设置 | Translation Settings
# ============================================================
TRANSLATION_MODEL = "qwen3.5:0.8b"  # Ollama 模型名称 | Ollama model name
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama 服务地址 | Ollama service URL
TARGET_LANGUAGE = "zh"  # 目标语言 | Target language

# ============================================================
# 语音识别设置 | Speech Recognition Settings
# ============================================================
WHISPER_MODEL_SIZE = "base"  # tiny, base, small, medium, large-v3, large-v3-turbo
SPEECH_THRESHOLD = 0.5  # 语音检测阈值 (0-1) | Speech detection threshold

# ============================================================
# 音频设置 | Audio Settings
# ============================================================
AUDIO_SAMPLE_RATE = 16000  # 采样率 (Hz) | Sample rate
AUDIO_CHUNK_SIZE = 4096  # 音频块大小 | Audio chunk size
AUDIO_DEVICE_INDEX = None  # None = 默认设备 | None = default device

# ============================================================
# 热键设置 | Hotkey Settings
# ============================================================
HOTKEY_SELECT_REGION = "ctrl+alt+2"  # 选择翻译区域 | Select translation region
HOTKEY_TOGGLE_OVERLAY = "ctrl+alt+3"  # 显示/隐藏浮动窗口 | Toggle floating window
HOTKEY_SPEECH_MODE = "ctrl+alt+4"  # 开始/停止语音翻译 | Start/stop speech translation
HOTKEY_OCR_MODE = "ctrl+alt+5"  # OCR 截图翻译 | OCR screenshot translation

# ============================================================
# OCR 设置 | OCR Settings
# ============================================================
OCR_LANGUAGES = "eng+chi_sim"  # Tesseract 语言 | Tesseract languages
OCR_CONFIDENCE_THRESHOLD = 60  # 识别置信度阈值 | Recognition confidence threshold

# ============================================================
# UI 设置 | UI Settings
# ============================================================
OVERLAY_WIDTH = 500  # 浮动窗口宽度 | Overlay window width
OVERLAY_HEIGHT = 200  # 浮动窗口高度 | Overlay window height
OVERLAY_OPACITY = 0.9  # 窗口透明度 (0-1) | Window opacity
OVERLAY_POSITION_X = 100  # 窗口 X 坐标 | Window X position
OVERLAY_POSITION_Y = 100  # 窗口 Y 坐标 | Window Y position
