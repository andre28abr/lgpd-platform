"""Demo demonstrável (Parte 7): caixa de saída de e-mails, seed rico e segunda empresa."""
import models


def test_caixa_de_saida_registra_email_em_dry_run(client, csrf, login, app):
    client.get("/login")
    client.post("/senha/esqueci", data={"csrf_token": csrf(), "email": "ana@acme.com.br"})

    with app.app_context():
        e = (models.EmailEnviado.query.filter_by(destinatario="ana@acme.com.br")
             .order_by(models.EmailEnviado.id.desc()).first())
        assert e is not None and e.enviado is False
        assert "redefinição de senha" in e.assunto and "/senha/redefinir/" in e.corpo
        assert e.empresa_id == 1

    login("dpo@acme.com.br")
    corpo = client.get("/admin/emails").get_data(as_text=True)
    assert "ana@acme.com.br" in corpo and "Modo demonstração" in corpo


def test_caixa_de_saida_e_por_empresa(login, client, app):
    login("dpo@novaera.com.br")
    corpo = client.get("/admin/emails").get_data(as_text=True)
    assert "ana@acme.com.br" not in corpo


def test_seed_tem_segunda_empresa_isolada(login, client, app):
    with app.app_context():
        assert models.Empresa.query.filter_by(slug="nova-era").first() is not None
    login("dpo@novaera.com.br")
    corpo = client.get("/ropa/").get_data(as_text=True)
    assert "Agendamento de consultas" in corpo
    assert "Folha de pagamento" not in corpo  # dado da Acme não aparece


def test_seed_pilar2_tem_situacoes_variadas(app):
    with app.app_context():
        pedidos = models.PedidoTitular.query.filter_by(empresa_id=1).all()
        status = {p.status for p in pedidos}
        assert {"recebido", "em_andamento", "concluido"} <= status
        assert any(p.atrasado for p in pedidos)
        assert models.RopaRegistro.query.filter_by(empresa_id=1).count() >= 5
        assert models.Diagnostico.query.filter_by(empresa_id=1, status="concluido").count() >= 1
        assert models.Ripd.query.filter_by(empresa_id=1).count() >= 2
