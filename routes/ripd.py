"""RIPD — Relatório de Impacto à Proteção de Dados (Art. 38)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import fk_do_tenant, papeis
from services.auditoria import registrar
from services.ripd_pdf import ripd_pdf

bp = Blueprint("ripd", __name__, url_prefix="/ripd")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    pass


def _do_empresa(rid):
    r = db.session.get(models.Ripd, rid)
    if not r or r.empresa_id != current_user.empresa_id:
        abort(404)
    return r


@bp.route("/")
def listar():
    relatorios = (
        models.Ripd.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.Ripd.criado_em.desc()).all()
    )
    return render_template("ripd/listar.html", relatorios=relatorios)


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:rid>/editar", methods=["GET", "POST"])
def form(rid=None):
    relatorio = _do_empresa(rid) if rid else None
    ropas = (
        models.RopaRegistro.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.RopaRegistro.atividade).all()
    )

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        if not titulo:
            flash("Informe o título do relatório.", "erro")
        else:
            if relatorio is None:
                relatorio = models.Ripd(empresa_id=current_user.empresa_id)
                db.session.add(relatorio)
            # Só aceita um ROPA da própria empresa (evita ler dado de outro tenant via PDF).
            relatorio.ropa_id = fk_do_tenant(
                models.RopaRegistro, request.form.get("ropa_id"), current_user.empresa_id,
            )
            relatorio.titulo = titulo
            relatorio.descricao_tratamento = request.form.get("descricao_tratamento") or ""
            relatorio.probabilidade = _faixa(request.form.get("probabilidade"))
            relatorio.impacto = _faixa(request.form.get("impacto"))
            relatorio.medidas = request.form.get("medidas") or ""
            residual = request.form.get("risco_residual") or ""
            relatorio.risco_residual = residual if residual in models.RISCO_LABELS else None
            relatorio.conclusao = request.form.get("conclusao") or ""
            relatorio.status = "concluido" if request.form.get("status") == "concluido" else "rascunho"
            registrar("ripd_salvo", titulo)
            db.session.commit()
            flash("RIPD salvo.", "ok")
            return redirect(url_for("ripd.listar"))

    return render_template("ripd/form.html", relatorio=relatorio, ropas=ropas,
                           niveis=models.RISCO_NIVEIS)


@bp.route("/<int:rid>/excluir", methods=["POST"])
def excluir(rid):
    relatorio = _do_empresa(rid)
    registrar("ripd_excluido", relatorio.titulo)
    db.session.delete(relatorio)
    db.session.commit()
    flash("RIPD excluído.", "ok")
    return redirect(url_for("ripd.listar"))


@bp.route("/<int:rid>/pdf")
def pdf(rid):
    relatorio = _do_empresa(rid)
    buf = ripd_pdf(current_user.empresa, relatorio)
    return send_file(buf, mimetype="application/pdf", as_attachment=False,
                     download_name=f"ripd-{relatorio.id}.pdf")


def _faixa(valor):
    try:
        return max(1, min(3, int(valor)))
    except (TypeError, ValueError):
        return 1
