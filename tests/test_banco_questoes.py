"""Checklist automático do banco de questões e do sorteio da prova.

A validação JURÍDICA (o enunciado diz o que a fonte diz?) é humana — do Encarregado, com o CSV
de `flask exportar-questoes`. Este arquivo garante a parte que dá para automatizar: forma,
ancoragem, equilíbrio, unicidade, e o comportamento da prova.
"""
import re
from collections import Counter

import models
from conteudo import QUESTOES, TRILHAS
from extensions import db
from routes.provas import _balancear, _sortear_questoes

MINIMO_POR_AREA = {"GERAL": 40}
MINIMO_PADRAO = 30
# Citação de fonte: artigo/inciso da lei, resolução, guia, enunciado ou página oficial da ANPD.
FONTES = re.compile(r"(arts?\. |res\. |resolução|guia|enunciado|página cis)", re.IGNORECASE)


def test_cobertura_de_areas_e_tamanho_do_pool():
    assert set(QUESTOES) == set(models.AREA_CODES)
    for area, itens in QUESTOES.items():
        assert len(itens) >= MINIMO_POR_AREA.get(area, MINIMO_PADRAO), f"{area}: {len(itens)} questões"


def test_forma_de_cada_questao():
    enunciados = Counter()
    for area, itens in QUESTOES.items():
        for enunciado, artigo, explic, dif, alternativas in itens:
            ctx = f"[{area}] {enunciado[:60]}"
            assert enunciado.strip().endswith(("?", ":")), f"{ctx}: enunciado deve terminar com ? ou :"
            assert len(alternativas) == 4, f"{ctx}: 4 alternativas"
            assert sum(1 for _, ok in alternativas if ok) == 1, f"{ctx}: exatamente 1 correta"
            textos = [t for t, _ in alternativas]
            assert len(set(textos)) == 4 and all(t.strip() for t in textos), f"{ctx}: alternativas únicas e não vazias"
            # A fonte vive no campo `artigo` (exibido na correção ao lado da explicação e coluna
            # "fonte" do CSV de revisão). Ela precisa existir e ser específica (artigo, resolução,
            # guia ou enunciado); a explicação precisa ser substantiva.
            assert artigo and FONTES.search(artigo), f"{ctx}: fonte ausente no campo artigo ({artigo!r})"
            assert len(explic) >= 40, f"{ctx}: explicação curta demais"
            assert dif in (1, 2, 3), f"{ctx}: dificuldade inválida"
            enunciados[enunciado] += 1
    duplicados = [e for e, n in enunciados.items() if n > 1]
    assert not duplicados, f"enunciados duplicados: {duplicados}"


def test_cada_area_tem_os_tres_niveis_de_dificuldade():
    for area, itens in QUESTOES.items():
        niveis = {dif for _, _, _, dif, _ in itens}
        assert niveis == {1, 2, 3}, f"{area}: níveis presentes {niveis}"


def test_trilhas_cobrem_todas_as_areas():
    assert {t["area"] for t in TRILHAS} == set(models.AREA_CODES)
    assert len({t["slug"] for t in TRILHAS}) == len(TRILHAS)
    for t in TRILHAS:
        assert "Art." in t["conteudo"], f"trilha {t['slug']} sem referência a artigo"


def test_biblioteca_seedada_reflete_o_banco(app):
    with app.app_context():
        globais = models.Questao.query.filter(models.Questao.empresa_id.is_(None)).count()
        assert globais == sum(len(v) for v in QUESTOES.values())
        assert models.Trilha.query.filter(models.Trilha.empresa_id.is_(None)).count() == len(TRILHAS)


def test_balanceamento_alterna_dificuldades():
    class Q:
        def __init__(self, d):
            self.dificuldade = d
    pool = [Q(1)] * 10 + [Q(2)] * 10 + [Q(3)] * 10
    escolhidas = _balancear(pool, 9)
    assert Counter(q.dificuldade for q in escolhidas) == {1: 3, 2: 3, 3: 3}


def test_sorteio_7_da_area_mais_3_gerais(app):
    with app.app_context():
        questoes, erro = _sortear_questoes(1, "RH", 7, 3)
        assert erro is None and len(questoes) == 10
        areas = Counter(q.area for q in questoes)
        assert areas == {"RH": 7, "GERAL": 3}
        assert len({q.id for q in questoes}) == 10
        assert len({q.dificuldade for q in questoes}) >= 2


def test_pool_insuficiente_recusa_a_prova(app):
    with app.app_context():
        questoes, erro = _sortear_questoes(1, "RH", 50, 3)   # 50 × fator 2 > 30 disponíveis
        assert questoes == [] and "insuficiente" in erro


def test_prova_real_tem_10_questoes_e_limite_diario(login, client, csrf, app):
    login("bruno@acme.com.br")
    ids = []
    for _ in range(app.config["PROVAS_POR_DIA"]):
        r = client.post("/provas/iniciar", data={"csrf_token": csrf()})
        assert r.status_code in (302, 303) and "/provas/" in r.headers["Location"]
        ids.append(int(re.search(r"/provas/(\d+)", r.headers["Location"]).group(1)))
    with app.app_context():
        prova = db.session.get(models.Prova, ids[0])
        assert prova.total_questoes == 10
        assert Counter(i.questao.area for i in prova.itens) == {"RH": 7, "GERAL": 3}

    r = client.post("/provas/iniciar", data={"csrf_token": csrf()}, follow_redirects=True)
    assert "Limite de" in r.get_data(as_text=True)
