"""
app.py — Interface principal da IA Local RAG
Chat com documentos locais. Sem login. 100% privado.
"""

import streamlit as st
import tempfile
import shutil
import time
from pathlib import Path
import requests
from core.config import cfg

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Soberana Intelligence — Universal RAG",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fundo geral - branco */
.stApp {
    background-color: #f8f9fb;
}

/* Sidebar - cinza claro */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* Header principal */
.main-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
}
.main-header p {
    color: #64748b;
    font-size: 0.9rem;
}

/* Mensagens do chat - usuario */
.chat-msg-user {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    margin-left: 15%;
    color: white;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2);
}

/* Mensagens do chat - IA */
.chat-msg-ai {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px 16px 16px 4px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    margin-right: 15%;
    color: #1e293b;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.fonte-tag {
    display: inline-block;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #2563eb;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.75rem;
    margin-right: 4px;
    margin-top: 4px;
}

/* Botoes */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* Remover borda padrao do streamlit */
[data-testid="stDecoration"] { display: none; }
footer { display: none; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Funções auxiliares ───────────────────────────────────────────────────────

def verificar_ollama() -> bool:
    """Verifica se o Ollama está rodando."""
    try:
        r = requests.get("http://localhost:11434", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def listar_modelos(provider: str) -> list[str]:
    """Lista modelos disponíveis baseados no provedor selecionado."""
    if provider == "Local (Ollama)":
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                modelos = [m["name"] for m in r.json().get("models", [])]
                modelos = [m for m in modelos if "embed" not in m and "minilm" not in m]
                if "llama3.2:3b" in modelos:
                    modelos.remove("llama3.2:3b")
                    modelos.insert(0, "llama3.2:3b")
                return modelos if modelos else ["llama3.2:3b"]
        except:
            pass
        return ["llama3.2:3b"]
    elif provider == "OpenAI (Pro)":
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    elif provider == "Groq (Ultra Speed)":
        return ["llama-3.1-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
    elif provider == "Gemini (Google)":
        return ["gemini-1.5-pro", "gemini-1.5-flash"]
    elif provider == "Hugging Face (OSS)":
        return ["mistralai/Mistral-7B-Instruct-v0.3", "meta-llama/Llama-3.2-3B-Instruct", "microsoft/Phi-3-mini-4k-instruct"]
    return ["Selecione um provedor"]


def indexar_documento(arquivo_path: Path, nome: Path) -> tuple[bool, str]:
    """Processa e indexa um documento no banco vetorial."""
    try:
        from core.config import garantir_pastas
        from core.loaders import carregar_pasta
        from core.vectorstore import criar_vectorstore, dividir_documentos

        garantir_pastas()

        # Copia para pasta documentos/outros
        dest = Path("documentos/outros") / nome.name
        shutil.copy2(arquivo_path, dest)

        docs = carregar_pasta(Path("documentos/outros"))
        if not docs:
            return False, "Nenhum conteúdo foi extraído do arquivo."

        chunks = dividir_documentos(docs)
        criar_vectorstore(chunks)
        return True, f"{len(chunks)} trechos indexados com sucesso!"
    except Exception as e:
        return False, f"Erro ao indexar: {str(e)}"


def perguntar_ia(pergunta: str, modelo: str, historico: list) -> dict:
    """Faz uma pergunta à IA usando o pipeline RAG com memória de conversa."""
    try:
        from core.config import cfg, garantir_pastas
        from core.vectorstore import banco_existe, carregar_vectorstore
        import os
        
        garantir_pastas()
        if not banco_existe():
            return {"resposta": "⚠️ Nenhum documento foi indexado ainda.", "fontes": [], "modo": "sem_banco"}

        # Constrói string de histórico (últimas 4 mensagens para não pesar o i5)
        contexto_historico = ""
        for m in historico[-4:]:
            role = "Usuário" if m["role"] == "user" else "IA"
            contexto_historico += f"{role}: {m['content']}\n"
        # Re-cria chain com modelos e memória do ambiente classic
        from langchain_ollama import ChatOllama
        from langchain_classic.chains import RetrievalQA
        from langchain_core.prompts import PromptTemplate

        vs = carregar_vectorstore()
        
        provider = st.session_state.get("provider", "Local (Ollama)")
        
        if provider == "Local (Ollama)":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model=modelo, 
                base_url=cfg.ollama_url, 
                temperature=0.1,
                num_ctx=2048, 
                num_predict=512,
                num_thread=8
            )
        elif provider == "OpenAI (Pro)":
            from langchain_openai import ChatOpenAI
            key = st.session_state.get("openai_key") or cfg.openai_api_key
            if not key: return {"resposta": "❌ Chave OpenAI não encontrada no .env nem na interface.", "fontes": [], "modo": "erro"}
            llm = ChatOpenAI(model=modelo, api_key=key, temperature=0.1)
        elif provider == "Groq (Ultra Speed)":
            from langchain_groq import ChatGroq
            key = st.session_state.get("groq_key") or cfg.groq_api_key
            if not key: return {"resposta": "❌ Chave Groq não encontrada no .env nem na interface.", "fontes": [], "modo": "erro"}
            llm = ChatGroq(model=modelo, groq_api_key=key, temperature=0.1)
        elif provider == "Gemini (Google)":
            from langchain_google_genai import ChatGoogleGenerativeAI
            key = st.session_state.get("gemini_key") or cfg.gemini_api_key
            if not key: return {"resposta": "❌ Chave Gemini não encontrada no .env nem na interface.", "fontes": [], "modo": "erro"}
            llm = ChatGoogleGenerativeAI(model=modelo, google_api_key=key, temperature=0.1)
        elif provider == "Hugging Face (OSS)":
            from langchain_huggingface import HuggingFaceEndpoint
            key = st.session_state.get("hf_key") or cfg.huggingface_api_key
            if not key: return {"resposta": "❌ Token Hugging Face não encontrado no .env nem na interface.", "fontes": [], "modo": "erro"}
            llm = HuggingFaceEndpoint(repo_id=modelo, huggingfacehub_api_token=key, temperature=0.1)
        else:
            return {"resposta": "❌ Provedor inválido.", "fontes": [], "modo": "erro"}

        # INJEÇÃO JÁ NO TEMPLATE (Pulo do Gato para evitar erro de chaves)
        template_com_historico = cfg.prompt_template.replace("{chat_history}", contexto_historico)
        
        prompt = PromptTemplate(
            template=template_com_historico, 
            input_variables=["context", "question"]
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vs.as_retriever(search_type="similarity", search_kwargs={"k": cfg.top_k}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )
        
        # Gerador para STREAMING (Dá a sensação de velocidade instantânea)
        def stream_response():
            full_res = ""
            # O RetrievalQA clássico não suporta stream nativo com fontes de forma simples, 
            # então vamos usar o invoke mas avisar que estamos processando.
            # Para velocidade real em CPU, vamos diminuir a carga do i5:
            resultado = chain.invoke({"query": pergunta})
            return resultado

        resultado = stream_response()
        
        # Limpeza de fontes para exibir apenas nomes de arquivos únicos
        fontes = list(set([doc.metadata.get("fonte", "Desconhecida") for doc in resultado.get("source_documents", [])]))
        return {"resposta": resultado["result"], "fontes": fontes, "modo": "rag"}
    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)}", "fontes": [], "modo": "erro"}


# ── Session State ────────────────────────────────────────────────────────────
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "modelo" not in st.session_state:
    st.session_state.modelo = "phi3.5:latest"


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌌 Soberana Intelligence")
    st.markdown("---")

    # Status do Ollama
    ollama_ok = verificar_ollama()
    if ollama_ok:
        st.success("✅ Ollama conectado")
    else:
        st.error("❌ Ollama offline")
        st.info("Abra o Ollama antes de continuar.")

    st.markdown("### 🔌 Conexão")
    provider = st.selectbox(
        "Modo de Inteligência:",
        ["Local (Ollama)", "OpenAI (Pro)", "Groq (Ultra Speed)", "Gemini (Google)", "Hugging Face (OSS)"],
        index=0,
        help="Local para privacidade total. Cloud para poder máximo de processamento."
    )
    st.session_state.provider = provider

    st.markdown("### 🤖 Modelo")
    modelos = listar_modelos(provider)
    modelo_sel = st.selectbox(
        "Selecione o motor:", 
        modelos, 
        index=0, 
        label_visibility="collapsed"
    )
    st.session_state.modelo = modelo_sel

    with st.expander("🔑 Configurar APIs Cloud"):
        st.info("🔒 Modo Seguro: As chaves do seu arquivo .env são usadas automaticamente. Para usar uma nova chave temporária, insira abaixo.")
        st.session_state.openai_key = st.text_input("OpenAI Key:", value="", type="password", placeholder="Deixe vazio para usar o .env")
        st.session_state.groq_key = st.text_input("Groq Key:", value="", type="password", placeholder="Deixe vazio para usar o .env")
        st.session_state.gemini_key = st.text_input("Gemini Key:", value="", type="password", placeholder="Deixe vazio para usar o .env")
        st.session_state.hf_key = st.text_input("Hugging Face Token:", value="", type="password", placeholder="Deixe vazio para usar o .env")
        st.caption("As chaves inseridas aqui têm prioridade sobre o .env.")

    st.markdown("### 📂 Enviar Documento")
    st.caption("PDF, TXT, CSV ou Excel")
    
    arquivo = st.file_uploader(
        "Arraste ou clique para selecionar",
        type=["pdf", "txt", "csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    if arquivo:
        if st.button("⚡ Indexar Documento", use_container_width=True):
            with st.spinner("Processando e indexando..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(arquivo.name).suffix) as tmp:
                    tmp.write(arquivo.getvalue())
                    tmp_path = Path(tmp.name)
                ok, msg = indexar_documento(tmp_path, Path(arquivo.name))
                tmp_path.unlink(missing_ok=True)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    st.markdown("---")

    # Documentos indexados
    from pathlib import Path as P
    banco = P("banco_vetorial")
    docs_path = P("documentos/outros")
    
    st.markdown("### 📚 Documentos na base")
    arquivos_doc = list(docs_path.glob("*")) if docs_path.exists() else []
    if arquivos_doc:
        for f in arquivos_doc:
            st.markdown(f"📄 `{f.name}`")
    else:
        st.caption("Nenhum documento indexado ainda.")

    st.markdown("---")
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.mensagens = []
        st.rerun()


# ── ÁREA PRINCIPAL ───────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌌 SOBERANA INTELLIGENCE</h1>
    <p>A Inteligência Universal de Ultra-Alta Performance — Processamento Deep Documents</p>
</div>
""", unsafe_allow_html=True)

# Exibir histórico do chat
chat_container = st.container()
with chat_container:
    if not st.session_state.mensagens:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #94a3b8;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🌌</div>
            <p style="font-size: 1.1rem; color: #1e293b; font-weight: 500;">Pronto para o Próximo Nível?</p>
            <p style="font-size: 0.95rem; color: #64748b;">Suba seus documentos na lateral e ative o processamento Soberano.</p>
            <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 1rem;">Módulos Ativos: RAG · Deep Reasoning · Total Privacy</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.mensagens:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                fontes_html = ""
                if msg.get("fontes"):
                    fontes_html = "<br><br><strong style='font-size:0.8rem;color:#64748b'>📎 Fontes:</strong><br>"
                    for f in msg["fontes"]:
                        fontes_html += f'<span class="fonte-tag">📄 {f}</span>'
                st.markdown(
                    f'<div class="chat-msg-ai">🧠 {msg["content"]}{fontes_html}</div>',
                    unsafe_allow_html=True
                )

# Input do chat
pergunta = st.chat_input("Faça sua pergunta sobre os documentos...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})

    with st.status("🌌 Ativando Raciocínio Soberano...", expanded=True) as status:
        st.write("Mapeando contexto documental...")
        resultado = perguntar_ia(pergunta, st.session_state.modelo, st.session_state.mensagens)
        status.update(label="🚀 Processamento Concluído!", state="complete", expanded=False)

    # Efeito de escrita (mais agradável e parece mais rápido)
    def efeito_escrita(texto):
        for palavra in texto.split(" "):
            yield palavra + " "
            time.sleep(0.02)

    st.session_state.mensagens.append({
        "role": "assistant",
        "content": resultado["resposta"],
        "fontes": resultado.get("fontes", [])
    })
    st.rerun()
