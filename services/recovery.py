"""Códigos de recuperação de uso único para o 2FA."""
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

import models
from extensions import db


def gerar_codigos(usuario, quantidade: int = 10):
    """Recria os códigos do usuário e devolve a lista em texto plano (mostrar UMA vez)."""
    models.RecoveryCode.query.filter_by(usuario_id=usuario.id).delete()
    codigos = []
    for _ in range(quantidade):
        codigo = secrets.token_hex(4)  # 8 caracteres hex
        codigos.append(codigo)
        db.session.add(models.RecoveryCode(usuario_id=usuario.id, code_hash=generate_password_hash(codigo)))
    return codigos


def consumir(usuario, codigo: str) -> bool:
    """Valida e marca como usado um código de recuperação; True se válido."""
    codigo = (codigo or "").strip().lower()
    if not codigo:
        return False
    for rc in usuario.recovery_codes:
        if not rc.usado and check_password_hash(rc.code_hash, codigo):
            rc.usado = True
            return True
    return False


def restantes(usuario) -> int:
    return sum(1 for rc in usuario.recovery_codes if not rc.usado)
