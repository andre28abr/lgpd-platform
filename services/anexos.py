"""Anexos como evidência: validação, armazenamento em disco e escopo por tenant."""
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

import models
from extensions import db

ALVOS = {"ripd": models.Ripd, "incidente": models.Incidente, "pedido": models.PedidoTitular}

# Assinaturas mínimas: a extensão sozinha não prova nada.
_ASSINATURAS = {
    "pdf": (b"%PDF",),
    "png": (b"\x89PNG",),
    "jpg": (b"\xff\xd8",),
    "jpeg": (b"\xff\xd8",),
    "xlsx": (b"PK",),
    "docx": (b"PK",),
}


def pasta(empresa_id: int) -> str:
    base = current_app.config.get("ANEXOS_DIR") or os.path.join(current_app.instance_path, "uploads")
    caminho = os.path.join(base, str(empresa_id))
    os.makedirs(caminho, exist_ok=True)
    return caminho


def alvo_do_tenant(tipo: str, alvo_id: int, empresa_id: int):
    """O registro dono do anexo, se existir e pertencer à empresa; senão None."""
    modelo = ALVOS.get(tipo)
    if not modelo:
        return None
    obj = db.session.get(modelo, alvo_id)
    return obj if obj and obj.empresa_id == empresa_id else None


def listar(tipo: str, alvo_id: int, empresa_id: int):
    return (models.Anexo.query.filter_by(empresa_id=empresa_id, alvo_tipo=tipo, alvo_id=alvo_id)
            .order_by(models.Anexo.criado_em.desc()).all())


def salvar(arquivo, empresa_id: int, tipo: str, alvo_id: int, usuario) -> models.Anexo:
    """Valida e grava. Levanta ValueError com mensagem para o usuário."""
    cfg = current_app.config
    nome = secure_filename(arquivo.filename or "")
    ext = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if not nome or ext not in cfg["ANEXO_EXTENSOES"]:
        raise ValueError("Tipo de arquivo não permitido. Aceitos: "
                         + ", ".join(sorted(cfg["ANEXO_EXTENSOES"])) + ".")
    dados = arquivo.read()
    if not dados:
        raise ValueError("O arquivo está vazio.")
    if len(dados) > cfg["ANEXO_MAX_MB"] * 1024 * 1024:
        raise ValueError(f"O arquivo excede {cfg['ANEXO_MAX_MB']} MB.")
    assinaturas = _ASSINATURAS.get(ext)
    if assinaturas and not any(dados.startswith(a) for a in assinaturas):
        raise ValueError("O conteúdo do arquivo não corresponde à extensão informada.")

    nome_arquivo = f"{uuid.uuid4().hex}.{ext}"
    destino = os.path.join(pasta(empresa_id), nome_arquivo)
    with open(destino, "wb") as f:
        f.write(dados)
    try:
        os.chmod(destino, 0o600)
    except OSError:
        pass

    anexo = models.Anexo(
        empresa_id=empresa_id, alvo_tipo=tipo, alvo_id=alvo_id, nome_original=nome[:255],
        nome_arquivo=nome_arquivo, mime=arquivo.mimetype, tamanho=len(dados),
        enviado_por_id=getattr(usuario, "id", None),
    )
    db.session.add(anexo)
    return anexo


def caminho(anexo: models.Anexo) -> str:
    return os.path.join(pasta(anexo.empresa_id), anexo.nome_arquivo)


def excluir(anexo: models.Anexo) -> None:
    try:
        os.remove(caminho(anexo))
    except FileNotFoundError:
        pass
    db.session.delete(anexo)
