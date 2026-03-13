; ==============================================================================
; IA_Local_Installer.iss — Script Inno Setup — IA Local RAG v2.0
; ==============================================================================
; Para gerar o instalador .EXE: instale o Inno Setup (jrsoftware.org)
; e compile este arquivo clicando em Build > Compile.
; ==============================================================================

[Setup]
AppId={{IA-LOCAL-RAG-GLEYSON-V2}
AppName=IA Local Soberana
AppVersion=2.3
AppPublisher=Gleyson Tavares
AppCopyright=© 2025 Gleyson Tavares
DefaultDirName={localappdata}\IA Local Soberana
DefaultGroupName=IA Local Soberana
OutputBaseFilename=Instalador_IA_Soberana_Soberana_v2.3
UsePreviousAppDir=no
PrivilegesRequired=lowest
AllowNoIcons=yes

; Visual
WizardStyle=modern
WizardImageFile="wizard_image.png"
WizardSmallImageFile="wizard_small.png"
SetupIconFile="icon.ico"
UninstallDisplayIcon="{app}\icon.ico"

; Versão e Compartilhamento
VersionInfoDescription=IA Local Soberana - Instalador
VersionInfoVersion=2.0
VersionInfoCompany=Gleyson Tavares
VersionInfoCopyright=© 2025 Gleyson Tavares
VersionInfoProductName=IA Local Soberana
LicenseFile=LICENCA.txt

; Compressão máxima
Compression=lzma2/ultra64
InternalCompressLevel=ultra
SolidCompression=yes

; Plataforma
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Telas do wizard
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; 1. Aplicativo Blindado (PyInstaller)
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\dist\launcher\*"; \
    DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Scripts de Apoio
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\INICIAR_IA.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\PERGUNTAR_IA.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\abrir_ia.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\LEIA-ME.txt"; DestDir: "{app}"; Flags: ignoreversion

; 3. Recursos Visuais e Ícones
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\favicon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\wizard_image.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\GleysonMiranda\Downloads\IA_Local\wizard_small.png"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\documentos"
Name: "{app}\documentos\extratos"
Name: "{app}\documentos\planilhas"
Name: "{app}\documentos\outros"
Name: "{app}\banco_vetorial"
Name: "{app}\dados_db"
Name: "{app}\logs"

[Icons]
; Atalhos Web
Name: "{group}\IA Local Soberana (Interface Web)"; Filename: "{app}\abrir_ia.vbs"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\IA Local Soberana"; Filename: "{app}\abrir_ia.vbs"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

; Atalho Terminal (Direto)
Name: "{group}\IA Local SOBERANA (Terminal)"; Filename: "{app}\PERGUNTAR_IA.bat"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\IA Local (Chat Rápido)"; Filename: "{app}\PERGUNTAR_IA.bat"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
; 1. Instala Ollama silenciosamente (se nao estiver instalado)
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -Command ""if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {{ winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements }}"" "; \
    Flags: runhidden waituntilterminated; \
    StatusMsg: "Configurando motor de IA (Ollama)... Isso pode levar um momento."

; 2. Instala Python 3.11 silenciosamente (se nao estiver instalado)
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -Command ""if (-not (Get-Command python -ErrorAction SilentlyContinue)) {{ winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements }}"" "; \
    Flags: runhidden waituntilterminated; \
    StatusMsg: "Configurando ambiente de execução (Python)..."

; 3. Abrir o aplicativo ao finalizar a instalacao
Filename: "{app}\abrir_ia.vbs"; \
    Description: "{cm:LaunchProgram,IA Local Soberana}"; \
    Flags: shellexec postinstall skipifsilent nowait runasoriginaluser

Filename: "{app}\LEIA-ME.txt"; \
    Description: "Ver instruções de uso (Importante)"; \
    Flags: postinstall shellexec skipifsilent

[UninstallDelete]
; Limpeza profunda de arquivos gerados em tempo de execucao
Type: filesandordirs; Name: "{app}\banco_vetorial"
Type: filesandordirs; Name: "{app}\dados_db"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\documentos"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\venv"
Type: files; Name: "{app}\.env"
