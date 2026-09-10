"""Anexos (evidências): o Encarregado envia e exclui; o Gestor pode baixar."""
from flask import Blueprint, abort, flash, redirect, request, send_file, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import papeis
from services import anexos as svc
from services.auditoria import registrar

bp = Blueprint("anexos", __name__, url_prefix="/anexos")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    if request.method != "GET" and not current_user.is_encarregado:
        abort(403)


def _volta_para(tipo, alvo_id):
    destinos = {
        "ripd": ("ripd.form", "rid"),
        "incidente": ("incidentes.gerir", "iid"),
        "pedido": ("direitos.gerir", "pid"),
    }
    endpoint, parametro = destinos[tipo]
    return redirect(url_for(endpoint, **{parametro: alvo_id}))


@bp.route("/<tipo>/<int:alvo_id>", methods=["POST"])
def enviar(tipo, alvo_id):
    alvo = svc.alvo_do_tenant(tipo, alvo_id, current_user.empresa_id)
    if not alvo:
        abort(404)
    arquivo = request.files.get("arquivo")
    if not arquivo:
        flash("Selecione um arquivo.", "erro")
        return _volta_para(tipo, alvo_id)
    try:
        anexo = svc.salvar(arquivo, current_user.empresa_id, tipo, alvo_id, current_user)
    except ValueError as erro:
        flash(str(erro), "erro")
        return _volta_para(tipo, alvo_id)
    registrar("anexo_enviado", f"{tipo}#{alvo_id} {anexo.nome_original}")
    db.session.commit()
    flash("Anexo adicionado.", "ok")
    return _volta_para(tipo, alvo_id)


def _anexo_do_tenant(anexo_id):
    anexo = db.session.get(models.Anexo, anexo_id)
    if not anexo or anexo.empresa_id != current_user.empresa_id:
        abort(404)
    return anexo


@bp.route("/<int:anexo_id>")
def baixar(anexo_id):
    anexo = _anexo_do_tenant(anexo_id)
    return send_file(svc.caminho(anexo), as_attachment=True, download_name=anexo.nome_original,
                     mimetype=anexo.mime or "application/octet-stream")


@bp.route("/<int:anexo_id>/excluir", methods=["POST"])
def excluir(anexo_id):
    anexo = _anexo_do_tenant(anexo_id)
    tipo, alvo_id = anexo.alvo_tipo, anexo.alvo_id
    registrar("anexo_excluido", f"{tipo}#{alvo_id} {anexo.nome_original}")
    svc.excluir(anexo)
    db.session.commit()
    flash("Anexo excluído.", "ok")
    return _volta_para(tipo, alvo_id)
