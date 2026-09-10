"""Páginas públicas (sem login): política, healthcheck e o portal do titular."""
from datetime import timedelta

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import text

import models
from extensions import db, limiter
from services.auditoria import registrar
from services.notificacoes import notificar_novo_pedido
from utils import agora_utc

bp = Blueprint("publico", __name__)

PRAZO_DIAS = 15  # prazo interno de atendimento adotado pela plataforma


@bp.route("/politica-de-privacidade")
def politica():
    return render_template("publico/politica.html")


@bp.route("/saude")
def saude():
    """Healthcheck para Docker/orquestrador: 200 só se a app E o banco respondem."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — qualquer falha de banco é "indisponível"
        return jsonify(status="erro", banco="indisponivel"), 503
    return jsonify(status="ok")


# ── Portal do titular (Art. 18) ─────────────────────────────────────────────
def _empresa_ou_404(slug):
    empresa = models.Empresa.query.filter_by(slug=slug, ativo=True).first()
    if not empresa:
        abort(404)
    return empresa


@bp.route("/titular/<slug>", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def titular(slug):
    """O titular abre o pedido sozinho e recebe um protocolo. Na vida real, a empresa
    publica este link no site/aviso de privacidade; na demo, ele fica na tela de login."""
    empresa = _empresa_ou_404(slug)
    if request.method == "POST":
        nome = (request.form.get("nome_titular") or "").strip()
        contato = (request.form.get("contato") or "").strip()
        tipo = request.form.get("tipo") or ""
        descricao = (request.form.get("descricao") or "").strip()
        if not nome or not contato or tipo not in models.TIPO_DIREITO_LABELS:
            flash("Informe seu nome, um contato e o tipo de pedido.", "erro")
        else:
            pedido = models.PedidoTitular(
                empresa_id=empresa.id, nome_titular=nome, contato=contato, tipo=tipo,
                descricao=descricao, status="recebido", prazo=agora_utc() + timedelta(days=PRAZO_DIAS),
                protocolo=models.PedidoTitular.gerar_protocolo(), origem="portal",
            )
            db.session.add(pedido)
            registrar("pedido_titular_portal", f"{tipo} - {pedido.protocolo}", empresa_id=empresa.id)
            db.session.commit()
            notificar_novo_pedido(pedido, empresa)
            return redirect(url_for("publico.titular_protocolo", slug=slug, protocolo=pedido.protocolo))
    return render_template("publico/titular.html", empresa=empresa, tipos=models.TIPOS_DIREITO)


@bp.route("/titular/<slug>/consultar", methods=["POST"])
@limiter.limit("20 per hour")
def titular_consultar(slug):
    _empresa_ou_404(slug)
    codigo = (request.form.get("protocolo") or "").strip().upper()
    return redirect(url_for("publico.titular_protocolo", slug=slug, protocolo=codigo or "-"))


@bp.route("/titular/<slug>/protocolo/<protocolo>")
def titular_protocolo(slug, protocolo):
    """Andamento do pedido pelo protocolo. Mostra o mínimo: tipo, status e prazos —
    nunca os dados do titular (quem tem o código pode não ser o titular)."""
    empresa = _empresa_ou_404(slug)
    pedido = models.PedidoTitular.query.filter_by(empresa_id=empresa.id, protocolo=protocolo.upper()).first()
    return render_template("publico/titular_protocolo.html", empresa=empresa, pedido=pedido,
                           protocolo=protocolo.upper())
