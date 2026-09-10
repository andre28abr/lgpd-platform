"""Configuração dos testes.

Isola o banco em um SQLite temporário e impede que o .env do projeto sobrescreva
essa escolha (LGPD_SKIP_DOTENV). Deve rodar antes de importar a aplicação.
"""
import os
import tempfile

os.environ["LGPD_SKIP_DOTENV"] = "1"
# Padrão: SQLite temporário. O CI define LGPD_TEST_DATABASE_URL para rodar a
# mesma suíte contra um PostgreSQL de verdade.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = os.environ.get("LGPD_TEST_DATABASE_URL") or ("sqlite:///" + _db_path)
# Chave fixa nos testes: evita gravar instance/secret_key do projeto durante a suíte.
os.environ.setdefault("SECRET_KEY", "chave-de-teste-nao-usar-em-producao-0123456789abcdef")
# Anexos em pasta temporária: a suíte não escreve em instance/uploads do projeto.
os.environ["ANEXOS_DIR"] = tempfile.mkdtemp(prefix="lgpd-anexos-")

import pytest  # noqa: E402

import seed as seed_mod  # noqa: E402
from app import app as flask_app  # noqa: E402
from extensions import db, limiter  # noqa: E402


@pytest.fixture(scope="session")
def app():
    flask_app.config["TESTING"] = True
    # O limiter lê RATELIMIT_ENABLED no init_app; desligar pelo atributo é o
    # que de fato vale em runtime e evita 429 entre os testes.
    limiter.enabled = False
    with flask_app.app_context():
        db.create_all()
        seed_mod.executar_seed()
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf(client):
    def _token():
        with client.session_transaction() as s:
            return s.get("_csrf_token")
    return _token


@pytest.fixture()
def login(client, csrf):
    def _login(email, senha="lgpd1234"):
        client.get("/login")
        return client.post(
            "/login", data={"email": email, "senha": senha, "csrf_token": csrf()},
        )
    return _login
