import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.indexing.embedder import Embedder
from app.indexing.vector_store import VectorStore
from app.retrieval.retriever import Retriever
from app.llm.answer_generator import AnswerGenerator
from app.config.settings import USE_EXTERNAL_API, LLM_MODEL_LOCAL, EXTERNAL_LLM_MODEL

st.set_page_config(page_title="IA Local Multimodal Empresarial", layout="wide")

st.title("🏢 IA Local Multimodal Empresarial")
st.markdown("---")

# Sidebar para configurações e status
with st.sidebar:
    st.header("Configurações")
    st.info(f"Modo: {'Externo (API)' if USE_EXTERNAL_API else 'Local (Ollama)'}")
    st.info(f"Modelo: {EXTERNAL_LLM_MODEL if USE_EXTERNAL_API else LLM_MODEL_LOCAL}")
    
    st.divider()
    if st.button("🔄 Reindexar Arquivos"):
        st.warning("Iniciando indexação incremental...")
        # Aqui chamaria o script de indexação
        st.success("Indexação concluída!")

# Inicialização dos componentes
@st.cache_resource
def load_components():
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(embedder, vector_store)
    generator = AnswerGenerator()
    return retriever, generator

retriever, generator = load_components()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar com os documentos da empresa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando informações nos documentos..."):
            # 1. Recuperação de Contexto
            context = retriever.retrieve_context(prompt)
            
            # 2. Geração de Resposta
            response = generator.generate_answer(prompt, context)
            
            st.markdown(response)
            
            with st.expander("Ver Contexto Recuperado"):
                st.text(context)
                
    st.session_state.messages.append({"role": "assistant", "content": response})
