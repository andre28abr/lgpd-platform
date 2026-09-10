"""Utilitários compartilhados pelos blueprints."""
import re
import unicodedata
from functools import wraps
from urllib.parse import urlparse

from flask import abort, request
from flask_login import current_user

from extensions import db


def gestor_somente_leitura(*endpoints_de_edicao):
    """Nos módulos do Pilar 2 o Gestor apenas visualiza; só o Encarregado altera.

    Devolve uma função para chamar no ``before_request`` do blueprint: para quem
    não é Encarregado, bloqueia (403) qualquer método que não seja GET/HEAD e
    também as páginas de formulário listadas em ``endpoints_de_edicao`` — o
    gestor não deve nem abrir a tela de edição. Exportações (GET) continuam
    liberadas: exportar é visualizar.
    """
    def checar():
        if current_user.is_encarregado:
            return
        if request.method not in ("GET", "HEAD") or request.endpoint in endpoints_de_edicao:
            abort(403)
    return checar


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


def fk_do_tenant(modelo, valor, empresa_id):
    """Converte um id vindo do formulário em um id válido DA EMPRESA, ou None.

    Fecha o IDOR por chave estrangeira (ex.: um ``ropa_id``/``setor_id`` de outro
    tenant enviado no POST) e evita o 500 de ``int()`` em entrada não numérica.
    Um valor inválido ou de outra empresa é silenciosamente descartado.
    """
    if not valor:
        return None
    try:
        obj_id = int(valor)
    except (TypeError, ValueError):
        return None
    # no_autoflush: chamado no meio do preenchimento de um registro novo já na
    # sessão — não pode disparar o flush de um objeto ainda incompleto.
    with db.session.no_autoflush:
        obj = db.session.get(modelo, obj_id)
    if not obj or getattr(obj, "empresa_id", None) != empresa_id:
        return None
    return obj.id


def txt(valor, limite: int) -> str:
    """Texto de formulário: tira espaços e corta no tamanho da coluna.

    O SQLite aceita qualquer tamanho em silêncio; o PostgreSQL rejeita o INSERT e a
    página viraria 500 — inclusive no portal público, que recebe entrada anônima.
    """
    return (valor or "").strip()[:limite]


def slugify(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "item"
