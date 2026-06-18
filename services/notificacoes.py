"""Notificações por e-mail: reavaliações, pedidos de titular e incidentes."""
import models
from extensions import db
from services.auditoria import registrar
from services.email import enviar
from services.metricas import pendencias_empresa

_PENDENTES = {"vencido", "sem_certificado", "vencendo"}


def notificar_reavaliacoes(empresa) -> tuple[int, int]:
    """Notifica colaboradores com certificação pendente. Retorna (notificados, total)."""
    pendentes = [l for l in pendencias_empresa(empresa.id) if l["status"] in _PENDENTES]
    for linha in pendentes:
        usuario = linha["usuario"]
        rotulo = linha["status"].replace("_", " ")
        corpo = (
            f"Olá, {usuario.nome}.\n\n"
            f"Sua certificação de LGPD está com status: {rotulo}.\n"
            f"Acesse a plataforma para refazer a avaliação e manter sua conformidade em dia.\n\n"
            f"Empresa: {empresa.nome}"
        )
        enviar(usuario.email, "LGPD: sua certificação precisa de atenção", corpo)

    registrar("reavaliacoes_notificadas", f"{len(pendentes)} colaborador(es)", empresa_id=empresa.id)
    db.session.commit()
    return len(pendentes), len(pendentes)


def _encarregados_emails(empresa_id):
    encarregados = models.Usuario.query.filter_by(
        empresa_id=empresa_id, papel=models.PAPEL_ENCARREGADO, ativo=True).all()
    return [u.email for u in encarregados]


def notificar_novo_pedido(pedido, empresa):
    prazo = pedido.prazo.strftime("%d/%m/%Y") if pedido.prazo else "—"
    corpo = (f"Novo pedido de titular: {pedido.tipo_label}.\n"
             f"Titular: {pedido.nome_titular}. Prazo de atendimento: {prazo}.")
    for email in _encarregados_emails(empresa.id):
        enviar(email, "LGPD: novo pedido de titular", corpo)


def notificar_pedido_concluido(pedido):
    if pedido.contato and "@" in pedido.contato:
        enviar(pedido.contato, "LGPD: seu pedido foi atendido",
               f"Olá, {pedido.nome_titular}. Seu pedido ({pedido.tipo_label}) foi concluído.")


def notificar_novo_incidente(incidente, empresa):
    corpo = (f"Incidente registrado: {incidente.titulo}.\n"
             f"Risco: {incidente.risco_label}. Avalie a comunicação à ANPD e aos titulares (Art. 48).")
    for email in _encarregados_emails(empresa.id):
        enviar(email, "LGPD: novo incidente de segurança", corpo)
