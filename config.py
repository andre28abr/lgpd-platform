"""Configuração da aplicação.

A plataforma é *Postgres-ready* mas roda em SQLite por padrão (zero config).
Toda a diferença entre os dois bancos vive em ``resolve_database_uri`` e nas
``engine_options`` calculadas no app factory — o resto do código é agnóstico
graças ao SQLAlchemy.
"""
import os


def _normalize(uri: str) -> str:
    # Heroku/alguns provedores entregam 'postgres://', que o SQLAlchemy moderno
    # não aceita; normaliza para 'postgresql://'.
    if uri.startswith("postgres://"):
        return "postgresql://" + uri[len("postgres://"):]
    return uri


def resolve_database_uri(instance_path: str) -> str:
    """Decide o banco a partir de DATABASE_URL, caindo em SQLite local."""
    uri = (os.environ.get("DATABASE_URL") or "").strip()
    if uri:
        return _normalize(uri)
    os.makedirs(instance_path, exist_ok=True)
    return "sqlite:///" + os.path.join(instance_path, "lgpd.db")


def engine_options_for(uri: str) -> dict:
    """Opções de engine específicas por dialeto."""
    if uri.startswith("postgresql"):
        # Evita 'server closed the connection' após timeout/restart do Postgres.
        return {"pool_pre_ping": True, "pool_recycle": 280}
    return {}


def _as_bool(value: str) -> bool:
    return (value or "").strip().lower() in ("1", "true", "yes", "on", "sim")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-inseguro-troque-em-producao"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessão / cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool(os.environ.get("SESSION_COOKIE_SECURE"))
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 horas

    # Regras de avaliação / certificação
    NOTA_CORTE = int(os.environ.get("NOTA_CORTE", "70"))
    QUESTOES_POR_PROVA = int(os.environ.get("QUESTOES_POR_PROVA", "8"))
    CERT_VALIDADE_DIAS = int(os.environ.get("CERT_VALIDADE_DIAS", "365"))
    TEMPO_PROVA_MIN = int(os.environ.get("TEMPO_PROVA_MIN", "15"))  # 0 = sem limite

    # Bloqueio de conta por tentativas de login malsucedidas
    LOGIN_MAX_TENTATIVAS = int(os.environ.get("LOGIN_MAX_TENTATIVAS", "5"))
    LOGIN_BLOQUEIO_MIN = int(os.environ.get("LOGIN_BLOQUEIO_MIN", "15"))

    # E-mail (notificações). Sem MAIL_SERVER => modo "dry-run" (apenas registra no log).
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = _as_bool(os.environ.get("MAIL_USE_TLS", "true"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM", "nao-responder@plataforma-lgpd.local")

    # Logging em arquivo (rotação). Vazio desativa o arquivo (mantém só stdout).
    LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")

    # Reavaliação: dias antes do vencimento que disparam notificação
    REAVALIACAO_DIAS = int(os.environ.get("REAVALIACAO_DIAS", "30"))

    # Feed de legislação/notícias (RSS). Vazio => mostra só as referências fixas.
    FEED_URL = os.environ.get("FEED_URL", "")
