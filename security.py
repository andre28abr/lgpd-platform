"""Proteções transversais: CSRF por sessão e cabeçalhos de segurança.

Mantém a mesma filosofia do sc-platform (token CSRF por sessão validado em toda
mutação) sem depender de Flask-WTF.
"""
import hmac
import secrets

from flask import abort, current_app, request, session

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_csrf_token() -> str:
    """Token estável por sessão, exposto aos templates via context processor."""
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf() -> None:
    """Valida o token em qualquer requisição que altere estado."""
    if request.method in SAFE_METHODS:
        return
    enviado = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    real = session.get("_csrf_token")
    if not real or not enviado or not hmac.compare_digest(str(real), str(enviado)):
        abort(400, description="Token CSRF inválido ou ausente.")


def validar_senha(senha: str):
    """Política mínima de senha. Retorna mensagem de erro ou None se ok."""
    senha = senha or ""
    if len(senha) < 8:
        return "A senha deve ter ao menos 8 caracteres."
    if senha.isdigit():
        return "A senha não pode conter apenas números."
    return None


def apply_security_headers(response):
    """Cabeçalhos defensivos básicos aplicados a toda resposta."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
    )
    # HSTS só faz sentido (e só é honrado) atrás de HTTPS; SESSION_COOKIE_SECURE
    # é o sinal do operador de que o site está servido com TLS.
    if current_app.config.get("SESSION_COOKIE_SECURE"):
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response
