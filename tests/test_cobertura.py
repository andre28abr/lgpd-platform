"""Caminhos de erro, integrações simuladas (SMTP, feed RSS) e comandos de CLI.

Nada aqui toca a rede: SMTP e feedparser são substituídos por dublês. O objetivo é
que os ramos "quando dá errado" também tenham teste — é neles que a demo costuma quebrar.
"""
import io
import json
import os

import models
from config import _normalize, engine_options_for, resolve_database_uri
from extensions import db
from routes._helpers import destino_seguro, slugify
from security import validar_senha
from services import anexos as svc_anexos
from services.auditoria import registrar
from services.email import enviar
from services.pdf_utils import celula_planilha, esc
from services.prazos import notificar_prazos


# ── utilitários puros ───────────────────────────────────────────────────────
def test_helpers_puros(tmp_path, monkeypatch):
    assert destino_seguro(None) is None
    assert destino_seguro("https://evil.example") is None
    assert destino_seguro("//evil.example") is None
    assert destino_seguro("relativo-sem-barra") is None
    assert destino_seguro("/painel") == "/painel"
    assert slugify("") == "item" and slugify("Ação & Reação!") == "acao-reacao"
    assert validar_senha("12345678") == "A senha não pode conter apenas números."
    assert validar_senha("curta") and validar_senha("senhaSegura1") is None
    assert esc(None) == "" and esc("a<b\nc") == "a&lt;b<br/>c"
    assert celula_planilha(5) == 5 and celula_planilha("=SOMA(A1)") == "'=SOMA(A1)"
    assert _normalize("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert engine_options_for("postgresql://x")["pool_pre_ping"] is True
    assert engine_options_for("sqlite:///x") == {}
    monkeypatch.delenv("DATABASE_URL", raising=False)
    uri = resolve_database_uri(str(tmp_path / "inst"))
    assert uri.startswith("sqlite:///") and os.path.isdir(tmp_path / "inst")


# ── e-mail: caminho SMTP real, simulado ─────────────────────────────────────
class _SMTPFalso:
    enviados = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.timeout = host, port, timeout

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, user, pwd):
        pass

    def send_message(self, msg):
        _SMTPFalso.enviados.append((msg["To"], msg["Subject"]))


class _SMTPQuebrado(_SMTPFalso):
    def send_message(self, msg):
        raise OSError("servidor fora do ar")


def test_email_smtp_sucesso_e_falha_sao_registrados(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, "MAIL_SERVER", "smtp.teste.local")
        monkeypatch.setitem(app.config, "MAIL_USERNAME", "u")
        monkeypatch.setitem(app.config, "MAIL_PASSWORD", "p")
        monkeypatch.setattr("services.email.smtplib.SMTP", _SMTPFalso)
        assert enviar("dest@x.com", "Assunto\r\ninjetado", "corpo", empresa_id=1) is True
        para, assunto = _SMTPFalso.enviados[-1]
        assert para == "dest@x.com" and "\r" not in assunto and "\n" not in assunto  # CR/LF removidos
        registro = (models.EmailEnviado.query.filter_by(destinatario="dest@x.com")
                    .order_by(models.EmailEnviado.id.desc()).first())
        assert registro.enviado is True

        monkeypatch.setattr("services.email.smtplib.SMTP", _SMTPQuebrado)
        assert enviar("dest2@x.com", "x", "y", empresa_id=1) is False  # falha vira log, não exceção
        registro = models.EmailEnviado.query.filter_by(destinatario="dest2@x.com").first()
        assert registro is not None and registro.enviado is False


# ── legislação: feed simulado, com e sem falha ──────────────────────────────
def test_legislacao_com_feed_simulado(login, client, app, monkeypatch):
    login("ana@acme.com.br")
    assert "Lei nº 13.709/2018" in client.get("/legislacao/").get_data(as_text=True)  # sem feed

    class _Feed:
        entries = [{"title": "Nova resolução", "link": "https://www.gov.br/anpd/x", "published": "hoje"}]

    monkeypatch.setitem(app.config, "FEED_URL", "https://exemplo.invalido/feed")
    monkeypatch.setattr("feedparser.parse", lambda url: _Feed())
    assert "Nova resolução" in client.get("/legislacao/").get_data(as_text=True)

    def _explode(url):
        raise OSError("sem rede")
    monkeypatch.setattr("feedparser.parse", _explode)
    assert "Não foi possível carregar o feed" in client.get("/legislacao/").get_data(as_text=True)


# ── healthcheck com banco fora ──────────────────────────────────────────────
def test_saude_devolve_503_sem_banco(client, monkeypatch):
    class _SessaoQuebrada:
        def execute(self, *a, **k):
            raise RuntimeError("banco indisponível")

        def remove(self):  # chamado no teardown do app context
            pass
    monkeypatch.setattr("routes.publico.db.session", _SessaoQuebrada())
    r = client.get("/saude")
    assert r.status_code == 503 and r.get_json()["banco"] == "indisponivel"


# ── certificados: listagem, 404 e 403 ───────────────────────────────────────
def test_certificados_listar_404_e_403(login, client, app):
    login("ana@acme.com.br")
    with app.app_context():
        ana = models.Usuario.query.filter_by(email="ana@acme.com.br").first()
        codigo_ana = models.Certificado.query.filter_by(usuario_id=ana.id).first().codigo
        joao = models.Usuario.query.filter_by(email="joao@acme.com.br").first()
        cert_joao = models.Certificado.query.filter_by(usuario_id=joao.id).first().id
    r = client.get("/certificados/")
    assert r.status_code == 200 and codigo_ana in r.get_data(as_text=True)
    assert client.get("/certificados/999999.pdf").status_code == 404
    assert client.get(f"/certificados/{cert_joao}.pdf").status_code == 403  # de outro colaborador


# ── portal do titular: validação ────────────────────────────────────────────
def test_portal_rejeita_pedido_incompleto(client, csrf):
    client.get("/titular/acme")
    r = client.post("/titular/acme", data={"csrf_token": csrf(), "nome_titular": "", "contato": "", "tipo": "ACESSO"})
    assert r.status_code == 200 and "Informe seu nome" in r.get_data(as_text=True)


# ── anexos: ramos de erro ───────────────────────────────────────────────────
def test_anexos_erros(login, client, csrf, app, monkeypatch):
    with app.app_context():
        p = models.PedidoTitular(empresa_id=1, nome_titular="Anexo Erros", tipo="ACESSO")
        db.session.add(p)
        db.session.commit()
        pid = p.id
    login("dpo@acme.com.br")
    r = client.post(f"/anexos/pedido/{pid}", data={"csrf_token": csrf()}, content_type="multipart/form-data",
                    follow_redirects=True)
    assert "Selecione um arquivo" in r.get_data(as_text=True)
    assert client.post(f"/anexos/tipo-desconhecido/{pid}", data={"csrf_token": csrf()},
                       content_type="multipart/form-data").status_code == 404
    r = client.post(f"/anexos/pedido/{pid}", data={"csrf_token": csrf(), "arquivo": (io.BytesIO(b""), "vazio.txt")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert "vazio" in r.get_data(as_text=True)
    monkeypatch.setitem(app.config, "ANEXO_MAX_MB", 0)
    r = client.post(f"/anexos/pedido/{pid}", data={"csrf_token": csrf(), "arquivo": (io.BytesIO(b"abc"), "g.txt")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert "excede" in r.get_data(as_text=True)
    monkeypatch.setitem(app.config, "ANEXO_MAX_MB", 5)
    # excluir anexo cujo arquivo já sumiu do disco não pode quebrar
    client.post(f"/anexos/pedido/{pid}", data={"csrf_token": csrf(), "arquivo": (io.BytesIO(b"ok"), "some.txt")},
                content_type="multipart/form-data")
    with app.app_context():
        a = models.Anexo.query.filter_by(alvo_id=pid).first()
        os.remove(svc_anexos.caminho(a))
        aid = a.id
    assert client.post(f"/anexos/{aid}/excluir", data={"csrf_token": csrf()}).status_code in (302, 303)


# ── auditoria: pendentes na mesma sessão e falha silenciosa ─────────────────
def test_auditoria_encadeia_pendentes_e_engole_falha(app):
    with app.app_context():
        a = registrar("pendente_1", "a", empresa_id=1)          # sem commit
        b = registrar("pendente_2", "b", empresa_id=1)          # encadeia no pendente, não no banco
        db.session.commit()
        from services.auditoria import _hash_do_log
        assert b.hash == _hash_do_log(b, a.hash)
        assert registrar(12345, None, empresa_id=1, commit=True) is None  # acao inválida: vira log, não 500


# ── prazos sem alertas ──────────────────────────────────────────────────────
def test_prazos_sem_alertas_nao_envia(app):
    with app.app_context():
        nova_era = models.Empresa.query.filter_by(slug="nova-era").first()
        assert notificar_prazos(nova_era) == (0, 0)


# ── trilhas: encarregado vê todas; usuário sem setor vê só a Geral ──────────
def test_trilhas_visiveis_por_papel(login, client, app):
    login("dpo@acme.com.br")
    corpo = client.get("/trilhas/").get_data(as_text=True)
    assert "Jurídico" in corpo and "Atendimento" in corpo
    with app.app_context():
        u = models.Usuario(empresa_id=1, nome="Sem Setor Trilha", email="semsetor.trilha@acme.com.br")
        u.definir_senha("lgpd1234")
        db.session.add(u)
        db.session.commit()
    client.post("/logout", data={"csrf_token": _csrf(client)})
    login("semsetor.trilha@acme.com.br")
    corpo = client.get("/trilhas/").get_data(as_text=True)
    assert "Fundamentos da LGPD" in corpo and "LGPD no RH" not in corpo


def _csrf(client):
    with client.session_transaction() as s:
        return s.get("_csrf_token")


# ── comandos de CLI ─────────────────────────────────────────────────────────
def test_cli_comandos(app, tmp_path, monkeypatch):
    runner = app.test_cli_runner()

    r = runner.invoke(args=["exportar-questoes", str(tmp_path / "q.csv")])
    assert r.exit_code == 0 and "229 questões" in r.output
    assert len((tmp_path / "q.csv").read_text(encoding="utf-8").splitlines()) >= 230

    r = runner.invoke(args=["exportar-empresa", "acme", str(tmp_path / "acme.json")])
    assert r.exit_code == 0
    dados = json.loads((tmp_path / "acme.json").read_text(encoding="utf-8"))
    assert dados["empresa"]["slug"] == "acme"
    assert runner.invoke(args=["exportar-empresa", "nao-existe", str(tmp_path / "x.json")]).exit_code == 1

    r = runner.invoke(args=["importar-empresa", str(tmp_path / "acme.json"), "--slug", "acme-cli"])
    assert r.exit_code == 0 and "importada como 'acme-cli'" in r.output
    # importar de novo na mesma instalação: e-mails já sufixados ganham novo sufixo, sem colisão
    r = runner.invoke(args=["importar-empresa", str(tmp_path / "acme.json"), "--slug", "acme-cli"])
    assert r.exit_code == 0 and "importada como 'acme-cli-2'" in r.output

    assert runner.invoke(args=["expurgar", "--auditoria", "0", "--emails", "0"]).exit_code == 0
    r = runner.invoke(args=["auditoria-verificar"])
    assert r.exit_code == 0 and "íntegra" in r.output
    assert runner.invoke(args=["enviar-reavaliacoes"]).exit_code == 0
    assert runner.invoke(args=["prazos"]).exit_code == 0
    assert "Tabelas criadas" in runner.invoke(args=["init-db"]).output

    # demo-reset recusa banco que não é SQLite (sem --forcar)
    monkeypatch.setitem(app.config, "SQLALCHEMY_DATABASE_URI", "postgresql://x/y")
    r = runner.invoke(args=["demo-reset", "--confirmar"])
    assert r.exit_code == 1 and "não é SQLite" in r.output
