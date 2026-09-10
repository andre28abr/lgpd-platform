"""Indicadores de privacidade do Encarregado (Pilar 2), calculados em poucas consultas."""
from collections import Counter

import models


def kpis_empresa(empresa_id):
    pedidos = models.PedidoTitular.query.filter_by(empresa_id=empresa_id).all()
    fechados = [p for p in pedidos if p.status in ("concluido", "recusado")]
    no_prazo = [p for p in fechados if p.concluido_em and p.prazo and p.concluido_em <= p.prazo]
    abertos = [p for p in pedidos if p.status not in ("concluido", "recusado")]

    incidentes = models.Incidente.query.filter_by(empresa_id=empresa_id).all()
    ripds = models.Ripd.query.filter_by(empresa_id=empresa_id).all()
    ropas = models.RopaRegistro.query.filter_by(empresa_id=empresa_id).all()

    por_base = Counter(r.base_legal_label for r in ropas)
    total_ropa = len(ropas)
    bases = [{"label": label, "n": n, "pct": round(n / total_ropa * 100) if total_ropa else 0}
             for label, n in por_base.most_common()]

    return {
        "pedidos": {
            "total": len(pedidos), "abertos": len(abertos),
            "atrasados": sum(1 for p in abertos if p.atrasado),
            "pct_no_prazo": round(len(no_prazo) / len(fechados) * 100) if fechados else None,
        },
        "incidentes": {
            "total": len(incidentes),
            "abertos": sum(1 for i in incidentes if i.status != "encerrado"),
            "sem_anpd": sum(1 for i in incidentes if i.status != "encerrado" and not i.comunicado_anpd),
        },
        "ripd": {"total": len(ripds), "rascunho": sum(1 for r in ripds if r.status == "rascunho")},
        "ropa": {"total": total_ropa, "por_base": bases,
                 "sem_base": sum(1 for r in ropas if not r.base_legal)},
    }
