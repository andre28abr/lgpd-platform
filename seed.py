"""Popula a biblioteca curada (trilhas + questões) e uma empresa de demonstração.

Idempotente: se a empresa de demonstração já existir, não faz nada. Para
recriar do zero, apague o banco (instance/lgpd.db) e rode `flask seed` de novo.

O conteúdo é ancorado na Lei nº 13.709/2018 (LGPD). As questões trazem o artigo
de referência e uma explicação, exibidos na correção da prova.
"""

import models
from extensions import db
from utils import agora_utc

SENHA_DEMO = "lgpd1234"


# ─────────────────────────── Trilhas (Markdown) ───────────────────────────
TRILHAS = [
    {
        "area": "GERAL", "ordem": 1,
        "titulo": "Fundamentos da LGPD",
        "slug": "fundamentos-lgpd",
        "resumo": "Conceitos essenciais: dado pessoal, bases legais, princípios e papéis.",
        "conteudo": """# Fundamentos da LGPD

A **Lei Geral de Proteção de Dados** (Lei nº 13.709/2018) regula o tratamento de
dados pessoais por pessoas físicas e jurídicas, com o objetivo de proteger a
liberdade, a privacidade e o livre desenvolvimento da personalidade.

## Conceitos centrais
- **Dado pessoal**: informação relacionada a pessoa natural identificada ou
  identificável (Art. 5º, I).
- **Dado pessoal sensível**: origem racial/étnica, convicção religiosa, opinião
  política, saúde, vida sexual, dado genético ou biométrico (Art. 5º, II).
- **Titular**: a pessoa a quem os dados se referem.
- **Controlador**: quem toma as decisões sobre o tratamento.
- **Operador**: quem trata dados em nome do controlador.

## As bases legais (Art. 7º)
O consentimento é a mais conhecida, mas é **apenas uma** entre dez hipóteses.
Outras muito usadas nas empresas:
- cumprimento de obrigação legal ou regulatória;
- execução de contrato;
- legítimo interesse do controlador.

## Princípios (Art. 6º)
Finalidade, adequação, **necessidade** (minimização), livre acesso, qualidade,
transparência, segurança, prevenção, não discriminação e **responsabilização
(accountability)**.

## Quem fiscaliza
A **ANPD** (Autoridade Nacional de Proteção de Dados) edita normas, fiscaliza e
aplica sanções (Art. 52), que vão de advertência a multa de até 2% do
faturamento, limitada a R$ 50 milhões por infração.
""",
    },
    {
        "area": "RH", "ordem": 1,
        "titulo": "LGPD no RH",
        "slug": "lgpd-no-rh",
        "resumo": "Dados sensíveis de saúde e biometria, retenção e bases legais no RH.",
        "conteudo": """# LGPD no RH

O RH é um dos setores que mais tratam **dados sensíveis**: atestados e exames
(saúde), biometria (ponto), filiação sindical, além de dados de dependentes —
inclusive **menores** (Art. 14).

## Bases legais típicas
- Folha, admissão e obrigações trabalhistas: **obrigação legal/regulatória**
  (Art. 7º, II).
- Execução do contrato de trabalho (Art. 7º, V).

## Pontos de atenção
- **Biometria** é dado sensível (Art. 11): use só quando necessário e com
  segurança reforçada.
- **Currículos** de candidatos não contratados precisam de prazo de retenção;
  elimine quando não houver mais finalidade (Art. 15 e 16).
- **Compartilhar** dados com plano de saúde exige finalidade específica e
  informação ao titular.
- Monitoramento de e-mail/jornada exige **transparência** e política clara.
""",
    },
    {
        "area": "FINANCEIRO", "ordem": 1,
        "titulo": "LGPD no Financeiro",
        "slug": "lgpd-no-financeiro",
        "resumo": "Retenção fiscal, bureaus de crédito, prevenção à fraude e segurança.",
        "conteudo": """# LGPD no Financeiro

## Retenção por obrigação legal
Documentos fiscais e contábeis com dados pessoais devem ser mantidos pelos
prazos legais — base de **obrigação legal** (Art. 7º, II; Art. 16, I). Depois do
prazo, elimine.

## Bureaus e prevenção à fraude
- Consulta a bureaus de crédito e análise de risco costumam apoiar-se em
  **legítimo interesse** (Art. 7º, IX e Art. 10) ou obrigação, conforme o caso —
  sempre com transparência.
- **Open Finance**: o compartilhamento depende de **consentimento** do titular.

## Segurança é regra (Art. 46)
Planilhas com dados de clientes trafegando sem proteção são incidente em
potencial. Nunca exponha débitos a terceiros — fere finalidade e privacidade.
""",
    },
    {
        "area": "TI", "ordem": 1,
        "titulo": "LGPD em TI e Segurança",
        "slug": "lgpd-ti-seguranca",
        "resumo": "Medidas de segurança, operadores de nuvem, logs e resposta a incidente.",
        "conteudo": """# LGPD em TI e Segurança da Informação

## Medidas de segurança (Art. 46)
A lei exige medidas **técnicas e administrativas** aptas a proteger os dados.
Boas práticas: criptografia, **menor privilégio** de acesso, segregação de
ambientes e proteção de backups.

## Operador e nuvem
O provedor que trata dados **em nome** da empresa é **operador** (Art. 5º, VII) e
responde solidariamente se descumprir a lei ou as instruções (Art. 42).

## Incidentes (Art. 48)
Incidente que possa acarretar risco relevante deve ser comunicado à **ANPD** e
aos **titulares** em prazo razoável. **Logs** são essenciais para rastrear e
responder.
""",
    },
    {
        "area": "MARKETING", "ordem": 1,
        "titulo": "LGPD em Marketing e Vendas",
        "slug": "lgpd-marketing-vendas",
        "resumo": "Consentimento, cookies, opt-out, perfis e decisão automatizada.",
        "conteudo": """# LGPD em Marketing e Vendas

## Consentimento de verdade
Consentimento precisa ser **livre, informado e inequívoco** (Art. 5º, XII).
Base comprada de e-mails, sem base legal, é problema na certa.

## Cookies e transparência
Cookies não essenciais exigem informação e, em regra, **consentimento**. O
titular pode **revogar** a qualquer momento (Art. 8º, §5º) e pedir **opt-out**.

## Perfis e decisão automatizada
Decisões tomadas só por tratamento automatizado podem ser **revisadas** a pedido
do titular (Art. 20). Enriquecer base com dados de terceiros exige avaliar base
legal e transparência.
""",
    },
]


# ─────────────────────────── Banco de questões ───────────────────────────
# Formato: (enunciado, artigo, explicacao, dificuldade, [(alt, correta?), ...])
QUESTOES = {
    "GERAL": [
        ("O que é um dado pessoal segundo a LGPD?", "Art. 5º, I",
         "Dado pessoal é informação relacionada a pessoa natural identificada ou identificável.", 1,
         [("Informação sobre pessoa natural identificada ou identificável", True),
          ("Apenas o CPF e o RG", False),
          ("Somente dados financeiros", False),
          ("Qualquer dado de empresas", False)]),
        ("Qual órgão fiscaliza a aplicação da LGPD no Brasil?", "Art. 55-A",
         "A ANPD é a Autoridade Nacional de Proteção de Dados.", 1,
         [("ANPD", True), ("Receita Federal", False), ("Procon", False), ("Banco Central", False)]),
        ("Qual destes é considerado dado pessoal sensível?", "Art. 5º, II",
         "Dados de saúde, biometria, origem racial, convicção religiosa etc. são sensíveis.", 1,
         [("Dado de saúde do titular", True), ("Nome completo", False),
          ("Endereço comercial", False), ("Número de telefone", False)]),
        ("O consentimento é a única base legal para tratar dados pessoais?", "Art. 7º",
         "Não. A LGPD prevê dez bases legais; consentimento é apenas uma delas.", 1,
         [("Não, existem dez bases legais", True), ("Sim, é a única", False),
          ("Sim, exceto para o governo", False), ("Apenas para dados sensíveis", False)]),
        ("Quem decide sobre as finalidades e meios do tratamento é o:", "Art. 5º, VI",
         "O controlador é quem toma as decisões sobre o tratamento.", 1,
         [("Controlador", True), ("Operador", False), ("Titular", False), ("Encarregado", False)]),
        ("Tratar somente os dados estritamente necessários refere-se ao princípio da:", "Art. 6º, III",
         "É o princípio da necessidade (minimização).", 2,
         [("Necessidade", True), ("Publicidade", False), ("Gratuidade", False), ("Portabilidade", False)]),
        ("Em um incidente de segurança com risco relevante, deve-se comunicar:", "Art. 48",
         "Comunica-se à ANPD e aos titulares afetados em prazo razoável.", 2,
         [("A ANPD e os titulares afetados", True), ("Apenas o setor de TI", False),
          ("Somente a polícia", False), ("Ninguém, se for interno", False)]),
        ("A sanção de multa prevista na LGPD pode chegar a:", "Art. 52",
         "Até 2% do faturamento, limitada a R$ 50 milhões por infração.", 3,
         [("2% do faturamento, até R$ 50 milhões por infração", True),
          ("10% do faturamento sem limite", False),
          ("Prisão do gestor", False), ("R$ 1.000 fixos", False)]),
        ("O direito de obter a eliminação de dados tratados com consentimento é um:", "Art. 18, VI",
         "É um dos direitos do titular previstos no Art. 18.", 2,
         [("Direito do titular", True), ("Dever do operador", False),
          ("Privilégio do controlador", False), ("Poder da ANPD apenas", False)]),
        ("O princípio que exige prestar contas e demonstrar conformidade é:", "Art. 6º, X",
         "É a responsabilização e prestação de contas (accountability).", 2,
         [("Responsabilização e prestação de contas", True), ("Anonimato", False),
          ("Onerosidade", False), ("Irretroatividade", False)]),
    ],
    "RH": [
        ("Um atestado médico de colaborador é classificado como:", "Art. 5º, II",
         "Dados de saúde são dados pessoais sensíveis.", 1,
         [("Dado pessoal sensível", True), ("Dado anônimo", False),
          ("Dado público", False), ("Dado não pessoal", False)]),
        ("A base legal típica para tratar dados da folha de pagamento é:", "Art. 7º, II",
         "Cumprimento de obrigação legal/regulatória trabalhista.", 2,
         [("Cumprimento de obrigação legal", True), ("Consentimento do empregado", False),
          ("Interesse do concorrente", False), ("Não precisa de base legal", False)]),
        ("Ao coletar biometria para o ponto, o cuidado extra existe porque ela é:", "Art. 11",
         "Biometria é dado sensível e exige segurança reforçada e necessidade.", 2,
         [("Dado sensível", True), ("Dado público", False),
          ("Irrelevante para a LGPD", False), ("Dado de empresa", False)]),
        ("Currículos de candidatos não contratados devem:", "Art. 15-16",
         "Precisam de prazo de retenção e eliminação quando não há mais finalidade.", 2,
         [("Ter prazo de retenção e ser eliminados depois", True),
          ("Ser guardados para sempre", False),
          ("Ser vendidos a parceiros", False),
          ("Ser publicados no site", False)]),
        ("Dados de dependentes menores do colaborador exigem:", "Art. 14",
         "Tratamento no melhor interesse da criança/adolescente, com cuidado reforçado.", 2,
         [("Cuidado reforçado, no melhor interesse do menor", True),
          ("Nenhum cuidado especial", False),
          ("Divulgação obrigatória", False),
          ("Consentimento do empregador apenas", False)]),
        ("Compartilhar dados do funcionário com o plano de saúde requer:", "Art. 6º, I",
         "Finalidade específica e informação ao titular (transparência).", 2,
         [("Finalidade específica e transparência", True),
          ("Nada, é livre", False),
          ("Apenas aviso ao gestor", False),
          ("Autorização do sindicato somente", False)]),
        ("Monitorar e-mail corporativo dos colaboradores exige principalmente:", "Art. 6º, VI",
         "Transparência: política clara e informação prévia aos colaboradores.", 2,
         [("Transparência e política prévia", True),
          ("Sigilo absoluto da empresa", False),
          ("Proibição total pela LGPD", False),
          ("Consentimento de clientes", False)]),
        ("Publicar a lista de aniversariantes com data de nascimento, sem avaliação, é:", "Art. 6º, III",
         "Deve-se avaliar necessidade, finalidade e expectativa do titular.", 3,
         [("Inadequado sem avaliar necessidade e finalidade", True),
          ("Sempre permitido", False),
          ("Obrigatório por lei", False),
          ("Indiferente para a LGPD", False)]),
    ],
    "FINANCEIRO": [
        ("Notas fiscais com dados pessoais são retidas com base em:", "Art. 7º, II",
         "Obrigação legal/regulatória fiscal define o prazo de guarda.", 2,
         [("Cumprimento de obrigação legal", True), ("Consentimento do cliente", False),
          ("Marketing", False), ("Curiosidade", False)]),
        ("A análise para prevenção à fraude costuma se apoiar em:", "Art. 7º, IX",
         "Legítimo interesse do controlador, com salvaguardas (Art. 10).", 3,
         [("Legítimo interesse", True), ("Consentimento sempre", False),
          ("Nenhuma base", False), ("Interesse público apenas", False)]),
        ("No Open Finance, o compartilhamento de dados do cliente depende de:", "Art. 7º, I",
         "Consentimento específico do titular.", 2,
         [("Consentimento do titular", True), ("Decisão do gerente", False),
          ("Ordem da Receita", False), ("Nada", False)]),
        ("Enviar planilha de clientes por e-mail sem proteção configura:", "Art. 46",
         "Falha de segurança; a lei exige medidas técnicas e administrativas.", 2,
         [("Falha nas medidas de segurança", True), ("Boa prática", False),
          ("Exigência legal", False), ("Anonimização", False)]),
        ("Expor o valor da dívida de um cliente a terceiros na cobrança:", "Art. 6º, I",
         "Fere a finalidade e a privacidade do titular.", 2,
         [("Viola finalidade e privacidade", True), ("É permitido sempre", False),
          ("É obrigatório", False), ("Não tem relação com a LGPD", False)]),
        ("Dados bancários de clientes, quanto à segurança, exigem:", "Art. 46",
         "Proteção elevada, mesmo não sendo 'sensíveis' na definição legal.", 2,
         [("Proteção elevada e controle de acesso", True),
          ("Nenhum cuidado", False),
          ("Publicação periódica", False),
          ("Compartilhamento livre", False)]),
        ("Após o fim da relação e dos prazos legais, dados financeiros devem ser:", "Art. 16",
         "Eliminados quando não há mais finalidade ou obrigação que justifique a guarda.", 2,
         [("Eliminados", True), ("Mantidos para sempre", False),
          ("Vendidos", False), ("Publicados", False)]),
        ("Consulta a bureau de crédito deve sempre observar:", "Art. 6º, VI",
         "Transparência e a base legal adequada ao caso.", 2,
         [("Transparência e base legal adequada", True),
          ("Sigilo do titular sobre tudo", False),
          ("Proibição total", False),
          ("Apenas autorização verbal", False)]),
    ],
    "TI": [
        ("O Art. 46 da LGPD trata de:", "Art. 46",
         "Medidas técnicas e administrativas de segurança dos dados.", 1,
         [("Medidas de segurança dos dados", True), ("Bases legais", False),
          ("Direitos do titular", False), ("Sanções", False)]),
        ("Um provedor de nuvem que trata dados em nome da empresa é:", "Art. 5º, VII",
         "É o operador, que age conforme instruções do controlador.", 2,
         [("Operador", True), ("Controlador", False), ("Titular", False), ("Encarregado", False)]),
        ("O princípio de conceder o mínimo de acesso necessário chama-se:", "Art. 46",
         "Menor privilégio — apoia a segurança e a minimização.", 2,
         [("Menor privilégio", True), ("Acesso total", False),
          ("Livre acesso público", False), ("Portabilidade", False)]),
        ("Logs de acesso são importantes principalmente para:", "Art. 48",
         "Rastreabilidade e resposta a incidentes.", 2,
         [("Rastreabilidade e resposta a incidentes", True),
          ("Aumentar o consumo de disco", False),
          ("Marketing", False),
          ("Nada relevante", False)]),
        ("Criptografar dados pessoais armazenados é exemplo de:", "Art. 46",
         "Medida técnica de segurança e proteção.", 1,
         [("Medida técnica de segurança", True), ("Base legal", False),
          ("Sanção", False), ("Anonimização garantida", False)]),
        ("Backups que contêm dados pessoais devem ser:", "Art. 46",
         "Protegidos e sujeitos a política de retenção, como os dados de produção.", 2,
         [("Protegidos e com retenção definida", True),
          ("Ignorados pela LGPD", False),
          ("Públicos", False),
          ("Mantidos sem critério", False)]),
        ("O operador responde solidariamente quando:", "Art. 42",
         "Quando descumpre a LGPD ou as instruções lícitas do controlador.", 3,
         [("Descumpre a lei ou as instruções do controlador", True),
          ("Sempre, em qualquer caso", False),
          ("Nunca responde", False),
          ("Apenas se for público", False)]),
        ("Diante de um incidente com risco relevante, a equipe deve:", "Art. 48",
         "Acionar a comunicação à ANPD e aos titulares em prazo razoável.", 2,
         [("Comunicar ANPD e titulares", True),
          ("Apagar os logs", False),
          ("Esconder o caso", False),
          ("Esperar o próximo ano", False)]),
    ],
    "MARKETING": [
        ("O consentimento válido na LGPD deve ser:", "Art. 5º, XII",
         "Livre, informado e inequívoco.", 1,
         [("Livre, informado e inequívoco", True), ("Presumido", False),
          ("Genérico e oculto", False), ("Permanente e irrevogável", False)]),
        ("Disparar e-mail marketing para uma base comprada normalmente:", "Art. 7º",
         "Carece de base legal/consentimento e desrespeita a expectativa do titular.", 2,
         [("Carece de base legal", True), ("É recomendado", False),
          ("É obrigatório", False), ("Não envolve dados pessoais", False)]),
        ("Cookies não essenciais, em regra, exigem:", "Art. 8º",
         "Informação e consentimento do titular.", 2,
         [("Consentimento e informação", True), ("Nada", False),
          ("Ordem judicial", False), ("Pagamento", False)]),
        ("Quando o titular revoga o consentimento, a empresa deve:", "Art. 8º, §5º",
         "Atender prontamente, cessando o tratamento baseado naquele consentimento.", 2,
         [("Atender prontamente a revogação", True),
          ("Ignorar o pedido", False),
          ("Cobrar uma taxa", False),
          ("Esperar 1 ano", False)]),
        ("Decisões tomadas unicamente por tratamento automatizado podem ser:", "Art. 20",
         "O titular pode solicitar a revisão de decisões automatizadas.", 2,
         [("Revisadas a pedido do titular", True),
          ("Mantidas sem questionamento", False),
          ("Proibidas sempre", False),
          ("Aplicadas em segredo", False)]),
        ("Enriquecer a base de leads com dados de terceiros exige:", "Art. 6º",
         "Avaliar base legal e garantir transparência ao titular.", 3,
         [("Avaliar base legal e transparência", True),
          ("Nada, é livre", False),
          ("Somente pagar pela base", False),
          ("Apenas aviso interno", False)]),
        ("Oferecer opção de descadastro (opt-out) em campanhas é:", "Art. 18",
         "Boa prática alinhada aos direitos do titular.", 1,
         [("Alinhado aos direitos do titular", True),
          ("Opcional e dispensável", False),
          ("Proibido", False),
          ("Irrelevante", False)]),
        ("Compartilhar a lista de leads com um parceiro comercial:", "Art. 6º, I",
         "Exige finalidade informada e base legal — não é livre.", 2,
         [("Exige base legal e finalidade informada", True),
          ("Pode ser feito livremente", False),
          ("É sempre proibido por lei", False),
          ("Independe de consentimento sempre", False)]),
    ],
    "ATENDIMENTO": [
        ("Ao receber um pedido de acesso aos dados, o atendimento deve primeiro:", "Art. 18, II",
         "Confirmar a identidade do requerente para não entregar dados a terceiros.", 2,
         [("Confirmar a identidade do titular", True),
          ("Negar sempre", False),
          ("Publicar os dados", False),
          ("Cobrar uma taxa alta", False)]),
        ("O fornecimento de dados ao titular, em regra, deve ser:", "Art. 18",
         "De forma facilitada e gratuita.", 2,
         [("Facilitado e gratuito", True),
          ("Pago e burocrático", False),
          ("Negado", False),
          ("Somente presencial", False)]),
        ("Registrar os pedidos dos titulares é importante para:", "Art. 6º, X",
         "Demonstrar conformidade (accountability).", 2,
         [("Demonstrar conformidade", True),
          ("Atrapalhar o atendimento", False),
          ("Vender dados", False),
          ("Nada", False)]),
        ("Se um terceiro pede dados de outra pessoa, o atendimento deve:", "Art. 18",
         "Não entregar sem verificar a legitimidade/identidade do titular.", 2,
         [("Recusar sem verificar a legitimidade", True),
          ("Entregar imediatamente", False),
          ("Publicar os dados", False),
          ("Ignorar a LGPD", False)]),
    ],
    "JURIDICO": [
        ("Contratos com operadores devem conter:", "Art. 39",
         "Cláusulas de proteção de dados, definindo instruções e responsabilidades.", 2,
         [("Cláusulas de proteção de dados", True),
          ("Nenhuma menção a dados", False),
          ("Apenas preço", False),
          ("Proibição de segurança", False)]),
        ("A transferência internacional de dados deve observar:", "Art. 33",
         "As hipóteses e requisitos do Art. 33 (ex.: país adequado, cláusulas, consentimento).", 3,
         [("Os requisitos do Art. 33", True),
          ("Nenhuma regra", False),
          ("Somente o câmbio", False),
          ("Apenas idioma do contrato", False)]),
        ("A figura do Encarregado (DPO) está prevista no:", "Art. 41",
         "O Art. 41 trata da indicação do encarregado pelo controlador.", 1,
         [("Art. 41", True), ("Art. 1º", False), ("Art. 60", False), ("Art. 7º", False)]),
        ("O operador responde solidariamente quando:", "Art. 42",
         "Descumpre a LGPD ou não segue as instruções lícitas do controlador.", 3,
         [("Descumpre a lei ou as instruções", True),
          ("Sempre, sem exceção", False),
          ("Nunca", False),
          ("Apenas se for órgão público", False)]),
    ],
}


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
    if models.Empresa.query.filter_by(slug="acme").first():
        print("Empresa de demonstração já existe — nada a fazer.")
        print("Para recriar, apague instance/lgpd.db e rode 'flask seed' novamente.")
        return

    _seed_biblioteca()
    _seed_empresa()
    _seed_segunda_empresa()
    db.session.commit()
    print("Seed concluído.")
    print("  Acme (empresa principal): dpo@acme.com.br / gestor.rh@acme.com.br / ana@acme.com.br")
    print("  Nova Era Saúde (segunda empresa, para ver o isolamento): dpo@novaera.com.br")
    print(f"  Senha de todos: {SENHA_DEMO}")


def _seed_biblioteca():
    if not models.Trilha.query.first():
        for t in TRILHAS:
            db.session.add(models.Trilha(
                empresa_id=None, area=t["area"], titulo=t["titulo"], slug=t["slug"],
                resumo=t["resumo"], conteudo_md=t["conteudo"], ordem=t["ordem"], publicada=True,
            ))
    if not models.Questao.query.first():
        for area, itens in QUESTOES.items():
            for enunciado, artigo, explic, dif, alternativas in itens:
                q = models.Questao(
                    empresa_id=None, area=area, enunciado=enunciado,
                    artigo=artigo, explicacao=explic, dificuldade=dif, ativo=True,
                )
                db.session.add(q)
                db.session.flush()
                for ordem, (texto, correta) in enumerate(alternativas):
                    db.session.add(models.Alternativa(
                        questao_id=q.id, texto=texto, correta=correta, ordem=ordem,
                    ))
    if not models.DiagnosticoPergunta.query.first():
        ordem_por_dim = {}
        for dimensao, texto in DIAG_PERGUNTAS:
            ordem = ordem_por_dim.get(dimensao, 0)
            ordem_por_dim[dimensao] = ordem + 1
            db.session.add(models.DiagnosticoPergunta(
                dimensao=dimensao, texto=texto, peso=1, ordem=ordem, ativo=True,
            ))
    db.session.flush()


def _seed_empresa():
    empresa = models.Empresa(nome="Acme Indústria e Comércio", slug="acme")
    db.session.add(empresa)
    db.session.flush()

    setores = {}
    for nome, area in SETORES_DEMO:
        s = models.Setor(
            empresa_id=empresa.id, nome=nome,
            slug=nome.lower().replace(" ", "-"), area=area,
        )
        db.session.add(s)
        db.session.flush()
        setores[area] = s

    usuarios = {}
    for nome, email, papel, area in USUARIOS_DEMO:
        u = models.Usuario(
            empresa_id=empresa.id, nome=nome, email=email, papel=papel,
            setor_id=setores[area].id if area else None,
        )
        u.definir_senha(SENHA_DEMO)
        db.session.add(u)
        db.session.flush()
        usuarios[email] = u

    # Lança provas concluídas + certificados para alimentar o ranking
    dias = 365
    for email, (nota, aprovado) in RESULTADOS_DEMO.items():
        u = usuarios[email]
        prova = models.Prova(
            empresa_id=empresa.id, usuario_id=u.id, setor_id=u.setor_id,
            area=u.setor.area, nota_corte=70, nota=nota, aprovado=aprovado,
            status="concluida", finalizado_em=agora_utc(),
        )
        db.session.add(prova)
        db.session.flush()
        if aprovado:
            import secrets
            db.session.add(models.Certificado(
                empresa_id=empresa.id, usuario_id=u.id, prova_id=prova.id,
                setor_id=u.setor_id, area=u.setor.area, codigo=secrets.token_hex(8),
                nota=nota, valido_ate=models.Certificado.validade_padrao(dias),
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
        probabilidade=3, impacto=3, medidas="", risco_residual=None,
        conclusao="", status="rascunho",
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
