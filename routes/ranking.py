"""Ranking de conformidade entre os setores + exportações (Excel/PDF)."""
from flask import Blueprint, render_template, send_file
from flask_login import current_user, login_required

import models
from routes._helpers import papeis
from services.metricas import ranking_empresa
from services.relatorios import conformidade_pdf, ranking_excel

bp = Blueprint("ranking", __name__, url_prefix="/ranking")


@bp.route("/")
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def index():
    linhas = ranking_empresa(current_user.empresa_id)
    return render_template("ranking/index.html", linhas=linhas, setor_atual=current_user.setor_id)


@bp.route("/exportar.xlsx")
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def exportar_xlsx():
    buf = ranking_excel(current_user.empresa)
    return send_file(
        buf, as_attachment=True, download_name="ranking-lgpd.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/relatorio.pdf")
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def relatorio_pdf():
    buf = conformidade_pdf(current_user.empresa)
    return send_file(buf, mimetype="application/pdf", as_attachment=False,
                     download_name="relatorio-conformidade.pdf")
