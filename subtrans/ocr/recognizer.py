"""
OCR 文字识别 - 使用 Tesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, List


class OCRRecognizer:
    def __init__(self, lang: str = None):
        """
        初始化 OCR 识别器

        Args:
            lang: Tesseract 语言代码，如 'eng', 'chi_sim', 'jpn', 'kor' 等
                  可以组合，如 'eng+chi_sim+jpn+kor'
        """
        if lang is None:
            # 默认支持多种语言
            lang = 'eng+chi_sim+chi_tra+jpn+kor'
        self.lang = lang

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        预处理图像以提高 OCR 准确率

        Args:
            image: PIL Image 对象

        Returns:
            预处理后的图像
        """
        # 调整大小（提高分辨率有助于识别）
        w, h = image.size
        if w < 800:
            new_w, new_h = 800, int(h * 800 / w)
            image = image.resize((new_w, new_h), Image.LANCZOS)

        # 转换为灰度
        img = image.convert('L')

        # 提高对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)

        # 提高锐度
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)

        # 应用阈值二值化（更高阈值减少背景干扰）
        img = img.point(lambda x: 0 if x < 150 else 255, '1')
        img = img.convert('L')

        return img

    def recognize(self, image: Image.Image) -> str:
        """
        从图片中识别文字

        Args:
            image: PIL Image 对象

        Returns:
            识别出的文字
        """
        try:
            # 预处理图像
            processed = self._preprocess_image(image)

            # 设置 Tesseract 配置
            # PSM 7 = 把文本当作单行处理（适合字幕）
            config = f'--oem 3 --psm 7'

            text = pytesseract.image_to_string(
                processed,
                lang=self.lang,
                config=config
            )

            # 清理文字
            text = self._clean_text(text)
            return text
        except Exception as e:
            print(f"OCR recognition error: {e}")
            return ""

    def recognize_with_boxes(self, image: Image.Image) -> List[dict]:
        """
        识别文字并返回每个字符的位置信息

        Args:
            image: PIL Image 对象

        Returns:
            包含文字和位置信息的字典列表
        """
        try:
            # 预处理图像
            processed = self._preprocess_image(image)

            data = pytesseract.image_to_data(
                processed,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )

            results = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
                    results.append({
                        'text': text,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': data['conf'][i]
                    })

            return results
        except Exception as e:
            print(f"OCR recognition error: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        """清理识别的文字"""
        # 移除多余空白
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        return '\n'.join(lines)

    @staticmethod
    def is_lang_available(lang: str) -> bool:
        """检查语言包是否可用"""
        available = pytesseract.get_languages()
        return lang in available


# 全局实例
_default_recognizer: Optional[OCRRecognizer] = None


def get_recognizer(lang: str = None) -> OCRRecognizer:
    """获取全局 OCR 识别器实例"""
    global _default_recognizer
    if _default_recognizer is None:
        _default_recognizer = OCRRecognizer(lang)
    return _default_recognizer
