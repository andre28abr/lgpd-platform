# Imagem da Plataforma LGPD.
# Usa Python 3.12 (estável e com wheels para todas as dependências).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# instance/ (SQLite, secret_key, uploads) e logs/ ficam fora do git (.dockerignore); precisam
# existir na imagem já com o dono certo — assim o volume nomeado montado em /app/instance
# herda a permissão do appuser em vez de nascer como root e derrubar o boot.
RUN chmod +x entrypoint.sh \
 && useradd --create-home --uid 10001 appuser \
 && mkdir -p /app/instance /app/logs \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Só marca o container como saudável se a app e o banco respondem (rota /saude).
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/saude', timeout=4).status == 200 else 1)"

CMD ["./entrypoint.sh"]
