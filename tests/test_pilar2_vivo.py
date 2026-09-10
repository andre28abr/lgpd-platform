"""Pilar 2 vivo (Parte 8): portal do titular com protocolo, prazos e KPIs no painel."""
import re
from datetime import datetime

import models
from services.prazos import dias_uteis_desde


def test_portal_do_titular_abre_pedido_e_gera_protocolo(client, csrf, app):
    assert client.get("/titular/acme").status_code == 200
    assert client.get("/titular/nao-existe").status_code == 404

    client.get("/titular/acme")
    r = client.post("/titular/acme", data={
        "csrf_token": csrf(), "nome_titular": "Titular do Portal", "contato": "portal@example.com",
        "tipo": "PORTABILIDADE", "descricao": "Quero meus dados em formato aberto.",
    })
    assert r.status_code in (302, 303)
    protocolo = re.search(r"/protocolo/(LGPD-[0-9A-F]{8})", r.headers["Location"]).group(1)

    corpo = client.get(f"/titular/acme/protocolo/{protocolo}").get_data(as_text=True)
    assert protocolo in corpo and "Recebido" in corpo
    assert "Titular do Portal" not in corpo  # a página pública não expõe o nome

    with app.app_context():
        p = models.PedidoTitular.query.filter_by(protocolo=protocolo).first()
        assert p.empresa_id == 1 and p.origem == "portal" and p.status == "recebido"
        assert p.prazo is not None
        # O DPO foi avisado (caixa de saída).
        assert models.EmailEnviado.query.filter_by(empresa_id=1, destinatario="dpo@acme.com.br").count() >= 1


def test_consulta_de_protocolo_desconhecido(client, csrf):
    corpo = client.get("/titular/acme/protocolo/LGPD-00000000").get_data(as_text=True)
    assert "não encontrado" in corpo
    client.get("/titular/acme")
    r = client.post("/titular/acme/consultar", data={"csrf_token": csrf(), "protocolo": "lgpd-abc"})
    assert "/protocolo/LGPD-ABC" in r.headers["Location"]


def test_dpo_ve_o_pedido_do_portal_com_protocolo(login, client, app):
    login("dpo@acme.com.br")
    corpo = client.get("/direitos/").get_data(as_text=True)
    assert "portal" in corpo and "LGPD-" in corpo


def test_dias_uteis():
    seg = datetime(2026, 9, 7, 10, 0)   # segunda-feira
    assert dias_uteis_desde(seg, datetime(2026, 9, 8, 9, 0)) == 1    # terça
    assert dias_uteis_desde(seg, datetime(2026, 9, 11, 9, 0)) == 4   # sexta
    assert dias_uteis_desde(seg, datetime(2026, 9, 14, 9, 0)) == 5   # próxima segunda (pula fim de semana)
    assert dias_uteis_desde(seg, seg) == 0


def test_painel_do_dpo_mostra_alertas_e_kpis(login, client):
    login("dpo@acme.com.br")
    corpo = client.get("/").get_data(as_text=True)
    assert "Atenção agora" in corpo and "atrasado" in corpo        # pedido atrasado do seed
    assert "Resolução CD/ANPD nº 15/2024" in corpo                  # incidente sem ANPD do seed
    assert "Indicadores de privacidade" in corpo and "ROPA por base legal" in corpo


def test_cli_prazos(app):
    r = app.test_cli_runner().invoke(args=["prazos", "--email"])
    assert r.exit_code == 0, r.output
    assert "acme:" in r.output and "atrasado" in r.output and "notificado" in r.output
