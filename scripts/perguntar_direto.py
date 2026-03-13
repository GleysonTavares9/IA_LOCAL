import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.config import cfg, garantir_pastas
from core.vectorstore import banco_existe, carregar_vectorstore
from core.rag_chain import criar_chain, perguntar

def main():
    garantir_pastas()
    
    if not banco_existe():
        print("❌ Banco vetorial não encontrado. Por favor, indexe o documento primeiro via app.")
        return

    print("🤖 Inicializando IA (Llama 3.2)...")
    chain = criar_chain()
    if not chain:
        print("❌ Falha ao inicializar o pipeline RAG.")
        return

    while True:
        try:
            pergunta = input("\n💬 Digite sua pergunta (ou 'sair'): ")
            if pergunta.lower() in ["sair", "exit", "q"]:
                break
            
            print("🔍 Buscando resposta nos documentos...")
            res = perguntar(chain, pergunta)
            
            print("-" * 50)
            print(f"🧠 RESPOSTA:\n{res['resposta']}")
            print("-" * 50)
            if res["fontes"]:
                print(f"📎 FONTES: {', '.join(f['fonte'] for f in res['fontes'])}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
