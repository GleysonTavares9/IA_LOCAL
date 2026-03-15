import requests
from typing import List, Dict, Any
from google import genai
from app.config.settings import (
    USE_EXTERNAL_API, 
    OLLAMA_BASE_URL, 
    LLM_MODEL_LOCAL, 
    GEMINI_API_KEY, 
    EXTERNAL_LLM_MODEL
)
from app.utils.logger import logger

class AnswerGenerator:
    def __init__(self):
        self.use_external = USE_EXTERNAL_API
        if self.use_external:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = EXTERNAL_LLM_MODEL
        else:
            self.ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
            self.model = LLM_MODEL_LOCAL

    def generate_answer(self, prompt: str, context: str) -> str:
        """Gera uma resposta baseada no contexto fornecido."""
        full_prompt = f"""
        Você é um assistente de IA empresarial. Use o contexto abaixo para responder à pergunta de forma profissional e precisa.
        Se a resposta não estiver no contexto, diga que não sabe com base nos documentos internos.
        Sempre cite as fontes mencionadas no contexto.

        CONTEXTO:
        {context}

        PERGUNTA:
        {prompt}

        RESPOSTA:
        """
        
        if self.use_external:
            return self._generate_gemini_answer(full_prompt)
        else:
            return self._generate_ollama_answer(full_prompt)

    def _generate_gemini_answer(self, prompt: str) -> str:
        """Gera resposta usando a API do Gemini."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta no Gemini: {e}")
            return "Erro ao processar sua solicitação via API externa."

    def _generate_ollama_answer(self, prompt: str) -> str:
        """Gera resposta usando o Ollama local."""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Erro no Ollama: {response.text}")
                return "Erro ao processar sua solicitação localmente."
        except Exception as e:
            logger.error(f"Erro ao gerar resposta no Ollama: {e}")
            return "Erro de conexão com o servidor local de IA."
