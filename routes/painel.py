"""Painel inicial, adaptado ao papel do usuário."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from services.kpis import kpis_empresa
from services.metricas import (
    certificado_vigente,
    resumo_empresa,
    resumo_setor,
    ultima_prova,
)
from services.prazos import PRAZO_ANPD_DIAS_UTEIS, alertas_empresa

bp = Blueprint("painel", __name__)


@bp.route("/")
@login_required
def index():
    usuario = current_user

    if usuario.is_encarregado:
        return render_template(
            "painel/encarregado.html",
            dados=resumo_empresa(usuario.empresa_id),
            alertas=alertas_empresa(usuario.empresa_id),
            kpis=kpis_empresa(usuario.empresa_id),
            prazo_anpd=PRAZO_ANPD_DIAS_UTEIS,
        )

    if usuario.is_gestor:
        resumo = resumo_setor(usuario.setor) if usuario.setor else None
        return render_template("painel/gestor.html", setor=usuario.setor, resumo=resumo)

    from routes.trilhas import progresso_trilhas
    area = usuario.setor.area if usuario.setor else None
    lidas, total = progresso_trilhas()
    return render_template(
        "painel/colaborador.html",
        cert=certificado_vigente(usuario.id, area),
        ultima=ultima_prova(usuario.id),
        trilhas_lidas=lidas, trilhas_total=total,
    )
