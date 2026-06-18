"""Trilha de auditoria: registra ações sensíveis para accountability (Art. 6º, X)."""
from flask import has_request_context, request
from flask_login import current_user

import models
from extensions import db


def registrar(acao, detalhe=None, usuario=None, empresa_id=None, commit=False):
    """Cria um registro de auditoria. Resolve usuário/empresa/IP do contexto."""
    u = usuario
    if u is None and has_request_context() and current_user.is_authenticated:
        u = current_user._get_current_object()

    log = models.AuditLog(
        acao=acao,
        detalhe=(detalhe or "")[:255] or None,
        usuario_id=getattr(u, "id", None),
        empresa_id=empresa_id if empresa_id is not None else getattr(u, "empresa_id", None),
        ip=request.remote_addr if has_request_context() else None,
    )
    db.session.add(log)
    if commit:
        db.session.commit()
    return log
