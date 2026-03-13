# ==============================================================================
# instalar_e_rodar.ps1 — Script de Deploy Automatizado IA Local RAG
# Use este script para instalar o projeto em qualquer nova máquina Windows.
# ==============================================================================

# Configuração de Cores
$Cyan = "cyan"
$Green = "green"
$Yellow = "yellow"
$Red = "red"

Clear-Host
Write-Host "====================================================" -ForegroundColor $Cyan
Write-Host "   🤖 INSTALADOR AUTOMÁTICO - IA LOCAL RAG" -ForegroundColor $Cyan
Write-Host "====================================================" -ForegroundColor $Cyan
Write-Host "   100% Local · Soberano · Privado" -ForegroundColor $Cyan
Write-Host "====================================================" -ForegroundColor $Cyan

# 1. Verificar Execução (Permissões)
$CurrentPolicy = Get-ExecutionPolicy
if ($CurrentPolicy -eq "Restricted") {
    Write-Host "⚠️  Permissão de script restrita. Ajustando para o processo atual..." -ForegroundColor $Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
}

# 2. Verificar Python
Write-Host "`n[1/6] Verificando Python..." -ForegroundColor $Cyan
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Erro: Python não encontrado no PATH!" -ForegroundColor $Red
    Write-Host "Por favor, instale em: https://www.python.org/downloads/" -ForegroundColor $Yellow
    exit
}
python --version

# 3. Criar Estrutura de Pastas
Write-Host "`n[2/6] Verificando estrutura de pastas..." -ForegroundColor $Cyan
$Pastas = @("documentos/pdfs", "documentos/planilhas", "documentos/outros", "dados_db", "logs", "banco_vetorial")
foreach ($Pasta in $Pastas) {
    if (!(Test-Path $Pasta)) {
        New-Item -ItemType Directory -Path $Pasta | Out-Null
        Write-Host "   ✅ Pasta criada: $Pasta" -ForegroundColor $Green
    }
}

# 4. Configurar Ambiente Virtual (VENV)
Write-Host "`n[3/6] Configurando Ambiente Virtual (venv)..." -ForegroundColor $Cyan
if (!(Test-Path "venv")) {
    Write-Host "   📦 Criando novo venv..." -ForegroundColor $Yellow
    python -m venv venv
    Write-Host "   ✅ Venv criado." -ForegroundColor $Green
}

Write-Host "   📥 Instalando/Atualizando dependências (pode demorar)..." -ForegroundColor $Yellow
& .\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
Write-Host "   ✅ Bibliotecas instaladas." -ForegroundColor $Green

# 5. Verificar Ollama e Modelos
Write-Host "`n[4/6] Verificando Ollama e Modelos..." -ForegroundColor $Cyan
if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "   ⚠️  Ollama não encontrado. Tentando instalar via Winget..." -ForegroundColor $Yellow
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements
    Write-Host "   🚀 Ollama instalado. Por favor, certifique-se que ele está aberto (ícone na barra de tarefas)." -ForegroundColor $Yellow
}

Write-Host "   🧠 Baixando modelos (Llama 3.1 + Embeddings)..." -ForegroundColor $Yellow
Write-Host "   (Se já existirem, ele apenas verificará os arquivos)" -ForegroundColor $Cyan
ollama pull llama3.1:8b
ollama pull nomic-embed-text
Write-Host "   ✅ Modelos prontos." -ForegroundColor $Green

# 6. Inicializar Banco de Dados
Write-Host "`n[5/6] Inicializando Banco de Dados de Exemplo..." -ForegroundColor $Cyan
& .\venv\Scripts\python.exe scripts/criar_db_exemplo.py
Write-Host "   ✅ Banco SQLite pronto." -ForegroundColor $Green

# 7. Iniciar Aplicação
Write-Host "`n[6/6] ✨ TUDO PRONTO! Iniciando IA Local..." -ForegroundColor $Cyan
Write-Host "====================================================" -ForegroundColor $Cyan
Write-Host "   Acesse no navegador: http://localhost:8501" -ForegroundColor $Green
Write-Host "====================================================" -ForegroundColor $Cyan

& .\venv\Scripts\streamlit.exe run app.py
