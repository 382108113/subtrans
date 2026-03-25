"""
实时音频捕获 - 从 BlackHole 设备捕获系统音频
"""
import pyaudio
import numpy as np
import wave
import io
from typing import Optional, Callable

from subtrans import config


class AudioCapture:
    """实时音频捕获器"""

    def __init__(self, device_index: int = None, sample_rate: int = None, chunk_size: int = None):
        """
        初始化音频捕获

        Args:
            device_index: 音频设备索引，None 表示默认设备
            sample_rate: 采样率，Whisper 需要 16000
            chunk_size: 每次读取的帧数
        """
        self.device_index = device_index if device_index is not None else config.AUDIO_DEVICE_INDEX
        self.sample_rate = sample_rate or config.AUDIO_SAMPLE_RATE
        self.chunk_size = chunk_size or config.AUDIO_CHUNK_SIZE
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.frames = []

    def list_devices(self):
        """列出所有音频输入设备"""
        p = pyaudio.PyAudio()
        devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append((i, info['name'], info['maxInputChannels']))
        p.terminate()
        return devices

    def find_blackhole_device(self) -> Optional[int]:
        """查找 BlackHole 设备索引"""
        devices = self.list_devices()
        for idx, name, _ in devices:
            if 'blackhole' in name.lower():
                return idx
        return None

    def start(self):
        """开始录音"""
        if self.is_recording:
            return

        self.audio = pyaudio.PyAudio()

        # 如果没指定设备，尝试找 BlackHole
        device_index = self.device_index
        if device_index is None:
            device_index = self.find_blackhole_device()
            if device_index is None:
                print("警告: 未找到 BlackHole 设备，使用默认设备")

        # 打开音频流
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )

        self.is_recording = True
        self.frames = []
        print(f"开始录音 (设备: {device_index}, 采样率: {self.sample_rate})")

    def read_chunk(self) -> Optional[bytes]:
        """读取一段音频数据"""
        if not self.is_recording:
            return None
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            self.frames.append(data)
            return data
        except Exception as e:
            print(f"读取音频错误: {e}")
            return None

    def stop(self) -> bytes:
        """停止录音并返回 WAV 数据"""
        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio:
            self.audio.terminate()
            self.audio = None

        # 合并为 WAV
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))

        data = buffer.getvalue()
        self.frames = []
        return data

    def get_latest_audio(self, seconds: float = 5.0) -> bytes:
        """获取最近 N 秒的音频数据"""
        # 先读取一些新数据
        if self.is_recording and self.stream:
            chunks_to_read = int(seconds * self.sample_rate / self.chunk_size)
            for _ in range(min(chunks_to_read, 10)):  # 最多读10块
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    self.frames.append(data)
                except:
                    break

        if not self.frames:
            return b''

        # 计算需要的帧数
        total_chunks = int(seconds * self.sample_rate / self.chunk_size)
        recent_frames = self.frames[-total_chunks:] if len(self.frames) > total_chunks else self.frames

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(recent_frames))

        return buffer.getvalue()
