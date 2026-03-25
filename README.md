# SubTrans

> 🤖 AI-Generated: This project was built with AI assistance

实时视频/游戏字幕翻译软件，带有浮动 overlay 显示。
Real-time subtitle translation software with floating overlay display for video games.

## Features | 功能特性

- **屏幕区域选择** - 选择需要翻译的屏幕区域
- **浮动翻译窗口** - 显示翻译结果的浮动 overlay
- **语音识别翻译** - 实时语音识别并翻译
- **OCR 文字识别** - 捕获屏幕文字并进行翻译

| English | 中文 |
|---------|------|
| Screen region selection | 屏幕区域选择 |
| Floating translation window | 浮动翻译窗口 |
| Speech recognition & translation | 语音识别翻译 |
| OCR text recognition | OCR 文字识别 |

## System Requirements | 系统要求

- **操作系统 | OS**: macOS
- **Python**: 3.9+
- **内存 | RAM**: 推荐 8GB+ | Recommended 8GB+
- **音频 | Audio**: BlackHole 2ch (用于系统音频捕获 | for system audio capture)

## Tech Stack | 技术栈

| Component | 技术 |
|-----------|------|
| Speech Recognition | Whisper (base model) + Silero VAD |
| Translation Engine | Ollama (qwen3.5:0.8b) |
| UI Framework | PyQt6 |
| Audio Capture | BlackHole 2ch + PyAudio |
| OCR | Tesseract |

## Installation | 安装步骤

### 1. Clone the repository | 克隆仓库

```bash
git clone https://github.com/382108113/subtrans.git
cd subtrans
```

### 2. Create virtual environment (recommended) | 创建虚拟环境 (推荐)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies | 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. Install system dependencies | 安装系统依赖

```bash
# 安装 Tesseract (OCR)
brew install tesseract tesseract-lang

# 安装 BlackHole (音频捕获)
brew install blackhole-2ch
```

### 5. Configure Ollama | 配置 Ollama

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载翻译模型
ollama pull qwen3.5:0.8b
```

### 6. Configure Audio (Important!) | 配置音频 (重要!)

要让软件捕获系统音频，需要设置音频路由：

1. 打开 **系统设置 → 声音 → 输出**
2. 选择 **BlackHole 2ch** 作为输出设备
3. 或者使用多输出设备，将 BlackHole 2ch 与扬声器/耳机一起选中

To capture system audio, configure audio routing:

1. Open **System Settings → Sound → Output**
2. Select **BlackHole 2ch** as output device
3. Or use multi-output device, selecting both BlackHole 2ch and speakers/headphones

### 7. Grant Screen Recording Permission | 授予屏幕录制权限

软件需要屏幕录制权限来捕获屏幕内容：
1. 打开 **系统设置 → 隐私与安全性 → 屏幕录制**
2. 添加并启用你的 Python 应用或终端

The software needs screen recording permission:
1. Open **System Settings → Privacy & Security → Screen Recording**
2. Add and enable your Python app or terminal

### 8. Run | 运行

```bash
python run.py
```

## Usage | 使用方法

### Hotkeys | 热键

| Hotkey | 功能 | Description |
|--------|------|-------------|
| Ctrl+Alt+2 | 选择翻译区域 | Select translation region |
| Ctrl+Alt+3 | 显示/隐藏浮动窗口 | Toggle floating window |
| Ctrl+Alt+4 | 开始/停止语音翻译 | Start/stop speech translation |
| Ctrl+Alt+5 | OCR 截图翻译 | OCR screenshot translation |

### Speech Translation Mode | 语音翻译模式

1. 按 Ctrl+Alt+4 开始语音翻译
2. 对着麦克风说话，软件会实时识别并翻译
3. 再次按 Ctrl+Alt+4 停止

1. Press Ctrl+Alt+4 to start speech translation
2. Speak into the microphone, software will recognize and translate in real-time
3. Press Ctrl+Alt+4 again to stop

### OCR Translation Mode | OCR 翻译模式

1. 按 Ctrl+Alt+5 进入 OCR 模式
2. 选择要翻译的屏幕区域
3. 软件会识别区域内的文字并翻译显示

1. Press Ctrl+Alt+5 to enter OCR mode
2. Select the screen region to translate
3. Software will recognize and translate the text in the region

## Troubleshooting | 常见问题

### Q: 语音识别不工作？ | Speech recognition not working?
- 检查麦克风权限是否授予 | Check if microphone permission is granted
- 检查 BlackHole 是否正确配置 | Check if BlackHole is configured correctly
- 确保 Ollama 服务正在运行 | Ensure Ollama service is running

### Q: 翻译质量不好？ | Poor translation quality?
- qwen3.5:0.8b 是轻量模型，如需更好效果可换用更大模型
- qwen3.5:0.8b is a lightweight model, switch to a larger model for better results

### Q: 音频延迟高？ | High audio latency?
- 尝试降低音频缓冲大小 | Try reducing audio buffer size
- 检查系统负载 | Check system load

## Project Structure | 项目结构

```
subtrans/
├── main.py                 # 主程序入口 | Main entry point
├── asr/                    # 语音识别模块 | Speech recognition module
│   ├── audio_capture.py    # 音频捕获 | Audio capture
│   ├── speech_recognizer.py # Whisper 识别 | Whisper recognition
│   └── streaming_recognizer.py # 流式识别 + VAD | Streaming + VAD
├── capture/                # 屏幕捕获模块 | Screen capture module
├── ocr/                    # OCR 文字识别 | OCR text recognition
├── translator/             # 翻译模块 | Translation module
│   └── ollama_translator.py # Ollama 翻译 | Ollama translation
├── ui/                     # UI 模块 | UI module
│   ├── overlay.py          # 浮动窗口 | Floating window
│   └── selection.py        # 区域选择 | Region selection
└── utils/                  # 工具模块 | Utilities module
    └── hotkeys.py          # 全局热键 | Global hotkeys
```

## Build & Package | 构建打包

```bash
# 安装 pyinstaller
pip install pyinstaller

# 打包
rm -rf build dist
python3 -m PyInstaller SubTrans.spec

# 运行打包后的程序
./dist/SubTrans
```

## License | 许可证

MIT License

---

⭐ Star History

If you find this project useful, please give it a Star!
如果你觉得这个项目有用，请给个 Star！
