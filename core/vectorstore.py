"""
core/vectorstore.py — Gerenciamento do banco vetorial ChromaDB.
Responsabilidades: criar, atualizar e consultar embeddings com Ollama.
"""

import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from core.config import cfg

logger = logging.getLogger(__name__)


def _get_embeddings() -> OllamaEmbeddings:
    """Factory para o modelo de embeddings."""
    return OllamaEmbeddings(
        model=cfg.embedding_model,
        base_url=cfg.ollama_url,
    )


def dividir_documentos(documentos: List[Document]) -> List[Document]:
    """
    Divide os documentos em chunks para indexação vetorial.
    Usa separadores hierárquicos para preservar contexto textual.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documentos)
    logger.info("%d chunks gerados a partir de %d documentos.", len(chunks), len(documentos))
    return chunks


def criar_vectorstore(chunks: List[Document]) -> Chroma:
    """
    Cria um banco vetorial ChromaDB a partir dos chunks.
    Se já existir, substitui a coleção existente.
    """
    logger.info(
        "Criando banco vetorial em '%s' com coleção '%s'...",
        cfg.chroma_path,
        cfg.collection_name,
    )
    embeddings = _get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(cfg.chroma_path),
        collection_name=cfg.collection_name,
    )
    logger.info("Banco vetorial criado com %d embeddings.", len(chunks))
    return vectorstore


def carregar_vectorstore() -> Chroma | None:
    """
    Carrega um banco vetorial ChromaDB existente.
    Retorna None se o banco não existir.
    """
    if not cfg.chroma_path.exists() or not any(cfg.chroma_path.iterdir()):
        logger.warning("Banco vetorial não encontrado em '%s'.", cfg.chroma_path)
        return None

    embeddings = _get_embeddings()
    vectorstore = Chroma(
        persist_directory=str(cfg.chroma_path),
        embedding_function=embeddings,
        collection_name=cfg.collection_name,
    )
    logger.info("Banco vetorial carregado de '%s'.", cfg.chroma_path)
    return vectorstore


def banco_existe() -> bool:
    """Verifica se o banco vetorial já foi criado."""
    return cfg.chroma_path.exists() and any(cfg.chroma_path.iterdir())


def contagem_documentos() -> int:
    """Retorna a quantidade de chunks indexados no banco."""
    vs = carregar_vectorstore()
    if vs is None:
        return 0
    try:
        return vs._collection.count()
    except Exception:
        return 0
