"""
在线翻译器 - 使用 Ollama 本地大模型
"""
import requests
import subprocess
import time
from typing import Optional

from subtrans import config


class OllamaTranslator:
    """基于 Ollama 的翻译器"""

    def __init__(self, model: str = None, base_url: str = None):
        """
        初始化 Ollama 翻译器

        Args:
            model: Ollama 模型名称
            base_url: Ollama 服务地址
        """
        self.model = model or config.TRANSLATION_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self._server_process = None

    def start_server(self):
        """启动 Ollama 服务"""
        # 检查是否已经在运行
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print("Ollama 服务已运行")
                return True
        except:
            pass

        print("正在启动 Ollama 服务...")
        try:
            # 在后台启动 ollama serve
            self._server_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # 等待服务启动
            for _ in range(30):  # 最多等待30秒
                try:
                    response = requests.get(f"{self.base_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        print("Ollama 服务启动成功")
                        return True
                except:
                    time.sleep(1)
            print("Ollama 服务启动超时")
            return False
        except Exception as e:
            print(f"启动 Ollama 失败: {e}")
            return False

    def stop_server(self):
        """停止 Ollama 服务"""
        if self._server_process:
            self._server_process.terminate()
            self._server_process = None

    def load_model(self, target_lang: str = 'zh'):
        """预加载模型（Ollama 不需要，预留接口）"""
        self.start_server()

    def translate(self, text: str, target_lang: str = "zh", source_lang: str = None) -> str:
        """
        翻译文本

        Args:
            text: 源文本
            target_lang: 目标语言 (zh/en/ja/ko)
            source_lang: 源语言 (可选)

        Returns:
            翻译后的文本
        """
        if not text.strip():
            return ""

        # 构建提示词
        source = source_lang or "auto"
        lang_map = {"zh": "中文", "en": "英文", "ja": "日文", "ko": "韩文"}
        target_name = lang_map.get(target_lang, target_lang)

        prompt = f"""请将以下{source}文本翻译成{target_name}，只输出翻译结果，不要解释，不要思考过程：

{text}"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,  # 关闭思考过程
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500,
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"[翻译失败: HTTP {response.status_code}]"

        except requests.exceptions.Timeout:
            return "[翻译超时]"
        except Exception as e:
            return f"[翻译错误: {e}]"

    def translate_async(self, text: str, target_lang: str = "zh",
                       callback=None, source_lang: str = None):
        """异步翻译"""
        def _translate():
            result = self.translate(text, target_lang, source_lang)
            if callback:
                callback(result)

        import threading
        thread = threading.Thread(target=_translate)
        thread.start()


# 全局实例
_translator: Optional[OllamaTranslator] = None


def get_ollama_translator(model: str = None) -> OllamaTranslator:
    """获取全局 Ollama 翻译器"""
    global _translator
    if model is None:
        model = config.TRANSLATION_MODEL
    if _translator is None:
        _translator = OllamaTranslator(model)
        _translator.start_server()
    return _translator
