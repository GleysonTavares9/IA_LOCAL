"""
core/rag_chain.py — Pipeline RAG: recuperação de contexto + geração de resposta.
Usa LangChain + Ollama para responder perguntas com base nos documentos indexados.
"""

import logging
from typing import TypedDict

from langchain_ollama import ChatOllama
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from core.config import cfg
from core.vectorstore import carregar_vectorstore

logger = logging.getLogger(__name__)


class RespostaRAG(TypedDict):
    """Estrutura de resposta do pipeline RAG."""
    resposta: str
    fontes: list[dict]
    pergunta: str


def _build_prompt() -> PromptTemplate:
    return PromptTemplate(
        template=cfg.prompt_template,
        input_variables=["context", "question"],
    )


def _build_llm() -> ChatOllama:
    return ChatOllama(
        model=cfg.llm_model,
        base_url=cfg.ollama_url,
        temperature=cfg.temperature,
        num_predict=512,
        streaming=True,
    )


def criar_chain() -> RetrievalQA | None:
    """
    Monta o pipeline RetrievalQA.
    Retorna None se o banco vetorial não existir.
    """
    vectorstore = carregar_vectorstore()
    if vectorstore is None:
        logger.error("Banco vetorial não encontrado. Execute 'indexar.py' primeiro.")
        return None

    chain = RetrievalQA.from_chain_type(
        llm=_build_llm(),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": cfg.top_k},
        ),
        chain_type_kwargs={"prompt": _build_prompt()},
        return_source_documents=True,
    )
    logger.info("Pipeline RAG inicializado com modelo '%s'.", cfg.llm_model)
    return chain


def perguntar(chain: RetrievalQA, pergunta: str, callbacks=None) -> RespostaRAG:
    """
    Executa uma consulta RAG e retorna resposta estruturada.

    Args:
        chain: Pipeline RAG já inicializado.
        pergunta: Texto da pergunta do usuário.
        callbacks: Handlers de streaming (Opcional).

    Returns:
        RespostaRAG com texto da resposta e metadados das fontes.
    """
    config_dict = {}
    if callbacks:
        config_dict["callbacks"] = callbacks
        
    resultado = chain.invoke({"query": pergunta}, config=config_dict)

    # Extrair fontes sem duplicatas
    fontes_vistas = set()
    fontes = []
    for doc in resultado.get("source_documents", []):
        fonte = doc.metadata.get("fonte", "Desconhecida")
        if fonte not in fontes_vistas:
            fontes_vistas.add(fonte)
            fontes.append({
                "fonte": fonte,
                "tipo": doc.metadata.get("tipo", ""),
                "pagina": doc.metadata.get("page", ""),
                "trecho": doc.page_content[:200],
            })

    return RespostaRAG(
        resposta=resultado["result"],
        fontes=fontes,
        pergunta=pergunta,
    )
