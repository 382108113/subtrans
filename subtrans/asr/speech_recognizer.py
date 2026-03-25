"""
语音识别 - 使用 OpenAI Whisper
"""
import os
import torch
from typing import Optional

# 设置离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'  # 离线模式
os.environ['HF_HUB_OFFLINE'] = '1'


class SpeechRecognizer:
    """基于 Whisper 的语音识别"""

    def __init__(self, model_size: str = "base"):
        """
        初始化语音识别器

        Args:
            model_size: 模型大小，如 'tiny', 'base', 'small', 'medium', 'large-v3', 'large-v3-turbo'
        """
        self.model_size = model_size
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """加载模型"""
        if self.pipe is not None:
            return

        print(f"正在加载语音识别模型 Whisper {self.model_size}...")

        try:
            from transformers import pipeline

            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=f"openai/whisper-{self.model_size}",
                device=self.device,
                torch_dtype=torch.float32
            )
            print("语音识别模型加载完成！")
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise

    def recognize(self, audio_path: str = None, audio_data: bytes = None) -> str:
        """
        识别语音

        Args:
            audio_path: 音频文件路径
            audio_data: 音频数据（bytes）

        Returns:
            识别的文字
        """
        if self.pipe is None:
            self.load_model()

        try:
            import numpy as np
            import wave
            import io

            if audio_path:
                # 从文件加载
                with wave.open(audio_path, 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    sample_rate = wf.getframerate()
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            elif audio_data:
                # 从字节数据加载 WAV
                wav_io = io.BytesIO(audio_data)
                with wave.open(wav_io, 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    sample_rate = wf.getframerate()
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                return ""

            # 重采样到 16000（如果需要）
            if sample_rate != 16000:
                # 简单线性重采样
                ratio = 16000 / sample_rate
                new_length = int(len(audio) * ratio)
                indices = np.linspace(0, len(audio) - 1, new_length)
                audio = np.interp(indices, np.arange(len(audio)), audio)

            # 限制长度（Whisper 对长音频支持有限）
            max_audio_length = 30 * 16000  # 30秒
            if len(audio) > max_audio_length:
                audio = audio[:max_audio_length]

            # 识别（不指定语言让其自动检测）
            result = self.pipe(
                audio,
                generate_kwargs={"task": "transcribe"}
            )

            return result.get("text", "").strip()

        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""

    def recognize_from_file(self, audio_path: str) -> str:
        """从音频文件识别"""
        return self.recognize(audio_path=audio_path)


# 全局实例
_recognizer: Optional[SpeechRecognizer] = None


def get_speech_recognizer(model_size: str = "base") -> SpeechRecognizer:
    """获取全局语音识别器实例"""
    global _recognizer
    if _recognizer is None:
        _recognizer = SpeechRecognizer(model_size)
    return _recognizer
