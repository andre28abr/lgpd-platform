import re

import models
from extensions import db


def _rodar(client, app, csrf, valor):
    r = client.post("/diagnostico/iniciar", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    did = int(re.search(r"/diagnostico/(\d+)", r.headers["Location"]).group(1))
    token = csrf()
    with app.app_context():
        perguntas = models.DiagnosticoPergunta.query.all()
        assert perguntas
        data = {"csrf_token": token}
        for p in perguntas:
            data[f"p_{p.id}"] = valor
    r = client.post(f"/diagnostico/{did}/responder", data=data)
    assert r.status_code in (302, 303)
    return did


def test_diagnostico_score_maximo(login, client, app, csrf):
    login("dpo@acme.com.br")
    did = _rodar(client, app, csrf, "2")
    assert "100" in client.get(f"/diagnostico/{did}/resultado").get_data(as_text=True)
    with app.app_context():
        d = db.session.get(models.Diagnostico, did)
        assert d.score == 100.0 and d.nivel == "Otimizado"


def test_diagnostico_score_minimo(login, client, app, csrf):
    login("dpo@acme.com.br")
    did = _rodar(client, app, csrf, "0")
    with app.app_context():
        d = db.session.get(models.Diagnostico, did)
        assert d.score == 0.0 and d.nivel == "Inicial"


def test_grafico_evolucao_renderiza(login, client, app, csrf):
    login("dpo@acme.com.br")
    _rodar(client, app, csrf, "2")
    _rodar(client, app, csrf, "1")
    body = client.get("/diagnostico/").get_data(as_text=True)
    assert "<svg" in body and "polyline" in body
