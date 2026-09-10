@echo off
rem ─────────────────────────────────────────────────────────────────────────
rem  Plataforma LGPD — inicialização local (Windows)
rem  Cria o ambiente, prepara o banco (SQLite), popula a demonstração e sobe o
rem  servidor em http://127.0.0.1:8080
rem
rem  Uso:  clique duas vezes, ou no terminal:  INICIAR-WINDOWS.bat
rem        INICIAR-WINDOWS.bat --reset   recria a demonstração do zero
rem  Requisito: Python 3.12+ instalado (marque "Add python.exe to PATH").
rem ─────────────────────────────────────────────────────────────────────────
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale o Python 3.12+ ^(com "Add to PATH"^) e tente de novo.
  pause
  exit /b 1
)

if not exist ".venv\" (
  echo -^> Criando ambiente virtual...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo -^> Instalando dependencias...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

set FLASK_APP=app

if "%~1"=="--reset" (
  echo -^> Recriando a demonstracao...
  flask demo-reset --confirmar
) else (
  echo -^> Aplicando migracoes...
  flask db upgrade
  echo -^> Populando dados de demonstracao ^(se ainda nao existirem^)...
  flask seed
)

echo.
echo ------------------------------------------------
echo   Plataforma LGPD em http://127.0.0.1:8080
echo   Encarregado:  dpo@acme.com.br
echo   Gestor:       gestor.rh@acme.com.br
echo   Colaborador:  ana@acme.com.br
echo   2a empresa:   dpo@novaera.com.br
echo   Senha de todos: lgpd1234   (Ctrl+C para encerrar)
echo ------------------------------------------------
echo.

python app.py
pause
