"""Perfil do usuário: 2FA (TOTP) com códigos de recuperação."""
import base64
import io

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from extensions import db
from services.auditoria import registrar
from services.recovery import gerar_codigos, restantes

bp = Blueprint("perfil", __name__, url_prefix="/perfil")


@bp.route("/")
@login_required
def index():
    return render_template("perfil/index.html", codigos_restantes=restantes(current_user))


@bp.route("/2fa/ativar", methods=["GET", "POST"])
@login_required
def ativar_2fa():
    import pyotp

    if current_user.mfa_ativo:
        flash("A verificação em duas etapas já está ativa.", "info")
        return redirect(url_for("perfil.index"))

    secret = session.get("_2fa_secret_prov") or pyotp.random_base32()
    session["_2fa_secret_prov"] = secret

    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").replace(" ", "")
        if pyotp.TOTP(secret).verify(codigo, valid_window=1):
            current_user.totp_secret = secret
            current_user.mfa_ativo = True
            session.pop("_2fa_secret_prov", None)
            session["_recovery_show"] = gerar_codigos(current_user)
            registrar("2fa_ativado", current_user.email)
            db.session.commit()
            flash("Verificação em duas etapas ativada. Guarde seus códigos de recuperação.", "ok")
            return redirect(url_for("perfil.codigos"))
        flash("Código inválido. Confira o app autenticador e tente de novo.", "erro")

    uri = pyotp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="Plataforma LGPD")
    return render_template("perfil/ativar_2fa.html", secret=secret, qr=_qr_data_uri(uri))


@bp.route("/2fa/codigos")
@login_required
def codigos():
    codigos = session.pop("_recovery_show", None)
    if not codigos:
        return redirect(url_for("perfil.index"))
    return render_template("perfil/codigos.html", codigos=codigos)


@bp.route("/2fa/codigos/regenerar", methods=["POST"])
@login_required
def regenerar_codigos():
    if current_user.mfa_ativo:
        session["_recovery_show"] = gerar_codigos(current_user)
        registrar("2fa_codigos_regenerados", current_user.email)
        db.session.commit()
        return redirect(url_for("perfil.codigos"))
    return redirect(url_for("perfil.index"))


@bp.route("/2fa/desativar", methods=["POST"])
@login_required
def desativar_2fa():
    current_user.mfa_ativo = False
    current_user.totp_secret = None
    models_limpar_recovery(current_user)
    registrar("2fa_desativado", current_user.email)
    db.session.commit()
    flash("Verificação em duas etapas desativada.", "ok")
    return redirect(url_for("perfil.index"))


def models_limpar_recovery(usuario):
    import models
    models.RecoveryCode.query.filter_by(usuario_id=usuario.id).delete()


def _qr_data_uri(uri: str) -> str:
    import qrcode

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
