"""Prazos vivos: o que o Encarregado precisa olhar agora.

- Pedidos do titular atrasados ou vencendo (prazo interno de 15 dias).
- Incidentes abertos ainda não comunicados à ANPD, com a contagem de DIAS ÚTEIS
  desde a ciência — a Resolução CD/ANPD nº 15/2024 fixa 3 dias úteis para a
  comunicação de incidente que possa acarretar risco ou dano relevante.
- RIPDs em rascunho.
"""
from datetime import timedelta

import models
from services.email import enviar
from utils import agora_utc

PRAZO_ANPD_DIAS_UTEIS = 3   # Resolução CD/ANPD nº 15/2024
AVISO_PEDIDO_DIAS = 3       # pedidos vencendo em até N dias entram no alerta


def dias_uteis_desde(inicio, fim=None) -> int:
    """Dias úteis (seg–sex) decorridos entre ``inicio`` e ``fim`` (padrão: agora).
    Não considera feriados — é um indicador, não um cálculo jurídico."""
    fim = fim or agora_utc()
    if not inicio or fim <= inicio:
        return 0
    primeiro, ultimo = inicio.date() + timedelta(days=1), fim.date()
    if ultimo < primeiro:
        return 0
    # O(1): semanas inteiras valem 5 dias úteis; só o resto é percorrido dia a dia.
    semanas, resto = divmod((ultimo - primeiro).days + 1, 7)
    total = semanas * 5
    dia = primeiro + timedelta(days=semanas * 7)
    for _ in range(resto):
        if dia.weekday() < 5:
            total += 1
        dia += timedelta(days=1)
    return total


def alertas_empresa(empresa_id):
    agora = agora_utc()
    abertos = models.PedidoTitular.query.filter(
        models.PedidoTitular.empresa_id == empresa_id,
        models.PedidoTitular.status.in_(("recebido", "em_andamento")),
    ).all()
    atrasados = [p for p in abertos if p.atrasado]
    vencendo = [p for p in abertos if not p.atrasado and p.prazo
                and (p.prazo - agora) <= timedelta(days=AVISO_PEDIDO_DIAS)]

    incidentes = []
    for inc in models.Incidente.query.filter(
        models.Incidente.empresa_id == empresa_id, models.Incidente.status != "encerrado",
        models.Incidente.comunicado_anpd.is_(False),
    ).all():
        dias = dias_uteis_desde(inc.ocorrido_em or inc.criado_em)
        incidentes.append({
            "incidente": inc, "dias_uteis": dias,
            # Risco alto = comunicação exigível; estourado = passou dos 3 dias úteis.
            "exigivel": inc.risco == "alto",
            "estourado": inc.risco == "alto" and dias > PRAZO_ANPD_DIAS_UTEIS,
        })

    ripd_rascunho = models.Ripd.query.filter_by(empresa_id=empresa_id, status="rascunho").count()
    return {
        "pedidos_atrasados": atrasados,
        "pedidos_vencendo": vencendo,
        "incidentes_sem_anpd": incidentes,
        "ripd_rascunho": ripd_rascunho,
        "total": len(atrasados) + len(vencendo) + len(incidentes) + (1 if ripd_rascunho else 0),
    }


def notificar_prazos(empresa) -> tuple[int, int]:
    """Envia aos Encarregados um resumo dos alertas. Retorna (enviados, alertas)."""
    a = alertas_empresa(empresa.id)
    if not a["total"]:
        return 0, 0
    linhas = [f"Alertas de prazo — {empresa.nome}", ""]
    for p in a["pedidos_atrasados"]:
        linhas.append(f"- ATRASADO: pedido {p.protocolo or p.id} ({p.tipo_label}) venceu em {p.prazo:%d/%m/%Y}.")
    for p in a["pedidos_vencendo"]:
        linhas.append(f"- Vencendo: pedido {p.protocolo or p.id} ({p.tipo_label}) até {p.prazo:%d/%m/%Y}.")
    for i in a["incidentes_sem_anpd"]:
        marca = "PRAZO ESTOURADO" if i["estourado"] else ("comunicação exigível" if i["exigivel"] else "avaliar")
        linhas.append(f"- Incidente sem comunicação à ANPD: \"{i['incidente'].titulo}\" — "
                      f"{i['dias_uteis']} dia(s) útil(eis) ({marca}).")
    if a["ripd_rascunho"]:
        linhas.append(f"- {a['ripd_rascunho']} RIPD(s) em rascunho.")
    corpo = "\n".join(linhas)
    enviados = 0
    encarregados = models.Usuario.query.filter_by(
        empresa_id=empresa.id, papel=models.PAPEL_ENCARREGADO, ativo=True).all()
    for u in encarregados:
        if enviar(u.email, "LGPD: alertas de prazo", corpo, remetente=empresa.email_remetente,
                  empresa_id=empresa.id):
            enviados += 1
    return enviados, a["total"]
