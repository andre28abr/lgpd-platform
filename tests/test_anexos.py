"""Anexos como evidência (Parte 9a): validação, escopo por tenant e papéis."""
import io
import os

import models
from extensions import db
from services import anexos as svc


def _pedido(app):
    with app.app_context():
        p = models.PedidoTitular(empresa_id=1, nome_titular="Anexos", tipo="ACESSO")
        db.session.add(p)
        db.session.commit()
        return p.id


def _envia(client, csrf, pid, nome, conteudo):
    return client.post(f"/anexos/pedido/{pid}", data={
        "csrf_token": csrf(), "arquivo": (io.BytesIO(conteudo), nome),
    }, content_type="multipart/form-data")


def test_dpo_anexa_e_baixa(login, client, csrf, app):
    pid = _pedido(app)
    login("dpo@acme.com.br")
    r = _envia(client, csrf, pid, "resposta ao titular.txt", b"Resposta enviada em 10/09.")
    assert r.status_code in (302, 303)
    with app.app_context():
        a = models.Anexo.query.filter_by(alvo_tipo="pedido", alvo_id=pid).first()
        assert a is not None and a.empresa_id == 1 and a.nome_original == "resposta_ao_titular.txt"
        assert os.path.exists(svc.caminho(a))
        aid = a.id
    r = client.get(f"/anexos/{aid}")
    assert r.status_code == 200 and r.data == b"Resposta enviada em 10/09."
    assert "attachment" in r.headers["Content-Disposition"]
    assert "resposta_ao_titular.txt" in client.get(f"/direitos/{pid}").get_data(as_text=True)


def test_rejeita_extensao_e_conteudo_falso(login, client, csrf, app):
    pid = _pedido(app)
    login("dpo@acme.com.br")
    r = _envia(client, csrf, pid, "malware.exe", b"MZ...")
    assert "não permitido" in client.get(f"/direitos/{pid}").get_data(as_text=True) or r.status_code in (302, 303)
    r = _envia(client, csrf, pid, "falso.pdf", b"isto nao e um pdf")
    assert r.status_code in (302, 303)
    with app.app_context():
        assert models.Anexo.query.filter_by(alvo_id=pid).count() == 0


def test_gestor_baixa_mas_nao_envia(login, client, csrf, app):
    pid = _pedido(app)
    login("dpo@acme.com.br")
    _envia(client, csrf, pid, "contrato.pdf", b"%PDF-1.4 conteudo")
    with app.app_context():
        aid = models.Anexo.query.filter_by(alvo_id=pid).first().id
    client.post("/logout", data={"csrf_token": csrf()})

    login("gestor.rh@acme.com.br")
    assert client.get(f"/anexos/{aid}").status_code == 200
    assert _envia(client, csrf, pid, "x.txt", b"x").status_code == 403
    assert client.post(f"/anexos/{aid}/excluir", data={"csrf_token": csrf()}).status_code == 403


def test_anexo_de_outra_empresa_e_404(login, client, csrf, app):
    pid = _pedido(app)
    login("dpo@acme.com.br")
    _envia(client, csrf, pid, "interno.txt", b"segredo da acme")
    with app.app_context():
        aid = models.Anexo.query.filter_by(alvo_id=pid).first().id
    client.post("/logout", data={"csrf_token": csrf()})

    login("dpo@novaera.com.br")
    assert client.get(f"/anexos/{aid}").status_code == 404
    assert _envia(client, csrf, pid, "invasao.txt", b"x").status_code == 404  # alvo de outra empresa


def test_dpo_exclui_anexo_e_arquivo(login, client, csrf, app):
    pid = _pedido(app)
    login("dpo@acme.com.br")
    _envia(client, csrf, pid, "temp.txt", b"apagar")
    with app.app_context():
        a = models.Anexo.query.filter_by(alvo_id=pid).first()
        aid, caminho = a.id, svc.caminho(a)
    assert os.path.exists(caminho)
    client.post(f"/anexos/{aid}/excluir", data={"csrf_token": csrf()})
    assert not os.path.exists(caminho)
    with app.app_context():
        assert db.session.get(models.Anexo, aid) is None
