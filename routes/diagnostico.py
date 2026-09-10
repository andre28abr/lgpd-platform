"""Diagnóstico de maturidade em privacidade (nível empresa)."""

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

import models
from extensions import db
from routes._helpers import papeis
from services.auditoria import registrar
from services.diagnostico import computar
from services.diagnostico_pdf import diagnostico_pdf
from utils import agora_utc

bp = Blueprint("diagnostico", __name__, url_prefix="/diagnostico")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO, models.PAPEL_GESTOR)
def _restringe():
    pass


def _perguntas():
    return models.DiagnosticoPergunta.query.filter_by(ativo=True).order_by(
        models.DiagnosticoPergunta.dimensao, models.DiagnosticoPergunta.ordem).all()


def _do_empresa(diag_id):
    diag = db.session.get(models.Diagnostico, diag_id)
    if not diag or diag.empresa_id != current_user.empresa_id:
        abort(404)
    return diag


@bp.route("/")
def index():
    historico = models.Diagnostico.query.filter_by(empresa_id=current_user.empresa_id).order_by(
        models.Diagnostico.criado_em.desc()).all()
    setores = models.Setor.query.filter_by(empresa_id=current_user.empresa_id).order_by(models.Setor.nome).all()
    return render_template("diagnostico/index.html", historico=historico, setores=setores,
                           grafico=_grafico_evolucao(historico))


@bp.route("/iniciar", methods=["POST"])
def iniciar():
    if not _perguntas():
        flash("Nenhuma pergunta de diagnóstico cadastrada.", "aviso")
        return redirect(url_for("diagnostico.index"))

    setor_id = request.form.get("setor_id") or None
    if setor_id and not models.Setor.query.filter_by(
            id=int(setor_id), empresa_id=current_user.empresa_id).first():
        setor_id = None

    diag = models.Diagnostico(
        empresa_id=current_user.empresa_id, usuario_id=current_user.id,
        setor_id=int(setor_id) if setor_id else None,
    )
    db.session.add(diag)
    db.session.commit()
    return redirect(url_for("diagnostico.responder", diag_id=diag.id))


def _grafico_evolucao(historico):
    """Pontos de um sparkline (SVG) com a evolução do score dos diagnósticos concluídos."""
    concluidos = sorted(
        [d for d in historico if d.status == "concluido" and d.score is not None],
        key=lambda d: d.finalizado_em,
    )
    if len(concluidos) < 2:
        return None
    largura, altura, pad = 600, 120, 12
    n = len(concluidos)
    pontos = []
    for i, d in enumerate(concluidos):
        x = pad + (largura - 2 * pad) * (i / (n - 1))
        y = altura - pad - (altura - 2 * pad) * (d.score / 100)
        pontos.append({"x": round(x, 1), "y": round(y, 1), "score": d.score,
                       "data": d.finalizado_em.strftime("%d/%m/%y")})
    return {
        "w": largura, "h": altura, "pontos": pontos,
        "linha": " ".join(f"{p['x']},{p['y']}" for p in pontos),
    }


@bp.route("/<int:diag_id>")
def responder(diag_id):
    diag = _do_empresa(diag_id)
    if diag.status == "concluido":
        return redirect(url_for("diagnostico.resultado", diag_id=diag.id))
    grupos = {}
    for p in _perguntas():
        grupos.setdefault(p.dimensao, []).append(p)
    return render_template("diagnostico/responder.html", diag=diag, grupos=grupos)


@bp.route("/<int:diag_id>/responder", methods=["POST"])
def salvar(diag_id):
    diag = _do_empresa(diag_id)
    if diag.status == "concluido":
        return redirect(url_for("diagnostico.resultado", diag_id=diag.id))

    for r in list(diag.respostas):
        db.session.delete(r)
    db.session.flush()
    for p in _perguntas():
        bruto = request.form.get(f"p_{p.id}")
        valor = int(bruto) if bruto in ("0", "1", "2") else 0
        diag.respostas.append(models.DiagnosticoResposta(pergunta_id=p.id, valor=valor))

    score, nivel, _linhas, _plano = computar(diag)
    diag.score, diag.nivel = score, nivel
    diag.status, diag.finalizado_em = "concluido", agora_utc()
    registrar("diagnostico_concluido", f"score={score} nivel={nivel}")
    db.session.commit()
    return redirect(url_for("diagnostico.resultado", diag_id=diag.id))


@bp.route("/<int:diag_id>/resultado")
def resultado(diag_id):
    diag = _do_empresa(diag_id)
    if diag.status != "concluido":
        return redirect(url_for("diagnostico.responder", diag_id=diag.id))
    score, nivel, linhas, plano = computar(diag)
    delta = _delta_anterior(diag, score)
    return render_template("diagnostico/resultado.html", diag=diag, score=score, nivel=nivel,
                           linhas=linhas, plano=plano, delta=delta)


@bp.route("/<int:diag_id>/pdf")
def pdf(diag_id):
    diag = _do_empresa(diag_id)
    if diag.status != "concluido":
        abort(404)
    score, nivel, linhas, plano = computar(diag)
    buf = diagnostico_pdf(current_user.empresa, diag, score, nivel, linhas, plano)
    return send_file(buf, mimetype="application/pdf", as_attachment=False,
                     download_name=f"diagnostico-maturidade-{diag.id}.pdf")


def _delta_anterior(diag, score):
    """Variação do score em relação ao diagnóstico concluído anterior."""
    anterior = (
        models.Diagnostico.query.filter(
            models.Diagnostico.empresa_id == current_user.empresa_id,
            models.Diagnostico.status == "concluido",
            models.Diagnostico.id != diag.id,
            models.Diagnostico.finalizado_em < diag.finalizado_em,
        ).order_by(models.Diagnostico.finalizado_em.desc()).first()
    )
    if anterior and anterior.score is not None:
        return round(score - anterior.score, 1)
    return None
