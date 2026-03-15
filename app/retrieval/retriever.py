from typing import List, Dict, Any
from app.indexing.embedder import Embedder
from app.indexing.vector_store import VectorStore
from app.utils.logger import logger

class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve_context(self, query: str, n_results: int = 5) -> str:
        """Busca os chunks mais relevantes e constrói o contexto para o LLM."""
        logger.info(f"Buscando contexto para a consulta: {query}")
        
        # Gera embedding para a consulta
        query_embeddings = self.embedder.get_embeddings(query)
        if not query_embeddings:
            return ""
            
        # Busca no banco vetorial
        results = self.vector_store.query(query_embeddings, n_results=n_results)
        
        if not results or not results.get('documents'):
            return "Nenhum documento relevante encontrado."
            
        # Constrói o contexto formatado
        context_parts = []
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        for i, doc in enumerate(documents):
            meta = metadatas[i]
            source = meta.get('file_name', 'Desconhecido')
            context_parts.append(f"--- Fonte: {source} ---\n{doc}\n")
            
        return "\n".join(context_parts)
