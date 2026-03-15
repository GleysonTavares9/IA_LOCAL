from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from app.config.settings import SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE
from app.utils.logger import logger

class SupabaseDB:
    def __init__(self):
        if not USE_SUPABASE or not SUPABASE_URL or not SUPABASE_KEY:
            self.client = None
            return
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def is_active(self) -> bool:
        return self.client is not None

    def register_file(self, file_data: Dict[str, Any]) -> Optional[str]:
        """Registra um arquivo no Supabase."""
        if not self.is_active(): return None
        try:
            # Upsert baseado no file_path
            response = self.client.table("files").upsert(file_data, on_conflict="file_path").execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao registrar arquivo no Supabase: {e}")
            return None

    def save_chunks(self, file_id: str, chunks: List[Dict[str, Any]]):
        """Salva chunks no Supabase."""
        if not self.is_active(): return
        try:
            # Prepara dados para inserção em massa
            data = []
            for i, chunk in enumerate(chunks):
                data.append({
                    "file_id": file_id,
                    "chunk_index": i,
                    "content": chunk['content'],
                    "metadata_json": chunk.get('metadata_json'),
                    "vector_id": chunk.get('vector_id')
                })
            self.client.table("chunks").insert(data).execute()
        except Exception as e:
            logger.error(f"Erro ao salvar chunks no Supabase: {e}")

    def search_vectors(self, query_embedding: List[float], match_threshold: float = 0.5, match_count: int = 5):
        """Busca vetores usando RPC no Supabase (pgvector)."""
        if not self.is_active(): return []
        try:
            # Assume que existe uma função RPC 'match_chunks' no Supabase
            rpc_params = {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
            }
            response = self.client.rpc("match_chunks", rpc_params).execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro na busca vetorial do Supabase: {e}")
            return []
