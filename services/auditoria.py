"""Trilha de auditoria: registra ações sensíveis para accountability (Art. 6º, X).

Cada registro carrega um SHA-256 que encadeia o registro anterior. Alterar ou
apagar uma linha "por fora" (acesso direto ao banco) quebra a cadeia, e
``flask auditoria-verificar`` aponta onde. Não impede a adulteração — torna-a
detectável, que é o que accountability exige.

Limite conhecido: com vários workers gravando ao mesmo tempo, dois registros
podem apontar para o mesmo anterior (bifurcação). A verificação acusa isso
como quebra — um falso positivo raro, mas possível em produção multi-worker.
"""
import hashlib

from flask import current_app, has_request_context, request
from flask_login import current_user

import models
from extensions import db
from utils import agora_utc


def _assinatura(hash_anterior, acao, detalhe, usuario_id, empresa_id, ip, criado_em) -> str:
    base = "|".join([
        hash_anterior or "", acao or "", detalhe or "", str(usuario_id or ""),
        str(empresa_id or ""), ip or "", criado_em.isoformat(),
    ])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _hash_do_log(log, hash_anterior) -> str:
    return _assinatura(hash_anterior, log.acao, log.detalhe, log.usuario_id,
                       log.empresa_id, log.ip, log.criado_em)


def _ultimo_hash():
    """Hash do último registro — inclusive um ainda não commitado nesta sessão."""
    pendentes = [o for o in db.session.new if isinstance(o, models.AuditLog) and o.hash]
    if pendentes:
        return pendentes[-1].hash
    with db.session.no_autoflush:
        ultimo = models.AuditLog.query.order_by(models.AuditLog.id.desc()).first()
    return ultimo.hash if ultimo else None


def registrar(acao, detalhe=None, usuario=None, empresa_id=None, commit=False):
    """Cria um registro de auditoria. Resolve usuário/empresa/IP do contexto.

    É *best-effort*: a trilha nunca pode derrubar a ação que está auditando.
    Qualquer falha vira log de erro e a função devolve ``None``. Os campos são
    truncados aos limites das colunas (``acao`` 120, ``detalhe`` 255) — o SQLite
    truncaria em silêncio, mas o PostgreSQL rejeitaria o INSERT.
    """
    try:
        u = usuario
        if u is None and has_request_context() and current_user.is_authenticated:
            u = current_user._get_current_object()

        log = models.AuditLog(
            acao=(acao or "")[:120],
            detalhe=(detalhe or "")[:255] or None,
            usuario_id=getattr(u, "id", None),
            empresa_id=empresa_id if empresa_id is not None else getattr(u, "empresa_id", None),
            ip=(request.remote_addr or "")[:45] if has_request_context() else None,
            criado_em=agora_utc(),  # explícito: entra no hash antes do flush
        )
        log.hash = _hash_do_log(log, _ultimo_hash())
        db.session.add(log)
        if commit:
            db.session.commit()
        return log
    except Exception:  # noqa: BLE001 — auditoria não pode falhar a operação principal
        if commit:
            db.session.rollback()
        current_app.logger.exception("falha ao registrar auditoria acao=%s", acao)
        return None


ACAO_EXPURGO = "auditoria_expurgada"


def ancora_do_expurgo():
    """Hash do último registro removido pelo expurgo mais recente (ou None).

    O expurgo (``ciclo_vida.expurgar``) grava um marcador ``ancora=<hash>``; a
    verificação parte dele, para o primeiro registro sobrevivente continuar
    conferindo contra o seu antecessor real, mesmo depois de apagado.
    """
    marcador = (models.AuditLog.query.filter_by(acao=ACAO_EXPURGO)
                .order_by(models.AuditLog.id.desc()).first())
    if marcador and marcador.detalhe and "ancora=" in marcador.detalhe:
        valor = marcador.detalhe.split("ancora=", 1)[1].split()[0]
        return valor if valor and valor != "-" else None
    return None


def verificar_cadeia():
    """Percorre a trilha em ordem e reconfere cada hash.

    Retorna ``(ok, verificados, id_quebrado)``. Registros anteriores à cadeia
    (hash None) são pulados, mas continuam contando como "anterior" dos próximos.
    """
    anterior, verificados = ancora_do_expurgo(), 0
    for log in models.AuditLog.query.order_by(models.AuditLog.id).all():
        if log.hash is not None:
            if log.hash != _hash_do_log(log, anterior):
                return False, verificados, log.id
            verificados += 1
        anterior = log.hash
    return True, verificados, None
