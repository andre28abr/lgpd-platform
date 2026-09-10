"""Isolamento multi-tenant: a empresa A nunca lê, grava ou referencia dados da empresa B.

Complementa test_rbac.py (papéis dentro de UMA empresa) com uma segunda empresa
real, exercitando o guard de registro primário (404) e a validação das chaves
estrangeiras enviadas em formulários (ropa_id, setor_id, responsavel_id).
"""
import re
from datetime import timedelta

import pytest

import models
from app import _carregar_ou_gerar_secret_key
from extensions import db
from utils import agora_utc


@pytest.fixture(scope="module")
def beta(app):
    """Segunda empresa ("beta") com um registro de cada módulo do Pilar 2."""
    with app.app_context():
        empresa = models.Empresa(nome="Beta Ltda", slug="beta")
        db.session.add(empresa)
        db.session.flush()
        setor = models.Setor(empresa_id=empresa.id, nome="Comercial Beta", slug="comercial-beta", area="MARKETING")
        usuario = models.Usuario(empresa_id=empresa.id, nome="Bia Beta", email="bia@beta.com.br",
                                 papel=models.PAPEL_ENCARREGADO)
        usuario.definir_senha("lgpd1234")
        db.session.add_all([setor, usuario])
        db.session.flush()
        ropa = models.RopaRegistro(empresa_id=empresa.id, atividade="Prospeccao secreta da Beta")
        ripd = models.Ripd(empresa_id=empresa.id, titulo="RIPD interno da Beta")
        pedido = models.PedidoTitular(empresa_id=empresa.id, nome_titular="Titular da Beta", tipo="ACESSO")
        incidente = models.Incidente(empresa_id=empresa.id, titulo="Incidente da Beta")
        db.session.add_all([ropa, ripd, pedido, incidente])
        db.session.commit()
        return {
            "empresa_id": empresa.id, "setor_id": setor.id, "usuario_id": usuario.id,
            "ropa_id": ropa.id, "ripd_id": ripd.id, "pedido_id": pedido.id, "incidente_id": incidente.id,
        }


def test_acesso_cruzado_a_registro_primario_retorna_404(login, client, beta):
    login("dpo@acme.com.br")
    for url in (
        f"/ropa/{beta['ropa_id']}/editar",
        f"/ripd/{beta['ripd_id']}/editar",
        f"/ripd/{beta['ripd_id']}/pdf",
        f"/direitos/{beta['pedido_id']}",
        f"/incidentes/{beta['incidente_id']}",
        f"/admin/usuarios/{beta['usuario_id']}/editar",
    ):
        assert client.get(url).status_code == 404, url


def test_listagens_mostram_so_o_proprio_tenant(login, client, beta):
    login("dpo@acme.com.br")
    assert "Prospeccao secreta da Beta" not in client.get("/ropa/").get_data(as_text=True)
    assert "RIPD interno da Beta" not in client.get("/ripd/").get_data(as_text=True)


def test_ripd_nao_vincula_ropa_de_outra_empresa(login, client, app, csrf, beta):
    login("dpo@acme.com.br")
    r = client.post("/ripd/novo", data={
        "csrf_token": csrf(), "titulo": "RIPD teste isolamento", "ropa_id": str(beta["ropa_id"]),
    })
    assert r.status_code in (302, 303)
    with app.app_context():
        ripd = models.Ripd.query.filter_by(titulo="RIPD teste isolamento").first()
        assert ripd is not None
        assert ripd.ropa_id is None
        rid = ripd.id
    pdf = client.get(f"/ripd/{rid}/pdf")
    assert pdf.status_code == 200
    assert b"Prospeccao secreta da Beta" not in pdf.data


def test_ropa_nao_vincula_setor_de_outra_empresa(login, client, app, csrf, beta):
    login("dpo@acme.com.br")
    r = client.post("/ropa/novo", data={
        "csrf_token": csrf(), "atividade": "ROPA teste isolamento", "setor_id": str(beta["setor_id"]),
    })
    assert r.status_code in (302, 303)
    with app.app_context():
        reg = models.RopaRegistro.query.filter_by(atividade="ROPA teste isolamento").first()
        assert reg is not None and reg.setor_id is None


def test_admin_nao_vincula_usuario_a_setor_de_outra_empresa(login, client, app, csrf, beta):
    login("dpo@acme.com.br")
    r = client.post("/admin/usuarios", data={
        "csrf_token": csrf(), "nome": "Novo Isolado", "email": "isolado@acme.com.br",
        "senha": "senhaSegura1", "papel": models.PAPEL_COLABORADOR, "setor_id": str(beta["setor_id"]),
    })
    assert r.status_code in (302, 303)
    with app.app_context():
        u = models.Usuario.query.filter_by(email="isolado@acme.com.br").first()
        assert u is not None and u.setor_id is None


def test_pedido_nao_aceita_responsavel_de_outra_empresa(login, client, app, csrf, beta):
    login("dpo@acme.com.br")
    r = client.post("/direitos/novo", data={
        "csrf_token": csrf(), "nome_titular": "Titular Isolado", "tipo": "ACESSO",
    })
    pid = int(re.search(r"/direitos/(\d+)", r.headers["Location"]).group(1))
    r = client.post(f"/direitos/{pid}", data={
        "csrf_token": csrf(), "status": "em_andamento", "responsavel_id": str(beta["usuario_id"]),
    })
    assert r.status_code in (302, 303)
    with app.app_context():
        assert db.session.get(models.PedidoTitular, pid).responsavel_id is None


def test_id_nao_numerico_em_formulario_nao_gera_500(login, client, csrf):
    login("dpo@acme.com.br")
    r = client.post("/ropa/novo", data={
        "csrf_token": csrf(), "atividade": "ROPA id invalido", "setor_id": "abc",
    })
    assert r.status_code in (302, 303)


def test_prova_enviada_apos_o_prazo_nao_e_corrigida(login, client, app, csrf):
    login("ana@acme.com.br")
    r = client.post("/provas/iniciar", data={"csrf_token": csrf()})
    pid = int(re.search(r"/provas/(\d+)", r.headers["Location"]).group(1))

    token = csrf()
    with app.app_context():
        prova = db.session.get(models.Prova, pid)
        assert prova.tempo_limite_min, "o teste depende de TEMPO_PROVA_MIN > 0"
        # Simula uma prova iniciada bem antes do limite (+ tolerância) ter expirado.
        prova.criado_em = agora_utc() - timedelta(minutes=prova.tempo_limite_min + 5)
        data = {"csrf_token": token}
        for item in prova.itens:
            data[f"questao_{item.id}"] = str(next(a.id for a in item.questao.alternativas if a.correta))
        db.session.commit()

    r = client.post(f"/provas/{pid}/responder", data=data)
    assert r.status_code in (302, 303)
    with app.app_context():
        prova = db.session.get(models.Prova, pid)
        assert prova.status == "concluida"
        assert prova.aprovado is False
        assert prova.nota == 0.0
        assert prova.certificado is None


def test_secret_key_gerada_e_persistida(tmp_path):
    chave = _carregar_ou_gerar_secret_key(str(tmp_path))
    assert len(chave) == 64
    assert chave not in ("dev-inseguro-troque-em-producao", "troque-esta-chave-em-producao")
    assert _carregar_ou_gerar_secret_key(str(tmp_path)) == chave  # estável entre reinícios
