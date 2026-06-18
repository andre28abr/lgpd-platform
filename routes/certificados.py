"""Certificados: listagem, PDF e verificação pública por código."""
from flask import Blueprint, abort, render_template, send_file
from flask_login import current_user, login_required

import models
from extensions import db
from services.certificado_pdf import gerar_pdf

bp = Blueprint("certificados", __name__, url_prefix="/certificados")


@bp.route("/")
@login_required
def listar():
    certs = (
        models.Certificado.query.filter_by(usuario_id=current_user.id)
        .order_by(models.Certificado.emitido_em.desc())
        .all()
    )
    return render_template("certificados/listar.html", certificados=certs)


@bp.route("/<int:cert_id>.pdf")
@login_required
def pdf(cert_id):
    cert = db.session.get(models.Certificado, cert_id)
    if not cert:
        abort(404)
    # O dono vê o seu; o encarregado vê os da própria empresa.
    dono = cert.usuario_id == current_user.id
    gestor_mesma_empresa = current_user.is_encarregado and cert.empresa_id == current_user.empresa_id
    if not (dono or gestor_mesma_empresa):
        abort(403)

    buffer = gerar_pdf(cert)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"certificado-lgpd-{cert.codigo}.pdf",
    )


@bp.route("/verificar/<codigo>")
def verificar(codigo):
    """Página pública de verificação de autenticidade (sem login)."""
    cert = models.Certificado.query.filter_by(codigo=codigo).first()
    return render_template("certificados/verificar.html", cert=cert, codigo=codigo)
