import re

import models
from extensions import db


def test_ropa_crud(login, client, csrf, app):
    login("dpo@acme.com.br")
    assert client.get("/ropa/").status_code == 200

    client.post("/ropa/novo", data={
        "atividade": "Controle de ponto", "titulares": "Colaboradores",
        "categorias_dados": "biometria", "finalidade": "registro de jornada",
        "base_legal": "OBRIGACAO_LEGAL", "retencao": "5 anos",
        "compartilhamento": "", "setor_id": "", "csrf_token": csrf()})
    with app.app_context():
        r = models.RopaRegistro.query.filter_by(atividade="Controle de ponto").first()
        assert r is not None and r.base_legal == "OBRIGACAO_LEGAL"
        rid = r.id

    resp = client.post(f"/ropa/{rid}/excluir", data={"csrf_token": csrf()})
    assert resp.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.RopaRegistro, rid) is None


def test_pedido_titular_fluxo(login, client, csrf, app):
    login("dpo@acme.com.br")
    assert client.get("/direitos/").status_code == 200

    r = client.post("/direitos/novo", data={
        "nome_titular": "Maria Teste", "contato": "maria@ex.com",
        "tipo": "ACESSO", "descricao": "quero meus dados", "csrf_token": csrf()})
    assert r.status_code in (302, 303)
    pid = int(re.search(r"/direitos/(\d+)", r.headers["Location"]).group(1))
    with app.app_context():
        p = db.session.get(models.PedidoTitular, pid)
        assert p.status == "recebido" and p.prazo is not None

    client.post(f"/direitos/{pid}", data={"status": "concluido", "observacoes": "ok", "csrf_token": csrf()})
    with app.app_context():
        p = db.session.get(models.PedidoTitular, pid)
        assert p.status == "concluido" and p.concluido_em is not None


def test_colaborador_bloqueado_na_fase2(login, client):
    login("ana@acme.com.br")
    assert client.get("/ropa/").status_code == 403
    assert client.get("/direitos/").status_code == 403


def test_ripd_crud(login, client, csrf, app):
    login("dpo@acme.com.br")
    assert client.get("/ripd/").status_code == 200
    client.post("/ripd/novo", data={
        "titulo": "RIPD teste", "ropa_id": "", "descricao_tratamento": "x",
        "probabilidade": "3", "impacto": "3", "medidas": "y",
        "risco_residual": "medio", "conclusao": "z", "status": "concluido", "csrf_token": csrf()})
    with app.app_context():
        r = models.Ripd.query.filter_by(titulo="RIPD teste").first()
        assert r is not None and r.risco_inerente == 9 and r.status == "concluido"
        rid = r.id
    resp = client.post(f"/ripd/{rid}/excluir", data={"csrf_token": csrf()})
    assert resp.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.Ripd, rid) is None


def test_incidente_fluxo(login, client, csrf, app):
    login("dpo@acme.com.br")
    assert client.get("/incidentes/").status_code == 200
    r = client.post("/incidentes/novo", data={
        "titulo": "Vazamento teste", "ocorrido_em": "2026-06-01", "num_titulares": "5",
        "risco": "alto", "descricao": "d", "dados_afetados": "nome", "csrf_token": csrf()})
    assert r.status_code in (302, 303)
    iid = int(re.search(r"/incidentes/(\d+)", r.headers["Location"]).group(1))
    with app.app_context():
        inc = db.session.get(models.Incidente, iid)
        assert inc.risco == "alto" and inc.num_titulares == 5

    client.post(f"/incidentes/{iid}", data={
        "status": "encerrado", "risco": "alto", "comunicado_anpd": "on",
        "comunicado_anpd_em": "2026-06-02", "medidas": "ok", "csrf_token": csrf()})
    with app.app_context():
        inc = db.session.get(models.Incidente, iid)
        assert inc.status == "encerrado" and inc.comunicado_anpd is True and inc.comunicado_anpd_em is not None


def test_privacidade_hub_e_legislacao(login, client):
    login("dpo@acme.com.br")
    assert client.get("/privacidade/").status_code == 200
    assert client.get("/legislacao/").status_code == 200


def test_colaborador_bloqueado_nos_novos_modulos(login, client):
    login("ana@acme.com.br")
    assert client.get("/ripd/").status_code == 403
    assert client.get("/incidentes/").status_code == 403
    assert client.get("/privacidade/").status_code == 403
    assert client.get("/legislacao/").status_code == 200  # aberta a qualquer usuário logado


def test_ripd_pdf(login, client, csrf, app):
    login("dpo@acme.com.br")
    client.post("/ripd/novo", data={
        "titulo": "RIPD pdf", "probabilidade": "2", "impacto": "2",
        "status": "rascunho", "csrf_token": csrf()})
    with app.app_context():
        rid = models.Ripd.query.filter_by(titulo="RIPD pdf").first().id
    r = client.get(f"/ripd/{rid}/pdf")
    assert r.status_code == 200 and r.headers["Content-Type"].startswith("application/pdf")


def test_politica_publica_sem_login(client):
    r = client.get("/politica-de-privacidade")
    assert r.status_code == 200
    assert "privacidade" in r.get_data(as_text=True).lower()
