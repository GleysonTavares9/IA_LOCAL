@echo off
setlocal
title IA Local Soberana

cd /d "%~dp0"

echo ===========================================================
echo   IA LOCAL SOBERANA v2.3 - HYBRID INTELLIGENCE
echo ===========================================================

echo 1. Verificando componentes...

set ENGINE=
if exist "launcher.exe" set ENGINE=launcher.exe
if exist "dist\launcher\launcher.exe" if "%ENGINE%"=="" set ENGINE=dist\launcher\launcher.exe

if not "%ENGINE%"=="" goto :ENGINE_OK
echo [ERRO] Motor de IA (launcher.exe) nao encontrado.
pause
exit /b 1

:ENGINE_OK
echo 2. Verificando servidor local...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if not errorlevel 1 goto :OLLAMA_OK
echo [INFO] Iniciando Ollama...
start "" "ollama" serve
timeout /t 3 >nul

:OLLAMA_OK
echo 3. Ativando Raciocinio Soberano...
:: Inicia o motor em background (/B) para nao abrir nova janela preta
start /B "Engine Soberana" "%ENGINE%"

echo ===========================================================
echo   SISTEMA ATIVADO COM SUCESSO!
echo ===========================================================
timeout /t 5 >nul
start "" "http://localhost:8501"
exit
