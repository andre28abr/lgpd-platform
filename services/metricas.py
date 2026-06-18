"""Métricas de conformidade: progresso individual, por setor e ranking da empresa.

Regra de "em dia": o colaborador tem certificado válido (não vencido) para a área
do seu setor. A média do setor usa a nota da última prova concluída de cada um.
"""
import models


def ultima_prova(usuario_id):
    return (
        models.Prova.query.filter_by(usuario_id=usuario_id, status="concluida")
        .order_by(models.Prova.finalizado_em.desc())
        .first()
    )


def certificado_vigente(usuario_id, area=None):
    query = models.Certificado.query.filter_by(usuario_id=usuario_id)
    if area:
        query = query.filter_by(area=area)
    cert = query.order_by(models.Certificado.emitido_em.desc()).first()
    return cert if (cert and cert.valido) else None


def resumo_setor(setor):
    colaboradores = [
        u for u in setor.usuarios if u.ativo and u.papel == models.PAPEL_COLABORADOR
    ]
    notas, em_dia = [], 0
    for u in colaboradores:
        prova = ultima_prova(u.id)
        if prova and prova.nota is not None:
            notas.append(prova.nota)
        if certificado_vigente(u.id, setor.area):
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


def ranking_empresa(empresa_id):
    setores = models.Setor.query.filter_by(empresa_id=empresa_id).all()
    linhas = [resumo_setor(s) for s in setores]
    linhas.sort(key=lambda r: (r["pct_em_dia"], r["media"] or 0), reverse=True)
    for posicao, linha in enumerate(linhas, start=1):
        linha["posicao"] = posicao
    return linhas


def resumo_empresa(empresa_id):
    ranking = ranking_empresa(empresa_id)
    n_colab = sum(r["n"] for r in ranking)
    em_dia = sum(r["em_dia"] for r in ranking)
    return {
        "setores": len(ranking),
        "colaboradores": n_colab,
        "em_dia": em_dia,
        "pct_conformidade": round(em_dia / n_colab * 100) if n_colab else 0,
        "ranking": ranking,
    }


def pendencias_empresa(empresa_id):
    """Lista colaboradores por situação de certificação (vencido / vencendo / em dia)."""
    usuarios = (
        models.Usuario.query
        .filter_by(empresa_id=empresa_id, ativo=True, papel=models.PAPEL_COLABORADOR)
        .order_by(models.Usuario.nome).all()
    )
    linhas = []
    for u in usuarios:
        area = u.setor.area if u.setor else None
        cert = certificado_vigente(u.id, area)
        ultimo = (
            models.Certificado.query.filter_by(usuario_id=u.id)
            .order_by(models.Certificado.emitido_em.desc()).first()
        )
        if cert:
            dias = cert.dias_para_vencer
            status, valido_ate = ("vencendo" if dias <= 30 else "em_dia"), cert.valido_ate
        elif ultimo:
            status, valido_ate, dias = "vencido", ultimo.valido_ate, None
        else:
            status, valido_ate, dias = "sem_certificado", None, None
        linhas.append({"usuario": u, "setor": u.setor, "status": status,
                       "valido_ate": valido_ate, "dias": dias})

    ordem = {"vencido": 0, "sem_certificado": 1, "vencendo": 2, "em_dia": 3}
    linhas.sort(key=lambda r: (ordem.get(r["status"], 9), r["usuario"].nome))
    return linhas
