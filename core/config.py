"""
core/config.py — Configurações centralizadas da IA Local RAG
Todas as variáveis de ambiente são carregadas aqui com valores padrão seguros.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env a partir da raiz do projeto
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


@dataclass(frozen=True)
class Config:
    # Paths
    base_dir: Path = _BASE_DIR
    docs_pdfs: Path = _BASE_DIR / "documentos" / "pdfs"
    docs_planilhas: Path = _BASE_DIR / "documentos" / "planilhas"
    docs_outros: Path = _BASE_DIR / "documentos" / "outros"
    chroma_path: Path = _BASE_DIR / "banco_vetorial"
    dados_db: Path = _BASE_DIR / "dados_db"
    logs_path: Path = _BASE_DIR / "logs"

    # Ollama
    ollama_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.2")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-minilm")

    # Cloud APIs (Opcionais)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")

    # Provedor padrão
    provider_default: str = os.getenv("AI_PROVIDER", "local") # local, openai, groq, gemini

    # RAG
    collection_name: str = os.getenv("COLLECTION_NAME", "minha_base_conhecimento")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K_RESULTS", "4"))
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dados_db/base.db")

    # Prompt
    # Prompt Universal Nível NASA
    prompt_template: str = """VOCÊ É A UNIVERSAL INTELLIGENCE SOBERANA - UM SUPERCOMPUTADOR DE ANÁLISE DOCUMENTAL.
Sua capacidade de processamento envolve raciocínio lógico avançado, análise técnica e extração cirúrgica de dados de qualquer domínio.

DOMÍNIOS DE EXPERTISE:
1. ANÁLISE CONTÁBIL: Domínio total de balancetes. Colunas típicas: [Código] [Nº] [Conta] [Saldo Anterior] [Débito] [Crédito] [Saldo Atual].
2. ANÁLISE JURÍDICA: Identificação de cláusulas, riscos e prazos.
3. ENGENHARIA E TÉCNICA: Leitura de manuais, especificações e normas.
4. CIÊNCIA DE DADOS: Síntese de informações dispersas em grandes volumes de texto.

REGRAS SOBERANAS:
- Nunca invente dados. Se não estiver no contexto, seja honesto.
- Se a pergunta for sobre valores, seja preciso e indique a unidade monetária.
- Se a pergunta for complexa, use Raciocínio Passo a Passo (Chain of Thought).
- Mantenha sempre um tom profissional, soberano e altamente inteligente.

HISTÓRICO DA CONVERSA:
{chat_history}

CONTEXTO DOCUMENTAL:
{context}

DESAFIO DO USUÁRIO: {question}

SOLUÇÃO DA INTELIGÊNCIA SOBERANA:"""


# Instância global singleton
cfg = Config()


def garantir_pastas():
    """Cria todas as pastas necessárias do projeto."""
    pastas = [
        cfg.docs_pdfs,
        cfg.docs_planilhas,
        cfg.docs_outros,
        cfg.chroma_path,
        cfg.dados_db,
        cfg.logs_path,
    ]
    for pasta in pastas:
        pasta.mkdir(parents=True, exist_ok=True)
