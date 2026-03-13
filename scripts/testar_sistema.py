"""
scripts/testar_sistema.py — Suite de testes de sanidade do sistema RAG.
Use: python scripts/testar_sistema.py

Verifica:
  1. Ollama acessível e modelos disponíveis
  2. Modelo de embeddings funcional
  3. Leitura de documento de teste
  4. Indexação de chunks no ChromaDB
  5. Busca por similaridade
  6. Pipeline RAG end-to-end
"""

import sys
import json
import textwrap
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    import urllib.request as requests  # fallback

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import cfg, garantir_pastas

console = Console()
resultados: list[dict] = []


def teste(nome: str):
    """Decorador simples para registrar resultado de cada teste."""
    def wrapper(fn):
        def inner(*args, **kwargs):
            try:
                fn(*args, **kwargs)
                resultados.append({"teste": nome, "status": "✅ OK", "erro": ""})
                console.print(f"  ✅ [green]{nome}[/green]")
                return True
            except Exception as exc:
                resultados.append({"teste": nome, "status": "❌ FALHOU", "erro": str(exc)})
                console.print(f"  ❌ [red]{nome}[/red]: {exc}")
                return False
        return inner
    return wrapper


# ── Testes ────────────────────────────────────────────────────────────────────

@teste("Ollama acessível")
def t1_ollama():
    import urllib.request
    req = urllib.request.urlopen(f"{cfg.ollama_url}/api/tags", timeout=5)
    data = json.loads(req.read())
    modelos = [m["name"] for m in data.get("models", [])]
    if not modelos:
        raise RuntimeError("Nenhum modelo encontrado. Rode: ollama pull llama3.1:8b")
    console.print(f"     Modelos: {', '.join(modelos[:3])}")


@teste("Modelo de embeddings")
def t2_embeddings():
    from langchain_ollama import OllamaEmbeddings
    emb = OllamaEmbeddings(model=cfg.embedding_model, base_url=cfg.ollama_url)
    vetor = emb.embed_query("teste de embedding em português")
    if len(vetor) < 100:
        raise RuntimeError(f"Vetor suspeito: apenas {len(vetor)} dimensões")
    console.print(f"     Vetor de {len(vetor)} dimensões gerado.")


@teste("Carregar documento de teste")
def t3_documento():
    from langchain_community.document_loaders import TextLoader
    doc_path = cfg.docs_pdfs / "_teste_sanidade.txt"
    doc_path.write_text(
        "Este é um documento de teste do sistema IA Local RAG.\n"
        "Política de reembolso: até 7 dias úteis via boleto ou cartão.\n"
        "Contato: suporte@empresa.com.br ou (11) 9999-0000.",
        encoding="utf-8"
    )
    loader = TextLoader(str(doc_path), encoding="utf-8")
    docs = loader.load()
    if not docs:
        raise RuntimeError("Nenhum documento carregado.")
    console.print(f"     {len(docs)} documento(s) carregado(s).")


@teste("Indexar no ChromaDB")
def t4_indexar():
    import shutil
    from langchain_community.document_loaders import TextLoader
    from langchain_ollama import OllamaEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    doc_path = cfg.docs_pdfs / "_teste_sanidade.txt"
    loader = TextLoader(str(doc_path), encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_documents(docs)

    test_db = cfg.chroma_path.parent / "_chroma_teste"
    if test_db.exists():
        shutil.rmtree(test_db)

    emb = OllamaEmbeddings(model=cfg.embedding_model, base_url=cfg.ollama_url)
    vs = Chroma.from_documents(chunks, emb, persist_directory=str(test_db))

    if test_db.exists():
        shutil.rmtree(test_db)

    console.print(f"     {len(chunks)} chunk(s) indexado(s) com sucesso.")


@teste("Busca por similaridade")
def t5_busca():
    from core.vectorstore import carregar_vectorstore, banco_existe
    if not banco_existe():
        raise RuntimeError("Banco vetorial principal não existe. Rode indexar.py primeiro.")
    vs = carregar_vectorstore()
    resultados_busca = vs.similarity_search("reembolso prazo", k=2)
    console.print(f"     {len(resultados_busca)} resultado(s) encontrado(s).")


@teste("Pipeline RAG completo")
def t6_pipeline():
    from core.rag_chain import criar_chain, perguntar
    from core.vectorstore import banco_existe
    if not banco_existe():
        raise RuntimeError("Banco vetorial não existe. Rode indexar.py primeiro.")
    chain = criar_chain()
    if not chain:
        raise RuntimeError("Falha ao criar chain RAG.")
    resultado = perguntar(chain, "qual o prazo de reembolso?")
    if not resultado["resposta"]:
        raise RuntimeError("Chain retornou resposta vazia.")
    console.print(f"     Resposta: {resultado['resposta'][:80]}...")


# ── Execução ─────────────────────────────────────────────────────────────────

def main():
    garantir_pastas()

    console.print(Panel.fit(
        "[bold cyan]🔬 Suite de Testes — IA Local RAG[/bold cyan]\n"
        f"[dim]{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/dim]",
        border_style="cyan",
    ))

    console.print("\n[bold]Executando testes...[/bold]\n")

    t1_ollama()
    t2_embeddings()
    t3_documento()
    t4_indexar()
    t5_busca()
    t6_pipeline()

    # Limpar arquivo de teste
    doc_path = cfg.docs_pdfs / "_teste_sanidade.txt"
    if doc_path.exists():
        doc_path.unlink()

    # Tabela de resultados
    console.print()
    table = Table(title="📊 Resultado dos Testes", show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Teste", style="white")
    table.add_column("Status", width=12)
    table.add_column("Erro", style="dim red")

    passou = 0
    for i, r in enumerate(resultados, 1):
        table.add_row(str(i), r["teste"], r["status"], r["erro"])
        if "OK" in r["status"]:
            passou += 1

    console.print(table)

    total = len(resultados)
    if passou == total:
        console.print(Panel(
            f"[bold green]🎉 Todos os {total} testes passaram![/bold green]\n"
            "O sistema está funcionando corretamente.",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[bold red]⚠️  {passou}/{total} testes passaram.[/bold red]\n"
            "Resolva os erros acima antes de usar o sistema.",
            border_style="red",
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
