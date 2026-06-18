#!/bin/sh
# Entrypoint do container: aplica migrações e (opcionalmente) popula a demo,
# depois sobe o gunicorn.
set -e

export FLASK_APP=app

echo "→ Aplicando migrações..."
flask db upgrade

if [ "${SEED_DEMO:-0}" = "1" ]; then
  echo "→ Populando dados de demonstração..."
  flask seed
fi

# -w 1 por padrão: o rate limit usa armazenamento em memória (não compartilhado
# entre workers). Para escalar, aponte o Flask-Limiter para Redis e suba WEB_CONCURRENCY.
exec gunicorn -w "${WEB_CONCURRENCY:-1}" -b 0.0.0.0:8080 --access-logfile - app:app
