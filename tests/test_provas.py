import re

import models
from extensions import db


def test_fluxo_prova_aprovacao_e_certificado(login, client, app, csrf):
    login("ana@acme.com.br")
    r = client.post("/provas/iniciar", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    pid = int(re.search(r"/provas/(\d+)", r.headers["Location"]).group(1))

    token = csrf()
    with app.app_context():
        prova = db.session.get(models.Prova, pid)
        assert prova.total_questoes > 0
        data = {"csrf_token": token}
        for item in prova.itens:
            correta = next(a.id for a in item.questao.alternativas if a.correta)
            data[f"questao_{item.id}"] = str(correta)

    r = client.post(f"/provas/{pid}/responder", data=data)
    assert r.status_code in (302, 303)
    assert "Aprovado" in client.get(f"/provas/{pid}/resultado").get_data(as_text=True)

    with app.app_context():
        prova = db.session.get(models.Prova, pid)
        assert prova.nota == 100.0
        assert prova.certificado is not None
        cert_id, codigo = prova.certificado.id, prova.certificado.codigo

    r = client.get(f"/certificados/{cert_id}.pdf")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/pdf")

    publico = app.test_client()
    r = publico.get(f"/certificados/verificar/{codigo}")
    assert r.status_code == 200
    assert "válido" in r.get_data(as_text=True).lower()
