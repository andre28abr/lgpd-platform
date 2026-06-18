"""Utilitários compartilhados pelos blueprints."""
import re
import unicodedata
from functools import wraps
from urllib.parse import urlparse

from flask import abort
from flask_login import current_user


def papeis(*permitidos):
    """Restringe a rota aos papéis informados (use após @login_required)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.papel not in permitidos:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def destino_seguro(target: str):
    """Evita open redirect: só aceita caminhos relativos do próprio site."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    if not target.startswith("/") or target.startswith("//"):
        return None
    return target


def slugify(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "item"
