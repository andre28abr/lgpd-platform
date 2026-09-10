"""`flask demo-reset` — roda POR ÚLTIMO (prefixo zz): apaga e recria o banco de teste.

Só faz sentido em SQLite: o comando recusa outros bancos por design (a recusa tem teste
próprio em test_cobertura). No job de PostgreSQL do CI, estes dois são pulados."""
import os

import pytest

import models
from extensions import db

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "sqlite").startswith("sqlite"),
    reason="demo-reset é exclusivo do SQLite",
)


def test_demo_reset_exige_confirmacao(app):
    r = app.test_cli_runner().invoke(args=["demo-reset"])
    assert r.exit_code == 1 and "--confirmar" in r.output


def test_demo_reset_recria_a_demonstracao(app):
    with app.app_context():
        db.session.add(models.Empresa(nome="Lixo", slug="lixo"))
        db.session.commit()
    r = app.test_cli_runner().invoke(args=["demo-reset", "--confirmar"])
    assert r.exit_code == 0, r.output
    with app.app_context():
        assert models.Empresa.query.filter_by(slug="lixo").first() is None
        assert models.Empresa.query.filter_by(slug="acme").first() is not None
        assert models.Usuario.query.filter_by(email="dpo@acme.com.br").first() is not None
