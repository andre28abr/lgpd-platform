"""Envio de e-mail por SMTP, com fallback "dry-run" quando não há servidor.

Sem MAIL_SERVER configurado, apenas registra no log (útil em desenvolvimento e
demonstração, sem depender de infraestrutura de e-mail).
"""
import smtplib
from email.message import EmailMessage

from flask import current_app


def enviar(destinatario: str, assunto: str, corpo: str) -> bool:
    """Retorna True se o e-mail foi de fato enviado; False em modo dry-run."""
    cfg = current_app.config
    servidor = cfg.get("MAIL_SERVER")

    if not servidor:
        current_app.logger.info("email dry-run para=%s assunto=%r", destinatario, assunto)
        return False

    msg = EmailMessage()
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(corpo)

    with smtplib.SMTP(servidor, cfg["MAIL_PORT"]) as s:
        if cfg.get("MAIL_USE_TLS"):
            s.starttls()
        if cfg.get("MAIL_USERNAME"):
            s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        s.send_message(msg)
    return True
