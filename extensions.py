"""Instâncias das extensões Flask, isoladas para evitar import circular."""
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Em memória por padrão (processo único). Para múltiplos workers/instâncias,
# defina RATELIMIT_STORAGE_URI=redis://host:6379 — aí o limite passa a ser
# compartilhado entre os processos.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)
