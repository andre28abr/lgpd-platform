import models
from extensions import db


def test_excluir_trilha(login, client, csrf, app):
    login("dpo@acme.com.br")
    client.post("/admin/trilhas/nova", data={
        "titulo": "Trilha Temp", "area": "GERAL", "resumo": "x",
        "conteudo_md": "conteudo", "publicada": "on", "csrf_token": csrf()})
    with app.app_context():
        t = models.Trilha.query.filter_by(titulo="Trilha Temp").first()
        assert t is not None
        tid = t.id
    r = client.post(f"/admin/trilhas/{tid}/excluir", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.Trilha, tid) is None


def test_criar_e_excluir_questao(login, client, csrf, app):
    login("dpo@acme.com.br")
    client.post("/admin/questoes/nova", data={
        "enunciado": "Pergunta temp?", "area": "GERAL", "artigo": "Art. 1",
        "explicacao": "porque sim", "dificuldade": "1",
        "alt_0": "certa", "alt_1": "errada", "alt_2": "", "alt_3": "",
        "correta": "0", "csrf_token": csrf()})
    with app.app_context():
        q = models.Questao.query.filter_by(enunciado="Pergunta temp?").first()
        assert q is not None and len(q.alternativas) == 2
        qid = q.id
    r = client.post(f"/admin/questoes/{qid}/excluir", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.Questao, qid) is None


def test_notificar_reavaliacoes_dry_run(login, client, csrf):
    login("dpo@acme.com.br")
    r = client.post("/admin/reavaliacoes/notificar", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)


def test_auditoria_csv(login, client):
    login("dpo@acme.com.br")
    r = client.get("/admin/auditoria.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    assert "acao" in r.get_data(as_text=True)


def test_configuracoes_acessivel(login, client):
    login("dpo@acme.com.br")
    assert client.get("/admin/configuracoes").status_code == 200
