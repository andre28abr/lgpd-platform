"""Regressões das correções da auditoria (Parte 2): PDFs, notificações, auditoria, métricas."""

from sqlalchemy import event

import models
from extensions import db
from services.auditoria import registrar
from services.metricas import pendencias_empresa, ranking_empresa, resumo_empresa
from services.notificacoes import notificar_reavaliacoes


def test_ripd_pdf_nao_quebra_com_caracteres_de_marcacao(login, client, app, csrf):
    """'<', '>' e '&' em texto livre derrubavam o Paragraph do ReportLab (500)."""
    login("dpo@acme.com.br")
    r = client.post("/ripd/novo", data={
        "csrf_token": csrf(),
        "titulo": "Tratamento de menores < 18 anos & responsáveis",
        "descricao_tratamento": "Se idade < 18, exigir consentimento\nLinha 2 > linha 1",
        "medidas": "Cifrar dados <sensíveis>",
        "conclusao": "Risco aceitável se medidas <= implementadas",
    })
    assert r.status_code in (302, 303)
    with app.app_context():
        rid = models.Ripd.query.filter(models.Ripd.titulo.like("Tratamento de menores%")).first().id
    r = client.get(f"/ripd/{rid}/pdf")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/pdf")


def test_notificacao_em_dry_run_nao_finge_envio(login, client, app, csrf):
    with app.app_context():
        empresa = models.Empresa.query.filter_by(slug="acme").first()
        enviados, total = notificar_reavaliacoes(empresa)
        assert enviados == 0          # sem MAIL_SERVER nada foi enviado de verdade
        assert total >= 1             # a demo tem colaboradores sem certificado

    login("dpo@acme.com.br")
    r = client.post("/admin/reavaliacoes/notificar", data={"csrf_token": csrf()}, follow_redirects=True)
    corpo = r.get_data(as_text=True)
    assert "dry-run" in corpo and "nenhum e-mail enviado" in corpo


def test_auditoria_trunca_campos_e_nao_falha(app):
    with app.app_context():
        log = registrar("x" * 300, "y" * 600, empresa_id=1, commit=True)
        assert log is not None
        assert len(log.acao) == 120 and len(log.detalhe) == 255


def test_ranking_usa_numero_constante_de_consultas(app):
    """Antes: 1 + S + 2·(S·U) consultas. Agora: 5, independente do tamanho da empresa."""
    with app.app_context():
        contagem = []

        def _contar(*_args, **_kwargs):
            contagem.append(1)

        event.listen(db.engine, "before_cursor_execute", _contar)
        try:
            linhas = ranking_empresa(1)
        finally:
            event.remove(db.engine, "before_cursor_execute", _contar)
        assert linhas, "a empresa demo tem setores"
        assert len(contagem) <= 6, f"{len(contagem)} consultas — N+1 voltou?"


def test_resumo_empresa_conta_colaborador_sem_setor(app):
    with app.app_context():
        u = models.Usuario(empresa_id=1, nome="Sem Setor", email="semsetor@acme.com.br",
                           papel=models.PAPEL_COLABORADOR, setor_id=None)
        u.definir_senha("lgpd1234")
        db.session.add(u)
        db.session.commit()

        dados = resumo_empresa(1)
        assert dados["sem_setor"] >= 1
        assert dados["colaboradores"] >= sum(r["n"] for r in dados["ranking"]) + 1
        # e as pendências vêem a mesma pessoa
        assert any(p["usuario"].email == "semsetor@acme.com.br" for p in pendencias_empresa(1))
