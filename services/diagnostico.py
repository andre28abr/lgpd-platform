"""Cálculo do diagnóstico de maturidade em privacidade.

Cada pergunta é respondida numa escala 0 (não atende) / 1 (parcial) / 2 (atende).
O score é o percentual de pontos obtidos sobre o máximo possível, ponderado pelo
peso de cada pergunta — global e por dimensão. O plano de ação destaca as
dimensões abaixo de 70%.
"""
import models

NIVEIS = [(0, "Inicial"), (40, "Em desenvolvimento"), (70, "Gerenciado"), (90, "Otimizado")]

TIPS = {
    "GOVERNANCA": ("Formalize a política de privacidade, indique o Encarregado (Art. 41) "
                   "e mantenha treinamento periódico."),
    "BASES_LEGAIS": ("Defina a base legal e a finalidade de cada tratamento (Art. 7º e 11) "
                     "e monte o registro de operações — ROPA (Art. 37)."),
    "SEGURANCA": "Aplique menor privilégio de acesso, criptografia e cláusulas de proteção com operadores (Art. 46).",
    "DIREITOS": "Crie um canal para atender pedidos do titular (Art. 18), com verificação de identidade e prazos.",
    "INCIDENTES": "Tenha um plano de resposta a incidentes com comunicação à ANPD e aos titulares (Art. 48).",
}


def nivel_de(score: float) -> str:
    nome = "Inicial"
    for limite, label in NIVEIS:
        if score >= limite:
            nome = label
    return nome


def computar(diagnostico):
    """Retorna (score, nivel, linhas_por_dimensao, plano_de_acao)."""
    perguntas = {p.id: p for p in models.DiagnosticoPergunta.query.all()}
    dims, obtido_total, max_total = {}, 0, 0

    for r in diagnostico.respostas:
        p = perguntas.get(r.pergunta_id)
        if not p:
            continue
        obtido_total += r.valor * p.peso
        max_total += 2 * p.peso
        d = dims.setdefault(p.dimensao, [0, 0])
        d[0] += r.valor * p.peso
        d[1] += 2 * p.peso

    score = round(obtido_total / max_total * 100, 1) if max_total else 0.0
    linhas = [
        {"dimensao": code, "label": models.label_dimensao(code),
         "pct": round(o / m * 100) if m else 0}
        for code, (o, m) in dims.items()
    ]
    linhas.sort(key=lambda x: x["pct"])
    plano = [{"label": x["label"], "tip": TIPS.get(x["dimensao"], "")} for x in linhas if x["pct"] < 70]
    return score, nivel_de(score), linhas, plano
