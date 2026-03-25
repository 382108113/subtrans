"""
实时语音识别 - 使用 Whisper + Silero VAD
"""
import os
import time
import torch
import numpy as np
from typing import Optional, Callable

# 设置离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'


class StreamingSpeechRecognizer:
    """实时流式语音识别器"""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.pipe = None
        self.vad_model = None
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.is_streaming = False

    def load_models(self):
        """加载 VAD 和 Whisper 模型"""
        # 加载 Silero VAD
        if self.vad_model is None:
            try:
                import silero_vad
                self.vad_model = silero_vad.load_silero_vad(onnx=True)
                print(f"Silero VAD 模型已加载 (设备: {self.device})")
            except Exception as e:
                print(f"VAD 模型加载失败: {e}")
                self.vad_model = None

        # 加载 Whisper
        if self.pipe is None:
            print(f"正在加载语音识别模型 Whisper {self.model_size}...")
            print(f"使用设备: {self.device}")

            try:
                from transformers import pipeline
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=f"openai/whisper-{self.model_size}",
                    device=self.device,
                    torch_dtype=torch.float32
                )
                print("Whisper 模型加载完成！")
            except Exception as e:
                print(f"Whisper 模型加载失败: {e}")
                raise

    def _compute_energy(self, audio: np.ndarray) -> float:
        """计算音频能量"""
        return np.sqrt(np.mean(audio ** 2))

    def recognize_streaming(self, audio_callback, result_callback: Callable[[str], None],
                          speech_threshold: float = 0.5):
        """
        流式识别 - Silero VAD

        Args:
            audio_callback: 返回音频数据的回调
            result_callback: 识别结果回调
            speech_threshold: 语音检测阈值 (0-1)
        """
        self.load_models()

        self.is_streaming = True
        sample_rate = 16000
        vad_chunk_size = 512  # Silero VAD 需要 512 samples (16ms at 16kHz)
        audio_buffer = np.array([], dtype=np.float32)  # 累积的音频
        speech_buffer = []  # 累积的语音片段
        is_speaking = False
        last_speech_time = None

        def process_speech():
            nonlocal speech_buffer
            if not speech_buffer:
                return

            audio = np.concatenate(speech_buffer)
            speech_buffer = []

            if len(audio) > sample_rate * 30:
                audio = audio[-sample_rate * 30:]

            try:
                print(f"[VAD] 处理 {len(audio)/sample_rate:.1f}秒 语音...")
                result = self.pipe(audio, generate_kwargs={"task": "transcribe"})
                text = result.get("text", "").strip()
                if text:
                    print(f"[VAD] 识别: {text[:80]}...")
                    result_callback(text)
            except Exception as e:
                print(f"识别错误: {e}")

        while self.is_streaming:
            try:
                chunk = audio_callback()
                if chunk is None:
                    break

                if isinstance(chunk, bytes):
                    audio = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
                else:
                    audio = chunk

                # 累积音频
                audio_buffer = np.concatenate([audio_buffer, audio]) if len(audio_buffer) > 0 else audio

                # 处理累积的音频，每次取 512 samples
                while len(audio_buffer) >= vad_chunk_size:
                    vad_audio = audio_buffer[:vad_chunk_size]
                    audio_buffer = audio_buffer[vad_chunk_size:]

                    # VAD 检测
                    if self.vad_model is not None:
                        with torch.no_grad():
                            speech_prob = self.vad_model(torch.from_numpy(vad_audio), sample_rate).item()

                        is_speech = speech_prob > speech_threshold

                        if is_speech:
                            if not is_speaking:
                                is_speaking = True
                                print(f"[VAD] 开始说话 (prob={speech_prob:.2f})")
                            speech_buffer.append(vad_audio.copy())
                            last_speech_time = time.time()
                        else:
                            if is_speaking and speech_buffer:
                                silence = time.time() - last_speech_time if last_speech_time else 0
                                total_dur = sum(len(x) for x in speech_buffer) / sample_rate

                                if silence > 1.0 or total_dur >= 5.0:
                                    print(f"[VAD] 说话结束 (duration={total_dur:.1f}s)")
                                    process_speech()
                                    is_speaking = False
                                    speech_buffer = []
                    else:
                        # 能量检测回退
                        energy = self._compute_energy(vad_audio)
                        if energy > 0.01:
                            if not is_speaking:
                                is_speaking = True
                            speech_buffer.append(vad_audio.copy())
                            last_speech_time = time.time()

            except Exception as e:
                print(f"流式识别错误: {e}")
                continue

        if speech_buffer:
            process_speech()

    def stop(self):
        """停止流式识别"""
        self.is_streaming = False


# 全局实例
_streaming_recognizer: Optional[StreamingSpeechRecognizer] = None


def get_streaming_recognizer(model_size: str = "base") -> StreamingSpeechRecognizer:
    """获取全局流式语音识别器"""
    global _streaming_recognizer
    if _streaming_recognizer is None:
        _streaming_recognizer = StreamingSpeechRecognizer(model_size)
    return _streaming_recognizer
