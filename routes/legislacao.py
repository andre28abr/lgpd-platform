"""Legislação: feed (ANPD) opcional + referências fixas."""
from flask import Blueprint, current_app, render_template
from flask_login import login_required

bp = Blueprint("legislacao", __name__, url_prefix="/legislacao")

REFERENCIAS = [
    ("Lei nº 13.709/2018 (LGPD)",
     "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm"),
    ("ANPD — Autoridade Nacional de Proteção de Dados", "https://www.gov.br/anpd/pt-br"),
    ("ANPD — Notícias", "https://www.gov.br/anpd/pt-br/assuntos/noticias"),
    ("ANPD — Documentos e publicações", "https://www.gov.br/anpd/pt-br/documentos-e-publicacoes"),
]


@bp.route("/")
@login_required
def index():
    url = (current_app.config.get("FEED_URL") or "").strip()
    itens, erro = [], None
    if url:
        try:
            import feedparser
            feed = feedparser.parse(url)
            for entrada in feed.entries[:15]:
                itens.append({
                    "titulo": entrada.get("title", "(sem título)"),
                    "link": entrada.get("link", "#"),
                    "data": entrada.get("published", ""),
                })
            if not itens:
                erro = "O feed não retornou itens."
        except Exception as ex:  # noqa: BLE001 — feed externo pode falhar de várias formas
            erro = f"Não foi possível carregar o feed: {ex}"
    return render_template("legislacao/index.html", itens=itens, erro=erro,
                           referencias=REFERENCIAS, feed_url=url)
