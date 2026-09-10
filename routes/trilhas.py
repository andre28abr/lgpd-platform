"""Trilhas de treinamento (conteúdo curado em Markdown) e progresso de leitura."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

import models
from extensions import db

bp = Blueprint("trilhas", __name__, url_prefix="/trilhas")


def _areas_do_usuario():
    """Áreas visíveis: a do setor + GERAL; encarregado vê todas."""
    if current_user.is_encarregado:
        return models.AREA_CODES
    if current_user.setor:
        return [current_user.setor.area, "GERAL"]
    return ["GERAL"]


def _query_visivel():
    areas = _areas_do_usuario()
    return models.Trilha.query.filter(
        models.Trilha.publicada.is_(True),
        models.Trilha.area.in_(areas),
        or_(models.Trilha.empresa_id.is_(None), models.Trilha.empresa_id == current_user.empresa_id),
    )


def _lidas_ids():
    return {le.trilha_id for le in models.TrilhaLeitura.query.filter_by(usuario_id=current_user.id).all()}


def progresso_trilhas():
    """(lidas, total) das trilhas visíveis ao usuário atual — alimenta o painel."""
    ids = {t.id for t in _query_visivel().all()}
    return len(_lidas_ids() & ids), len(ids)


@bp.route("/")
@login_required
def listar():
    trilhas = _query_visivel().order_by(models.Trilha.area, models.Trilha.ordem).all()
    grupos = {}
    for t in trilhas:
        grupos.setdefault(t.area, []).append(t)
    return render_template("trilhas/listar.html", grupos=grupos, lidas=_lidas_ids())


@bp.route("/<slug>")
@login_required
def ver(slug):
    trilha = _query_visivel().filter(models.Trilha.slug == slug).first()
    if not trilha:
        abort(404)
    leitura = models.TrilhaLeitura.query.filter_by(usuario_id=current_user.id, trilha_id=trilha.id).first()
    return render_template("trilhas/ver.html", trilha=trilha, leitura=leitura)


@bp.route("/<slug>/lida", methods=["POST"])
@login_required
def marcar_lida(slug):
    trilha = _query_visivel().filter(models.Trilha.slug == slug).first()
    if not trilha:
        abort(404)
    if not models.TrilhaLeitura.query.filter_by(usuario_id=current_user.id, trilha_id=trilha.id).first():
        db.session.add(models.TrilhaLeitura(usuario_id=current_user.id, trilha_id=trilha.id))
        try:
            db.session.commit()
        except IntegrityError:  # dois cliques simultâneos: o segundo perde para o UNIQUE, sem 500
            db.session.rollback()
    flash("Trilha marcada como lida.", "ok")
    return redirect(url_for("trilhas.ver", slug=slug))
