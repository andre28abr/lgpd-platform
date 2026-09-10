#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
#  Plataforma LGPD — inicialização local (Linux e macOS)
#  Cria o ambiente, prepara o banco (SQLite), popula a demonstração e sobe o
#  servidor em http://127.0.0.1:8080
#
#  Uso:  ./iniciar.sh            (primeira vez: chmod +x iniciar.sh)
#        ./iniciar.sh --reset    recria a demonstração do zero
# ─────────────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3 não encontrado. Instale o Python 3.12+ e tente de novo."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "→ Criando ambiente virtual..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "→ Instalando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

export FLASK_APP=app

if [ "${1:-}" = "--reset" ]; then
  echo "→ Recriando a demonstração..."
  flask demo-reset --confirmar
else
  echo "→ Aplicando migrações..."
  flask db upgrade
  echo "→ Populando dados de demonstração (se ainda não existirem)..."
  flask seed
fi

echo ""
echo "──────────────────────────────────────────────"
echo "  Plataforma LGPD em http://127.0.0.1:8080"
echo "  Encarregado:  dpo@acme.com.br"
echo "  Gestor:       gestor.rh@acme.com.br"
echo "  Colaborador:  ana@acme.com.br"
echo "  2ª empresa:   dpo@novaera.com.br"
echo "  Senha de todos: lgpd1234   (Ctrl+C para encerrar)"
echo "──────────────────────────────────────────────"
echo ""

exec python app.py
