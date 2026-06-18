"""Utilidades pequenas, sem dependências da aplicação."""
from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Agora em UTC, porém *naive* (sem tzinfo).

    Mantém a compatibilidade com o restante do código (que compara datetimes
    naive) e com o armazenamento em SQLite/Postgres, sem o DeprecationWarning
    de ``datetime.utcnow()`` (Python 3.12+).
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
