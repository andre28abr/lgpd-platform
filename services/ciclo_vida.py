"""Ciclo de vida dos dados da PRÓPRIA plataforma — a LGPD aplicada a ela mesma.

- Anonimização de usuário desligado (Art. 12 e 16): remove o que identifica a
  pessoa e mantém o histórico estatístico (provas, certificados, auditoria por id).
- Expurgo por política de retenção (Art. 15 e 16): auditoria e caixa de saída
  de e-mails, preservando a integridade da cadeia de hash da auditoria.
"""
import secrets
from datetime import timedelta

from werkzeug.security import generate_password_hash

import models
from extensions import db
from services.auditoria import ACAO_EXPURGO, registrar
from utils import agora_utc


def anonimizar_usuario(usuario) -> None:
    """Irreversível. O usuário precisa estar inativo (o chamador garante).

    Nome e e-mail viram rótulos neutros; senha e 2FA são destruídos; cópias de
    e-mail para o endereço antigo saem da caixa de saída. Provas, certificados e
    registros de auditoria continuam apontando para o id (pseudônimo)."""
    email_antigo = usuario.email
    usuario.nome = f"Colaborador anonimizado #{usuario.id}"
    usuario.email = f"anonimizado-{usuario.id}@invalido.local"
    usuario.senha_hash = generate_password_hash(secrets.token_hex(32))
    usuario.totp_secret, usuario.mfa_ativo = None, False
    usuario.ativo = False
    usuario.anonimizado_em = agora_utc()
    models.RecoveryCode.query.filter_by(usuario_id=usuario.id).delete(synchronize_session=False)
    models.EmailEnviado.query.filter_by(destinatario=email_antigo).delete(synchronize_session=False)


def expurgar(dias_auditoria: int, dias_emails: int) -> tuple[int, int]:
    """Apaga registros mais antigos que a retenção. Retorna (logs, emails) removidos.

    Para a auditoria, grava um marcador com a *âncora* (hash do último registro
    removido) — ``verificar_cadeia`` parte dela e a cadeia continua estrita.
    """
    agora = agora_utc()
    n_logs = n_emails = 0

    if dias_emails > 0:
        limite = agora - timedelta(days=dias_emails)
        n_emails = (models.EmailEnviado.query.filter(models.EmailEnviado.criado_em < limite)
                    .delete(synchronize_session=False))

    if dias_auditoria > 0:
        limite = agora - timedelta(days=dias_auditoria)
        # A cadeia é encadeada por id; a retenção é aplicada como um PREFIXO contíguo:
        # remove-se tudo até o último registro fora da retenção. Assim a âncora é,
        # por construção, o antecessor do primeiro sobrevivente.
        ultimo_removido = (models.AuditLog.query.filter(models.AuditLog.criado_em < limite)
                           .order_by(models.AuditLog.id.desc()).first())
        if ultimo_removido:
            ancora = ultimo_removido.hash or "-"
            id_corte = ultimo_removido.id
            n_logs = (models.AuditLog.query.filter(models.AuditLog.id <= id_corte)
                      .delete(synchronize_session=False))
            sobrevivente = models.AuditLog.query.filter(models.AuditLog.id > id_corte).first()
            # Sem sobreviventes, o marcador é o primeiro registro e encadeia do zero.
            if not sobrevivente:
                ancora = "-"
            registrar(ACAO_EXPURGO, f"ate={limite:%Y-%m-%d} removidos={n_logs} ancora={ancora}")

    db.session.commit()
    return n_logs, n_emails
