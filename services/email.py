"""Envio de e-mail por SMTP, com fallback "dry-run" quando não há servidor.

Sem MAIL_SERVER configurado, nada sai para a rede — mas TODO e-mail (enviado ou
não) fica registrado na caixa de saída (``EmailEnviado``), visível em
Administração → E-mails. É o que permite demonstrar reset de senha e
notificações sem depender de infraestrutura de e-mail.
"""
import re
import smtplib
from email.message import EmailMessage

from flask import current_app

import models
from extensions import db

SMTP_TIMEOUT_S = 10


def _linha_unica(valor: str) -> str:
    # Cabeçalhos não aceitam CR/LF (a stdlib levantaria ValueError); remove em vez de quebrar.
    return (valor or "").replace("\r", " ").replace("\n", " ").strip()


def _registrar_saida(empresa_id, de, para, assunto, corpo, enviado) -> None:
    """Guarda a cópia na caixa de saída. Best-effort: nunca derruba o envio."""
    try:
        db.session.add(models.EmailEnviado(
            empresa_id=empresa_id, remetente=de, destinatario=para,
            assunto=assunto[:255], corpo=corpo, enviado=enviado,
        ))
        db.session.commit()
    except Exception:  # noqa: BLE001 — a caixa de saída é acessória
        db.session.rollback()
        current_app.logger.exception("falha ao registrar e-mail na caixa de saída")


def enviar(destinatario: str, assunto: str, corpo: str, remetente: str | None = None,
           empresa_id: int | None = None) -> bool:
    """Retorna True se o e-mail foi de fato enviado; False em dry-run ou falha.

    ``remetente`` permite que cada empresa assine suas notificações (configurável
    pelo Encarregado); em branco, vale o MAIL_FROM da plataforma. ``empresa_id``
    escopa a cópia na caixa de saída ao tenant.

    Nunca propaga exceção: uma falha de SMTP não pode derrubar a ação que a
    disparou (registrar um pedido, notificar reavaliações). O erro vai para o log.
    """
    cfg = current_app.config
    servidor = cfg.get("MAIL_SERVER")
    destinatario, assunto = _linha_unica(destinatario), _linha_unica(assunto)
    de = _linha_unica(remetente) or cfg["MAIL_FROM"]

    if not servidor:
        # Dry-run (demo): a caixa de saída é o ÚNICO canal — o link de reset fica íntegro
        # para o fluxo funcionar. O Encarregado já pode redefinir senhas pelo admin.
        current_app.logger.info("email dry-run de=%s para=%s assunto=%r", de, destinatario, assunto)
        _registrar_saida(empresa_id, de, destinatario, assunto, corpo, enviado=False)
        return False

    # Com SMTP real, a caixa de saída é só histórico: o token de reset não fica legível nela.
    corpo_registro = re.sub(r"/senha/redefinir/\S+", "/senha/redefinir/<token>", corpo)

    enviado = False
    try:
        msg = EmailMessage()
        msg["From"] = de
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(corpo)

        with smtplib.SMTP(servidor, cfg["MAIL_PORT"], timeout=SMTP_TIMEOUT_S) as s:
            if cfg.get("MAIL_USE_TLS"):
                s.starttls()
            if cfg.get("MAIL_USERNAME"):
                s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            s.send_message(msg)
        enviado = True
    except Exception:  # noqa: BLE001 — SMTP falha de muitas formas; todas viram log
        current_app.logger.exception("falha ao enviar e-mail para=%s assunto=%r", destinatario, assunto)
    _registrar_saida(empresa_id, de, destinatario, assunto, corpo_registro, enviado=enviado)
    return enviado
