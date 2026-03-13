import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

if __name__ == "__main__":
    # Garante que o diretório de trabalho seja a raiz do app
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    app_path = resolve_path("app.py")
    
    # Prepara os argumentos do Streamlit
    # Se o usuário passar argumentos no terminal, nós os incluímos
    st_args = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
        "--server.headless=true",
    ]
    
    # Se não houver porta definida nos argumentos extras, define a 8501 como padrão
    tem_porta = any("--server.port" in arg for arg in sys.argv)
    if not tem_porta:
        st_args.append("--server.port=8501")
        
    # Adiciona os argumentos que vieram do terminal (excluindo o nome do script)
    st_args.extend(sys.argv[1:])
    
    sys.argv = st_args
    sys.exit(stcli.main())
