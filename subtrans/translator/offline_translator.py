"""
离线翻译器 - 使用 opus-mt 和 NLLB 模型
"""
import os
import torch
from typing import Optional
from threading import Thread

# 设置离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'  # 离线模式
os.environ['HF_HUB_OFFLINE'] = '1'


class OfflineTranslator:
    """翻译器 - 优先使用快速的 opus-mt 模型"""

    # 快速直达模型映射 (source, target) -> model_name
    DIRECT_MODELS = {
        ('en', 'zh'): 'Helsinki-NLP/opus-mt-en-zh',  # 英文→中文，已缓存，最快
        ('zh', 'en'): 'Helsinki-NLP/opus-mt-zh-en',  # 中文→英文，已缓存
        ('ja', 'zh'): 'Helsinki-NLP/opus-mt-ja-zh',  # 日文→中文
        ('ko', 'zh'): 'Helsinki-NLP/opus-mt-ko-zh',  # 韩文→中文
    }

    # 目标语言选项
    TARGET_LANGS = ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru']

    def __init__(self, device: str = None):
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = device
        self.pipe = None
        self.current_model = None

    def load_model(self, source_lang: str = 'auto', target_lang: str = 'zh'):
        """加载翻译模型"""
        model_name = None

        # 优先使用直达模型
        if source_lang != 'auto':
            model_name = self.DIRECT_MODELS.get((source_lang, target_lang))

        if model_name is None:
            # 默认使用 NLLB
            model_name = "facebook/nllb-200-distilled-600M"

        if self.current_model == model_name and self.pipe is not None:
            return

        print(f"正在加载翻译模型 {model_name}...")

        try:
            from transformers import pipeline
            self.pipe = pipeline(
                "translation",
                model=model_name,
                device=0 if self.device == 'cuda' else -1
            )
            self.current_model = model_name
            print("翻译模型加载完成！")
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise

    def translate(self, text: str, target_lang: str = 'zh', source_lang: str = None) -> str:
        """翻译文本"""
        if not text.strip():
            return ""

        self.load_model(source_lang or 'auto', target_lang)

        try:
            result = self.pipe(text)
            if result and len(result) > 0:
                return result[0]['translation_text']
            return ""
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[翻译失败: {e}]"

    def translate_async(self, text: str, target_lang: str = 'zh',
                       callback=None, source_lang: str = None):
        """异步翻译"""
        def _translate():
            result = self.translate(text, target_lang, source_lang)
            if callback:
                callback(result)

        thread = Thread(target=_translate)
        thread.start()


def detect_language(text: str) -> str:
    """检测文本语言"""
    try:
        from langdetect import detect
        lang = detect(text)
        return lang
    except Exception:
        # 基于字符范围判断
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return 'zh'
        elif any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return 'ja'
        elif any('\uac00' <= c <= '\ud7af' for c in text):
            return 'ko'
        elif any('\u0400' <= c <= '\u04ff' for c in text):
            return 'ru'
        elif any('\u0600' <= c <= '\u06ff' for c in text):
            return 'ar'
        elif any('\u0e00' <= c <= '\u0e7f' for c in text):
            return 'th'
        elif any('\u0900' <= c <= '\u097f' for c in text):
            return 'hi'
        else:
            return 'en'


# 全局翻译器实例
_translator: Optional[OfflineTranslator] = None


def get_translator() -> OfflineTranslator:
    """获取全局翻译器实例"""
    global _translator
    if _translator is None:
        _translator = OfflineTranslator()
    return _translator
