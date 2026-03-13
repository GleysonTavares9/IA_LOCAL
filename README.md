# 🤖 IA Local RAG

> **IA local, soberana e gratuita** que responde perguntas com base nos seus documentos (PDFs, planilhas, CSVs) — sem API externa, sem custo recorrente, 100% privado.

**Stack:** Ollama · LangChain · ChromaDB · Streamlit

---

## ⚡ Início Rápido (3 passos)

```powershell
# 1. Instalar Ollama (Windows)
winget install Ollama.Ollama

# 2. Baixar os modelos
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# 3. Instalar dependências e iniciar
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Coloque seus PDFs em documentos\pdfs\ e planilhas em documentos\planilhas\
python indexar.py        # Indexar documentos
python chatbot.py        # Chat no terminal
streamlit run app.py     # Interface Web
```

Ou simplesmente execute `start.bat` para o menu interativo.

---

## 📁 Estrutura do Projeto

```
ia-local-rag/
├── core/                  ← Módulos compartilhados
│   ├── config.py          ← Configurações centralizadas
│   ├── loaders.py         ← Carregadores de documentos
│   ├── vectorstore.py     ← ChromaDB (criar/carregar)
│   └── rag_chain.py       ← Pipeline RAG
├── documentos/
│   ├── pdfs/              ← Coloque seus PDFs aqui
│   ├── planilhas/         ← Excel e CSV aqui
│   └── outros/            ← TXT, DOCX, etc.
├── scripts/
│   ├── criar_db_exemplo.py ← Cria banco SQLite de teste
│   └── testar_sistema.py   ← Suite de testes de sanidade
├── banco_vetorial/        ← ChromaDB (gerado automaticamente)
├── dados_db/              ← Banco SQL (opcional)
├── logs/                  ← Logs de execução
├── indexar.py             ← Indexar documentos
├── chatbot.py             ← Chat no terminal
├── app.py                 ← Interface Web (Streamlit)
├── db_agent.py            ← Consulta SQL em linguagem natural
├── start.bat              ← Inicializador Windows
├── .env                   ← Configurações (edite aqui)
└── requirements.txt
```

---

## 🔧 Configuração (.env)

| Variável | Padrão | Descrição |
|---|---|---|
| `LLM_MODEL` | `llama3.1:8b` | Modelo de linguagem |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `CHUNK_SIZE` | `1000` | Tamanho dos chunks |
| `CHUNK_OVERLAP` | `200` | Sobreposição entre chunks |
| `TOP_K_RESULTS` | `5` | Trechos buscados por pergunta |
| `LLM_TEMPERATURE` | `0.1` | Criatividade (0=factual, 1=criativo) |

### Modelos alternativos

| Modelo | RAM | Qualidade | Idioma |
|---|---|---|---|
| `llama3.1:8b` | 8 GB | ⭐⭐⭐⭐ | Ótimo PT |
| `qwen2.5:7b` | 8 GB | ⭐⭐⭐⭐⭐ | Excelente PT |
| `gemma3:4b` | 4 GB | ⭐⭐⭐ | Bom PT |
| `phi3:mini` | 4 GB | ⭐⭐ | OK |

---

## 📖 Uso

### Indexar documentos

```powershell
python indexar.py            # Indexar novos documentos
python indexar.py --limpar   # Apagar e reindexar tudo
python indexar.py --info     # Ver status do banco atual
```

### Chat no terminal

```powershell
python chatbot.py
```

Comandos disponíveis no chat:
- `ajuda` — lista todos os comandos
- `fontes` — documentos indexados
- `reindexar` — reprocessa sem sair
- `limpar` — apaga histórico da sessão
- `sair` — encerra

### Interface Web

```powershell
streamlit run app.py
# Acesse: http://localhost:8501
```

### Agente SQL (Text-to-SQL)

```powershell
# Criar banco de exemplo primeiro:
python scripts\criar_db_exemplo.py

# Iniciar agente:
python db_agent.py
python db_agent.py --url postgresql://user:pass@localhost/meubanco
```

---

## 🧪 Testar o sistema

```powershell
python scripts\testar_sistema.py
```

Executa 6 verificações: Ollama, embeddings, carregamento, indexação, busca e pipeline completo.

---

## 🛠️ Troubleshooting

| Problema | Solução |
|---|---|
| `Connection refused` no Ollama | `ollama serve` no terminal |
| Modelo não encontrado | `ollama pull llama3.1:8b` |
| Erro de memória | Use `gemma3:4b` e edite `LLM_MODEL` no `.env` |
| PDF não carrega | `pip install pymupdf pypdf2` |
| Planilha não carrega | `pip install openpyxl unstructured[xlsx]` |
| Respostas em inglês | Verifique o prompt em `core/config.py` |
| Banco corrompido | `python indexar.py --limpar` |

---

## 🗺️ Roadmap

- [x] RAG com PDFs e planilhas
- [x] ChromaDB vetorial
- [x] Interface Streamlit
- [x] Chatbot de terminal
- [x] Text-to-SQL (SQLite/PostgreSQL)
- [ ] API REST com FastAPI
- [ ] Indexação automática por watcher
- [ ] Multi-agentes (docs + DB)
- [ ] Autenticação e controle de acesso
- [ ] Fine-tuning com dados proprietários

---

*Stack: Ollama + LangChain + ChromaDB + Streamlit | 100% local · 100% privado · 100% gratuito*
