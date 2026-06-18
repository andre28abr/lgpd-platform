"""Painel inicial, adaptado ao papel do usuário."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from services.metricas import (
    certificado_vigente,
    resumo_empresa,
    resumo_setor,
    ultima_prova,
)

bp = Blueprint("painel", __name__)


@bp.route("/")
@login_required
def index():
    usuario = current_user

    if usuario.is_encarregado:
        return render_template("painel/encarregado.html", dados=resumo_empresa(usuario.empresa_id))

    if usuario.is_gestor:
        resumo = resumo_setor(usuario.setor) if usuario.setor else None
        return render_template("painel/gestor.html", setor=usuario.setor, resumo=resumo)

    area = usuario.setor.area if usuario.setor else None
    return render_template(
        "painel/colaborador.html",
        cert=certificado_vigente(usuario.id, area),
        ultima=ultima_prova(usuario.id),
    )
