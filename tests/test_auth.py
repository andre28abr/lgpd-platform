def test_pagina_login(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "conformidade" in r.get_data(as_text=True).lower()


def test_login_sucesso(login, client):
    r = login("dpo@acme.com.br")
    assert r.status_code in (302, 303)
    r = client.get("/")
    assert r.status_code == 200
    assert "Encarregado" in r.get_data(as_text=True)


def test_login_falha(login):
    r = login("dpo@acme.com.br", "senha-errada")
    assert r.status_code == 200
    assert "inválidos" in r.get_data(as_text=True).lower()


def test_csrf_bloqueia_post_sem_token(client):
    r = client.post("/login", data={"email": "x@y.z", "senha": "abc"})
    assert r.status_code == 400


def test_signup_cria_empresa(client, csrf):
    client.get("/cadastro")
    r = client.post("/cadastro", data={
        "empresa": "Nova Co", "nome": "Fulano de Tal",
        "email": "novo@nova.co", "senha": "segredo123", "csrf_token": csrf(),
    })
    assert r.status_code in (302, 303)
    r = client.get("/")
    assert r.status_code == 200  # já autenticado como Encarregado


def test_signup_senha_curta_rejeitada(client, csrf):
    client.get("/cadastro")
    r = client.post("/cadastro", data={
        "empresa": "Curta Co", "nome": "Beltrano",
        "email": "curta@co.co", "senha": "123", "csrf_token": csrf(),
    })
    assert "8 caracteres" in r.get_data(as_text=True)
