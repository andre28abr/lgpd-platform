"""Popula a biblioteca curada (trilhas + questões) e as empresas de demonstração.

- A biblioteca (conteúdo em ``conteudo/``) é atualizada de forma **idempotente** a cada
  ``flask seed``: trilhas são reescritas pelo slug e questões novas entram pelo enunciado —
  quem já tem um banco de demonstração recebe as questões novas sem recriar nada.
- As empresas de demonstração só são criadas se ainda não existirem. Para recriar tudo do
  zero: ``flask demo-reset --confirmar``.
"""

import models
from conteudo import QUESTOES, TRILHAS
from extensions import db
from utils import agora_utc

SENHA_DEMO = "lgpd1234"


# ───────────────────── Diagnóstico de maturidade (perguntas) ───────────────
# (dimensao, texto)
DIAG_PERGUNTAS = [
    ("GOVERNANCA", "A empresa tem uma política de privacidade publicada e atualizada."),
    ("GOVERNANCA", "Há um Encarregado (DPO) formalmente indicado (Art. 41)."),
    ("GOVERNANCA", "Os colaboradores recebem treinamento periódico em LGPD."),
    ("BASES_LEGAIS", "Cada tratamento de dados tem uma base legal definida (Art. 7º/11)."),
    ("BASES_LEGAIS", "Existe um registro das operações de tratamento — ROPA (Art. 37)."),
    ("BASES_LEGAIS", "As finalidades de uso dos dados são específicas e informadas aos titulares."),
    ("SEGURANCA", "O acesso a dados pessoais segue o princípio do menor privilégio."),
    ("SEGURANCA", "Dados sensíveis e credenciais são protegidos com criptografia/segregação (Art. 46)."),
    ("SEGURANCA", "Os contratos com operadores/fornecedores têm cláusulas de proteção de dados."),
    ("DIREITOS", "Há um canal para o titular exercer seus direitos (Art. 18)."),
    ("DIREITOS", "A identidade de quem solicita é verificada antes de atender pedidos."),
    ("DIREITOS", "Os pedidos de titulares são registrados e respondidos em prazo razoável."),
    ("INCIDENTES", "Existe um plano de resposta a incidentes de segurança."),
    ("INCIDENTES", "A equipe sabe quando e como comunicar a ANPD e os titulares (Art. 48)."),
    ("INCIDENTES", "Logs e trilhas de auditoria permitem investigar incidentes."),
]


# ─────────────────────────── Empresa de demonstração ───────────────────────
SETORES_DEMO = [
    ("Recursos Humanos", "RH"),
    ("Financeiro", "FINANCEIRO"),
    ("TI e Segurança", "TI"),
    ("Marketing", "MARKETING"),
]

# (nome, email, papel, area_do_setor | None)
USUARIOS_DEMO = [
    ("Marina Prado", "dpo@acme.com.br", models.PAPEL_ENCARREGADO, None),
    ("Carlos Lima", "gestor.rh@acme.com.br", models.PAPEL_GESTOR, "RH"),
    ("Ana Souza", "ana@acme.com.br", models.PAPEL_COLABORADOR, "RH"),
    ("Bruno Dias", "bruno@acme.com.br", models.PAPEL_COLABORADOR, "RH"),
    ("Paula Reis", "paula@acme.com.br", models.PAPEL_COLABORADOR, "FINANCEIRO"),
    ("João Melo", "joao@acme.com.br", models.PAPEL_COLABORADOR, "TI"),
]

# Resultados já lançados para o ranking nascer com dados (email -> (nota, aprovado))
RESULTADOS_DEMO = {
    "ana@acme.com.br": (90.0, True),
    "bruno@acme.com.br": (50.0, False),
    "paula@acme.com.br": (80.0, True),
    "joao@acme.com.br": (100.0, True),
}


def executar_seed():
    novas_trilhas, novas_questoes = atualizar_biblioteca()
    print(f"Biblioteca: {novas_trilhas} trilha(s) e {novas_questoes} questão(ões) adicionadas/atualizadas.")

    if models.Empresa.query.filter_by(slug="acme").first():
        if not models.Empresa.query.filter_by(slug="nova-era").first():
            _seed_segunda_empresa()  # instalações antigas ganham a 2ª empresa (isolamento demonstrável)
            print("Segunda empresa de demonstração (Nova Era Saúde) criada: dpo@novaera.com.br")
        db.session.commit()
        print("Empresa Acme já existe — mantida. Para recriar tudo: flask demo-reset --confirmar")
        return

    _seed_empresa()
    _seed_segunda_empresa()
    db.session.commit()
    print("Seed concluído.")
    print("  Acme (empresa principal): dpo@acme.com.br / gestor.rh@acme.com.br / ana@acme.com.br")
    print("  Nova Era Saúde (segunda empresa, para ver o isolamento): dpo@novaera.com.br")
    print(f"  Senha de todos: {SENHA_DEMO}")


def atualizar_biblioteca() -> tuple[int, int]:
    """Sincroniza a biblioteca global (empresa_id NULL) com ``conteudo/``. Idempotente.

    Trilhas: criadas ou reescritas pelo slug. Questões: adicionadas pelo enunciado;
    as globais que saíram do banco curado são DESATIVADAS (continuam existindo para
    as provas já feitas, mas deixam de ser sorteadas). Perguntas do diagnóstico: só
    na primeira vez. Retorna (trilhas gravadas, questões novas).
    """
    trilhas = 0
    for t in TRILHAS:
        trilha = models.Trilha.query.filter_by(empresa_id=None, slug=t["slug"]).first()
        if trilha is None:
            trilha = models.Trilha(empresa_id=None, slug=t["slug"])
            db.session.add(trilha)
        trilha.area, trilha.titulo, trilha.resumo = t["area"], t["titulo"], t["resumo"]
        trilha.conteudo_md, trilha.ordem, trilha.publicada = t["conteudo"], t["ordem"], True
        trilhas += 1

    existentes = {
        q.enunciado for q in models.Questao.query.with_entities(models.Questao.enunciado)
        .filter(models.Questao.empresa_id.is_(None)).all()
    }
    questoes = 0
    for area, itens in QUESTOES.items():
        for enunciado, artigo, explic, dif, alternativas in itens:
            if enunciado in existentes:
                continue
            q = models.Questao(empresa_id=None, area=area, enunciado=enunciado,
                               artigo=artigo, explicacao=explic, dificuldade=dif, ativo=True)
            db.session.add(q)
            db.session.flush()
            for ordem, (texto, correta) in enumerate(alternativas):
                db.session.add(models.Alternativa(questao_id=q.id, texto=texto, correta=correta, ordem=ordem))
            existentes.add(enunciado)
            questoes += 1

    # Questões globais que não estão mais no banco curado saem do sorteio.
    atuais = {e for itens in QUESTOES.values() for e, *_ in itens}
    desativadas = 0
    for q in models.Questao.query.filter(models.Questao.empresa_id.is_(None), models.Questao.ativo.is_(True)).all():
        if q.enunciado not in atuais:
            q.ativo = False
            desativadas += 1
    if desativadas:
        print(f"Biblioteca: {desativadas} questão(ões) antiga(s) desativada(s) (fora do banco curado atual).")

    if not models.DiagnosticoPergunta.query.first():
        ordem_por_dim = {}
        for dimensao, texto in DIAG_PERGUNTAS:
            ordem = ordem_por_dim.get(dimensao, 0)
            ordem_por_dim[dimensao] = ordem + 1
            db.session.add(models.DiagnosticoPergunta(dimensao=dimensao, texto=texto, peso=1, ordem=ordem, ativo=True))
    db.session.flush()
    return trilhas, questoes


def _seed_empresa():
    empresa = models.Empresa(nome="Acme Indústria e Comércio", slug="acme")
    db.session.add(empresa)
    db.session.flush()

    setores = {}
    for nome, area in SETORES_DEMO:
        s = models.Setor(empresa_id=empresa.id, nome=nome, slug=nome.lower().replace(" ", "-"), area=area)
        db.session.add(s)
        db.session.flush()
        setores[area] = s

    usuarios = {}
    for nome, email, papel, area in USUARIOS_DEMO:
        u = models.Usuario(empresa_id=empresa.id, nome=nome, email=email, papel=papel,
                           setor_id=setores[area].id if area else None)
        u.definir_senha(SENHA_DEMO)
        db.session.add(u)
        db.session.flush()
        usuarios[email] = u

    # Lança provas concluídas + certificados para alimentar o ranking
    import secrets
    from datetime import timedelta
    dias = 365
    feita_em = agora_utc() - timedelta(days=20)  # no passado: não conta no limite diário de tentativas
    for email, (nota, aprovado) in RESULTADOS_DEMO.items():
        u = usuarios[email]
        prova = models.Prova(empresa_id=empresa.id, usuario_id=u.id, setor_id=u.setor_id, area=u.setor.area,
                             nota_corte=70, nota=nota, aprovado=aprovado, status="concluida",
                             criado_em=feita_em, finalizado_em=feita_em)
        db.session.add(prova)
        db.session.flush()
        if aprovado:
            db.session.add(models.Certificado(
                empresa_id=empresa.id, usuario_id=u.id, prova_id=prova.id, setor_id=u.setor_id, area=u.setor.area,
                codigo=secrets.token_hex(8), nota=nota, emitido_em=feita_em,
                valido_ate=feita_em + timedelta(days=dias),
            ))

    _seed_pilar2(empresa, setores, usuarios)
    return empresa


def _seed_pilar2(empresa, setores, usuarios):
    """Dados de exemplo do Pilar 2 — o suficiente para a demo ter o que mostrar:
    ROPA por setor, pedidos em situações diferentes (no prazo, vencendo, atrasado,
    concluído), RIPDs, incidentes e um diagnóstico já concluído."""
    from datetime import timedelta

    agora = agora_utc()
    dpo = usuarios["dpo@acme.com.br"]

    ropas = [
        ("RH", "Folha de pagamento", "Colaboradores", "Nome, CPF, conta bancária, dependentes",
         "Processar a folha e cumprir obrigações trabalhistas", "OBRIGACAO_LEGAL",
         "Durante o vínculo + prazos legais", "Banco, contabilidade e órgãos públicos"),
        ("RH", "Recrutamento e seleção", "Candidatos", "Nome, contato, currículo, histórico profissional",
         "Avaliar candidatos a vagas", "LEGITIMO_INTERESSE",
         "6 meses após o encerramento da vaga", "Plataforma de recrutamento (operador)"),
        ("RH", "Controle de ponto biométrico", "Colaboradores", "Impressão digital (dado sensível), horários",
         "Registro de jornada", "OBRIGACAO_LEGAL", "5 anos", "Fornecedor do relógio de ponto (operador)"),
        ("FINANCEIRO", "Faturamento e cobrança", "Clientes", "Nome, CPF/CNPJ, endereço, dados de pagamento",
         "Emitir notas fiscais e cobrar", "CONTRATO", "5 anos (prazo fiscal)", "Contabilidade, banco, Receita"),
        ("MARKETING", "Newsletter", "Clientes e leads", "Nome, e-mail",
         "Envio de comunicações de marketing", "CONSENTIMENTO",
         "Até a revogação do consentimento", "Plataforma de e-mail marketing (operador)"),
        ("TI", "Logs de acesso aos sistemas", "Colaboradores", "Login, IP, data/hora, ações",
         "Segurança da informação e auditoria", "LEGITIMO_INTERESSE", "12 meses", "Provedor de nuvem (operador)"),
    ]
    for area, atividade, titulares, dados, fim, base, ret, comp in ropas:
        db.session.add(models.RopaRegistro(
            empresa_id=empresa.id, setor_id=setores[area].id, atividade=atividade, titulares=titulares,
            categorias_dados=dados, finalidade=fim, base_legal=base, retencao=ret, compartilhamento=comp,
        ))
    db.session.flush()
    ropa_biometria = models.RopaRegistro.query.filter_by(
        empresa_id=empresa.id, atividade="Controle de ponto biométrico").first()

    pedidos = [
        ("José da Silva", "jose@example.com", "ACESSO", "Solicita cópia dos seus dados pessoais.",
         "recebido", 12, None, None),
        ("Maria Oliveira", "maria@example.com", "ELIMINACAO", "Quer sair da newsletter e apagar o cadastro.",
         "em_andamento", 3, dpo, None),
        ("Carlos Pereira", "carlos@example.com", "CORRECAO", "Endereço cadastrado está desatualizado.",
         "recebido", -4, None, None),  # atrasado: o painel precisa acusar
        ("Fernanda Costa", "fernanda@example.com", "CONFIRMACAO", "Pergunta se a empresa trata seus dados.",
         "concluido", 2, dpo, "Confirmado o tratamento no cadastro de clientes; resposta enviada."),
    ]
    for nome, contato, tipo, desc, status, dias, resp, obs in pedidos:
        db.session.add(models.PedidoTitular(
            empresa_id=empresa.id, nome_titular=nome, contato=contato, tipo=tipo, descricao=desc,
            status=status, prazo=agora + timedelta(days=dias), responsavel_id=resp.id if resp else None,
            observacoes=obs, concluido_em=agora - timedelta(days=1) if status == "concluido" else None,
            criado_em=agora - timedelta(days=15 - dias),
            protocolo=models.PedidoTitular.gerar_protocolo(),
            origem="portal" if nome == "Carlos Pereira" else "interno",
        ))

    db.session.add(models.Ripd(
        empresa_id=empresa.id, ropa_id=ropa_biometria.id if ropa_biometria else None,
        titulo="Controle de ponto por biometria",
        descricao_tratamento="Coleta de digital para registro de jornada dos colaboradores.",
        probabilidade=2, impacto=3, medidas="Acesso restrito, criptografia e retenção mínima.",
        risco_residual="medio", conclusao="Tratamento viável com as medidas adotadas.", status="concluido",
    ))
    db.session.add(models.Ripd(
        empresa_id=empresa.id, titulo="Câmeras de segurança com reconhecimento facial",
        descricao_tratamento="Avaliação preliminar do uso de reconhecimento facial na portaria.",
        probabilidade=3, impacto=3, medidas="", risco_residual=None, conclusao="", status="rascunho",
    ))

    db.session.add(models.Incidente(
        empresa_id=empresa.id, titulo="E-mail enviado a destinatário errado",
        ocorrido_em=agora - timedelta(days=2), descricao="Planilha com dados de clientes enviada por engano.",
        dados_afetados="Nome e e-mail", num_titulares=12, risco="medio",
        comunicado_anpd=False, comunicado_titulares=True, comunicado_titulares_em=agora - timedelta(days=1),
        medidas="Solicitado o descarte ao destinatário e orientada a equipe.", status="em_tratamento",
    ))
    db.session.add(models.Incidente(
        empresa_id=empresa.id, titulo="Notebook de vendedor furtado",
        ocorrido_em=agora - timedelta(days=40), descricao="Equipamento com disco criptografado e senha.",
        dados_afetados="Cadastro de clientes (criptografado)", num_titulares=300, risco="baixo",
        comunicado_anpd=False, comunicado_titulares=False,
        medidas="Bloqueio remoto, troca de credenciais e boletim de ocorrência.", status="encerrado",
    ))

    # Um diagnóstico concluído, para o resultado e o plano de ação já existirem.
    diag = models.Diagnostico(empresa_id=empresa.id, usuario_id=dpo.id, setor_id=None,
                              criado_em=agora - timedelta(days=30), status="em_andamento")
    db.session.add(diag)
    db.session.flush()
    respostas = {"GOVERNANCA": 2, "BASES_LEGAIS": 1, "SEGURANCA": 1, "DIREITOS": 2, "INCIDENTES": 0}
    for p in models.DiagnosticoPergunta.query.all():
        diag.respostas.append(models.DiagnosticoResposta(pergunta_id=p.id, valor=respostas.get(p.dimensao, 1)))
    from services.diagnostico import computar
    diag.score, diag.nivel, _, _ = computar(diag)
    diag.status, diag.finalizado_em = "concluido", agora - timedelta(days=30)


def _seed_segunda_empresa():
    """Segunda empresa, com dados próprios: serve para mostrar o isolamento multi-tenant
    ao vivo — entre como dpo@novaera.com.br e nada da Acme aparece."""
    empresa = models.Empresa(nome="Nova Era Saúde", slug="nova-era")
    db.session.add(empresa)
    db.session.flush()
    setor = models.Setor(empresa_id=empresa.id, nome="Atendimento", slug="atendimento", area="ATENDIMENTO")
    db.session.add(setor)
    db.session.flush()
    for nome, email, papel, setor_id in (
        ("Helena Martins", "dpo@novaera.com.br", models.PAPEL_ENCARREGADO, None),
        ("Rafael Nunes", "rafael@novaera.com.br", models.PAPEL_COLABORADOR, setor.id),
    ):
        u = models.Usuario(empresa_id=empresa.id, nome=nome, email=email, papel=papel, setor_id=setor_id)
        u.definir_senha(SENHA_DEMO)
        db.session.add(u)
    db.session.add(models.RopaRegistro(
        empresa_id=empresa.id, setor_id=setor.id, atividade="Agendamento de consultas",
        titulares="Pacientes", categorias_dados="Nome, telefone, convênio, especialidade procurada",
        finalidade="Marcar e confirmar consultas", base_legal="TUTELA_SAUDE",
        retencao="20 anos (prontuário)", compartilhamento="Operadora do plano de saúde",
    ))
    return empresa
