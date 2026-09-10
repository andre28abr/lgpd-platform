"""Papéis no Pilar 2: o Gestor apenas visualiza; só o Encarregado altera.
Também: o único Encarregado ativo da empresa não pode ser rebaixado nem inativado."""
import models
from extensions import db


def _pedido_e_incidente(app):
    with app.app_context():
        pedido = models.PedidoTitular(empresa_id=1, nome_titular="Titular Papeis", tipo="ACESSO")
        inc = models.Incidente(empresa_id=1, titulo="Incidente Papeis")
        db.session.add_all([pedido, inc])
        db.session.commit()
        return pedido.id, inc.id


def test_gestor_visualiza_mas_nao_altera(login, client, csrf, app):
    pid, iid = _pedido_e_incidente(app)
    login("gestor.rh@acme.com.br")

    # Leitura liberada — inclusive exportações.
    for url in ("/ropa/", "/ripd/", "/direitos/", f"/direitos/{pid}", "/incidentes/", f"/incidentes/{iid}",
                "/diagnostico/", "/ropa/exportar.xlsx", "/ropa/relatorio.pdf"):
        assert client.get(url).status_code == 200, url

    # Telas de edição e qualquer mutação: 403.
    for url in ("/ropa/novo", "/ripd/novo", "/direitos/novo", "/incidentes/novo"):
        assert client.get(url).status_code == 403, url
    token = csrf()
    for url in ("/ropa/novo", "/ripd/novo", "/direitos/novo", "/incidentes/novo",
                f"/direitos/{pid}", f"/incidentes/{iid}", "/diagnostico/iniciar"):
        assert client.post(url, data={"csrf_token": token}).status_code == 403, url

    # Detalhe existente abre em modo leitura (sem botão de salvar); criar novo é 403.
    with app.app_context():
        reg = models.RopaRegistro(empresa_id=1, atividade="ROPA leitura gestor", finalidade="ver")
        db.session.add(reg)
        db.session.commit()
        reg_id = reg.id
    corpo = client.get(f"/ropa/{reg_id}/editar").get_data(as_text=True)
    assert "ROPA leitura gestor" in corpo and "Salvar registro" not in corpo

    # A interface não oferece o que ele não pode fazer.
    assert "Novo registro" not in client.get("/ropa/").get_data(as_text=True)
    assert "Registrar pedido" not in client.get("/direitos/").get_data(as_text=True)
    assert "Iniciar diagnóstico" not in client.get("/diagnostico/").get_data(as_text=True)
    assert 'name="status"' not in client.get(f"/direitos/{pid}").get_data(as_text=True)


def test_encarregado_continua_alterando(login, client, csrf):
    login("dpo@acme.com.br")
    assert client.get("/ropa/novo").status_code == 200
    r = client.post("/ropa/novo", data={"csrf_token": csrf(), "atividade": "ROPA do DPO"})
    assert r.status_code in (302, 303)


def test_ultimo_encarregado_nao_pode_ser_rebaixado_nem_inativado(login, client, csrf, app):
    login("dpo@acme.com.br")
    with app.app_context():
        dpo = models.Usuario.query.filter_by(email="dpo@acme.com.br").first()
        dpo_id = dpo.id
        assert models.Usuario.query.filter_by(empresa_id=1, papel=models.PAPEL_ENCARREGADO, ativo=True).count() == 1

    r = client.post(f"/admin/usuarios/{dpo_id}/editar",
                    data={"csrf_token": csrf(), "papel": models.PAPEL_COLABORADOR, "ativo": "on"},
                    follow_redirects=True)
    assert "único Encarregado ativo" in r.get_data(as_text=True)
    r = client.post(f"/admin/usuarios/{dpo_id}/editar",
                    data={"csrf_token": csrf(), "papel": models.PAPEL_ENCARREGADO},  # sem "ativo" = inativar
                    follow_redirects=True)
    assert "único Encarregado ativo" in r.get_data(as_text=True)
    with app.app_context():
        dpo = db.session.get(models.Usuario, dpo_id)
        assert dpo.is_encarregado and dpo.ativo

    # Com um segundo Encarregado, rebaixar esse segundo é permitido.
    with app.app_context():
        u2 = models.Usuario(empresa_id=1, nome="DPO 2", email="dpo2@acme.com.br", papel=models.PAPEL_ENCARREGADO)
        u2.definir_senha("lgpd1234")
        db.session.add(u2)
        db.session.commit()
        u2_id = u2.id
    client.post(f"/admin/usuarios/{u2_id}/editar",
                data={"csrf_token": csrf(), "papel": models.PAPEL_GESTOR, "ativo": "on"})
    with app.app_context():
        assert db.session.get(models.Usuario, u2_id).is_gestor
