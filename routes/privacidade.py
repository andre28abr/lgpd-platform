"""Hub de Gestão de Privacidade — agrega os módulos da fase 2."""
from flask import Blueprint, render_template
from flask_login import login_required

import models
from routes._helpers import papeis

bp = Blueprint("privacidade", __name__, url_prefix="/privacidade")


@bp.route("/")
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def index():
    eid = None
    from flask_login import current_user
    eid = current_user.empresa_id
    contagens = {
        "ropa": models.RopaRegistro.query.filter_by(empresa_id=eid).count(),
        "ripd": models.Ripd.query.filter_by(empresa_id=eid).count(),
        "direitos": models.PedidoTitular.query.filter_by(empresa_id=eid).count(),
        "incidentes": models.Incidente.query.filter_by(empresa_id=eid).count(),
        "diagnosticos": models.Diagnostico.query.filter_by(empresa_id=eid).count(),
    }
    return render_template("privacidade/index.html", c=contagens)
