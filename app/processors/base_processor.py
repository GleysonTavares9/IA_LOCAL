from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProcessor(ABC):
    """Classe base para todos os processadores de arquivos."""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extrai o texto bruto do arquivo."""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados específicos do arquivo."""
        pass
