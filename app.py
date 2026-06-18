"""App factory da Plataforma LGPD.

Expõe ``create_app()`` (factory) e ``app`` no nível do módulo para que tanto o
Flask CLI (``flask --app app``) quanto o gunicorn (``gunicorn app:app``) funcionem.
"""
import os
import sys

from dotenv import load_dotenv

# Carrega o .env DESTE projeto sobrescrevendo o ambiente — evita que uma
# DATABASE_URL definida na máquina para outro projeto "vaze" para cá.
# Os testes definem LGPD_SKIP_DOTENV=1 para controlar o banco de teste.
if os.environ.get("LGPD_SKIP_DOTENV") != "1":
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

import bleach
import markdown as md_lib
from flask import Flask, flash, redirect, render_template, request, url_for
from markupsafe import Markup
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config, engine_options_for, resolve_database_uri
from extensions import db, limiter, login_manager, migrate
from security import apply_security_headers, generate_csrf_token, validate_csrf

# Tags/atributos permitidos ao renderizar o Markdown das trilhas (defesa contra XSS).
_TAGS_OK = [
    "h1", "h2", "h3", "h4", "p", "br", "hr", "strong", "em", "ul", "ol", "li",
    "blockquote", "code", "pre", "a", "table", "thead", "tbody", "tr", "th", "td",
]
_ATTRS_OK = {"a": ["href", "title", "rel"], "th": ["align"], "td": ["align"]}


# Liga a checagem de chaves estrangeiras no SQLite (desligada por padrão no SQLite).
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _):
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    uri = resolve_database_uri(app.instance_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options_for(uri)

    # ── Extensões ──
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "aviso"

    import models  # noqa: F401 — registra os modelos no metadata

    @login_manager.user_loader
    def carregar_usuario(user_id):
        return db.session.get(models.Usuario, int(user_id))

    # ── CSRF + cabeçalhos de segurança ──
    @app.before_request
    def _csrf_guard():
        validate_csrf()

    @app.after_request
    def _headers(resp):
        return apply_security_headers(resp)

    # Logging estruturado (logfmt) com request-id, em stdout e arquivo rotativo.
    import logging
    from logging.handlers import RotatingFileHandler
    if not getattr(app, "_log_configurado", False):
        fmt = logging.Formatter("%(asctime)s level=%(levelname)s %(message)s")
        stream = logging.StreamHandler()
        stream.setFormatter(fmt)
        app.logger.addHandler(stream)
        log_file = app.config.get("LOG_FILE")
        if log_file:
            os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
            arquivo = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
            arquivo.setFormatter(fmt)
            app.logger.addHandler(arquivo)
        app.logger.setLevel(logging.INFO)
        app._log_configurado = True

    @app.before_request
    def _request_id():
        import uuid

        from flask import g
        g.request_id = uuid.uuid4().hex[:12]

    @app.before_request
    def _exigir_2fa():
        """Se a empresa exige 2FA e o usuário não ativou, força o enrolamento."""
        from flask_login import current_user
        if not current_user.is_authenticated:
            return None
        empresa = getattr(current_user, "empresa", None)
        if not empresa or not empresa.mfa_obrigatorio or current_user.mfa_ativo:
            return None
        permitidos = {"perfil.ativar_2fa", "perfil.codigos", "perfil.regenerar_codigos",
                      "auth.logout", "static"}
        if request.endpoint in permitidos:
            return None
        flash("Sua empresa exige verificação em duas etapas. Ative-a para continuar.", "aviso")
        return redirect(url_for("perfil.ativar_2fa"))

    @app.after_request
    def _log_request(resp):
        from flask import g
        from flask_login import current_user
        try:
            uid = current_user.id if current_user.is_authenticated else "-"
        except Exception:
            uid = "-"
        rid = getattr(g, "request_id", "-")
        resp.headers.setdefault("X-Request-ID", rid)
        app.logger.info("request id=%s method=%s path=%s status=%s user=%s",
                        rid, request.method, request.path, resp.status_code, uid)
        return resp

    @app.context_processor
    def _inject():
        return {"csrf_token": generate_csrf_token, "AREA_LABELS": models.AREA_LABELS}

    # ── Filtro Markdown seguro para as trilhas ──
    @app.template_filter("markdown")
    def _markdown(texto: str):
        if not texto:
            return ""
        bruto = md_lib.markdown(texto, extensions=["extra", "sane_lists"])
        limpo = bleach.clean(bruto, tags=_TAGS_OK, attributes=_ATTRS_OK, strip=True)
        return Markup(bleach.linkify(limpo))

    # ── Blueprints ──
    from routes.auth import bp as auth_bp
    from routes.painel import bp as painel_bp
    from routes.trilhas import bp as trilhas_bp
    from routes.provas import bp as provas_bp
    from routes.certificados import bp as certificados_bp
    from routes.ranking import bp as ranking_bp
    from routes.admin import bp as admin_bp
    from routes.diagnostico import bp as diagnostico_bp
    from routes.perfil import bp as perfil_bp
    from routes.ropa import bp as ropa_bp
    from routes.direitos import bp as direitos_bp
    from routes.ripd import bp as ripd_bp
    from routes.incidentes import bp as incidentes_bp
    from routes.legislacao import bp as legislacao_bp
    from routes.privacidade import bp as privacidade_bp
    from routes.publico import bp as publico_bp

    for bp in (auth_bp, painel_bp, trilhas_bp, provas_bp, certificados_bp,
               ranking_bp, admin_bp, diagnostico_bp, perfil_bp, ropa_bp, direitos_bp,
               ripd_bp, incidentes_bp, legislacao_bp, privacidade_bp, publico_bp):
        app.register_blueprint(bp)

    # ── Páginas de erro ──
    @app.errorhandler(403)
    def _403(_):
        return render_template("erro.html", codigo=403, mensagem="Você não tem acesso a esta página."), 403

    @app.errorhandler(404)
    def _404(_):
        return render_template("erro.html", codigo=404, mensagem="Página não encontrada."), 404

    @app.errorhandler(400)
    def _400(e):
        desc = getattr(e, "description", "Requisição inválida.")
        return render_template("erro.html", codigo=400, mensagem=desc), 400

    # ── Comandos CLI ──
    register_cli(app)
    return app


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Cria as tabelas direto (atalho local para SQLite, sem migrações)."""
        db.create_all()
        print("Tabelas criadas.")

    @app.cli.command("seed")
    def seed():
        """Popula a biblioteca curada + uma empresa de demonstração."""
        from seed import executar_seed
        executar_seed()

    @app.cli.command("enviar-reavaliacoes")
    def enviar_reavaliacoes():
        """Notifica colaboradores com certificação vencida/vencendo (rodar via cron)."""
        import models
        from services.notificacoes import notificar_reavaliacoes
        total = 0
        for empresa in models.Empresa.query.filter_by(ativo=True).all():
            notificados, _ = notificar_reavaliacoes(empresa)
            total += notificados
            print(f"{empresa.slug}: {notificados} notificado(s)")
        print(f"Total: {total}")


app = create_app()


def _abrir_navegador(url: str) -> None:
    """Abre o navegador no app, uma única vez, logo após o servidor subir."""
    import threading
    import webbrowser

    threading.Timer(1.5, lambda: webbrowser.open(url)).start()


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", "8080"))
    url = f"http://127.0.0.1:{porta}"

    # Abre o navegador automaticamente, exceto:
    #   - com a flag --no-browser (preview/headless);
    #   - com ABRIR_NAVEGADOR=0;
    #   - no processo filho do reloader (evita reabrir a cada alteração de arquivo).
    abrir = "--no-browser" not in sys.argv and os.environ.get("ABRIR_NAVEGADOR", "1") != "0"
    if abrir and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        _abrir_navegador(url)

    app.run(host="127.0.0.1", port=porta, debug=True)
