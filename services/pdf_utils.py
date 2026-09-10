"""Utilidades compartilhadas pelos PDFs gerados com ReportLab."""
from xml.sax.saxutils import escape


def esc(texto) -> str:
    """Escapa texto livre para uso em ``Paragraph``.

    ``Paragraph`` interpreta uma marcação XML própria: um simples ``<`` digitado
    pelo usuário ("menores < 18 anos") derruba a geração do PDF com ``ValueError``.
    Quebras de linha viram ``<br/>`` para preservar os parágrafos do texto.
    """
    if texto is None:
        return ""
    return escape(str(texto)).replace("\n", "<br/>")


def celula_planilha(valor):
    """Neutraliza injeção de fórmula em células de planilha (=, +, -, @)."""
    if isinstance(valor, str) and valor[:1] in ("=", "+", "-", "@"):
        return "'" + valor
    return valor
