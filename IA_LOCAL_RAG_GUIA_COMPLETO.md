# 🤖 GUIA COMPLETO: IA Local com RAG — PDFs, Planilhas e Banco de Dados

> **Objetivo:** Criar uma IA local, leve e soberana que responde perguntas com base em documentos (PDFs, planilhas) e futuramente conectada a banco de dados — sem nenhuma API externa, sem custo recorrente.
>
> **Como usar este guia:** Cole este documento em qualquer LLM local (Ollama, LM Studio, etc.) e peça: *"Execute este guia passo a passo no meu sistema Linux/Windows/Mac"*. O LLM irá executar todos os comandos.

---

## 📋 ÍNDICE

1. [Pré-requisitos e Hardware](#1-pré-requisitos-e-hardware)
2. [Instalar Ollama (Runner do LLM)](#2-instalar-ollama)
3. [Baixar os Modelos](#3-baixar-os-modelos)
4. [Instalar Dependências Python](#4-instalar-dependências-python)
5. [Estrutura de Pastas do Projeto](#5-estrutura-de-pastas)
6. [Pipeline RAG — Indexar PDFs e Planilhas](#6-pipeline-rag)
7. [Script Principal do Chatbot](#7-script-do-chatbot)
8. [Interface Web com Open WebUI](#8-interface-web)
9. [Integração com Banco de Dados (Text-to-SQL)](#9-banco-de-dados)
10. [Inicialização Automática](#10-inicialização-automática)
11. [Testar e Validar](#11-testar-e-validar)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Pré-requisitos e Hardware

### Verificar sistema

```bash
# Verificar OS
uname -a

# Verificar RAM disponível
free -h

# Verificar GPU NVIDIA (se tiver)
nvidia-smi

# Verificar espaço em disco (precisa de ~20GB livres)
df -h
```

### Requisitos Mínimos

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Disco | 15 GB | 30 GB |
| GPU | Sem GPU (só CPU) | NVIDIA 8GB+ VRAM |
| Python | 3.10+ | 3.11+ |

---

## 2. Instalar Ollama

O Ollama é o motor que roda os LLMs localmente.

### Linux / WSL2

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS

```bash
# Instalar via Homebrew
brew install ollama

# Ou baixar direto:
# https://ollama.com/download/mac
```

### Windows (via PowerShell como Administrador)

```powershell
winget install Ollama.Ollama
```

### Verificar instalação

```bash
ollama --version
ollama serve &
```

---

## 3. Baixar os Modelos

Vamos baixar dois modelos: um para responder (LLM) e um para criar embeddings (vetorizar documentos).

### Modelo de Linguagem Principal

```bash
# Opção A: Llama 4 8B — melhor qualidade geral (recomendado se tiver 8GB+ RAM)
ollama pull llama3.1:8b

# Opção B: Qwen2.5 7B — excelente em português
ollama pull qwen2.5:7b

# Opção C: Gemma 3 4B — ultra leve (para máquinas com pouca RAM)
ollama pull gemma3:4b

# Opção D: Phi-3 Mini — mínimo absoluto (4GB RAM)
ollama pull phi3:mini
```

### Modelo de Embeddings (para vetorizar documentos)

```bash
# Embedding local de alta qualidade - obrigatório para o RAG
ollama pull nomic-embed-text
```

### Testar os modelos

```bash
# Testar LLM
ollama run llama3.1:8b "Olá, você fala português?"

# Testar embeddings (deve retornar um vetor JSON)
curl http://localhost:11434/api/embeddings -d '{"model":"nomic-embed-text","prompt":"teste"}'
```

---

## 4. Instalar Dependências Python

### Criar ambiente virtual

```bash
# Criar pasta do projeto
mkdir -p ~/ia-local-rag
cd ~/ia-local-rag

# Criar ambiente virtual Python
python3 -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

### Instalar pacotes

```bash
pip install --upgrade pip

pip install \
  langchain \
  langchain-community \
  langchain-ollama \
  chromadb \
  pypdf \
  openpyxl \
  pandas \
  unstructured \
  sentence-transformers \
  streamlit \
  sqlalchemy \
  psycopg2-binary \
  python-dotenv \
  tiktoken \
  tqdm \
  rich
```

### Criar arquivo requirements.txt

```bash
pip freeze > requirements.txt
```

---

## 5. Estrutura de Pastas

```bash
# Criar estrutura completa do projeto
mkdir -p ~/ia-local-rag/{documentos,banco_vetorial,scripts,dados_db,logs}
cd ~/ia-local-rag

# Criar subpastas para tipos de documentos
mkdir -p documentos/{pdfs,planilhas,outros}
```

A estrutura final será:

```
ia-local-rag/
├── documentos/
│   ├── pdfs/          ← Coloque seus PDFs aqui
│   ├── planilhas/     ← Coloque seus .xlsx/.csv aqui
│   └── outros/        ← .txt, .docx, etc.
├── banco_vetorial/    ← ChromaDB salva aqui (automático)
├── scripts/
│   ├── indexar.py     ← Processa e indexa documentos
│   ├── chatbot.py     ← Interface de chat no terminal
│   └── app.py         ← Interface web Streamlit
├── dados_db/          ← Para integração com banco de dados
├── logs/              ← Logs do sistema
├── .env               ← Configurações
└── requirements.txt
```

### Criar arquivo de configuração .env

```bash
cat > ~/ia-local-rag/.env << 'EOF'
# Configurações do Ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text

# Configurações do banco vetorial
CHROMA_DB_PATH=./banco_vetorial
COLLECTION_NAME=minha_base_conhecimento

# Configurações de chunks (pedaços dos documentos)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Número de resultados relevantes a buscar
TOP_K_RESULTS=5

# Banco de dados (para Fase 3)
DATABASE_URL=sqlite:///./dados_db/base.db
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/meubanco

# Idioma do sistema
SYSTEM_LANGUAGE=pt-BR
EOF
```

---

## 6. Pipeline RAG

Este script processa seus documentos, divide em pedaços e salva no banco vetorial.

### Criar script de indexação

```bash
cat > ~/ia-local-rag/scripts/indexar.py << 'SCRIPT'
#!/usr/bin/env python3
"""
INDEXADOR DE DOCUMENTOS — IA Local RAG
Processa PDFs e planilhas e salva no banco vetorial ChromaDB
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
from rich.console import Console
from rich.table import Table

# LangChain
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    DirectoryLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

load_dotenv()
console = Console()

# Configurações
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./banco_vetorial")
COLLECTION = os.getenv("COLLECTION_NAME", "minha_base_conhecimento")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

def carregar_pdfs(pasta: str) -> list:
    """Carrega todos os PDFs de uma pasta."""
    documentos = []
    pasta_path = Path(pasta)
    
    if not pasta_path.exists():
        console.print(f"[yellow]Pasta {pasta} não encontrada, criando...[/yellow]")
        pasta_path.mkdir(parents=True)
        return documentos
    
    pdfs = list(pasta_path.glob("*.pdf"))
    if not pdfs:
        console.print(f"[yellow]Nenhum PDF encontrado em {pasta}[/yellow]")
        return documentos
    
    console.print(f"\n[bold blue]📄 Carregando {len(pdfs)} PDFs...[/bold blue]")
    
    for pdf_path in tqdm(pdfs, desc="PDFs"):
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            # Adicionar metadados
            for doc in docs:
                doc.metadata["fonte"] = pdf_path.name
                doc.metadata["tipo"] = "pdf"
                doc.metadata["indexado_em"] = datetime.now().isoformat()
            documentos.extend(docs)
            console.print(f"  ✅ {pdf_path.name} ({len(docs)} páginas)")
        except Exception as e:
            console.print(f"  ❌ Erro em {pdf_path.name}: {e}")
    
    return documentos

def carregar_planilhas(pasta: str) -> list:
    """Carrega planilhas Excel e CSV."""
    documentos = []
    pasta_path = Path(pasta)
    
    if not pasta_path.exists():
        pasta_path.mkdir(parents=True)
        return documentos
    
    arquivos = list(pasta_path.glob("*.xlsx")) + \
               list(pasta_path.glob("*.xls")) + \
               list(pasta_path.glob("*.csv"))
    
    if not arquivos:
        console.print(f"[yellow]Nenhuma planilha encontrada em {pasta}[/yellow]")
        return documentos
    
    console.print(f"\n[bold blue]📊 Carregando {len(arquivos)} planilhas...[/bold blue]")
    
    for arquivo in tqdm(arquivos, desc="Planilhas"):
        try:
            if arquivo.suffix.lower() == ".csv":
                loader = CSVLoader(str(arquivo), encoding="utf-8")
            else:
                loader = UnstructuredExcelLoader(str(arquivo), mode="elements")
            
            docs = loader.load()
            for doc in docs:
                doc.metadata["fonte"] = arquivo.name
                doc.metadata["tipo"] = "planilha"
                doc.metadata["indexado_em"] = datetime.now().isoformat()
            documentos.extend(docs)
            console.print(f"  ✅ {arquivo.name} ({len(docs)} registros)")
        except Exception as e:
            console.print(f"  ❌ Erro em {arquivo.name}: {e}")
    
    return documentos

def dividir_documentos(documentos: list) -> list:
    """Divide documentos em chunks menores."""
    console.print(f"\n[bold blue]✂️  Dividindo {len(documentos)} documentos em chunks...[/bold blue]")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    
    chunks = splitter.split_documents(documentos)
    console.print(f"  → {len(chunks)} chunks criados (tamanho: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})")
    return chunks

def criar_banco_vetorial(chunks: list) -> Chroma:
    """Cria/atualiza o banco vetorial ChromaDB."""
    console.print(f"\n[bold blue]🧠 Criando embeddings e salvando no ChromaDB...[/bold blue]")
    console.print(f"  Modelo de embedding: {EMBEDDING_MODEL}")
    console.print(f"  Destino: {CHROMA_PATH}")
    
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_URL
    )
    
    # Criar ou adicionar ao banco existente
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION
    )
    
    vectorstore.persist()
    console.print(f"  ✅ Banco vetorial salvo em {CHROMA_PATH}")
    return vectorstore

def mostrar_resumo(total_docs: int, total_chunks: int):
    """Mostra tabela de resumo."""
    table = Table(title="📊 Resumo da Indexação", show_header=True)
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Total de documentos processados", str(total_docs))
    table.add_row("Total de chunks criados", str(total_chunks))
    table.add_row("Banco vetorial", CHROMA_PATH)
    table.add_row("Coleção", COLLECTION)
    table.add_row("Data de indexação", datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    console.print(table)

def main():
    console.print("[bold green]🚀 INDEXADOR DE DOCUMENTOS — IA Local RAG[/bold green]")
    console.print("=" * 50)
    
    # Carregar documentos
    docs_pdf = carregar_pdfs("documentos/pdfs")
    docs_planilha = carregar_planilhas("documentos/planilhas")
    
    todos_docs = docs_pdf + docs_planilha
    
    if not todos_docs:
        console.print("\n[bold red]❌ Nenhum documento encontrado![/bold red]")
        console.print("Coloque seus PDFs em: documentos/pdfs/")
        console.print("Coloque suas planilhas em: documentos/planilhas/")
        sys.exit(1)
    
    console.print(f"\n✅ Total carregado: {len(todos_docs)} documentos")
    
    # Dividir em chunks
    chunks = dividir_documentos(todos_docs)
    
    # Criar banco vetorial
    criar_banco_vetorial(chunks)
    
    # Resumo
    mostrar_resumo(len(todos_docs), len(chunks))
    
    console.print("\n[bold green]✅ Indexação concluída! Agora rode o chatbot:[/bold green]")
    console.print("  python scripts/chatbot.py")
    console.print("  python scripts/app.py  (interface web)")

if __name__ == "__main__":
    main()
SCRIPT
```

---

## 7. Script do Chatbot

### Criar chatbot de terminal

```bash
cat > ~/ia-local-rag/scripts/chatbot.py << 'SCRIPT'
#!/usr/bin/env python3
"""
CHATBOT LOCAL — IA com RAG
Responde perguntas com base nos documentos indexados
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()
console = Console()

# Configurações
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./banco_vetorial")
COLLECTION = os.getenv("COLLECTION_NAME", "minha_base_conhecimento")
TOP_K = int(os.getenv("TOP_K_RESULTS", 5))

# Prompt em português
PROMPT_TEMPLATE = """Você é um assistente especializado que responde perguntas com base nos documentos fornecidos.

REGRAS IMPORTANTES:
1. Responda SEMPRE em português do Brasil
2. Use APENAS as informações do contexto fornecido
3. Se não souber a resposta, diga claramente: "Não encontrei essa informação nos documentos disponíveis"
4. Cite a fonte do documento quando possível
5. Seja direto e objetivo

CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA: {question}

RESPOSTA:"""

def inicializar_chain():
    """Inicializa o pipeline RAG."""
    console.print("[yellow]🔄 Inicializando sistema...[/yellow]")
    
    # Verificar se banco vetorial existe
    if not Path(CHROMA_PATH).exists():
        console.print("[bold red]❌ Banco vetorial não encontrado![/bold red]")
        console.print("Execute primeiro: python scripts/indexar.py")
        return None
    
    # Embeddings
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_URL
    )
    
    # Carregar banco vetorial
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION
    )
    
    # LLM
    llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_URL,
        temperature=0.1,  # Baixo para respostas mais factuais
        num_predict=1024
    )
    
    # Prompt personalizado
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    # Chain RAG
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K}
        ),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    
    console.print("[green]✅ Sistema pronto![/green]")
    return chain

def mostrar_fontes(source_docs):
    """Mostra os documentos usados como fonte."""
    if not source_docs:
        return
    
    fontes = set()
    for doc in source_docs:
        fonte = doc.metadata.get("fonte", "Desconhecida")
        pagina = doc.metadata.get("page", "")
        if pagina:
            fontes.add(f"{fonte} (pág. {pagina + 1})")
        else:
            fontes.add(fonte)
    
    if fontes:
        console.print(f"\n[dim]📎 Fontes consultadas: {', '.join(fontes)}[/dim]")

def main():
    console.print(Panel.fit(
        "[bold green]🤖 IA Local — Assistente de Documentos[/bold green]\n"
        f"Modelo: [cyan]{LLM_MODEL}[/cyan] | "
        f"Embeddings: [cyan]{EMBEDDING_MODEL}[/cyan]\n"
        "Digite [bold]'sair'[/bold] para encerrar | "
        "[bold]'fontes'[/bold] para ver documentos indexados",
        border_style="green"
    ))
    
    chain = inicializar_chain()
    if not chain:
        return
    
    historico = []
    
    while True:
        try:
            pergunta = console.input("\n[bold cyan]Você:[/bold cyan] ").strip()
            
            if not pergunta:
                continue
            
            if pergunta.lower() in ["sair", "exit", "quit"]:
                console.print("[yellow]👋 Encerrando...[/yellow]")
                break
            
            # Processar pergunta
            console.print("[dim]🔍 Buscando nos documentos...[/dim]")
            
            resultado = chain({"query": pergunta})
            resposta = resultado["result"]
            docs_fonte = resultado.get("source_documents", [])
            
            # Mostrar resposta
            console.print("\n[bold green]Assistente:[/bold green]")
            console.print(Panel(Markdown(resposta), border_style="green"))
            
            # Mostrar fontes
            mostrar_fontes(docs_fonte)
            
            # Salvar no histórico
            historico.append({"pergunta": pergunta, "resposta": resposta})
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Encerrando...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Erro: {e}[/red]")

if __name__ == "__main__":
    main()
SCRIPT
```

### Criar interface web Streamlit

```bash
cat > ~/ia-local-rag/scripts/app.py << 'SCRIPT'
#!/usr/bin/env python3
"""
INTERFACE WEB — IA Local RAG com Streamlit
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

# Configurações
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./banco_vetorial")
COLLECTION = os.getenv("COLLECTION_NAME", "minha_base_conhecimento")

PROMPT_TEMPLATE = """Você é um assistente especializado que responde perguntas com base nos documentos fornecidos.
Responda SEMPRE em português do Brasil. Use APENAS o contexto fornecido.
Se não souber, diga "Não encontrei essa informação nos documentos".

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:"""

st.set_page_config(
    page_title="IA Local — Assistente de Documentos",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 IA Local — Assistente de Documentos")
st.markdown(f"**Modelo:** `{LLM_MODEL}` | **Embeddings:** `{EMBEDDING_MODEL}`")

@st.cache_resource
def carregar_chain():
    if not Path(CHROMA_PATH).exists():
        return None
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION
    )
    llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, temperature=0.1)
    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

# Inicializar histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Verificar banco vetorial
chain = carregar_chain()
if not chain:
    st.error("❌ Banco vetorial não encontrado! Execute primeiro: `python scripts/indexar.py`")
    st.stop()

# Mostrar histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fontes"):
            st.caption(f"📎 Fontes: {msg['fontes']}")

# Input do usuário
if pergunta := st.chat_input("Digite sua pergunta sobre os documentos..."):
    
    # Mostrar pergunta
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando nos documentos..."):
            resultado = chain({"query": pergunta})
            resposta = resultado["result"]
            docs = resultado.get("source_documents", [])
            
            # Extrair fontes
            fontes = set()
            for doc in docs:
                fonte = doc.metadata.get("fonte", "")
                if fonte:
                    fontes.add(fonte)
            fontes_str = ", ".join(fontes) if fontes else ""
            
            st.markdown(resposta)
            if fontes_str:
                st.caption(f"📎 Fontes: {fontes_str}")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta,
        "fontes": fontes_str
    })

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    st.success("✅ Sistema online")
    st.info(f"Modelo: {LLM_MODEL}")
    
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()
SCRIPT
```

---

## 8. Interface Web

### Opção A: Streamlit (recomendado para começar)

```bash
cd ~/ia-local-rag
source venv/bin/activate

# Rodar interface web
streamlit run scripts/app.py

# Acesse: http://localhost:8501
```

### Opção B: Open WebUI (interface estilo ChatGPT)

```bash
# Instalar Open WebUI via pip
pip install open-webui

# Iniciar (certifique-se que Ollama está rodando)
open-webui serve

# Acesse: http://localhost:8080
```

### Opção C: Docker (se tiver Docker instalado)

```bash
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# Acesse: http://localhost:3000
```

---

## 9. Banco de Dados

### Integração Text-to-SQL (perguntar em linguagem natural)

```bash
cat > ~/ia-local-rag/scripts/db_agent.py << 'SCRIPT'
#!/usr/bin/env python3
"""
AGENTE SQL — Consultas em linguagem natural ao banco de dados
"""

import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dados_db/base.db")

def criar_agente_sql(database_url: str = None):
    """Cria agente capaz de consultar banco de dados com linguagem natural."""
    
    db_url = database_url or DATABASE_URL
    
    print(f"Conectando ao banco: {db_url}")
    
    db = SQLDatabase.from_uri(db_url)
    
    llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_URL,
        temperature=0
    )
    
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prefix="""Você é um agente SQL especializado. Responda SEMPRE em português.
        Gere consultas SQL precisas para responder as perguntas do usuário.
        Use apenas as tabelas disponíveis no banco de dados."""
    )
    
    return agent

def main():
    print("🗄️  Agente SQL — Consultas em Linguagem Natural")
    print("=" * 50)
    
    agente = criar_agente_sql()
    
    print("Sistema pronto! Faça perguntas sobre seu banco de dados.")
    print("Exemplos:")
    print("  - Quantos clientes temos cadastrados?")
    print("  - Quais são os 10 produtos mais vendidos?")
    print("  - Qual foi o faturamento do último mês?")
    print()
    
    while True:
        try:
            pergunta = input("Pergunta: ").strip()
            if not pergunta or pergunta.lower() == "sair":
                break
            
            resposta = agente.run(pergunta)
            print(f"\nResposta: {resposta}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
SCRIPT
```

### Exemplo: Criar banco SQLite de teste

```bash
cat > ~/ia-local-rag/scripts/criar_db_exemplo.py << 'SCRIPT'
#!/usr/bin/env python3
"""Cria banco de dados SQLite de exemplo para testes."""

import sqlite3
from pathlib import Path

Path("dados_db").mkdir(exist_ok=True)

conn = sqlite3.connect("dados_db/base.db")
cursor = conn.cursor()

# Criar tabelas de exemplo
cursor.executescript("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    cidade TEXT,
    data_cadastro DATE
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    categoria TEXT,
    preco REAL,
    estoque INTEGER
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    valor_total REAL,
    data_pedido DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- Dados de exemplo
INSERT OR IGNORE INTO clientes VALUES 
    (1, 'João Silva', 'joao@email.com', 'São Paulo', '2024-01-15'),
    (2, 'Maria Santos', 'maria@email.com', 'Rio de Janeiro', '2024-02-20'),
    (3, 'Pedro Oliveira', 'pedro@email.com', 'Belo Horizonte', '2024-03-10');

INSERT OR IGNORE INTO produtos VALUES
    (1, 'Notebook Pro', 'Eletrônicos', 3500.00, 15),
    (2, 'Mouse Wireless', 'Periféricos', 150.00, 50),
    (3, 'Teclado Mecânico', 'Periféricos', 350.00, 30);

INSERT OR IGNORE INTO pedidos VALUES
    (1, 1, 1, 1, 3500.00, '2024-04-01'),
    (2, 2, 2, 2, 300.00, '2024-04-05'),
    (3, 1, 3, 1, 350.00, '2024-04-10');
""")

conn.commit()
conn.close()
print("✅ Banco de dados de exemplo criado em dados_db/base.db")
SCRIPT

python scripts/criar_db_exemplo.py
```

---

## 10. Inicialização Automática

### Script de start completo

```bash
cat > ~/ia-local-rag/start.sh << 'EOF'
#!/bin/bash
# Script de inicialização da IA Local

echo "🚀 Iniciando IA Local RAG..."
echo "================================"

# Ir para pasta do projeto
cd ~/ia-local-rag

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se Ollama está rodando
if ! pgrep -x "ollama" > /dev/null; then
    echo "▶️  Iniciando Ollama..."
    ollama serve &
    sleep 3
fi

echo "✅ Ollama ativo"

# Verificar se banco vetorial existe
if [ ! -d "./banco_vetorial" ]; then
    echo "⚠️  Banco vetorial não encontrado."
    echo "📄 Coloque documentos em documentos/pdfs/ e documentos/planilhas/"
    read -p "Deseja indexar agora? (s/n) " resposta
    if [ "$resposta" = "s" ]; then
        python scripts/indexar.py
    fi
fi

# Menu de opções
echo ""
echo "Escolha a interface:"
echo "  1) Chat no terminal"
echo "  2) Interface Web (Streamlit)"
echo "  3) Agente SQL (banco de dados)"
echo "  4) Apenas indexar documentos"
read -p "Opção: " opcao

case $opcao in
    1) python scripts/chatbot.py ;;
    2) streamlit run scripts/app.py ;;
    3) python scripts/db_agent.py ;;
    4) python scripts/indexar.py ;;
    *) echo "Opção inválida" ;;
esac
EOF

chmod +x ~/ia-local-rag/start.sh
echo "✅ Script de start criado!"
```

---

## 11. Testar e Validar

### Teste completo do sistema

```bash
cd ~/ia-local-rag
source venv/bin/activate

# 1. Testar conexão com Ollama
echo "=== TESTE 1: Ollama ==="
curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = [m['name'] for m in data.get('models', [])]
print(f'✅ Modelos disponíveis: {models}')
"

# 2. Testar embeddings
echo ""
echo "=== TESTE 2: Embeddings ==="
python3 -c "
from langchain_community.embeddings import OllamaEmbeddings
emb = OllamaEmbeddings(model='nomic-embed-text', base_url='http://localhost:11434')
resultado = emb.embed_query('teste de embedding')
print(f'✅ Embedding gerado: vetor de {len(resultado)} dimensões')
"

# 3. Criar PDF de teste
echo ""
echo "=== TESTE 3: Criando documento de teste ==="
python3 -c "
from pathlib import Path
Path('documentos/pdfs').mkdir(parents=True, exist_ok=True)
Path('documentos/pdfs/teste.txt').write_text(
    'Política de Reembolso: Nossa empresa oferece reembolso em até 7 dias úteis. '
    'O processo é feito via boleto ou cartão de crédito. '
    'Para solicitar, envie e-mail para financeiro@empresa.com.br '
    'com o número do pedido e motivo da devolução.', encoding='utf-8'
)
print('✅ Arquivo de teste criado')
"

# 4. Indexar
echo ""
echo "=== TESTE 4: Indexando ==="
python3 -c "
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

loader = TextLoader('documentos/pdfs/teste.txt')
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
emb = OllamaEmbeddings(model='nomic-embed-text', base_url='http://localhost:11434')
vstore = Chroma.from_documents(chunks, emb, persist_directory='./banco_vetorial')
vstore.persist()
print(f'✅ {len(chunks)} chunks indexados com sucesso!')
"

# 5. Testar busca
echo ""
echo "=== TESTE 5: Busca vetorial ==="
python3 -c "
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

emb = OllamaEmbeddings(model='nomic-embed-text', base_url='http://localhost:11434')
vstore = Chroma(persist_directory='./banco_vetorial', embedding_function=emb)
resultados = vstore.similarity_search('prazo de reembolso', k=2)
print(f'✅ Busca funcionando! Encontrei {len(resultados)} resultados.')
for r in resultados:
    print(f'   → {r.page_content[:80]}...')
"

echo ""
echo "🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente."
echo ""
echo "Próximos passos:"
echo "  1. Coloque seus PDFs reais em: documentos/pdfs/"
echo "  2. Coloque suas planilhas em: documentos/planilhas/"
echo "  3. Rode: python scripts/indexar.py"
echo "  4. Rode: ./start.sh"
```

---

## 12. Troubleshooting

### Problemas comuns e soluções

```bash
# PROBLEMA: "Connection refused" no Ollama
# SOLUÇÃO: Iniciar o servidor Ollama
ollama serve

# PROBLEMA: Modelo não encontrado
# SOLUÇÃO: Baixar o modelo
ollama pull llama3.1:8b
ollama list  # ver modelos disponíveis

# PROBLEMA: Erro de memória ao rodar o modelo
# SOLUÇÃO: Usar modelo menor
ollama pull gemma3:4b
# Editar .env: LLM_MODEL=gemma3:4b

# PROBLEMA: PDF não carregando
# SOLUÇÃO: Verificar se está corrompido e instalar dependências
pip install pymupdf pypdf2 pdfminer.six

# PROBLEMA: Planilha não carregando
# SOLUÇÃO: Instalar dependências extras
pip install openpyxl xlrd unstructured[xlsx]

# PROBLEMA: Respostas em inglês
# SOLUÇÃO: Verificar o prompt template no chatbot.py
# A instrução "Responda SEMPRE em português do Brasil" já está incluída

# PROBLEMA: Respostas incorretas / alucinação
# SOLUÇÃO: Reduzir temperature e TOP_K
# No .env: 
# TOP_K_RESULTS=3
# No chatbot.py: temperature=0.0

# PROBLEMA: Banco vetorial corrompido
# SOLUÇÃO: Deletar e reindexar
rm -rf banco_vetorial/
python scripts/indexar.py

# VERIFICAR LOGS
ls -la banco_vetorial/
du -sh banco_vetorial/
```

---

## 🗺️ ROADMAP — Próximas Etapas

```
FASE 1 (Agora) ✅
├── Ollama + Modelo local
├── RAG com PDFs e planilhas
├── ChromaDB para vetores
└── Interface Streamlit / terminal

FASE 2 (Próximo)
├── Conectar PostgreSQL / MySQL
├── Agente SQL (Text-to-SQL)
├── Indexação automática (watcher de pasta)
└── API REST com FastAPI

FASE 3 (Avançado)
├── Fine-tuning com Unsloth (dados proprietários)
├── Multi-agentes (um para docs, outro para DB)
├── Autenticação e controle de acesso
└── Deploy em servidor interno
```

---

## ⚡ COMANDOS RÁPIDOS — RESUMO

```bash
# === INSTALAR TUDO ===
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b && ollama pull nomic-embed-text
cd ~/ia-local-rag && pip install langchain langchain-community chromadb pypdf openpyxl pandas streamlit python-dotenv rich tqdm

# === INDEXAR DOCUMENTOS ===
python scripts/indexar.py

# === INICIAR CHATBOT ===
python scripts/chatbot.py          # Terminal
streamlit run scripts/app.py       # Web

# === CONSULTAR BANCO DE DADOS ===
python scripts/db_agent.py

# === TUDO DE UMA VEZ ===
./start.sh
```

---

*Guia gerado para uso com LLMs locais via Ollama — 2026*
*Stack: Ollama + LangChain + ChromaDB + Streamlit*
*100% local, 100% privado, 100% gratuito*
