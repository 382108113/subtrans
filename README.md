# SubTrans

实时视频/游戏字幕翻译软件，带有浮动 overlay 显示。

## 功能特性

- **屏幕区域选择** - Ctrl+Alt+2 选择需要翻译的屏幕区域
- **浮动翻译窗口** - Ctrl+Alt+3 显示/隐藏浮动翻译 overlay
- **语音识别翻译** - Ctrl+Alt+4 开启语音实时翻译模式
- **OCR 文字识别** - 捕获屏幕文字并进行翻译

## 技术栈

- **语音识别**: Whisper (base model) + Silero VAD
- **翻译引擎**: Ollama (qwen3.5:0.8b)
- **UI框架**: PyQt6
- **音频捕获**: BlackHole 2ch + PyAudio
- **OCR**: Tesseract

## 系统要求

- macOS
- Python 3.9+
- BlackHole 2ch (用于系统音频捕获)
- Ollama (本地运行)

## 安装依赖

```bash
pip install -r requirements.txt

# 安装 Tesseract (macOS)
brew install tesseract

# 安装 BlackHole
brew install blackhole-2ch
```

## 配置 Ollama

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载翻译模型
ollama pull qwen3.5:0.8b
```

## 运行

```bash
python run.py
```

## 热键

| 热键 | 功能 |
|------|------|
| Ctrl+Alt+2 | 选择翻译区域 |
| Ctrl+Alt+3 | 切换浮动窗口 |
| Ctrl+Alt+4 | 开始/停止语音翻译 |
| Ctrl+Alt+5 | OCR 截图翻译 |

## 许可

MIT License
