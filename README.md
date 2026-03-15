# IA Local Multimodal Empresarial

Este projeto implementa uma solução de Inteligência Artificial local e multimodal para ambientes empresariais, focada em processar e responder a perguntas com base em documentos internos da empresa. A arquitetura é modular, escalável e projetada para funcionar 100% localmente, com a opção de integração com APIs externas para maior flexibilidade.

## Funcionalidades Principais

-   **Ingestão de Documentos**: Varredura e monitoramento de diretórios para identificar e processar arquivos novos ou alterados.
-   **Extração de Conteúdo Abrangente**: Suporte robusto para diversos formatos de arquivo, incluindo PDF, DOCX, XLSX, imagens (PNG, JPG, JPEG), vídeos (MP4, AVI, MOV) e textos (TXT, CSV, JSON).
-   **Enriquecimento de Metadados**: Geração automática de metadados e contexto adicional para cada documento.
-   **Chunking Inteligente**: Divisão do conteúdo em pedaços menores (chunks) para otimização de embeddings, preservando o contexto.
-   **Embeddings Multimodais**: Geração de vetores semânticos para os chunks, utilizando modelos locais (Ollama) ou externos (Gemini API).
-   **Banco de Dados Vetorial Escalável**: Armazenamento e busca semântica eficiente de chunks utilizando ChromaDB local ou Supabase (PostgreSQL + pgvector) para escalabilidade remota.
-   **Geração de Respostas**: Recuperação de contexto relevante e geração de respostas por LLMs locais (Ollama) ou externos (Gemini API), com citação de fontes.
-   **Interface de Usuário**: Aplicação interativa desenvolvida com Streamlit para fácil interação.
-   **Processamento Paralelo**: Pipeline de indexação otimizado com processamento paralelo para alta performance.

## Arquitetura

A arquitetura é dividida em camadas independentes para facilitar a manutenção e a escalabilidade:

1.  **Ingestão**: Localiza e registra arquivos novos/alterados.
2.  **Extração de Conteúdo**: Transforma arquivos em texto pesquisável.
3.  **Enriquecimento**: Cria metadados e contexto adicional.
4.  **Chunking**: Quebra o conteúdo em pedaços para embeddings.
5.  **Embeddings**: Converte chunks em vetores.
6.  **Banco Vetorial**: Armazena e busca vetores (ChromaDB local ou Supabase/pgvector).
7.  **Resposta**: Busca chunks, monta contexto e envia para LLM.
8.  **Interface**: Interação com o usuário (Streamlit).

## Estrutura do Projeto

```
ia_local/
│
├── app/
│   ├── ui/                 # Interface de usuário (Streamlit)
│   │   ├── streamlit_app.py
│   │   └── components/
│   │
│   ├── ingestion/          # Camada de Ingestão
│   │   ├── scanner.py
│   │   └── file_registry.py
│   │
│   ├── processors/         # Camada de Extração de Conteúdo
│   │   ├── base_processor.py
│   │   ├── pdf_processor.py
│   │   ├── docx_processor.py
│   │   ├── excel_processor.py
│   │   ├── image_processor.py
│   │   ├── video_processor.py
│   │   └── text_processor.py
│   │
│   ├── enrichment/         # Camada de Enriquecimento
│   │   ├── metadata.py
│   │   ├── tagging.py
│   │   └── classification.py
│   │
│   ├── indexing/           # Camada de Chunking, Embeddings e Vector Store
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── vector_store.py
│   │
│   ├── retrieval/          # Camada de Recuperação
│   │   ├── retriever.py
│   │   ├── ranker.py
│   │   └── context_builder.py
│   │
│   ├── llm/                # Camada de LLM e Visão
│   │   ├── prompt_builder.py
│   │   ├── answer_generator.py
│   │   └── vision_handler.py
│   │
│   ├── storage/            # Armazenamento de Metadados (SQLite e Supabase)
│   │   ├── metadata_db.py
│   │   ├── supabase_db.py
│   │   ├── file_store.py
│   │   └── audit.py
│   │
│   ├── config/             # Configurações da aplicação
│   │   ├── settings.py
│   │   └── models.py
│   │
│   └── utils/              # Utilitários gerais
│       ├── hashes.py
│       ├── logger.py
│       ├── paths.py
│       └── validators.py
│
├── data/                   # Armazenamento de dados (raw, processed, etc.)
│   ├── raw/
│   ├── processed/
│   ├── extracted/
│   ├── temp/
│   └── archives/
│
├── databases/              # Bancos de dados (ChromaDB, SQLite)
│   ├── chroma_db/
│   ├── metadata.sqlite
│   └── audit.sqlite
│
├── logs/                   # Logs da aplicação
│   ├── app.log
│   ├── ingestion.log
│   └── errors.log
│
├── models/                 # Configurações de modelos locais
│   └── local_model_configs/
│
├── tests/                  # Testes unitários e de integração
│
├── scripts/                # Scripts utilitários (indexação, etc.)
│   ├── initial_index.py
│   ├── reindex_changed.py
│   ├── backup_db.py
│   └── clean_temp.py
│
├── requirements.txt        # Dependências do Python
├── .env.example            # Exemplo de variáveis de ambiente
└── README.md               # Este arquivo
```

## Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd ia_local
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto, baseado no `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Edite o arquivo `.env` com suas configurações. Para usar a API externa do Gemini ou o Supabase, você precisará das chaves e URLs apropriadas.

    Exemplo de `.env`:
    ```
    # Configurações para Ollama (local)
    OLLAMA_BASE_URL=http://localhost:11434
    LLM_MODEL_LOCAL=llama3.2
    VISION_MODEL_LOCAL=llama3.2-vision
    EMBEDDING_MODEL_LOCAL=nomic-embed-text

    # Para usar API externa (ex: Gemini)
    USE_EXTERNAL_API=false # Mude para 'true' para usar a API externa
    GEMINI_API_KEY="SUA_CHAVE_API_GEMINI"
    EXTERNAL_LLM_MODEL=gemini-1.5-flash
    EXTERNAL_EMBEDDING_MODEL=text-embedding-004

    # Para usar Supabase (PostgreSQL + pgvector)
    USE_SUPABASE=false # Mude para 'true' para usar o Supabase
    SUPABASE_URL="SUA_URL_SUPABASE"
    SUPABASE_KEY="SUA_CHAVE_ANON_SUPABASE"
    VECTOR_DB_TYPE=chroma # Mude para 'supabase' para usar o Supabase como banco vetorial principal
    ```

5.  **Instale o Ollama (se for usar modelos locais):**
    Siga as instruções em [ollama.ai](https://ollama.ai/) para instalar o Ollama e baixar os modelos `llama3.2`, `llama3.2-vision` e `nomic-embed-text`.

6.  **Configuração do Supabase (se `USE_SUPABASE=true`):**
    *   Crie um projeto no [Supabase](https://supabase.com/).
    *   No seu projeto Supabase, vá em `Database` -> `Extensions` e habilite a extensão `pgvector`.
    *   Crie as tabelas `files` e `chunks` e a função RPC `match_chunks` no seu banco de dados Supabase. Um exemplo de SQL para isso pode ser:

        ```sql
        -- Tabela de Arquivos
        CREATE TABLE IF NOT EXISTS files (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            file_path TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            file_type TEXT NOT NULL,
            last_modified DOUBLE PRECISION NOT NULL,
            status TEXT DEFAULT 'pending',
            department TEXT,
            sensitivity TEXT,
            language TEXT,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Tabela de Chunks
        CREATE TABLE IF NOT EXISTS chunks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            file_id UUID REFERENCES files(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata_json JSONB,
            embedding VECTOR(1536), -- Ajuste a dimensão do vetor conforme seu modelo de embedding
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Função RPC para busca vetorial (pgvector)
        CREATE OR REPLACE FUNCTION match_chunks(
            query_embedding VECTOR(1536),
            match_threshold FLOAT,
            match_count INT
        ) RETURNS TABLE (
            id UUID,
            file_id UUID,
            chunk_index INTEGER,
            content TEXT,
            metadata_json JSONB,
            similarity FLOAT
        ) LANGUAGE plpgsql AS $$
        #variable_conflict use_column
        BEGIN
            RETURN QUERY
            SELECT
                id,
                file_id,
                chunk_index,
                content,
                metadata_json,
                1 - (chunks.embedding <=> query_embedding) AS similarity
            FROM chunks
            WHERE 1 - (chunks.embedding <=> query_embedding) > match_threshold
            ORDER BY similarity DESC
            LIMIT match_count;
        END;
        $$;
        ```

## Uso

1.  **Coloque seus documentos:**
    Adicione os arquivos que deseja indexar na pasta `data/raw/`.

2.  **Execute a indexação inicial:**
    ```bash
    python scripts/initial_index.py
    ```
    Este script varrerá a pasta `data/raw/`, processará os documentos, gerará embeddings e os armazenará no ChromaDB (e Supabase, se configurado).

3.  **Inicie a interface Streamlit:**
    ```bash
    streamlit run app/ui/streamlit_app.py
    ```
    Acesse a interface no seu navegador (geralmente `http://localhost:8501`).

## Próximos Passos e Evolução

-   Implementar `watcher.py` para monitoramento em tempo real de novos arquivos.
-   Adicionar mais opções de enriquecimento (classificação de sensibilidade, tags automáticas).
-   Desenvolver uma interface multiusuário ou desktop (FastAPI + React, Electron).
-   Implementar testes abrangentes.

---

**Desenvolvido por:** Manus AI
