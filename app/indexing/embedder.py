import requests
from typing import List, Union
from google import genai
from app.config.settings import (
    USE_EXTERNAL_API, 
    OLLAMA_BASE_URL, 
    EMBEDDING_MODEL_LOCAL, 
    GEMINI_API_KEY, 
    EXTERNAL_EMBEDDING_MODEL
)
from app.utils.logger import logger

class Embedder:
    def __init__(self):
        self.use_external = USE_EXTERNAL_API
        if self.use_external:
            # Inicializa o cliente Gemini conforme o documento 2
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = EXTERNAL_EMBEDDING_MODEL # Ex: "gemini-embedding-2-preview"
        else:
            self.ollama_url = f"{OLLAMA_BASE_URL}/api/embeddings"
            self.model = EMBEDDING_MODEL_LOCAL

    def get_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Gera embeddings para texto usando Ollama local ou Gemini API."""
        if self.use_external:
            return self._get_gemini_embeddings(text)
        else:
            return self._get_ollama_embeddings(text)

    def _get_gemini_embeddings(self, contents: Union[str, List[str]]) -> List[List[float]]:
        """Implementação baseada no documento 2 da Google."""
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=contents
            )
            # Se for uma única string, retorna uma lista contendo o embedding
            if isinstance(contents, str):
                return [result.embeddings[0].values]
            return [e.values for e in result.embeddings]
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings no Gemini: {e}")
            return []

    def _get_ollama_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Implementação local via Ollama."""
        try:
            texts = [text] if isinstance(text, str) else text
            embeddings = []
            for t in texts:
                response = requests.post(
                    self.ollama_url,
                    json={"model": self.model, "prompt": t}
                )
                if response.status_code == 200:
                    embeddings.append(response.json().get('embedding', []))
                else:
                    logger.error(f"Erro no Ollama: {response.text}")
            return embeddings
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings no Ollama: {e}")
            return []
