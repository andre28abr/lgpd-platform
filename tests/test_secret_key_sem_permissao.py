"""A geração da chave secreta não pode derrubar o boot quando instance/ não é gravável
(ex.: volume Docker montado como root)."""
import os
import stat

import pytest

from app import _carregar_ou_gerar_secret_key


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignora permissões de diretório")
def test_chave_temporaria_quando_instance_nao_e_gravavel(tmp_path):
    pasta = tmp_path / "instance"
    pasta.mkdir()
    pasta.chmod(stat.S_IRUSR | stat.S_IXUSR)  # leitura, sem escrita
    try:
        chave = _carregar_ou_gerar_secret_key(str(pasta))
        assert len(chave) == 64
        assert not (pasta / "secret_key").exists()  # não conseguiu persistir, mas não quebrou
    finally:
        pasta.chmod(stat.S_IRWXU)
