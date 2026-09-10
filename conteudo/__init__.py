"""Biblioteca curada: banco de questões e trilhas, chaveados por área.

Regra editorial: toda questão e trilha é ancorada em fonte oficial — o texto compilado da
Lei nº 13.709/2018 no Planalto, as Resoluções do Conselho Diretor da ANPD, os Enunciados e
os Guias Orientativos publicados em gov.br/anpd. O campo ``artigo`` aponta o dispositivo; a
``explicacao`` reproduz o que a fonte diz. Nada é "praxe de mercado" ou opinião. O conteúdo
é revisado pelo Encarregado da empresa antes de entrar em produção.

Formato de cada questão:
    (enunciado, artigo/fonte, explicacao, dificuldade 1–3, [(alternativa, correta?), ...])
"""
from conteudo.questoes_a import QUESTOES_A
from conteudo.questoes_b import QUESTOES_B
from conteudo.trilhas import TRILHAS

QUESTOES = {**QUESTOES_A, **QUESTOES_B}

__all__ = ["QUESTOES", "TRILHAS"]
