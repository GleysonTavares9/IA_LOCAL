import streamlit as st
import sys
import os
from pathlib import Path
import time

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.indexing.embedder import Embedder
from app.indexing.vector_store import VectorStore
from app.retrieval.retriever import Retriever
from app.llm.answer_generator import AnswerGenerator
from app.config.settings import USE_EXTERNAL_API, LLM_MODEL_LOCAL, EXTERNAL_LLM_MODEL, RAW_DATA_PATH
from app.storage.metadata_db import MetadataDB
from app.utils.sentiment import SentimentAnalyzer

# Configuração da Página
st.set_page_config(
    page_title="Enterprise AI | Multimodal Local",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Customizado para Visual Premium
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }
    .sentiment-badge {
        font-size: 0.8em;
        padding: 2px 8px;
        border-radius: 10px;
        margin-left: 10px;
    }
    .sentiment-positivo { background-color: #d4edda; color: #155724; }
    .sentiment-neutro { background-color: #fff3cd; color: #856404; }
    .sentiment-negativo { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

# Inicialização de Componentes
@st.cache_resource
def load_system():
    db = MetadataDB()
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(embedder, vector_store)
    generator = AnswerGenerator()
    sentiment_analyzer = SentimentAnalyzer()
    return db, retriever, generator, sentiment_analyzer

db, retriever, generator, sentiment_analyzer = load_system()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Enterprise AI")
    st.markdown("---")
    
    st.subheader("📁 Gestão de Documentos")
    uploaded_files = st.file_uploader(
        "Upload de novos arquivos", 
        accept_multiple_files=True,
        type=['pdf', 'docx', 'xlsx', 'png', 'jpg', 'txt', 'csv']
    )
    
    if uploaded_files:
        if st.button("🚀 Processar Arquivos"):
            with st.spinner("Indexando documentos..."):
                for uploaded_file in uploaded_files:
                    save_path = RAW_DATA_PATH / uploaded_file.name
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    time.sleep(1)
                st.success(f"{len(uploaded_files)} arquivos indexados!")
                st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Configurações")
    mode = "Externo (API)" if USE_EXTERNAL_API else "Local (Ollama)"
    st.info(f"**Modo Atual:** {mode}")
    st.caption(f"Modelo: {EXTERNAL_LLM_MODEL if USE_EXTERNAL_API else LLM_MODEL_LOCAL}")
    
    if st.button("🧹 Limpar Chat"):
        st.session_state.messages = []
        st.session_state.sentiments = []
        st.rerun()

# Área Principal
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Assistente Corporativo")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sentiments" not in st.session_state:
        st.session_state.sentiments = []

    # Container para o chat
    chat_container = st.container(height=500)
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Exibe sentimento se for mensagem do usuário
                if message["role"] == "user" and i < len(st.session_state.sentiments):
                    s = st.session_state.sentiments[i]
                    st.markdown(f"<span class='sentiment-badge sentiment-{s['sentiment']}'>{s['sentiment'].upper()}</span>", unsafe_allow_html=True)

    if prompt := st.chat_input("Pergunte algo sobre a empresa..."):
        # Análise de Sentimento
        with st.spinner("Analisando tom da mensagem..."):
            sentiment_res = sentiment_analyzer.analyze(prompt)
            st.session_state.sentiments.append(sentiment_res)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                st.markdown(f"<span class='sentiment-badge sentiment-{sentiment_res['sentiment']}'>{sentiment_res['sentiment'].upper()}</span>", unsafe_allow_html=True)

            with st.chat_message("assistant"):
                with st.spinner("Analisando base de conhecimento..."):
                    context = retriever.retrieve_context(prompt)
                    response = generator.generate_answer(prompt, context)
                    
                    placeholder = st.empty()
                    full_response = ""
                    for chunk in response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    
                    if context:
                        with st.expander("🔍 Fontes Consultadas"):
                            st.info(context)
                            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.sentiments.append(None) # Placeholder para a resposta da IA

with col2:
    st.subheader("📊 Status da Base")
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM files")
            total_files = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM chunks")
            total_chunks = cursor.fetchone()[0]
        
        st.metric("Documentos", total_files)
        st.metric("Fragmentos (Chunks)", total_chunks)
        
        # Dashboard de Sentimentos
        st.markdown("---")
        st.subheader("🎭 Humor do Usuário")
        if st.session_state.sentiments:
            valid_sentiments = [s['sentiment'] for s in st.session_state.sentiments if s]
            if valid_sentiments:
                pos = valid_sentiments.count('positivo')
                neu = valid_sentiments.count('neutro')
                neg = valid_sentiments.count('negativo')
                
                st.write(f"😊 Positivo: {pos}")
                st.write(f"😐 Neutro: {neu}")
                st.write(f"😡 Negativo: {neg}")
                
                # Barra de progresso visual
                total = len(valid_sentiments)
                st.progress(pos/total if total > 0 else 0, text="Positividade")
            else:
                st.caption("Nenhuma interação analisada.")
        else:
            st.caption("Aguardando interações...")
            
        st.markdown("---")
        st.subheader("📂 Arquivos Recentes")
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name, status FROM files ORDER BY created_at DESC LIMIT 5")
            for name, status in cursor.fetchall():
                icon = "✅" if status == 'completed' else "⏳"
                st.write(f"{icon} {name}")
    except:
        st.warning("Banco de dados ainda não inicializado.")
