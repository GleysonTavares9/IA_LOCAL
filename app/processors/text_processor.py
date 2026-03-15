import json
from typing import Dict, Any
from app.processors.base_processor import BaseProcessor
from app.utils.logger import logger

class TextProcessor(BaseProcessor):
    def extract_text(self, file_path: str) -> str:
        """Lê arquivos de texto direto (TXT, CSV, JSON)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de texto {file_path}: {e}")
            return ""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados básicos do arquivo de texto."""
        return {"type": "text"}
