"""ROPA — Registro das operações de tratamento (Art. 37)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import fk_do_tenant, papeis
from services.auditoria import registrar
from services.ropa_export import ropa_excel, ropa_pdf

bp = Blueprint("ropa", __name__, url_prefix="/ropa")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    pass


def _do_empresa(reg_id):
    reg = db.session.get(models.RopaRegistro, reg_id)
    if not reg or reg.empresa_id != current_user.empresa_id:
        abort(404)
    return reg


@bp.route("/")
def listar():
    registros = (
        models.RopaRegistro.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.RopaRegistro.atividade).all()
    )
    return render_template("ropa/listar.html", registros=registros)


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:reg_id>/editar", methods=["GET", "POST"])
def form(reg_id=None):
    reg = _do_empresa(reg_id) if reg_id else None
    setores = models.Setor.query.filter_by(empresa_id=current_user.empresa_id).order_by(models.Setor.nome).all()

    if request.method == "POST":
        atividade = (request.form.get("atividade") or "").strip()
        if not atividade:
            flash("Informe a atividade de tratamento.", "erro")
        else:
            if reg is None:
                reg = models.RopaRegistro(empresa_id=current_user.empresa_id)
                db.session.add(reg)
            reg.setor_id = fk_do_tenant(models.Setor, request.form.get("setor_id"), current_user.empresa_id)
            reg.atividade = atividade
            reg.titulares = (request.form.get("titulares") or "").strip()
            reg.categorias_dados = request.form.get("categorias_dados") or ""
            reg.finalidade = request.form.get("finalidade") or ""
            base = request.form.get("base_legal") or ""
            reg.base_legal = base if base in models.BASE_LEGAL_LABELS else None
            reg.retencao = (request.form.get("retencao") or "").strip()
            reg.compartilhamento = request.form.get("compartilhamento") or ""
            registrar("ropa_salvo", atividade)
            db.session.commit()
            flash("Registro salvo.", "ok")
            return redirect(url_for("ropa.listar"))

    return render_template("ropa/form.html", reg=reg, setores=setores, bases=models.BASES_LEGAIS)


@bp.route("/<int:reg_id>/excluir", methods=["POST"])
def excluir(reg_id):
    reg = _do_empresa(reg_id)
    registrar("ropa_excluido", reg.atividade)
    db.session.delete(reg)
    db.session.commit()
    flash("Registro excluído.", "ok")
    return redirect(url_for("ropa.listar"))


def _registros_da_empresa():
    return (
        models.RopaRegistro.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.RopaRegistro.atividade).all()
    )


@bp.route("/exportar.xlsx")
def exportar_xlsx():
    registrar("ropa_exportado", "xlsx", commit=True)
    return send_file(
        ropa_excel(current_user.empresa, _registros_da_empresa()),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True, download_name="ropa.xlsx",
    )


@bp.route("/relatorio.pdf")
def relatorio_pdf():
    registrar("ropa_exportado", "pdf", commit=True)
    return send_file(ropa_pdf(current_user.empresa, _registros_da_empresa()),
                     mimetype="application/pdf", as_attachment=False, download_name="ropa.pdf")
