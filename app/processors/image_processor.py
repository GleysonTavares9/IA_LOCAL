import requests
import base64
from typing import List, Dict, Any
from app.processors.base_processor import BaseProcessor
from app.config.settings import OLLAMA_BASE_URL, VISION_MODEL
from app.utils.logger import logger

class ImageProcessor(BaseProcessor):
    def extract_text(self, file_path: str) -> str:
        """Usa o modelo vision local para descrever a imagem."""
        logger.info(f"Processando imagem com {VISION_MODEL}: {file_path}")
        try:
            with open(file_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": VISION_MODEL,
                    "prompt": "Descreva detalhadamente o conteúdo desta imagem, incluindo qualquer texto visível (OCR).",
                    "images": [image_base64],
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Erro na API do Ollama para imagem: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Erro ao processar imagem {file_path}: {e}")
            return ""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados básicos da imagem."""
        # Poderia usar PIL para extrair EXIF, dimensões, etc.
        return {"type": "image"}
