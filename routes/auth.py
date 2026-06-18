"""Autenticação: login (rate limit, bloqueio de conta, 2FA), logout e cadastro."""
from datetime import datetime, timedelta

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

import models
from extensions import db, limiter
from routes._helpers import destino_seguro, slugify
from utils import agora_utc
from security import validar_senha
from services.auditoria import registrar

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("painel.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        usuario = models.Usuario.query.filter_by(email=email, ativo=True).first()

        if usuario and usuario.esta_bloqueado:
            registrar("login_bloqueado", email, commit=True)
            flash("Conta temporariamente bloqueada por tentativas malsucedidas. Tente mais tarde.", "erro")
            return render_template("auth/login.html")

        if usuario and usuario.conferir_senha(senha):
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate = None
            if usuario.mfa_ativo:
                session["_pre_2fa_user"] = usuario.id
                db.session.commit()
                return redirect(url_for("auth.login_2fa", next=request.args.get("next")))
            login_user(usuario)
            usuario.ultimo_login = agora_utc()
            registrar("login", email, usuario=usuario)
            db.session.commit()
            return redirect(destino_seguro(request.args.get("next")) or url_for("painel.index"))

        if usuario:
            _registrar_falha(usuario)
        registrar("login_falha", email, commit=True)
        flash("E-mail ou senha inválidos.", "erro")

    return render_template("auth/login.html")


def _registrar_falha(usuario):
    usuario.tentativas_falhas = (usuario.tentativas_falhas or 0) + 1
    maximo = current_app.config["LOGIN_MAX_TENTATIVAS"]
    if usuario.tentativas_falhas >= maximo:
        minutos = current_app.config["LOGIN_BLOQUEIO_MIN"]
        usuario.bloqueado_ate = agora_utc() + timedelta(minutes=minutos)
        usuario.tentativas_falhas = 0
        registrar("conta_bloqueada", usuario.email, usuario=usuario)
    db.session.commit()


@bp.route("/login/2fa", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login_2fa():
    uid = session.get("_pre_2fa_user")
    usuario = db.session.get(models.Usuario, uid) if uid else None
    if not usuario or not usuario.mfa_ativo:
        session.pop("_pre_2fa_user", None)
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        import pyotp
        from services.recovery import consumir
        bruto = (request.form.get("codigo") or "").replace(" ", "")
        ok_totp = bool(usuario.totp_secret) and pyotp.TOTP(usuario.totp_secret).verify(bruto, valid_window=1)
        ok_recovery = (not ok_totp) and consumir(usuario, bruto)
        if ok_totp or ok_recovery:
            session.pop("_pre_2fa_user", None)
            login_user(usuario)
            usuario.ultimo_login = agora_utc()
            registrar("login_2fa_recovery" if ok_recovery else "login_2fa", usuario.email, usuario=usuario)
            db.session.commit()
            return redirect(destino_seguro(request.args.get("next")) or url_for("painel.index"))
        registrar("login_2fa_falha", usuario.email, usuario=usuario, commit=True)
        flash("Código de verificação inválido.", "erro")

    return render_template("auth/login_2fa.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    registrar("logout", current_user.email, commit=True)
    logout_user()
    flash("Sessão encerrada com segurança.", "ok")
    return redirect(url_for("auth.login"))


@bp.route("/cadastro", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def cadastro():
    """Signup público: cria a empresa e o primeiro usuário (Encarregado)."""
    if current_user.is_authenticated:
        return redirect(url_for("painel.index"))

    if request.method == "POST":
        empresa_nome = (request.form.get("empresa") or "").strip()
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        erro_senha = validar_senha(senha)

        if not (empresa_nome and nome and email):
            flash("Preencha todos os campos.", "erro")
        elif erro_senha:
            flash(erro_senha, "erro")
        elif models.Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "erro")
        else:
            empresa = models.Empresa(nome=empresa_nome, slug=_slug_unico_empresa(slugify(empresa_nome)))
            db.session.add(empresa)
            db.session.flush()
            usuario = models.Usuario(
                empresa_id=empresa.id, nome=nome, email=email, papel=models.PAPEL_ENCARREGADO,
            )
            usuario.definir_senha(senha)
            db.session.add(usuario)
            db.session.flush()
            registrar("cadastro_empresa", f"{empresa.slug} / {email}", usuario=usuario, empresa_id=empresa.id)
            db.session.commit()
            login_user(usuario)
            flash("Empresa criada. Comece cadastrando seus setores e colaboradores.", "ok")
            return redirect(url_for("painel.index"))

    return render_template("auth/cadastro.html")


def _slug_unico_empresa(base):
    slug, n = base, 2
    while models.Empresa.query.filter_by(slug=slug).first():
        slug = f"{base}-{n}"
        n += 1
    return slug
