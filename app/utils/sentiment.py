import requests
from typing import Dict, Any
from google import genai
from app.config.settings import (
    USE_EXTERNAL_API, 
    OLLAMA_BASE_URL, 
    LLM_MODEL_LOCAL, 
    GEMINI_API_KEY, 
    EXTERNAL_LLM_MODEL
)
from app.utils.logger import logger

class SentimentAnalyzer:
    def __init__(self):
        self.use_external = USE_EXTERNAL_API
        if self.use_external:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = EXTERNAL_LLM_MODEL
        else:
            self.ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
            self.model = LLM_MODEL_LOCAL

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analisa o sentimento do texto e retorna uma classificação e pontuação."""
        prompt = f"""
        Analise o sentimento do seguinte texto e responda APENAS com um JSON no formato:
        {{"sentiment": "positivo" | "neutro" | "negativo", "score": 0.0 a 1.0, "reason": "breve explicação"}}
        
        TEXTO: "{text}"
        """
        
        try:
            if self.use_external:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                result_text = response.text
            else:
                response = requests.post(
                    self.ollama_url,
                    json={"model": self.model, "prompt": prompt, "stream": False}
                )
                result_text = response.json().get('response', '{}')
            
            # Limpeza básica para garantir que seja um JSON válido
            import json
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"sentiment": "neutro", "score": 0.5, "reason": "Não foi possível analisar."}
            
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {"sentiment": "neutro", "score": 0.5, "reason": "Erro técnico."}
