"""Incidentes de segurança (Art. 48): registro e acompanhamento."""
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import gestor_somente_leitura, papeis, txt
from services.auditoria import registrar
from services.notificacoes import notificar_novo_incidente

bp = Blueprint("incidentes", __name__, url_prefix="/incidentes")
_somente_leitura = gestor_somente_leitura("incidentes.novo")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    _somente_leitura()


def _do_empresa(iid):
    inc = db.session.get(models.Incidente, iid)
    if not inc or inc.empresa_id != current_user.empresa_id:
        abort(404)
    return inc


def _data(valor):
    valor = (valor or "").strip()
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        return None


def _inteiro(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


@bp.route("/")
def listar():
    incidentes = (
        models.Incidente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.Incidente.criado_em.desc()).all()
    )
    return render_template("incidentes/listar.html", incidentes=incidentes)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        titulo = txt(request.form.get("titulo"), 200)
        if not titulo:
            flash("Informe um título para o incidente.", "erro")
        else:
            risco = request.form.get("risco") or ""
            inc = models.Incidente(
                empresa_id=current_user.empresa_id, titulo=titulo,
                ocorrido_em=_data(request.form.get("ocorrido_em")),
                descricao=request.form.get("descricao") or "",
                dados_afetados=request.form.get("dados_afetados") or "",
                num_titulares=_inteiro(request.form.get("num_titulares")),
                risco=risco if risco in models.RISCO_LABELS else None,
                status="aberto",
            )
            db.session.add(inc)
            registrar("incidente_registrado", titulo)
            db.session.commit()
            notificar_novo_incidente(inc, current_user.empresa)
            flash("Incidente registrado.", "ok")
            return redirect(url_for("incidentes.gerir", iid=inc.id))
    return render_template("incidentes/novo.html", niveis=models.RISCO_NIVEIS)


@bp.route("/<int:iid>", methods=["GET", "POST"])
def gerir(iid):
    inc = _do_empresa(iid)
    if request.method == "POST":
        status = request.form.get("status") or inc.status
        if status in models.STATUS_INCIDENTE_LABELS:
            inc.status = status
        risco = request.form.get("risco") or ""
        inc.risco = risco if risco in models.RISCO_LABELS else None
        inc.comunicado_anpd = request.form.get("comunicado_anpd") == "on"
        inc.comunicado_anpd_em = _data(request.form.get("comunicado_anpd_em")) if inc.comunicado_anpd else None
        inc.comunicado_titulares = request.form.get("comunicado_titulares") == "on"
        inc.comunicado_titulares_em = (
            _data(request.form.get("comunicado_titulares_em")) if inc.comunicado_titulares else None
        )
        inc.medidas = request.form.get("medidas") or ""
        registrar("incidente_atualizado", f"{inc.id} -> {inc.status}")
        db.session.commit()
        flash("Incidente atualizado.", "ok")
        return redirect(url_for("incidentes.gerir", iid=inc.id))
    from services.anexos import listar as listar_anexos
    return render_template("incidentes/gerir.html", inc=inc,
                           status_opcoes=models.STATUS_INCIDENTE, niveis=models.RISCO_NIVEIS,
                           anexos=listar_anexos("incidente", inc.id, current_user.empresa_id))
