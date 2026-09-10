"""Envio de e-mail por SMTP, com fallback "dry-run" quando não há servidor.

Sem MAIL_SERVER configurado, apenas registra no log (útil em desenvolvimento e
demonstração, sem depender de infraestrutura de e-mail).
"""
import smtplib
from email.message import EmailMessage

from flask import current_app

SMTP_TIMEOUT_S = 10


def _linha_unica(valor: str) -> str:
    # Cabeçalhos não aceitam CR/LF (a stdlib levantaria ValueError); remove em vez de quebrar.
    return (valor or "").replace("\r", " ").replace("\n", " ").strip()


def enviar(destinatario: str, assunto: str, corpo: str, remetente: str | None = None) -> bool:
    """Retorna True se o e-mail foi de fato enviado; False em dry-run ou falha.

    ``remetente`` permite que cada empresa assine suas notificações (configurável
    pelo Encarregado); em branco, vale o MAIL_FROM da plataforma.

    Nunca propaga exceção: uma falha de SMTP não pode derrubar a ação que a
    disparou (registrar um pedido, notificar reavaliações). O erro vai para o log.
    """
    cfg = current_app.config
    servidor = cfg.get("MAIL_SERVER")
    destinatario, assunto = _linha_unica(destinatario), _linha_unica(assunto)
    de = _linha_unica(remetente) or cfg["MAIL_FROM"]

    if not servidor:
        current_app.logger.info("email dry-run de=%s para=%s assunto=%r", de, destinatario, assunto)
        return False

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
        return True
    except Exception:  # noqa: BLE001 — SMTP falha de muitas formas; todas viram log
        current_app.logger.exception("falha ao enviar e-mail para=%s assunto=%r", destinatario, assunto)
        return False
