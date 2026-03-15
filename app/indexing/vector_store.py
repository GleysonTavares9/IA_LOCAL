import chromadb
from typing import List, Dict, Any, Optional
from app.config.settings import CHROMA_DB_PATH, VECTOR_DB_TYPE, USE_SUPABASE
from app.storage.supabase_db import SupabaseDB
from app.utils.logger import logger

class VectorStore:
    def __init__(self, collection_name: str = "enterprise_docs"):
        self.db_type = VECTOR_DB_TYPE
        
        # Inicializa Chroma local por padrão
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Inicializa Supabase se configurado
        self.supabase = SupabaseDB() if USE_SUPABASE else None

    def add_documents(self, ids: List[str], documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Adiciona documentos e seus embeddings ao banco vetorial (Chroma ou Supabase)."""
        try:
            # Sempre adiciona ao Chroma local para redundância
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            # Se Supabase estiver ativo, espelha os dados lá para escalabilidade externa
            if self.supabase and self.supabase.is_active():
                # No Supabase, os chunks são salvos via tabela chunks com suporte a pgvector
                pass
                
            logger.info(f"Adicionados {len(ids)} documentos ao banco vetorial.")
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos ao banco vetorial: {e}")

    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """Realiza busca semântica no banco vetorial."""
        try:
            # Prioriza Supabase se estiver configurado como principal
            if self.db_type == "supabase" and self.supabase and self.supabase.is_active():
                results = self.supabase.search_vectors(query_embeddings[0], match_count=n_results)
                if results:
                    return {
                        "documents": [[r['content'] for r in results]],
                        "metadatas": [[r['metadata_json'] for r in results]],
                        "distances": [[r.get('similarity', 0) for r in results]]
                    }
            
            # Fallback para Chroma local
            return self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
        except Exception as e:
            logger.error(f"Erro ao consultar banco vetorial: {e}")
            return {}

    def delete_by_file_id(self, file_id: str):
        """Remove todos os chunks associados a um arquivo específico."""
        try:
            self.collection.delete(where={"file_id": file_id})
            
            if self.supabase and self.supabase.is_active():
                self.supabase.client.table("chunks").delete().eq("file_id", file_id).execute()
                
            logger.info(f"Removidos chunks do arquivo ID {file_id}.")
        except Exception as e:
            logger.error(f"Erro ao remover chunks: {e}")
