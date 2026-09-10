"""Exportar e importar uma empresa inteira em JSON (portabilidade/backup do tenant).

Exporta tudo que é da empresa — sem segredos (hash de senha, TOTP, códigos de
recuperação ficam de fora). A importação recria a empresa noutra instalação:
usuários recebem senha aleatória (redefinem pelo link) e e-mails já existentes
ganham um sufixo, porque o e-mail é único na plataforma.
"""
import secrets
from datetime import datetime

from werkzeug.security import generate_password_hash

import models
from extensions import db
from utils import agora_utc

VERSAO = 1


def _dt(valor):
    return valor.isoformat() if isinstance(valor, datetime) else None


def _ler_dt(valor):
    return datetime.fromisoformat(valor) if valor else None


def exportar_empresa(empresa) -> dict:
    eid = empresa.id
    q = lambda modelo: modelo.query.filter_by(empresa_id=eid).order_by(modelo.id).all()  # noqa: E731

    return {
        "versao": VERSAO,
        "exportado_em": _dt(agora_utc()),
        "empresa": {"nome": empresa.nome, "slug": empresa.slug, "mfa_obrigatorio": empresa.mfa_obrigatorio,
                    "email_remetente": empresa.email_remetente},
        "setores": [{"id": s.id, "nome": s.nome, "slug": s.slug, "area": s.area, "descricao": s.descricao}
                    for s in q(models.Setor)],
        "usuarios": [{"id": u.id, "nome": u.nome, "email": u.email, "papel": u.papel, "setor_id": u.setor_id,
                      "ativo": u.ativo, "criado_em": _dt(u.criado_em), "anonimizado_em": _dt(u.anonimizado_em)}
                     for u in q(models.Usuario)],
        "trilhas": [{"area": t.area, "titulo": t.titulo, "slug": t.slug, "resumo": t.resumo,
                     "conteudo_md": t.conteudo_md, "ordem": t.ordem, "publicada": t.publicada}
                    for t in q(models.Trilha)],
        "questoes": [{"area": qu.area, "enunciado": qu.enunciado, "artigo": qu.artigo, "explicacao": qu.explicacao,
                      "dificuldade": qu.dificuldade, "ativo": qu.ativo,
                      "alternativas": [{"texto": a.texto, "correta": a.correta, "ordem": a.ordem}
                                       for a in qu.alternativas]}
                     for qu in q(models.Questao)],
        "provas": [{"usuario_id": p.usuario_id, "setor_id": p.setor_id, "area": p.area, "nota_corte": p.nota_corte,
                    "nota": p.nota, "aprovado": p.aprovado, "status": p.status, "criado_em": _dt(p.criado_em),
                    "finalizado_em": _dt(p.finalizado_em),
                    "certificado": ({"codigo": p.certificado.codigo, "nota": p.certificado.nota,
                                     "emitido_em": _dt(p.certificado.emitido_em),
                                     "valido_ate": _dt(p.certificado.valido_ate)} if p.certificado else None)}
                   for p in q(models.Prova)],
        "ropa": [{"id": r.id, "setor_id": r.setor_id, "atividade": r.atividade, "titulares": r.titulares,
                  "categorias_dados": r.categorias_dados, "finalidade": r.finalidade, "base_legal": r.base_legal,
                  "retencao": r.retencao, "compartilhamento": r.compartilhamento}
                 for r in q(models.RopaRegistro)],
        "ripd": [{"ropa_id": r.ropa_id, "titulo": r.titulo, "descricao_tratamento": r.descricao_tratamento,
                  "probabilidade": r.probabilidade, "impacto": r.impacto, "medidas": r.medidas,
                  "risco_residual": r.risco_residual, "conclusao": r.conclusao, "status": r.status}
                 for r in q(models.Ripd)],
        "pedidos": [{"nome_titular": p.nome_titular, "contato": p.contato, "tipo": p.tipo, "descricao": p.descricao,
                     "status": p.status, "responsavel_id": p.responsavel_id, "criado_em": _dt(p.criado_em),
                     "prazo": _dt(p.prazo), "concluido_em": _dt(p.concluido_em), "observacoes": p.observacoes,
                     "protocolo": p.protocolo, "origem": p.origem}
                    for p in q(models.PedidoTitular)],
        "incidentes": [{"titulo": i.titulo, "ocorrido_em": _dt(i.ocorrido_em), "descricao": i.descricao,
                        "dados_afetados": i.dados_afetados, "num_titulares": i.num_titulares, "risco": i.risco,
                        "comunicado_anpd": i.comunicado_anpd, "comunicado_anpd_em": _dt(i.comunicado_anpd_em),
                        "comunicado_titulares": i.comunicado_titulares,
                        "comunicado_titulares_em": _dt(i.comunicado_titulares_em), "medidas": i.medidas,
                        "status": i.status, "criado_em": _dt(i.criado_em)}
                       for i in q(models.Incidente)],
        "diagnosticos": [{"usuario_id": d.usuario_id, "setor_id": d.setor_id, "criado_em": _dt(d.criado_em),
                          "finalizado_em": _dt(d.finalizado_em), "score": d.score, "nivel": d.nivel,
                          "status": d.status,
                          "respostas": [{"pergunta": r.pergunta.texto, "valor": r.valor} for r in d.respostas]}
                         for d in q(models.Diagnostico)],
    }


def _slug_livre(base):
    slug, n = base, 2
    while models.Empresa.query.filter_by(slug=slug).first():
        slug, n = f"{base}-{n}", n + 1
    return slug


def _email_livre(email, antigo_id):
    if not models.Usuario.query.filter_by(email=email).first():
        return email
    local, _, dominio = email.partition("@")
    return f"{local}+imp{antigo_id}@{dominio}"


def importar_empresa(dados: dict, slug: str | None = None):
    """Cria uma NOVA empresa a partir do JSON. Retorna (empresa, avisos)."""
    if dados.get("versao") != VERSAO:
        raise ValueError(f"Versão do arquivo não suportada: {dados.get('versao')}")
    avisos = []
    e = dados["empresa"]
    empresa = models.Empresa(nome=e["nome"], slug=_slug_livre(slug or e["slug"]),
                             mfa_obrigatorio=bool(e.get("mfa_obrigatorio")),
                             email_remetente=e.get("email_remetente"))
    db.session.add(empresa)
    db.session.flush()

    setores = {}
    for s in dados.get("setores", []):
        novo = models.Setor(empresa_id=empresa.id, nome=s["nome"], slug=s["slug"], area=s["area"],
                            descricao=s.get("descricao"))
        db.session.add(novo)
        db.session.flush()
        setores[s["id"]] = novo.id

    usuarios = {}
    for u in dados.get("usuarios", []):
        email = _email_livre(u["email"], u["id"])
        if email != u["email"]:
            avisos.append(f"e-mail {u['email']} já existia; importado como {email}")
        novo = models.Usuario(empresa_id=empresa.id, nome=u["nome"], email=email, papel=u["papel"],
                              setor_id=setores.get(u.get("setor_id")), ativo=bool(u.get("ativo", True)),
                              anonimizado_em=_ler_dt(u.get("anonimizado_em")),
                              senha_hash=generate_password_hash(secrets.token_hex(32)))
        db.session.add(novo)
        db.session.flush()
        usuarios[u["id"]] = novo.id
    if dados.get("usuarios"):
        avisos.append("usuários importados com senha aleatória — use 'Esqueci minha senha' para definir uma nova")

    for t in dados.get("trilhas", []):
        db.session.add(models.Trilha(empresa_id=empresa.id, **t))
    for qd in dados.get("questoes", []):
        alternativas = qd.pop("alternativas", [])
        qu = models.Questao(empresa_id=empresa.id, **qd)
        db.session.add(qu)
        db.session.flush()
        for a in alternativas:
            db.session.add(models.Alternativa(questao_id=qu.id, **a))

    for p in dados.get("provas", []):
        cert = p.pop("certificado", None)
        prova = models.Prova(empresa_id=empresa.id, usuario_id=usuarios[p.pop("usuario_id")],
                             setor_id=setores.get(p.pop("setor_id")),
                             criado_em=_ler_dt(p.pop("criado_em")) or agora_utc(),
                             finalizado_em=_ler_dt(p.pop("finalizado_em")), **p)
        db.session.add(prova)
        db.session.flush()
        if cert:
            codigo = cert["codigo"]
            if models.Certificado.query.filter_by(codigo=codigo).first():
                codigo = secrets.token_hex(8)
                avisos.append(f"certificado {cert['codigo']} já existia; novo código {codigo}")
            db.session.add(models.Certificado(
                empresa_id=empresa.id, usuario_id=prova.usuario_id, prova_id=prova.id, setor_id=prova.setor_id,
                area=prova.area, codigo=codigo, nota=cert["nota"],
                emitido_em=_ler_dt(cert.get("emitido_em")) or agora_utc(), valido_ate=_ler_dt(cert["valido_ate"]),
            ))

    ropas = {}
    for r in dados.get("ropa", []):
        antigo = r.pop("id")
        novo = models.RopaRegistro(empresa_id=empresa.id, setor_id=setores.get(r.pop("setor_id")), **r)
        db.session.add(novo)
        db.session.flush()
        ropas[antigo] = novo.id
    for r in dados.get("ripd", []):
        db.session.add(models.Ripd(empresa_id=empresa.id, ropa_id=ropas.get(r.pop("ropa_id")), **r))
    for p in dados.get("pedidos", []):
        db.session.add(models.PedidoTitular(
            empresa_id=empresa.id, responsavel_id=usuarios.get(p.pop("responsavel_id")),
            criado_em=_ler_dt(p.pop("criado_em")) or agora_utc(), prazo=_ler_dt(p.pop("prazo")),
            concluido_em=_ler_dt(p.pop("concluido_em")),
            protocolo=models.PedidoTitular.gerar_protocolo(), origem=p.pop("origem", None) or "interno",
            **{k: v for k, v in p.items() if k != "protocolo"},
        ))
    for i in dados.get("incidentes", []):
        db.session.add(models.Incidente(
            empresa_id=empresa.id, ocorrido_em=_ler_dt(i.pop("ocorrido_em")),
            comunicado_anpd_em=_ler_dt(i.pop("comunicado_anpd_em")),
            comunicado_titulares_em=_ler_dt(i.pop("comunicado_titulares_em")),
            criado_em=_ler_dt(i.pop("criado_em")) or agora_utc(), **i,
        ))

    perguntas = {p.texto: p.id for p in models.DiagnosticoPergunta.query.all()}
    for d in dados.get("diagnosticos", []):
        diag = models.Diagnostico(empresa_id=empresa.id, usuario_id=usuarios[d["usuario_id"]],
                                  setor_id=setores.get(d.get("setor_id")),
                                  criado_em=_ler_dt(d.get("criado_em")) or agora_utc(),
                                  finalizado_em=_ler_dt(d.get("finalizado_em")), score=d.get("score"),
                                  nivel=d.get("nivel"), status=d.get("status", "concluido"))
        db.session.add(diag)
        db.session.flush()
        for r in d.get("respostas", []):
            pid = perguntas.get(r["pergunta"])
            if pid:
                diag.respostas.append(models.DiagnosticoResposta(pergunta_id=pid, valor=r["valor"]))
            else:
                avisos.append(f"pergunta de diagnóstico não encontrada nesta instalação: {r['pergunta'][:60]}")

    db.session.commit()
    return empresa, avisos
