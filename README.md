# SubTrans

实时视频/游戏字幕翻译软件，带有浮动 overlay 显示。

## 功能特性

- **屏幕区域选择** - 选择需要翻译的屏幕区域
- **浮动翻译窗口** - 显示翻译结果的浮动 overlay
- **语音识别翻译** - 实时语音识别并翻译
- **OCR 文字识别** - 捕获屏幕文字并进行翻译

## 系统要求

- **操作系统**: macOS
- **Python**: 3.9+
- **内存**: 推荐 8GB+
- **音频**: BlackHole 2ch (用于系统音频捕获)

## 技术栈

| 组件 | 技术 |
|------|------|
| 语音识别 | Whisper (base model) + Silero VAD |
| 翻译引擎 | Ollama (qwen3.5:0.8b) |
| UI框架 | PyQt6 |
| 音频捕获 | BlackHole 2ch + PyAudio |
| OCR | Tesseract |

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/382108113/subtrans.git
cd subtrans
```

### 2. 创建虚拟环境 (推荐)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 安装系统依赖

```bash
# 安装 Tesseract (OCR)
brew install tesseract tesseract-lang

# 安装 BlackHole (音频捕获)
brew install blackhole-2ch
```

### 5. 配置 Ollama

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载翻译模型 (首次运行时会自动下载)
ollama pull qwen3.5:0.8b
```

### 6. 配置音频 (重要!)

要让软件捕获系统音频，需要设置音频路由：

1. 打开 **系统设置 → 声音 → 输出**
2. 选择 **BlackHole 2ch** 作为输出设备
3. 或者使用多输出设备，将 BlackHole 2ch 与扬声器/耳机一起选中

### 7. 授予屏幕录制权限

软件需要屏幕录制权限来捕获屏幕内容：
1. 打开 **系统设置 → 隐私与安全性 → 屏幕录制**
2. 添加并启用你的 Python 应用或终端

### 8. 运行

```bash
python run.py
```

## 使用方法

### 热键

| 热键 | 功能 |
|------|------|
| Ctrl+Alt+2 | 选择翻译区域 |
| Ctrl+Alt+3 | 显示/隐藏浮动翻译窗口 |
| Ctrl+Alt+4 | 开始/停止语音实时翻译 |
| Ctrl+Alt+5 | OCR 截图翻译 |

### 语音翻译模式

1. 按 Ctrl+Alt+4 开始语音翻译
2. 对着麦克风说话，软件会实时识别并翻译
3. 再次按 Ctrl+Alt+4 停止

### OCR 翻译模式

1. 按 Ctrl+Alt+5 进入 OCR 模式
2. 选择要翻译的屏幕区域
3. 软件会识别区域内的文字并翻译显示

## 常见问题

### Q: 语音识别不工作？
- 检查麦克风权限是否授予
- 检查 BlackHole 是否正确配置
- 确保 Ollama 服务正在运行

### Q: 翻译质量不好？
- qwen3.5:0.8b 是轻量模型，如需更好效果可换用更大模型
- 确保源语言检测正确

### Q: 音频延迟高？
- 尝试降低音频缓冲大小
- 检查系统负载

## 开发

### 项目结构

```
subtrans/
├── main.py                 # 主程序入口
├── asr/                    # 语音识别模块
│   ├── audio_capture.py    # 音频捕获
│   ├── speech_recognizer.py # Whisper 识别
│   └── streaming_recognizer.py # 流式识别 + VAD
├── capture/                # 屏幕捕获模块
├── ocr/                    # OCR 文字识别
├── translator/             # 翻译模块
│   └── ollama_translator.py # Ollama 翻译
├── ui/                     # UI 模块
│   ├── overlay.py          # 浮动窗口
│   └── selection.py        # 区域选择
└── utils/                  # 工具模块
    └── hotkeys.py          # 全局热键
```

### 构建打包

```bash
pip install pyinstaller
pyinstaller SubTrans.spec
```

## 许可证

MIT License

## Star History

如果你觉得这个项目有用，请给个 Star！
