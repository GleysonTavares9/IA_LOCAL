import PyPDF2
from typing import List, Dict, Any
from app.processors.base_processor import BaseProcessor
from app.utils.logger import logger

class PDFProcessor(BaseProcessor):
    def extract_text(self, file_path: str) -> str:
        """Extrai texto de um arquivo PDF."""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {e}")
        return text

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados do PDF."""
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info = reader.metadata
                if info:
                    metadata = {
                        'author': info.get('/Author', ''),
                        'creator': info.get('/Creator', ''),
                        'producer': info.get('/Producer', ''),
                        'subject': info.get('/Subject', ''),
                        'title': info.get('/Title', ''),
                        'pages': len(reader.pages)
                    }
        except Exception as e:
            logger.error(f"Erro ao extrair metadados do PDF {file_path}: {e}")
        return metadata
