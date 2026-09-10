"""Avaliações: sorteio de questões, aplicação, correção e emissão de certificado."""
import random
import secrets
from datetime import timedelta

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

import models
from extensions import db
from utils import agora_utc

bp = Blueprint("provas", __name__, url_prefix="/provas")

# Folga (segundos) além do tempo limite para o envio automático do navegador chegar.
TOLERANCIA_ENVIO_S = 30


def _pool(empresa_id, area):
    """Questões ativas da área: biblioteca global + as próprias da empresa."""
    return models.Questao.query.filter(
        models.Questao.area == area,
        models.Questao.ativo.is_(True),
        or_(models.Questao.empresa_id.is_(None), models.Questao.empresa_id == empresa_id),
    ).all()


def _balancear(questoes, quantidade):
    """Sorteia ``quantidade`` questões alternando entre os níveis de dificuldade (1, 2, 3),
    para a prova não sair só de fáceis nem só de difíceis."""
    por_nivel = {}
    for q in questoes:
        por_nivel.setdefault(q.dificuldade, []).append(q)
    for grupo in por_nivel.values():
        random.shuffle(grupo)
    escolhidas = []
    while len(escolhidas) < quantidade and any(por_nivel.values()):
        for nivel in sorted(por_nivel):
            if por_nivel[nivel] and len(escolhidas) < quantidade:
                escolhidas.append(por_nivel[nivel].pop())
    random.shuffle(escolhidas)
    return escolhidas


def _sortear_questoes(empresa_id, area, n_area, n_geral):
    """7 da área do setor + 3 gerais (config). Para a área GERAL, tudo vem do pool geral.
    Devolve (questoes, mensagem_de_erro): pool abaixo do mínimo recusa a prova."""
    cfg = current_app.config
    fator = cfg["POOL_MINIMO_FATOR"]
    if area == "GERAL":
        pool = _pool(empresa_id, "GERAL")
        total = n_area + n_geral
        if len(pool) < fator * total:
            return [], f"Banco insuficiente para a área Geral: {len(pool)} questões, mínimo {fator * total}."
        return _balancear(pool, total), None

    pool_area, pool_geral = _pool(empresa_id, area), _pool(empresa_id, "GERAL")
    if len(pool_area) < fator * n_area:
        return [], (f"Banco insuficiente para a área {models.label_area(area)}: {len(pool_area)} questões, "
                    f"mínimo {fator * n_area}. Cadastre mais questões em Administração.")
    if len(pool_geral) < fator * n_geral:
        return [], f"Banco insuficiente para a área Geral: {len(pool_geral)} questões, mínimo {fator * n_geral}."
    escolhidas = _balancear(pool_area, n_area) + _balancear(pool_geral, n_geral)
    random.shuffle(escolhidas)
    return escolhidas, None


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

    cfg = current_app.config
    hoje = agora_utc().replace(hour=0, minute=0, second=0, microsecond=0)
    feitas_hoje = models.Prova.query.filter(
        models.Prova.usuario_id == current_user.id, models.Prova.criado_em >= hoje,
    ).count()
    if feitas_hoje >= cfg["PROVAS_POR_DIA"]:
        flash(f"Limite de {cfg['PROVAS_POR_DIA']} avaliações por dia atingido. "
              "Estude a trilha e volte amanhã.", "aviso")
        return redirect(url_for("provas.index"))

    questoes, erro = _sortear_questoes(
        current_user.empresa_id, area, cfg["QUESTOES_POR_PROVA"], cfg["QUESTOES_GERAIS_POR_PROVA"],
    )
    if erro:
        flash(erro, "aviso")
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

    # Cronômetro validado no servidor: o countdown do navegador é só apoio visual.
    # Envio após o prazo (mais a tolerância) encerra a prova sem corrigir as respostas.
    if prova.expira_em and agora_utc() > prova.expira_em + timedelta(seconds=TOLERANCIA_ENVIO_S):
        for item in prova.itens:
            item.alternativa_escolhida_id = None
            item.correta = False
        prova.nota, prova.aprovado = 0.0, False
        prova.status, prova.finalizado_em = "concluida", agora_utc()
        db.session.commit()
        flash("Tempo esgotado. A prova foi encerrada e as respostas enviadas após o prazo "
              "não foram consideradas.", "erro")
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
