"""Administração do tenant (somente Encarregado): setores, usuários, trilhas e questões."""
from flask import (
    Blueprint,
    Response,
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
from routes._helpers import fk_do_tenant, papeis, slugify
from security import validar_senha
from services.auditoria import registrar
from services.metricas import pendencias_empresa
from services.notificacoes import notificar_reavaliacoes

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@login_required
@papeis(models.PAPEL_ENCARREGADO)
def _somente_encarregado():
    pass


@bp.route("/")
def index():
    empresa = current_user.empresa
    return render_template(
        "admin/index.html",
        empresa=empresa,
        n_setores=models.Setor.query.filter_by(empresa_id=empresa.id).count(),
        n_usuarios=models.Usuario.query.filter_by(empresa_id=empresa.id).count(),
        n_trilhas=models.Trilha.query.filter_by(empresa_id=empresa.id).count(),
        n_questoes=models.Questao.query.filter_by(empresa_id=empresa.id).count(),
    )


# ─────────────────────────────── Setores ───────────────────────────────────
@bp.route("/setores", methods=["GET", "POST"])
def setores():
    empresa_id = current_user.empresa_id
    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        area = request.form.get("area") or "GERAL"
        descricao = (request.form.get("descricao") or "").strip()
        if not nome or area not in models.AREA_CODES:
            flash("Informe um nome e uma área válida.", "erro")
        else:
            slug = _slug_unico(models.Setor, empresa_id, slugify(nome))
            db.session.add(models.Setor(
                empresa_id=empresa_id, nome=nome, slug=slug, area=area, descricao=descricao,
            ))
            registrar("setor_criado", nome)
            db.session.commit()
            flash(f"Setor '{nome}' criado.", "ok")
        return redirect(url_for("admin.setores"))

    lista = models.Setor.query.filter_by(empresa_id=empresa_id).order_by(models.Setor.nome).all()
    return render_template("admin/setores.html", setores=lista, areas=models.AREAS)


# ─────────────────────────────── Usuários ──────────────────────────────────
@bp.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    empresa_id = current_user.empresa_id
    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        papel = request.form.get("papel") or models.PAPEL_COLABORADOR
        setor_id = fk_do_tenant(models.Setor, request.form.get("setor_id"), empresa_id)
        erro_senha = validar_senha(senha)

        if not nome or not email or papel not in models.PAPEIS:
            flash("Preencha os campos obrigatórios.", "erro")
        elif erro_senha:
            flash(erro_senha, "erro")
        elif models.Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "erro")
        else:
            novo = models.Usuario(
                empresa_id=empresa_id, nome=nome, email=email, papel=papel, setor_id=setor_id,
            )
            novo.definir_senha(senha)
            db.session.add(novo)
            registrar("usuario_criado", email)
            db.session.commit()
            flash(f"Usuário '{nome}' criado.", "ok")
        return redirect(url_for("admin.usuarios"))

    lista = models.Usuario.query.filter_by(empresa_id=empresa_id).order_by(models.Usuario.nome).all()
    setores = models.Setor.query.filter_by(empresa_id=empresa_id).order_by(models.Setor.nome).all()
    return render_template(
        "admin/usuarios.html", usuarios=lista, setores=setores, papeis=models.PAPEL_LABELS,
    )


@bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
def usuario_editar(usuario_id):
    usuario = _do_tenant(models.Usuario, usuario_id)
    setores = models.Setor.query.filter_by(empresa_id=current_user.empresa_id).order_by(models.Setor.nome).all()

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "senha":
            nova = request.form.get("senha") or ""
            erro = validar_senha(nova)
            if erro:
                flash(erro, "erro")
            else:
                usuario.definir_senha(nova)
                registrar("senha_redefinida", usuario.email)
                db.session.commit()
                flash("Senha redefinida.", "ok")
        elif acao == "reset2fa":
            usuario.mfa_ativo = False
            usuario.totp_secret = None
            models.RecoveryCode.query.filter_by(usuario_id=usuario.id).delete()
            registrar("2fa_resetado", usuario.email)
            db.session.commit()
            flash("Verificação em duas etapas do usuário foi resetada.", "ok")
        else:
            papel = request.form.get("papel") or usuario.papel
            ativo = request.form.get("ativo") == "on"
            novo_papel = papel if papel in models.PAPEIS else usuario.papel
            perde_encarregado = usuario.is_encarregado and (novo_papel != models.PAPEL_ENCARREGADO or not ativo)
            if perde_encarregado and _ultimo_encarregado_ativo(usuario):
                flash("Este é o único Encarregado ativo da empresa. Promova outro usuário a Encarregado "
                      "antes de rebaixá-lo ou inativá-lo.", "erro")
                return redirect(url_for("admin.usuario_editar", usuario_id=usuario.id))
            if papel in models.PAPEIS:
                usuario.papel = papel
            usuario.setor_id = fk_do_tenant(
                models.Setor, request.form.get("setor_id"), current_user.empresa_id,
            )
            usuario.ativo = ativo
            registrar("usuario_editado", usuario.email)
            db.session.commit()
            flash("Usuário atualizado.", "ok")
        return redirect(url_for("admin.usuario_editar", usuario_id=usuario.id))

    return render_template(
        "admin/usuario_editar.html", usuario=usuario, setores=setores, papeis=models.PAPEL_LABELS,
    )


# ─────────────────────────────── Trilhas ───────────────────────────────────
@bp.route("/trilhas")
def trilhas():
    proprias = models.Trilha.query.filter_by(empresa_id=current_user.empresa_id).order_by(
        models.Trilha.area, models.Trilha.titulo).all()
    globais = models.Trilha.query.filter_by(empresa_id=None).order_by(
        models.Trilha.area, models.Trilha.titulo).all()
    return render_template("admin/trilhas.html", proprias=proprias, globais=globais)


@bp.route("/trilhas/nova", methods=["GET", "POST"])
@bp.route("/trilhas/<int:trilha_id>/editar", methods=["GET", "POST"])
def trilha_form(trilha_id=None):
    trilha = _do_tenant(models.Trilha, trilha_id) if trilha_id else None

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        area = request.form.get("area") or "GERAL"
        resumo = (request.form.get("resumo") or "").strip()
        conteudo = request.form.get("conteudo_md") or ""
        publicada = request.form.get("publicada") == "on"

        if not titulo or area not in models.AREA_CODES:
            flash("Informe título e uma área válida.", "erro")
        else:
            if trilha is None:
                trilha = models.Trilha(empresa_id=current_user.empresa_id, area=area,
                                       slug=_slug_unico_trilha(current_user.empresa_id, slugify(titulo)))
                db.session.add(trilha)
            trilha.titulo, trilha.area, trilha.resumo = titulo, area, resumo
            trilha.conteudo_md, trilha.publicada = conteudo, publicada
            registrar("trilha_salva", titulo)
            db.session.commit()
            flash("Trilha salva.", "ok")
            return redirect(url_for("admin.trilhas"))

    return render_template("admin/trilha_form.html", trilha=trilha, areas=models.AREAS)


# ─────────────────────────────── Questões ──────────────────────────────────
@bp.route("/questoes")
def questoes():
    lista = models.Questao.query.filter_by(empresa_id=current_user.empresa_id).order_by(
        models.Questao.area, models.Questao.id).all()
    return render_template("admin/questoes.html", questoes=lista)


@bp.route("/questoes/nova", methods=["GET", "POST"])
@bp.route("/questoes/<int:questao_id>/editar", methods=["GET", "POST"])
def questao_form(questao_id=None):
    questao = _do_tenant(models.Questao, questao_id) if questao_id else None

    if request.method == "POST":
        enunciado = (request.form.get("enunciado") or "").strip()
        area = request.form.get("area") or "GERAL"
        artigo = (request.form.get("artigo") or "").strip()
        explicacao = (request.form.get("explicacao") or "").strip()
        try:
            dificuldade = max(1, min(3, int(request.form.get("dificuldade") or 1)))
        except ValueError:
            dificuldade = 1
        textos = [(request.form.get(f"alt_{i}") or "").strip() for i in range(4)]
        try:
            correta = int(request.form.get("correta"))
        except (TypeError, ValueError):
            correta = -1
        preenchidas = [(i, t) for i, t in enumerate(textos) if t]

        if not enunciado or area not in models.AREA_CODES:
            flash("Informe enunciado e área válida.", "erro")
        elif len(preenchidas) < 2:
            flash("Cadastre ao menos duas alternativas.", "erro")
        elif correta not in [i for i, _ in preenchidas]:
            flash("Marque qual alternativa é a correta.", "erro")
        else:
            if questao is None:
                questao = models.Questao(empresa_id=current_user.empresa_id)
                db.session.add(questao)
            questao.enunciado, questao.area = enunciado, area
            questao.artigo, questao.explicacao, questao.dificuldade = artigo, explicacao, dificuldade
            # Recria as alternativas
            for alt in list(questao.alternativas):
                db.session.delete(alt)
            db.session.flush()
            for ordem, (idx, texto) in enumerate(preenchidas):
                questao.alternativas.append(models.Alternativa(
                    texto=texto, correta=(idx == correta), ordem=ordem,
                ))
            registrar("questao_salva", area)
            db.session.commit()
            flash("Questão salva.", "ok")
            return redirect(url_for("admin.questoes"))

    return render_template("admin/questao_form.html", questao=questao, areas=models.AREAS)


# ───────────────────────────── Exclusões ───────────────────────────────────
@bp.route("/trilhas/<int:trilha_id>/excluir", methods=["POST"])
def trilha_excluir(trilha_id):
    trilha = _do_tenant(models.Trilha, trilha_id)
    registrar("trilha_excluida", trilha.titulo)
    db.session.delete(trilha)
    db.session.commit()
    flash("Trilha excluída.", "ok")
    return redirect(url_for("admin.trilhas"))


@bp.route("/questoes/<int:questao_id>/excluir", methods=["POST"])
def questao_excluir(questao_id):
    questao = _do_tenant(models.Questao, questao_id)
    em_uso = models.ProvaItem.query.filter_by(questao_id=questao.id).first() is not None
    if em_uso:
        # Não dá para apagar sem quebrar provas já feitas — desativa (sai do sorteio).
        questao.ativo = False
        registrar("questao_desativada", f"id={questao.id} (em uso por provas)")
        db.session.commit()
        flash("A questão é usada em provas existentes; foi desativada em vez de excluída.", "aviso")
    else:
        registrar("questao_excluida", f"id={questao.id}")
        db.session.delete(questao)
        db.session.commit()
        flash("Questão excluída.", "ok")
    return redirect(url_for("admin.questoes"))


# ───────────────────────────── Configurações ───────────────────────────────
@bp.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    empresa = current_user.empresa
    if request.method == "POST":
        empresa.mfa_obrigatorio = request.form.get("mfa_obrigatorio") == "on"
        remetente = (request.form.get("email_remetente") or "").strip().lower()
        if remetente and "@" not in remetente:
            flash("Informe um e-mail de remetente válido (ou deixe em branco).", "erro")
            return redirect(url_for("admin.configuracoes"))
        empresa.email_remetente = remetente or None
        registrar("config_alterada",
                  f"mfa_obrigatorio={empresa.mfa_obrigatorio} email_remetente={empresa.email_remetente or '-'}")
        db.session.commit()
        flash("Configurações salvas.", "ok")
        return redirect(url_for("admin.configuracoes"))
    return render_template("admin/configuracoes.html", empresa=empresa)


# ───────────────────────────── Reavaliações / Auditoria ────────────────────
@bp.route("/reavaliacoes")
def reavaliacoes():
    return render_template("admin/reavaliacoes.html", linhas=pendencias_empresa(current_user.empresa_id))


@bp.route("/reavaliacoes/notificar", methods=["POST"])
def reavaliacoes_notificar():
    enviados, total = notificar_reavaliacoes(current_user.empresa)
    if current_app.config.get("MAIL_SERVER"):
        flash(f"{enviados} de {total} colaborador(es) notificado(s) por e-mail.", "ok")
    else:
        flash(f"Modo dry-run (sem MAIL_SERVER): {total} pendência(s) registrada(s) no log, "
              "nenhum e-mail enviado.", "aviso")
    return redirect(url_for("admin.reavaliacoes"))


@bp.route("/auditoria")
def auditoria():
    pagina = max(1, request.args.get("pagina", 1, type=int))
    por_pagina = 50
    query = (
        models.AuditLog.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.AuditLog.criado_em.desc())
    )
    total = query.count()
    logs = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
    return render_template("admin/auditoria.html", logs=logs, pagina=pagina, total=total,
                           tem_proxima=(pagina * por_pagina < total))


@bp.route("/emails")
def emails():
    """Caixa de saída: todo e-mail que a plataforma tentou enviar para esta empresa."""
    itens = (
        models.EmailEnviado.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.EmailEnviado.criado_em.desc()).limit(100).all()
    )
    return render_template("admin/emails.html", emails=itens,
                           dry_run=not current_app.config.get("MAIL_SERVER"))


@bp.route("/auditoria.csv")
def auditoria_csv():
    import csv
    import io

    registros = (
        models.AuditLog.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(models.AuditLog.criado_em.desc()).limit(5000).all()
    )
    buf = io.StringIO()
    escritor = csv.writer(buf)
    escritor.writerow(["data", "usuario", "acao", "detalhe", "ip"])
    for log in registros:
        escritor.writerow([
            log.criado_em.strftime("%Y-%m-%d %H:%M:%S"),
            log.usuario.email if log.usuario else "", log.acao, log.detalhe or "", log.ip or "",
        ])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=auditoria.csv"})


# ─────────────────────────────── Helpers ───────────────────────────────────
def _ultimo_encarregado_ativo(usuario) -> bool:
    """True se ``usuario`` é o único Encarregado ativo da empresa (não pode ser removido)."""
    ativos = models.Usuario.query.filter_by(
        empresa_id=usuario.empresa_id, papel=models.PAPEL_ENCARREGADO, ativo=True,
    ).count()
    return ativos <= 1 and usuario.ativo


def _do_tenant(modelo, obj_id):
    """Busca um registro garantindo que pertence à empresa do usuário."""
    obj = db.session.get(modelo, obj_id)
    if not obj or getattr(obj, "empresa_id", None) != current_user.empresa_id:
        abort(404)
    return obj


def _slug_unico(modelo, empresa_id, base):
    slug, n = base, 2
    while modelo.query.filter_by(empresa_id=empresa_id, slug=slug).first():
        slug = f"{base}-{n}"
        n += 1
    return slug


def _slug_unico_trilha(empresa_id, base):
    """Slug único entre as trilhas da empresa E a biblioteca global (rota /trilhas/<slug>)."""
    slug, n = base, 2
    while models.Trilha.query.filter(
        models.Trilha.slug == slug,
        or_(models.Trilha.empresa_id == empresa_id, models.Trilha.empresa_id.is_(None)),
    ).first():
        slug = f"{base}-{n}"
        n += 1
    return slug
