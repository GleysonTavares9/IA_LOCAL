"""
core/loaders.py — Carregadores de documentos com tratamento robusto de erros.
Suporta: PDF, CSV, Excel (.xlsx/.xls), TXT, DOCX
"""

import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    UnstructuredExcelLoader,
)

logger = logging.getLogger(__name__)


def _carregar_pdf(caminho: Path) -> List[Document]:
    """Carrega um PDF, retornando lista vazia em caso de erro."""
    try:
        loader = PyPDFLoader(str(caminho))
        docs = loader.load()
        for doc in docs:
            doc.metadata.update({"fonte": caminho.name, "tipo": "pdf"})
        return docs
    except Exception as exc:
        logger.error("Erro ao carregar PDF '%s': %s", caminho.name, exc)
        return []


def _carregar_csv(caminho: Path) -> List[Document]:
    """Carrega um CSV tentando UTF-8 e, em fallback, latin-1."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            loader = CSVLoader(
                file_path=str(caminho),
                encoding=enc,
                csv_args={"delimiter": ","},
            )
            docs = loader.load()
            for doc in docs:
                doc.metadata.update({"fonte": caminho.name, "tipo": "csv", "encoding": enc})
            return docs
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            logger.error("Erro ao carregar CSV '%s': %s", caminho.name, exc)
            return []
    logger.error("Falha ao detectar encoding de '%s'", caminho.name)
    return []


def _carregar_excel(caminho: Path) -> List[Document]:
    """Carrega planilha Excel usando UnstructuredExcelLoader."""
    try:
        loader = UnstructuredExcelLoader(str(caminho), mode="elements")
        docs = loader.load()
        for doc in docs:
            doc.metadata.update({"fonte": caminho.name, "tipo": "excel"})
        return docs
    except Exception as exc:
        logger.error("Erro ao carregar Excel '%s': %s", caminho.name, exc)
        return []


def _carregar_txt(caminho: Path) -> List[Document]:
    """Carrega arquivo texto plano."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            loader = TextLoader(str(caminho), encoding=enc)
            docs = loader.load()
            for doc in docs:
                doc.metadata.update({"fonte": caminho.name, "tipo": "txt"})
            return docs
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            logger.error("Erro ao carregar TXT '%s': %s", caminho.name, exc)
            return []
    return []


# Mapa de extensão → função carregadora
_LOADERS = {
    ".pdf": _carregar_pdf,
    ".csv": _carregar_csv,
    ".xlsx": _carregar_excel,
    ".xls": _carregar_excel,
    ".txt": _carregar_txt,
}


def carregar_pasta(pasta: Path, extensoes: List[str] | None = None) -> List[Document]:
    """
    Carrega todos os documentos suportados de uma pasta.

    Args:
        pasta: Caminho da pasta.
        extensoes: Lista de extensões a filtrar (ex: [".pdf", ".csv"]).
                   Se None, usa todas as extensões suportadas.

    Returns:
        Lista de documentos carregados.
    """
    if not pasta.exists():
        pasta.mkdir(parents=True, exist_ok=True)
        return []

    exts = extensoes or list(_LOADERS.keys())
    arquivos = [f for f in pasta.iterdir() if f.suffix.lower() in exts and f.is_file()]

    if not arquivos:
        return []

    todos: List[Document] = []
    for arq in sorted(arquivos):
        carregador = _LOADERS.get(arq.suffix.lower())
        if carregador:
            docs = carregador(arq)
            todos.extend(docs)
            logger.info("Carregado: %s (%d fragmentos)", arq.name, len(docs))

    return todos


def carregar_multiplas_pastas(*pastas: Path) -> List[Document]:
    """Agrega documentos de múltiplas pastas."""
    todos: List[Document] = []
    for pasta in pastas:
        todos.extend(carregar_pasta(pasta))
    return todos
