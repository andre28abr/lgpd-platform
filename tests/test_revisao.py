"""Regressões dos achados da revisão independente final (nenhum crítico; 2 altos, 5 médios, 9 baixos)."""
import io
import os
from datetime import datetime

import models
from extensions import db
from services import anexos as svc_anexos
from services.prazos import dias_uteis_desde


def test_xlsx_invalido_nao_gera_500(login, client, csrf):
    login("dpo@acme.com.br")
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (io.BytesIO(b"nao e zip"), "x.xlsx")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert r.status_code == 200 and "Não consegui ler a planilha" in r.get_data(as_text=True)


def test_excel_exportado_e_reimportavel(login, client, csrf, app):
    login("dpo@acme.com.br")
    with app.app_context():
        antes = models.RopaRegistro.query.filter_by(empresa_id=1).count()
    exportado = io.BytesIO(client.get("/ropa/exportar.xlsx").data)
    r = client.post("/ropa/importar", data={"csrf_token": csrf(), "planilha": (exportado, "ropa.xlsx")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert f"{antes} registro(s) importado(s)" in r.get_data(as_text=True)


def test_excluir_ripd_leva_os_anexos(login, client, csrf, app):
    login("dpo@acme.com.br")
    r = client.post("/ripd/novo", data={"csrf_token": csrf(), "titulo": "RIPD com anexo"})
    with app.app_context():
        rid = models.Ripd.query.filter_by(titulo="RIPD com anexo").first().id
    client.post(f"/anexos/ripd/{rid}", data={"csrf_token": csrf(), "arquivo": (io.BytesIO(b"%PDF-1.4 x"), "prova.pdf")},
                content_type="multipart/form-data")
    with app.app_context():
        anexo = models.Anexo.query.filter_by(alvo_tipo="ripd", alvo_id=rid).first()
        caminho = svc_anexos.caminho(anexo)
        assert os.path.exists(caminho)
    r = client.post(f"/ripd/{rid}/excluir", data={"csrf_token": csrf()})
    assert r.status_code in (302, 303)
    with app.app_context():
        assert models.Anexo.query.filter_by(alvo_tipo="ripd", alvo_id=rid).count() == 0
    assert not os.path.exists(caminho)
    # o próximo RIPD (que pode reaproveitar o id no SQLite) nasce sem evidências herdadas
    client.post("/ripd/novo", data={"csrf_token": csrf(), "titulo": "RIPD seguinte"})
    with app.app_context():
        novo = models.Ripd.query.filter_by(titulo="RIPD seguinte").first()
        assert svc_anexos.listar("ripd", novo.id, 1) == []


def test_diagnostico_setor_invalido_nao_gera_500(login, client, csrf):
    login("dpo@acme.com.br")
    r = client.post("/diagnostico/iniciar", data={"csrf_token": csrf(), "setor_id": "abc"})
    assert r.status_code in (302, 303) and "/diagnostico/" in r.headers["Location"]


def test_portal_trunca_no_tamanho_da_coluna(client, csrf, app):
    client.get("/titular/acme")
    r = client.post("/titular/acme", data={"csrf_token": csrf(), "nome_titular": "N" * 500,
                                           "contato": "c" * 500 + "@x.com", "tipo": "ACESSO"})
    assert r.status_code in (302, 303)
    with app.app_context():
        p = models.PedidoTitular.query.filter(models.PedidoTitular.nome_titular.like("NNNN%")).first()
        assert len(p.nome_titular) == 160 and len(p.contato) == 255


def test_auditoria_de_conta_registra_id_nao_email(login, client, csrf, app):
    login("dpo@acme.com.br")
    client.post("/admin/usuarios", data={"csrf_token": csrf(), "nome": "Sigilo", "email": "sigilo@acme.com.br",
                                         "senha": "senhaSegura1", "papel": models.PAPEL_COLABORADOR})
    with app.app_context():
        u = models.Usuario.query.filter_by(email="sigilo@acme.com.br").first()
        log = models.AuditLog.query.filter_by(acao="usuario_criado").order_by(models.AuditLog.id.desc()).first()
        assert log.detalhe == f"id={u.id}"
        assert models.AuditLog.query.filter(models.AuditLog.acao == "login",
                                            models.AuditLog.detalhe.like("%@%")).count() == 0


def test_dias_uteis_e_rapido_para_datas_absurdas():
    assert dias_uteis_desde(datetime(2026, 9, 7), datetime(2026, 9, 14, 9)) == 5
    assert dias_uteis_desde(datetime(1, 1, 1), datetime(2026, 9, 10)) > 500_000  # O(1), não itera dia a dia


def test_anexo_nome_nao_ascii_e_aceito_e_arquivo_sumido_da_404(login, client, csrf, app):
    with app.app_context():
        p = models.PedidoTitular(empresa_id=1, nome_titular="Unicode", tipo="ACESSO")
        db.session.add(p)
        db.session.commit()
        pid = p.id
    login("dpo@acme.com.br")
    dados = {"csrf_token": csrf(), "arquivo": (io.BytesIO(b"%PDF-1.4"), "報告.pdf")}
    r = client.post(f"/anexos/pedido/{pid}", data=dados, content_type="multipart/form-data", follow_redirects=True)
    assert "Anexo adicionado" in r.get_data(as_text=True)
    with app.app_context():
        a = models.Anexo.query.filter_by(alvo_id=pid).first()
        assert a.nome_original.endswith(".pdf")
        os.remove(svc_anexos.caminho(a))
        aid = a.id
    assert client.get(f"/anexos/{aid}").status_code == 404
