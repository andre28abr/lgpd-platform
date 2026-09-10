"""Páginas públicas (sem login) e healthcheck."""
from flask import Blueprint, jsonify, render_template
from sqlalchemy import text

from extensions import db

bp = Blueprint("publico", __name__)


@bp.route("/politica-de-privacidade")
def politica():
    return render_template("publico/politica.html")


@bp.route("/saude")
def saude():
    """Healthcheck para Docker/orquestrador: 200 só se a app E o banco respondem."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — qualquer falha de banco é "indisponível"
        return jsonify(status="erro", banco="indisponivel"), 503
    return jsonify(status="ok")
