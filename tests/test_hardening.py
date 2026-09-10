"""Regressões do hardening (Parte 3): sessão, enumeração, reautenticação do 2FA, HSTS, proxy."""
from datetime import timedelta

import pyotp
from werkzeug.middleware.proxy_fix import ProxyFix

import models
from app import create_app
from config import Config
from extensions import db
from utils import agora_utc


def _criar_usuario(app, email, papel=models.PAPEL_COLABORADOR):
    with app.app_context():
        u = models.Usuario(empresa_id=1, nome=email.split("@")[0], email=email, papel=papel)
        u.definir_senha("lgpd1234")
        db.session.add(u)
        db.session.commit()
        return u.id


def test_sessao_vira_permanente_no_login(login, client):
    login("ana@acme.com.br")
    with client.session_transaction() as s:
        assert s.permanent  # ativa PERMANENT_SESSION_LIFETIME (8 h)


def test_bloqueio_nao_revela_conta_sem_a_senha(login, client, app):
    _criar_usuario(app, "enum@acme.com.br")
    for _ in range(5):
        login("enum@acme.com.br", "senha-errada")

    # Sem a senha certa, a resposta é a genérica — não dá para enumerar contas bloqueadas.
    corpo = login("enum@acme.com.br", "outra-errada").get_data(as_text=True).lower()
    assert "bloqueada" not in corpo and "inválidos" in corpo
    # Com a senha certa, o dono fica sabendo do bloqueio.
    assert "bloqueada" in login("enum@acme.com.br").get_data(as_text=True).lower()


def test_desativar_e_regenerar_2fa_exigem_senha_atual(login, client, csrf, app):
    uid = _criar_usuario(app, "reauth@acme.com.br")
    login("reauth@acme.com.br")
    with app.app_context():
        u = db.session.get(models.Usuario, uid)
        u.mfa_ativo, u.totp_secret = True, pyotp.random_base32()
        db.session.commit()

    r = client.post("/perfil/2fa/desativar", data={"csrf_token": csrf()})  # sem senha
    assert r.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.Usuario, uid).mfa_ativo  # continua ativo

    r = client.post("/perfil/2fa/desativar", data={"csrf_token": csrf(), "senha": "errada"})
    with app.app_context():
        assert db.session.get(models.Usuario, uid).mfa_ativo

    client.post("/perfil/2fa/desativar", data={"csrf_token": csrf(), "senha": "lgpd1234"})
    with app.app_context():
        u = db.session.get(models.Usuario, uid)
        assert not u.mfa_ativo and u.totp_secret is None


def test_hsts_so_com_cookie_seguro(client, app):
    assert "Strict-Transport-Security" not in client.get("/login").headers
    app.config["SESSION_COOKIE_SECURE"] = True
    try:
        assert client.get("/login").headers["Strict-Transport-Security"].startswith("max-age=")
    finally:
        app.config["SESSION_COOKIE_SECURE"] = False


def test_csp_bloqueia_plugins(client):
    assert "object-src 'none'" in client.get("/login").headers["Content-Security-Policy"]


def test_pagina_publica_do_certificado_nao_expoe_a_nota(client, app):
    with app.app_context():
        ana = models.Usuario.query.filter_by(email="ana@acme.com.br").first()
        prova = models.Prova(empresa_id=1, usuario_id=ana.id, area="RH", nota=87.5, aprovado=True,
                             status="concluida", finalizado_em=agora_utc())
        db.session.add(prova)
        db.session.flush()
        db.session.add(models.Certificado(
            empresa_id=1, usuario_id=ana.id, prova_id=prova.id, area="RH", codigo="cod-teste-minimizacao",
            nota=87.5, valido_ate=agora_utc() + timedelta(days=30),
        ))
        db.session.commit()

    corpo = client.get("/certificados/verificar/cod-teste-minimizacao").get_data(as_text=True)
    assert "válido" in corpo.lower()
    assert "Aproveitamento" not in corpo and "87" not in corpo


def test_proxy_fix_ativado_por_configuracao():
    class ComProxy(Config):
        PROXY_FIX_HOPS = 1

    assert isinstance(create_app(ComProxy).wsgi_app, ProxyFix)
    assert not isinstance(create_app(Config).wsgi_app, ProxyFix)
