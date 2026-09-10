"""Métricas de conformidade: progresso individual, por setor e ranking da empresa.

Regra de "em dia": o colaborador tem certificado válido (não vencido) para a área
do seu setor. A média do setor usa a nota da última prova concluída de cada um
*naquela área* — uma prova de outra área não entra na média do setor.

As funções de empresa (ranking, resumo, pendências) carregam tudo em um número
constante de consultas (colaboradores, provas e certificados de uma vez) e
cruzam em memória — antes eram 2 consultas por colaborador, o que explodia
no painel e nas exportações conforme a empresa crescia.
"""
from flask import current_app
from sqlalchemy.orm import selectinload

import models


# ── Consultas pontuais (painel do colaborador) ──────────────────────────────
def ultima_prova(usuario_id, area=None):
    query = models.Prova.query.filter_by(usuario_id=usuario_id, status="concluida")
    if area:
        query = query.filter_by(area=area)
    return query.order_by(models.Prova.finalizado_em.desc()).first()


def certificado_vigente(usuario_id, area=None):
    query = models.Certificado.query.filter_by(usuario_id=usuario_id)
    if area:
        query = query.filter_by(area=area)
    cert = query.order_by(models.Certificado.emitido_em.desc()).first()
    return cert if (cert and cert.valido) else None


# ── Carga em lote (uma empresa inteira em 4 consultas) ──────────────────────
class _Dados:
    """Colaboradores ativos da empresa + última prova e último certificado de cada um."""

    def __init__(self, empresa_id):
        self.usuarios = (
            models.Usuario.query.options(selectinload(models.Usuario.setor))
            .filter_by(empresa_id=empresa_id, ativo=True, papel=models.PAPEL_COLABORADOR)
            .order_by(models.Usuario.nome).all()
        )
        ids = [u.id for u in self.usuarios]
        self.prova_por_area = {}   # (usuario_id, area) -> última prova concluída
        self.cert_por_area = {}    # (usuario_id, area) -> último certificado
        self.cert_ultimo = {}      # usuario_id -> último certificado (qualquer área)
        if not ids:
            return
        provas = (
            models.Prova.query
            .filter(models.Prova.usuario_id.in_(ids), models.Prova.status == "concluida")
            .order_by(models.Prova.finalizado_em.desc()).all()
        )
        for p in provas:
            self.prova_por_area.setdefault((p.usuario_id, p.area), p)
        certs = (
            models.Certificado.query.filter(models.Certificado.usuario_id.in_(ids))
            .order_by(models.Certificado.emitido_em.desc()).all()
        )
        for c in certs:
            self.cert_por_area.setdefault((c.usuario_id, c.area), c)
            self.cert_ultimo.setdefault(c.usuario_id, c)

    def vigente(self, usuario_id, area=None):
        cert = self.cert_por_area.get((usuario_id, area)) if area else self.cert_ultimo.get(usuario_id)
        return cert if (cert and cert.valido) else None


def _resumo_setor(setor, colaboradores, dados):
    notas, em_dia = [], 0
    for u in colaboradores:
        prova = dados.prova_por_area.get((u.id, setor.area))
        if prova and prova.nota is not None:
            notas.append(prova.nota)
        if dados.vigente(u.id, setor.area):
            em_dia += 1

    n = len(colaboradores)
    return {
        "setor": setor,
        "n": n,
        "avaliados": len(notas),
        "media": round(sum(notas) / len(notas), 1) if notas else None,
        "em_dia": em_dia,
        "pct_em_dia": round(em_dia / n * 100) if n else 0,
    }


def _ranking(setores, dados):
    por_setor = {}
    for u in dados.usuarios:
        por_setor.setdefault(u.setor_id, []).append(u)
    linhas = [_resumo_setor(s, por_setor.get(s.id, []), dados) for s in setores]
    linhas.sort(key=lambda r: (r["pct_em_dia"], r["media"] or 0), reverse=True)
    for posicao, linha in enumerate(linhas, start=1):
        linha["posicao"] = posicao
    return linhas


# ── API pública ─────────────────────────────────────────────────────────────
def resumo_setor(setor):
    """Resumo de um setor (painel do gestor)."""
    dados = _Dados(setor.empresa_id)
    return _resumo_setor(setor, [u for u in dados.usuarios if u.setor_id == setor.id], dados)


def ranking_empresa(empresa_id):
    setores = models.Setor.query.filter_by(empresa_id=empresa_id).all()
    return _ranking(setores, _Dados(empresa_id))


def resumo_empresa(empresa_id):
    """Visão da empresa. O denominador é TODO colaborador ativo — inclusive quem
    ainda não tem setor, que antes ficava invisível ao percentual de conformidade
    (mas aparecia nas pendências), e os dois números discordavam."""
    dados = _Dados(empresa_id)
    setores = models.Setor.query.filter_by(empresa_id=empresa_id).all()
    ranking = _ranking(setores, dados)
    sem_setor = [u for u in dados.usuarios if u.setor_id is None]
    em_dia = sum(r["em_dia"] for r in ranking) + sum(1 for u in sem_setor if dados.vigente(u.id))
    n_colab = len(dados.usuarios)
    return {
        "setores": len(ranking),
        "colaboradores": n_colab,
        "sem_setor": len(sem_setor),
        "em_dia": em_dia,
        "pct_conformidade": round(em_dia / n_colab * 100) if n_colab else 0,
        "ranking": ranking,
    }


def pendencias_empresa(empresa_id):
    """Lista colaboradores por situação de certificação (vencido / vencendo / em dia)."""
    dados = _Dados(empresa_id)
    dias_aviso = current_app.config.get("REAVALIACAO_DIAS", 30)
    linhas = []
    for u in dados.usuarios:
        area = u.setor.area if u.setor else None
        cert = dados.vigente(u.id, area)
        ultimo = dados.cert_ultimo.get(u.id)
        if cert:
            dias = cert.dias_para_vencer
            status, valido_ate = ("vencendo" if dias <= dias_aviso else "em_dia"), cert.valido_ate
        elif ultimo:
            status, valido_ate, dias = "vencido", ultimo.valido_ate, None
        else:
            status, valido_ate, dias = "sem_certificado", None, None
        linhas.append({"usuario": u, "setor": u.setor, "status": status,
                       "valido_ate": valido_ate, "dias": dias})

    ordem = {"vencido": 0, "sem_certificado": 1, "vencendo": 2, "em_dia": 3}
    linhas.sort(key=lambda r: (ordem.get(r["status"], 9), r["usuario"].nome))
    return linhas
