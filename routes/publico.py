"""Páginas públicas (sem login)."""
from flask import Blueprint, render_template

bp = Blueprint("publico", __name__)


@bp.route("/politica-de-privacidade")
def politica():
    return render_template("publico/politica.html")
