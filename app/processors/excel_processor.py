import pandas as pd
from typing import Dict, Any
from app.processors.base_processor import BaseProcessor
from app.utils.logger import logger

class ExcelProcessor(BaseProcessor):
    def extract_text(self, file_path: str) -> str:
        """Converte planilhas Excel para texto estruturado."""
        text = ""
        try:
            # Lê todas as abas
            xl = pd.ExcelFile(file_path)
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)
                text += f"--- Aba: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n\n"
        except Exception as e:
            logger.error(f"Erro ao extrair texto do Excel {file_path}: {e}")
        return text

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados básicos do Excel."""
        metadata = {}
        try:
            xl = pd.ExcelFile(file_path)
            metadata = {
                'sheets': xl.sheet_names,
                'num_sheets': len(xl.sheet_names)
            }
        except Exception as e:
            logger.error(f"Erro ao extrair metadados do Excel {file_path}: {e}")
        return metadata
