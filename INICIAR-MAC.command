#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────
#  Plataforma LGPD — inicialização local (macOS)
#  Cria o ambiente, prepara o banco (SQLite), popula a demonstração e sobe o
#  servidor em http://127.0.0.1:8080
# ─────────────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
  echo "→ Criando ambiente virtual..."
  "$PY" -m venv .venv
fi

source .venv/bin/activate

echo "→ Instalando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

export FLASK_APP=app

if [ -d "migrations" ]; then
  echo "→ Aplicando migrações..."
  flask db upgrade
else
  echo "→ Criando tabelas (SQLite)..."
  flask init-db
fi

echo "→ Populando dados de demonstração..."
flask seed

echo ""
echo "──────────────────────────────────────────────"
echo "  Plataforma LGPD em http://127.0.0.1:8080"
echo "  Login: dpo@acme.com.br   Senha: lgpd1234"
echo "  (Ctrl+C para encerrar)"
echo "──────────────────────────────────────────────"
echo ""

exec python app.py
