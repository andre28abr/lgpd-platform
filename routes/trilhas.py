"""Trilhas de treinamento (conteúdo curado em Markdown)."""
from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required
from sqlalchemy import or_

import models

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


@bp.route("/")
@login_required
def listar():
    trilhas = _query_visivel().order_by(models.Trilha.area, models.Trilha.ordem).all()
    # Agrupa por área para exibição.
    grupos = {}
    for t in trilhas:
        grupos.setdefault(t.area, []).append(t)
    return render_template("trilhas/listar.html", grupos=grupos)


@bp.route("/<slug>")
@login_required
def ver(slug):
    trilha = _query_visivel().filter(models.Trilha.slug == slug).first()
    if not trilha:
        abort(404)
    return render_template("trilhas/ver.html", trilha=trilha)
