import re

import models


def test_export_ranking(login, client):
    login("dpo@acme.com.br")
    r = client.get("/ranking/exportar.xlsx")
    assert r.status_code == 200
    assert "spreadsheetml" in r.headers["Content-Type"]

    r = client.get("/ranking/relatorio.pdf")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/pdf")


def test_diagnostico_pdf(login, client, app, csrf):
    login("dpo@acme.com.br")
    r = client.post("/diagnostico/iniciar", data={"csrf_token": csrf()})
    did = int(re.search(r"/diagnostico/(\d+)", r.headers["Location"]).group(1))
    token = csrf()
    with app.app_context():
        data = {"csrf_token": token}
        for p in models.DiagnosticoPergunta.query.all():
            data[f"p_{p.id}"] = "2"
    client.post(f"/diagnostico/{did}/responder", data=data)

    r = client.get(f"/diagnostico/{did}/pdf")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/pdf")
