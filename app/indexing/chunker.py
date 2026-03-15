from typing import List, Dict, Any
from app.config.settings import CHUNK_SIZE, CHUNK_OVERLAP

class TextChunker:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Divide o texto em chunks menores preservando o contexto."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk_content = text[start:end]
            
            # Tenta encontrar o fim de uma frase para não cortar no meio
            if end < text_len:
                last_period = chunk_content.rfind('.')
                if last_period != -1 and last_period > self.chunk_size * 0.8:
                    end = start + last_period + 1
                    chunk_content = text[start:end]
            
            chunks.append({
                'content': chunk_content,
                'metadata_json': str(metadata) if metadata else None
            })
            
            start = end - self.chunk_overlap
            if start >= text_len:
                break
                
        return chunks
