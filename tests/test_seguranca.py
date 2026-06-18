import pyotp

import models
from extensions import db


def test_2fa_fluxo_completo(login, client, csrf, app):
    login("paula@acme.com.br")

    # Ativação: o segredo provisório fica na sessão até a confirmação.
    assert client.get("/perfil/2fa/ativar").status_code == 200
    with client.session_transaction() as s:
        secret = s.get("_2fa_secret_prov")
    assert secret
    r = client.post("/perfil/2fa/ativar", data={"codigo": pyotp.TOTP(secret).now(), "csrf_token": csrf()})
    assert r.status_code in (302, 303)

    with app.app_context():
        u = models.Usuario.query.filter_by(email="paula@acme.com.br").first()
        assert u.mfa_ativo and u.totp_secret
        totp_secret = u.totp_secret

    client.post("/logout", data={"csrf_token": csrf()})

    # Login com senha agora exige o segundo fator.
    r = login("paula@acme.com.br")
    assert r.status_code in (302, 303)
    assert "/login/2fa" in r.headers["Location"]
    assert client.get("/").status_code in (302, 303)  # ainda não autenticado

    r = client.post("/login/2fa", data={"codigo": pyotp.TOTP(totp_secret).now(), "csrf_token": csrf()})
    assert r.status_code in (302, 303)
    assert client.get("/").status_code == 200


def test_bloqueio_por_tentativas(login, client, app):
    for _ in range(5):
        login("joao@acme.com.br", "senha-errada")

    with app.app_context():
        u = models.Usuario.query.filter_by(email="joao@acme.com.br").first()
        assert u.esta_bloqueado

    # Mesmo com a senha correta, a conta está temporariamente bloqueada.
    r = login("joao@acme.com.br")
    assert "bloqueada" in r.get_data(as_text=True).lower()


def test_login_com_codigo_recuperacao(login, client, csrf):
    login("bruno@acme.com.br")
    client.get("/perfil/2fa/ativar")
    with client.session_transaction() as s:
        secret = s.get("_2fa_secret_prov")
    client.post("/perfil/2fa/ativar", data={"codigo": pyotp.TOTP(secret).now(), "csrf_token": csrf()})
    with client.session_transaction() as s:
        codigos = s.get("_recovery_show")
    assert codigos and len(codigos) == 10
    codigo = codigos[0]
    client.post("/logout", data={"csrf_token": csrf()})

    r = login("bruno@acme.com.br")
    assert "/login/2fa" in r.headers["Location"]
    r = client.post("/login/2fa", data={"codigo": codigo, "csrf_token": csrf()})
    assert r.status_code in (302, 303)
    assert client.get("/").status_code == 200

    # O mesmo código não funciona de novo (uso único).
    client.post("/logout", data={"csrf_token": csrf()})
    login("bruno@acme.com.br")
    r = client.post("/login/2fa", data={"codigo": codigo, "csrf_token": csrf()})
    assert r.status_code == 200


def test_admin_reseta_2fa(login, client, csrf, app):
    with app.app_context():
        u = models.Usuario.query.filter_by(email="paula@acme.com.br").first()
        u.mfa_ativo, u.totp_secret = True, pyotp.random_base32()
        db.session.commit()
        uid = u.id
    login("dpo@acme.com.br")
    r = client.post(f"/admin/usuarios/{uid}/editar", data={"acao": "reset2fa", "csrf_token": csrf()})
    assert r.status_code in (302, 303)
    with app.app_context():
        u = db.session.get(models.Usuario, uid)
        assert not u.mfa_ativo and u.totp_secret is None


def test_mfa_obrigatorio_forca_enrolamento(login, client, csrf, app):
    try:
        login("dpo@acme.com.br")
        client.post("/admin/configuracoes", data={"mfa_obrigatorio": "on", "csrf_token": csrf()})
        client.post("/logout", data={"csrf_token": csrf()})
        login("ana@acme.com.br")
        r = client.get("/trilhas/")
        assert r.status_code in (302, 303)
        assert "/perfil/2fa/ativar" in r.headers["Location"]
    finally:
        with app.app_context():
            empresa = models.Empresa.query.filter_by(slug="acme").first()
            empresa.mfa_obrigatorio = False
            db.session.commit()
