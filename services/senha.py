"""Redefinição de senha por link temporário enviado por e-mail.

O token é assinado com a SECRET_KEY (itsdangerous) e carrega um sufixo do hash
da senha atual: assim que a senha muda, o link deixa de valer — uso único sem
precisar guardar nada no banco.
"""
from flask import current_app, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

import models
from extensions import db
from services.email import enviar

VALIDADE_S = 60 * 60  # 1 hora


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="redefinir-senha")


def gerar_token(usuario) -> str:
    return _serializer().dumps({"id": usuario.id, "h": usuario.senha_hash[-16:]})


def usuario_do_token(token):
    """Usuário dono do token, ou None se inválido, expirado, já usado ou inativo."""
    try:
        dados = _serializer().loads(token, max_age=VALIDADE_S)
    except (BadSignature, SignatureExpired):
        return None
    usuario = db.session.get(models.Usuario, dados.get("id"))
    if not usuario or not usuario.ativo or usuario.senha_hash[-16:] != dados.get("h"):
        return None
    return usuario


def enviar_link(usuario) -> bool:
    link = url_for("auth.redefinir_senha", token=gerar_token(usuario), _external=True)
    corpo = (
        f"Olá, {usuario.nome}.\n\n"
        f"Recebemos um pedido para redefinir a sua senha na Plataforma LGPD.\n"
        f"Use o link abaixo (válido por 1 hora):\n\n{link}\n\n"
        f"Se você não pediu isso, ignore esta mensagem — sua senha continua a mesma."
    )
    return enviar(usuario.email, "LGPD: redefinição de senha", corpo,
                  remetente=usuario.empresa.email_remetente)
