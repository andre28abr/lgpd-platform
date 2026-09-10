"""Pedidos do titular (Art. 18): registro e acompanhamento."""
from datetime import timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import fk_do_tenant, gestor_somente_leitura, papeis
from services.auditoria import registrar
from services.notificacoes import notificar_novo_pedido, notificar_pedido_concluido
from utils import agora_utc

bp = Blueprint("direitos", __name__, url_prefix="/direitos")
_somente_leitura = gestor_somente_leitura("direitos.novo")

PRAZO_DIAS = 15


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    _somente_leitura()


def _do_empresa(pid):
    pedido = db.session.get(models.PedidoTitular, pid)
    if not pedido or pedido.empresa_id != current_user.empresa_id:
        abort(404)
    return pedido


@bp.route("/")
def listar():
    pedidos = (
        models.PedidoTitular.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.PedidoTitular.criado_em.desc()).all()
    )
    return render_template("direitos/listar.html", pedidos=pedidos)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = (request.form.get("nome_titular") or "").strip()
        tipo = request.form.get("tipo") or ""
        if not nome or tipo not in models.TIPO_DIREITO_LABELS:
            flash("Informe o nome do titular e um tipo de pedido válido.", "erro")
        else:
            pedido = models.PedidoTitular(
                empresa_id=current_user.empresa_id, nome_titular=nome,
                contato=(request.form.get("contato") or "").strip(),
                tipo=tipo, descricao=request.form.get("descricao") or "",
                status="recebido", prazo=agora_utc() + timedelta(days=PRAZO_DIAS),
                protocolo=models.PedidoTitular.gerar_protocolo(), origem="interno",
            )
            db.session.add(pedido)
            registrar("pedido_titular_registrado", f"{tipo} - {nome}")
            db.session.commit()
            notificar_novo_pedido(pedido, current_user.empresa)
            flash("Pedido registrado.", "ok")
            return redirect(url_for("direitos.gerir", pid=pedido.id))
    return render_template("direitos/novo.html", tipos=models.TIPOS_DIREITO)


@bp.route("/<int:pid>", methods=["GET", "POST"])
def gerir(pid):
    pedido = _do_empresa(pid)
    if request.method == "POST":
        status = request.form.get("status") or pedido.status
        if status in models.STATUS_PEDIDO_LABELS:
            pedido.status = status
            pedido.concluido_em = agora_utc() if status in ("concluido", "recusado") else None
        pedido.responsavel_id = fk_do_tenant(
            models.Usuario, request.form.get("responsavel_id"), current_user.empresa_id,
        )
        pedido.observacoes = request.form.get("observacoes") or ""
        registrar("pedido_titular_atualizado", f"{pedido.id} -> {pedido.status}")
        db.session.commit()
        if pedido.status == "concluido":
            notificar_pedido_concluido(pedido)
        flash("Pedido atualizado.", "ok")
        return redirect(url_for("direitos.gerir", pid=pedido.id))

    usuarios = (
        models.Usuario.query.filter_by(empresa_id=current_user.empresa_id, ativo=True)
        .order_by(models.Usuario.nome).all()
    )
    return render_template("direitos/gerir.html", pedido=pedido,
                           status_opcoes=models.STATUS_PEDIDO, usuarios=usuarios)
