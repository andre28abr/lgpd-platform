def test_colaborador_bloqueado(login, client):
    login("ana@acme.com.br")
    assert client.get("/admin/usuarios").status_code == 403
    assert client.get("/ranking/").status_code == 403
    assert client.get("/diagnostico/").status_code == 403


def test_encarregado_acessa_areas_restritas(login, client):
    login("dpo@acme.com.br")
    assert client.get("/admin/").status_code == 200
    assert client.get("/ranking/").status_code == 200
    assert client.get("/diagnostico/").status_code == 200
    assert client.get("/admin/questoes").status_code == 200
    assert client.get("/admin/trilhas").status_code == 200
    assert client.get("/admin/auditoria").status_code == 200
    assert client.get("/admin/reavaliacoes").status_code == 200


def test_perfil_acessivel_a_qualquer_usuario(login, client):
    login("ana@acme.com.br")
    assert client.get("/perfil/").status_code == 200


def test_rota_protegida_redireciona_anonimo(client):
    r = client.get("/")
    assert r.status_code in (302, 303)
    assert "/login" in r.headers.get("Location", "")
