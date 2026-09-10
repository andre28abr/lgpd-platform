"""Ciclo de vida dos dados da própria plataforma (Parte 9b):
anonimização, expurgo com cadeia de hash íntegra, export/import da empresa."""
import json
from datetime import timedelta

import models
from extensions import db
from services.auditoria import registrar, verificar_cadeia
from services.ciclo_vida import expurgar
from services.portabilidade import exportar_empresa, importar_empresa
from utils import agora_utc


def _usuario(app, email, ativo=False):
    with app.app_context():
        u = models.Usuario(empresa_id=1, nome="Pessoa Desligada", email=email, ativo=ativo)
        u.definir_senha("lgpd1234")
        db.session.add(u)
        db.session.commit()
        return u.id


def test_anonimizacao_remove_identificacao_e_mantem_historico(login, client, csrf, app):
    uid = _usuario(app, "desligada@acme.com.br")
    with app.app_context():
        db.session.add(models.Prova(empresa_id=1, usuario_id=uid, area="RH", nota=80, aprovado=True,
                                    status="concluida", finalizado_em=agora_utc()))
        db.session.add(models.EmailEnviado(empresa_id=1, destinatario="desligada@acme.com.br",
                                           assunto="x", corpo="y"))
        db.session.commit()

    login("dpo@acme.com.br")
    r = client.post(f"/admin/usuarios/{uid}/editar", data={"csrf_token": csrf(), "acao": "anonimizar"})
    assert r.status_code in (302, 303)
    with app.app_context():
        u = db.session.get(models.Usuario, uid)
        assert u.anonimizado_em is not None
        assert "desligada" not in u.email and "Desligada" not in u.nome
        assert not u.ativo and u.totp_secret is None and not u.conferir_senha("lgpd1234")
        assert models.Prova.query.filter_by(usuario_id=uid).count() == 1          # histórico fica
        assert models.EmailEnviado.query.filter_by(destinatario="desligada@acme.com.br").count() == 0


def test_anonimizacao_exige_usuario_inativo_e_nao_o_proprio(login, client, csrf, app):
    uid = _usuario(app, "ativa@acme.com.br", ativo=True)
    login("dpo@acme.com.br")
    r = client.post(f"/admin/usuarios/{uid}/editar", data={"csrf_token": csrf(), "acao": "anonimizar"},
                    follow_redirects=True)
    assert "Inative o usuário" in r.get_data(as_text=True)
    with app.app_context():
        assert db.session.get(models.Usuario, uid).anonimizado_em is None
        dpo_id = models.Usuario.query.filter_by(email="dpo@acme.com.br").first().id
    r = client.post(f"/admin/usuarios/{dpo_id}/editar", data={"csrf_token": csrf(), "acao": "anonimizar"},
                    follow_redirects=True)
    assert "si mesmo" in r.get_data(as_text=True)


def test_expurgo_mantem_a_cadeia_de_hash_integra(app):
    with app.app_context():
        antigo = registrar("expurgo_teste_antigo", "vai sumir", empresa_id=1, commit=True)
        antigo.criado_em = agora_utc() - timedelta(days=400)
        db.session.commit()
        antigo_id = antigo.id
        recente_id = registrar("expurgo_teste_recente", "fica", empresa_id=1, commit=True).id
        db.session.add(models.EmailEnviado(empresa_id=1, destinatario="velho@x", assunto="a", corpo="b",
                                           criado_em=agora_utc() - timedelta(days=200)))
        db.session.commit()

        n_logs, n_emails = expurgar(dias_auditoria=365, dias_emails=90)
        assert n_logs >= 1 and n_emails >= 1
        assert db.session.get(models.AuditLog, antigo_id) is None
        assert db.session.get(models.AuditLog, recente_id) is not None
        ok, _, quebrado = verificar_cadeia()
        assert ok, f"cadeia quebrada em {quebrado} após o expurgo"
        marcador = (models.AuditLog.query.filter_by(acao="auditoria_expurgada")
                    .order_by(models.AuditLog.id.desc()).first())
        assert marcador and "ancora=" in marcador.detalhe


def test_expurgo_desligado_por_padrao(app):
    with app.app_context():
        assert app.config["AUDITORIA_RETENCAO_DIAS"] == 0
        n_logs, _ = expurgar(dias_auditoria=0, dias_emails=0)
        assert n_logs == 0


def test_export_import_da_empresa(login, client, app):
    login("dpo@acme.com.br")
    r = client.get("/admin/exportar.json")
    assert r.status_code == 200 and "attachment" in r.headers["Content-Disposition"]
    dados = json.loads(r.data)
    assert dados["versao"] == 1 and dados["empresa"]["slug"] == "acme"
    assert "senha_hash" not in json.dumps(dados) and "totp" not in json.dumps(dados)

    with app.app_context():
        empresa, avisos = importar_empresa(dados, slug="acme-copia")
        eid = empresa.id
        assert empresa.slug == "acme-copia"
        for modelo in (models.Setor, models.RopaRegistro, models.Ripd, models.PedidoTitular, models.Incidente):
            assert modelo.query.filter_by(empresa_id=eid).count() == modelo.query.filter_by(empresa_id=1).count()
        n_usuarios = models.Usuario.query.filter_by(empresa_id=1).count()
        assert models.Usuario.query.filter_by(empresa_id=eid).count() == n_usuarios
        assert any("já existia" in a for a in avisos)          # e-mails colidiram e ganharam sufixo
        # protocolos e certificados continuam únicos
        sem_protocolo = (models.PedidoTitular.query.filter_by(empresa_id=eid)
                         .filter(models.PedidoTitular.protocolo.is_(None)).count())
        assert sem_protocolo == 0
        copia = models.Usuario.query.filter_by(empresa_id=eid, papel=models.PAPEL_ENCARREGADO).first()
        assert copia.email != "dpo@acme.com.br" and not copia.conferir_senha("lgpd1234")
        # o JSON reexportado da cópia tem o mesmo formato
        assert exportar_empresa(empresa)["empresa"]["nome"] == dados["empresa"]["nome"]
