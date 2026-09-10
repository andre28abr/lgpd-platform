"""Partes 10–12: trilha lida, QR no certificado, comparativo por setor, importação do ROPA, tour."""
import io
import re

import models


def test_marcar_trilha_como_lida_e_progresso_no_painel(login, client, csrf, app):
    login("ana@acme.com.br")
    assert "0 <small>de" in client.get("/").get_data(as_text=True)
    r = client.post("/trilhas/lgpd-no-rh/lida", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    assert "Lida em" in client.get("/trilhas/lgpd-no-rh").get_data(as_text=True)
    assert "1 <small>de" in client.get("/").get_data(as_text=True)
    assert 'class="pill pill-ok">lida' in client.get("/trilhas/").get_data(as_text=True)
    client.post("/trilhas/lgpd-no-rh/lida", data={"csrf_token": csrf()})  # idempotente
    with app.app_context():
        assert models.TrilhaLeitura.query.count() >= 1
    assert client.post("/trilhas/nao-existe/lida", data={"csrf_token": csrf()}).status_code == 404


def test_certificado_pdf_com_qr(login, client, app):
    login("dpo@acme.com.br")
    with app.app_context():
        cert = models.Certificado.query.filter_by(empresa_id=1).first()
        cid = cert.id
    r = client.get(f"/certificados/{cid}.pdf")
    assert r.status_code == 200 and r.data.startswith(b"%PDF")
    assert b"/Image" in r.data or b"/XObject" in r.data  # o QR entra como imagem no PDF


def test_comparativo_por_setor(login, client, csrf, app):
    login("dpo@acme.com.br")
    corpo = client.get("/diagnostico/comparativo").get_data(as_text=True)
    assert "Empresa toda" in corpo and "Score geral" in corpo   # o seed tem um diagnóstico concluído
    r = client.get("/diagnostico/comparativo.pdf")
    assert r.status_code == 200 and r.data.startswith(b"%PDF")
    client.post("/logout", data={"csrf_token": csrf()})
    login("gestor.rh@acme.com.br")
    assert client.get("/diagnostico/comparativo").status_code == 200  # leitura liberada ao gestor


def test_importar_ropa_de_csv_e_xlsx(login, client, csrf, app):
    login("dpo@acme.com.br")
    r = client.get("/ropa/modelo.xlsx")
    assert r.status_code == 200 and "spreadsheetml" in r.headers["Content-Type"]

    csv_bytes = ("Atividade;Setor;Titulares;Categorias de dados;Finalidade;Base legal;Retenção;Compartilhamento\n"
                 "Controle de acesso predial;TI e Segurança;Visitantes;Nome, documento;Segurança patrimonial;"
                 "Legítimo interesse (Art. 7º, IX);90 dias;Empresa de portaria\n"
                 "Pesquisa de satisfação;Setor Inexistente;Clientes;E-mail;Melhorar o serviço;CONSENTIMENTO;1 ano;\n"
                 ";;;;;;;\n").encode("utf-8")
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (io.BytesIO(csv_bytes), "ropa.csv")},
                    content_type="multipart/form-data", follow_redirects=True)
    corpo = r.get_data(as_text=True)
    assert "2 registro(s) importado(s)" in corpo and "não existe" in corpo
    with app.app_context():
        reg = models.RopaRegistro.query.filter_by(empresa_id=1, atividade="Controle de acesso predial").first()
        assert reg.base_legal == "LEGITIMO_INTERESSE" and reg.setor.nome == "TI e Segurança"
        reg2 = models.RopaRegistro.query.filter_by(empresa_id=1, atividade="Pesquisa de satisfação").first()
        assert reg2.setor_id is None and reg2.base_legal == "CONSENTIMENTO"

    # xlsx gerado pelo próprio modelo é aceito
    modelo = io.BytesIO(client.get("/ropa/modelo.xlsx").data)
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (modelo, "m.xlsx")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert "1 registro(s) importado(s)" in r.get_data(as_text=True)

    # arquivo errado
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (io.BytesIO(b"x"), "ropa.txt")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert ".xlsx ou .csv" in r.get_data(as_text=True)


def test_gestor_nao_importa_ropa(login, client, csrf):
    login("gestor.rh@acme.com.br")
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (io.BytesIO(b"a"), "a.csv")},
                    content_type="multipart/form-data")
    assert r.status_code == 403


def test_tour_presente_nos_paineis(login, client, csrf):
    for email, chave in (("dpo@acme.com.br", "encarregado"), ("ana@acme.com.br", "colaborador"),
                         ("gestor.rh@acme.com.br", "gestor")):
        login(email)
        corpo = client.get("/").get_data(as_text=True)
        assert re.search(rf'data-tour="{chave}"\s+hidden', corpo), f"tour de {chave} ausente"
        client.post("/logout", data={"csrf_token": csrf()})
