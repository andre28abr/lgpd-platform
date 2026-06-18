"""Avaliações: sorteio de questões, aplicação, correção e emissão de certificado."""
import random
import secrets
from datetime import datetime

from flask import (
    Blueprint, abort, current_app, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

import models
from extensions import db
from utils import agora_utc

bp = Blueprint("provas", __name__, url_prefix="/provas")


def _sortear_questoes(empresa_id, area, quantidade):
    base = models.Questao.query.filter(
        models.Questao.area == area,
        models.Questao.ativo.is_(True),
        or_(models.Questao.empresa_id.is_(None), models.Questao.empresa_id == empresa_id),
    ).all()
    random.shuffle(base)
    return base[:quantidade]


@bp.route("/")
@login_required
def index():
    historico = (
        models.Prova.query.filter_by(usuario_id=current_user.id)
        .order_by(models.Prova.criado_em.desc())
        .all()
    )
    area_padrao = current_user.setor.area if current_user.setor else None
    return render_template(
        "provas/index.html",
        historico=historico,
        area_padrao=area_padrao,
        areas=models.AREAS,
    )


@bp.route("/iniciar", methods=["POST"])
@login_required
def iniciar():
    area = request.form.get("area") or (current_user.setor.area if current_user.setor else None)
    if not area or area not in models.AREA_CODES:
        flash("Selecione uma área válida para a avaliação.", "erro")
        return redirect(url_for("provas.index"))

    quantidade = current_app.config["QUESTOES_POR_PROVA"]
    questoes = _sortear_questoes(current_user.empresa_id, area, quantidade)
    if not questoes:
        flash("Ainda não há questões cadastradas para esta área.", "aviso")
        return redirect(url_for("provas.index"))

    prova = models.Prova(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        setor_id=current_user.setor_id,
        area=area,
        nota_corte=current_app.config["NOTA_CORTE"],
        tempo_limite_min=current_app.config["TEMPO_PROVA_MIN"] or None,
        status="em_andamento",
    )
    db.session.add(prova)
    db.session.flush()  # garante prova.id

    for ordem, questao in enumerate(questoes):
        ids_alt = [a.id for a in questao.alternativas]
        random.shuffle(ids_alt)
        db.session.add(models.ProvaItem(
            prova_id=prova.id,
            questao_id=questao.id,
            ordem=ordem,
            ordem_alternativas=",".join(str(i) for i in ids_alt),
        ))
    db.session.commit()
    return redirect(url_for("provas.realizar", prova_id=prova.id))


def _prova_do_usuario(prova_id):
    prova = db.session.get(models.Prova, prova_id)
    if not prova or prova.usuario_id != current_user.id:
        abort(404)
    return prova


@bp.route("/<int:prova_id>")
@login_required
def realizar(prova_id):
    prova = _prova_do_usuario(prova_id)
    if prova.status == "concluida":
        return redirect(url_for("provas.resultado", prova_id=prova.id))
    restante = None
    if prova.expira_em:
        restante = max(0, int((prova.expira_em - agora_utc()).total_seconds()))
    return render_template("provas/realizar.html", prova=prova, restante=restante)


@bp.route("/<int:prova_id>/responder", methods=["POST"])
@login_required
def responder(prova_id):
    prova = _prova_do_usuario(prova_id)
    if prova.status == "concluida":
        return redirect(url_for("provas.resultado", prova_id=prova.id))

    for item in prova.itens:
        escolha = request.form.get(f"questao_{item.id}")
        if escolha and escolha.isdigit():
            aid = int(escolha)
            alt = next((a for a in item.questao.alternativas if a.id == aid), None)
            item.alternativa_escolhida_id = aid if alt else None
            item.correta = bool(alt and alt.correta)
        else:
            item.alternativa_escolhida_id = None
            item.correta = False

    total = len(prova.itens)
    acertos = sum(1 for i in prova.itens if i.correta)
    prova.nota = round(acertos / total * 100, 1) if total else 0.0
    prova.aprovado = prova.nota >= prova.nota_corte
    prova.status = "concluida"
    prova.finalizado_em = agora_utc()

    if prova.aprovado and not prova.certificado:
        dias = current_app.config["CERT_VALIDADE_DIAS"]
        db.session.add(models.Certificado(
            empresa_id=prova.empresa_id,
            usuario_id=prova.usuario_id,
            prova_id=prova.id,
            setor_id=prova.setor_id,
            area=prova.area,
            codigo=secrets.token_hex(8),
            nota=prova.nota,
            valido_ate=models.Certificado.validade_padrao(dias),
        ))

    db.session.commit()
    return redirect(url_for("provas.resultado", prova_id=prova.id))


@bp.route("/<int:prova_id>/resultado")
@login_required
def resultado(prova_id):
    prova = _prova_do_usuario(prova_id)
    if prova.status != "concluida":
        return redirect(url_for("provas.realizar", prova_id=prova.id))
    return render_template("provas/resultado.html", prova=prova)
