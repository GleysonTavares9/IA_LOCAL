import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Caminhos Base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "databases"
LOG_DIR = BASE_DIR / "logs"

# Configurações de Modelos
USE_EXTERNAL_API = os.getenv("USE_EXTERNAL_API", "false").lower() == "true"

# Local (Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL_LOCAL = os.getenv("LLM_MODEL_LOCAL", "llama3.2")
VISION_MODEL_LOCAL = os.getenv("VISION_MODEL_LOCAL", "llama3.2-vision")
EMBEDDING_MODEL_LOCAL = os.getenv("EMBEDDING_MODEL_LOCAL", "nomic-embed-text")

# Externo (Gemini/OpenAI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EXTERNAL_LLM_MODEL = os.getenv("EXTERNAL_LLM_MODEL", "gemini-1.5-flash")
EXTERNAL_EMBEDDING_MODEL = os.getenv("EXTERNAL_EMBEDDING_MODEL", "text-embedding-004")

# Supabase (Escalabilidade Externa)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

# Configurações de Banco de Dados
SQLITE_DB_PATH = DB_DIR / "metadata.sqlite"
CHROMA_DB_PATH = str(DB_DIR / "chroma_db")
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma") # chroma ou supabase

# Configurações de Processamento
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Configurações de Ingestão
RAW_DATA_PATH = DATA_DIR / "raw"
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.xls', '.png', '.jpg', '.jpeg', '.mp4', '.avi', '.mov', '.txt', '.csv', '.json'}
