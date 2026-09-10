"""Trilhas de treinamento (Markdown), uma por área, casadas com o banco de questões.

Mesma regra editorial do banco: só o que está na Lei nº 13.709/2018 (Planalto) e nas
normas e guias da ANPD. Onde o texto cita prazo ou número, a fonte é indicada.
"""

TRILHAS = [
    {
        "area": "GERAL", "ordem": 1, "titulo": "Fundamentos da LGPD", "slug": "fundamentos-lgpd",
        "resumo": "Conceitos essenciais: dado pessoal, bases legais, princípios, papéis e sanções.",
        "conteudo": """# Fundamentos da LGPD

A **Lei Geral de Proteção de Dados Pessoais** (Lei nº 13.709/2018) regula o tratamento de
dados pessoais por pessoas naturais e jurídicas, públicas e privadas, para proteger os direitos
fundamentais de liberdade e de privacidade e o livre desenvolvimento da personalidade (Art. 1º).
Aplica-se mesmo a empresas com sede no exterior que ofereçam bens ou serviços a pessoas no Brasil
(Art. 3º).

## Conceitos centrais (Art. 5º)
- **Dado pessoal**: informação relacionada a pessoa natural identificada ou identificável.
- **Dado pessoal sensível**: origem racial ou étnica, convicção religiosa, opinião política,
  filiação a sindicato ou a organização religiosa, filosófica ou política, saúde, vida sexual,
  dado genético ou biométrico.
- **Titular**: a pessoa natural a quem os dados se referem — pessoa jurídica não é titular.
- **Controlador**: quem toma as decisões sobre o tratamento. **Operador**: quem trata em nome
  do controlador. **Encarregado**: canal de comunicação entre controlador, titulares e ANPD.
- **Tratamento**: toda operação com dados — coletar, acessar, armazenar, transmitir, eliminar.
- **Dado anonimizado** não é dado pessoal, salvo se a anonimização puder ser revertida com
  esforços razoáveis (Art. 12).

## As hipóteses legais (Art. 7º)
O consentimento é **uma** entre **dez** hipóteses. As mais usadas nas empresas: cumprimento de
obrigação legal ou regulatória (II), execução de contrato a pedido do titular (V), legítimo
interesse (IX) e proteção do crédito (X). Dados sensíveis seguem as hipóteses do Art. 11 — e o
legítimo interesse **não** está entre elas.

Dispensar o consentimento não dispensa os princípios nem os direitos do titular (Art. 7º, § 6º).

## Princípios (Art. 6º)
Finalidade, adequação, **necessidade** (mínimo necessário), livre acesso, qualidade dos dados,
transparência, segurança, prevenção, não discriminação e **responsabilização e prestação de
contas** — demonstrar que as medidas existem e funcionam.

## Direitos do titular (Art. 18)
Confirmação, acesso, correção, anonimização/bloqueio/eliminação, portabilidade, eliminação dos
dados consentidos, informação sobre compartilhamento, informação sobre a possibilidade de não
consentir e revogação. Atendimento **sem custos**; a declaração completa sobre existência e
acesso sai em até **15 dias** (Art. 19).

## Incidentes e sanções
Incidente com risco relevante: o **controlador** comunica a ANPD **e** os titulares em
**3 dias úteis** do conhecimento de que afetou dados pessoais (Art. 48; Resolução CD/ANPD
nº 15/2024). Sanções (Art. 52): de advertência a multa de até 2% do faturamento no Brasil,
limitada a R$ 50 milhões **por infração**, além de bloqueio, eliminação e suspensão — aplicadas
exclusivamente pela ANPD (Art. 55-K), em vigor desde 1º/8/2021.
""",
    },
    {
        "area": "RH", "ordem": 1, "titulo": "LGPD no RH", "slug": "lgpd-no-rh",
        "resumo": "Dados sensíveis de saúde e biometria, bases legais, retenção e desligamento.",
        "conteudo": """# LGPD no RH

O RH é o setor que mais trata **dados sensíveis** (Art. 5º, II): atestados e exames (saúde),
biometria do ponto, filiação sindical — além de dados de dependentes, inclusive **crianças**
(Art. 14).

## Bases legais típicas
- Folha, admissão, obrigações trabalhistas e previdenciárias: **obrigação legal ou regulatória**
  (Art. 7º, II; para sensíveis, Art. 11, II, "a"). Pedir consentimento aqui é desnecessário —
  e consentimento genérico é nulo (Art. 8º, § 4º).
- Execução do contrato de trabalho (Art. 7º, V) e procedimentos preliminares a pedido do
  candidato.
- **Tutela da saúde** (Art. 11, II, "f") vale só para profissionais e serviços de saúde — o RH,
  ao guardar um atestado, apoia-se na obrigação legal.

## Pontos de atenção
- **Biometria** é dado sensível; seu uso é critério de alto risco (Resolução CD/ANPD nº 2/2022),
  e a ANPD pode exigir relatório de impacto (Art. 38).
- **Currículos** de candidatos não contratados: eliminar ao fim da finalidade (Arts. 15 e 16),
  salvo hipótese legal de conservação.
- **Dependentes menores**: melhor interesse da criança (Art. 14); qualquer base dos Arts. 7º ou
  11 pode ser usada se o melhor interesse prevalecer (Enunciado CD/ANPD nº 1/2023).
- **Plano de saúde**: informar ao titular o compartilhamento e a finalidade (Art. 9º). A
  operadora não pode usar dados de saúde para selecionar riscos (Art. 11, § 5º).
- **Monitoramento**: webcam e registro de teclas são excessivos e desproporcionais mesmo se
  informados (Guia de Legítimo Interesse da ANPD). Transparência é obrigatória (Art. 6º, VI).
- **Quem vê o quê**: acesso na proporção da necessidade — menor privilégio (Guia de Segurança
  da ANPD). Nada de lista de CPFs no mural.
- **Desligamento**: documentos trabalhistas ficam pelo prazo legal (Art. 16, I); pedidos de
  eliminação que a lei impede recebem resposta com as razões (Art. 18, § 4º).
- **Encarregado**: o chefe do RH acumular a função pode ser conflito de interesse (Resolução
  CD/ANPD nº 18/2024). Treinar a equipe é atribuição do encarregado (Art. 41, § 2º, III).
""",
    },
    {
        "area": "FINANCEIRO", "ordem": 1, "titulo": "LGPD no Financeiro", "slug": "lgpd-no-financeiro",
        "resumo": "Retenção fiscal, proteção do crédito, cobrança, decisões automatizadas e multas.",
        "conteudo": """# LGPD no Financeiro

## Retenção por obrigação legal
Notas fiscais e documentos contábeis com dados pessoais ficam pelos prazos legais — conservação
autorizada para **cumprimento de obrigação legal** (Art. 16, I). Depois do prazo, elimine.

## Crédito, fraude e bureaus
- A LGPD tem hipótese própria para **proteção do crédito** (Art. 7º, X). Consulta a bureau exige
  base adequada e **transparência** ao titular (Art. 6º, VI).
- **Prevenção à fraude** com dados sensíveis só na identificação e autenticação de cadastro em
  sistemas eletrônicos (Art. 11, II, "g"). Com dados não sensíveis, o legítimo interesse pede
  **teste de balanceamento** documentado (Guia da ANPD, 2024).
- Decisão de crédito **unicamente automatizada**: o cliente pode pedir revisão e conhecer os
  critérios, observados os segredos comercial e industrial (Art. 20).

## Dados financeiros e segurança
Dados bancários **não** estão na lista de sensíveis, mas são critério de **risco relevante** em
incidentes (Resolução CD/ANPD nº 15/2024, art. 5º, III) e exigem proteção (Art. 46): controle de
acesso, MFA, backups off-line, mídias removíveis cifradas (Guia de Segurança da ANPD).
Planilha de clientes por e-mail sem proteção e cobrança que revela a dívida a terceiros são
falhas de segurança e de finalidade.

## Compartilhamento
Contabilidade externa é **operadora** e segue instruções (Art. 39). Compartilhar com outro
controlador dados obtidos por consentimento exige **consentimento específico** (Art. 7º, § 5º).
Pagamento a fornecedor no exterior é transferência internacional: base legal **e** mecanismo do
Art. 33 (Resolução CD/ANPD nº 19/2024).

## Sanções em números (Art. 52; Resolução CD/ANPD nº 4/2023)
Multa de até 2% do faturamento no Brasil, excluídos os tributos, limitada a R$ 50 milhões por
infração; multa diária com o mesmo teto. Cessar a infração antes de a ANPD agir reduz a multa em
75%; cada reincidência específica agrava 10% (até 40%). Pagamento em 20 dias úteis, com 25% de
redução se houver renúncia ao recurso. Órgãos públicos não recebem multa (Art. 52, § 3º).
""",
    },
    {
        "area": "TI", "ordem": 1, "titulo": "LGPD em TI e Segurança", "slug": "lgpd-ti-seguranca",
        "resumo": "Medidas de segurança, operadores de nuvem, incidentes (3 dias úteis) e transferência internacional.",
        "conteudo": """# LGPD em TI e Segurança da Informação

## Medidas de segurança (Arts. 46 a 49)
A lei exige medidas **técnicas e administrativas** aptas a proteger os dados, **desde a concepção**
do produto até a execução (Art. 46, § 2º), e mesmo **após o término** do tratamento (Art. 47).
O Guia de Segurança da ANPD recomenda: menor privilégio (need to know), **MFA**, senhas fortes e
não compartilhadas, patches em dia, antivírus que o usuário não desliga, criptografia (exemplo de
pseudonimização), backups em local distinto e **não sincronizados em tempo real**, mídias
removíveis inventariadas e cifradas, descarte com destruição registrada.

## Operador, suboperador e nuvem
O provedor que trata dados **em nome** da empresa é **operador** (Art. 5º, VII) e segue instruções
(Art. 39); a nuvem que o operador contrata é **suboperadora** (Guia de Agentes da ANPD). Contrato
com SLA de segurança e MFA (Guia de Segurança). O operador responde solidariamente se descumprir
a lei ou as instruções (Art. 42, § 1º, I).

## Incidentes (Art. 48; Resolução CD/ANPD nº 15/2024)
- **Incidente** é evento adverso **confirmado** que viola confidencialidade, integridade,
  disponibilidade ou autenticidade. Vulnerabilidade sozinha não é incidente.
- Havendo **risco relevante** (dados sensíveis, de crianças/idosos, financeiros, de autenticação,
  sob sigilo ou em larga escala), o **controlador** comunica a ANPD **e** os titulares em
  **3 dias úteis** do conhecimento de que afetou dados pessoais (em dobro para pequeno porte).
- O **operador** informa o controlador sem demora injustificada.
- Registro do incidente — inclusive dos não comunicados — por **5 anos**.
- Logs servem para investigar, registrar e responder à ANPD com a causa principal.

## Transferência internacional (Art. 33; Resolução CD/ANPD nº 19/2024)
Servidor no exterior exige **base legal E mecanismo**: decisão de adequação (a União Europeia e o
EEE foram reconhecidos pela Resolução nº 32/2026), **cláusulas-padrão** da ANPD adotadas sem
alteração, normas corporativas globais ou cláusulas específicas aprovadas. Coleta feita
diretamente do exterior não é transferência — mas a LGPD se aplica.

## Privacidade por padrão
Configurações protetivas ativadas automaticamente, sem ação do usuário (Guia do Encarregado, 2024).
""",
    },
    {
        "area": "MARKETING", "ordem": 1, "titulo": "LGPD em Marketing e Vendas", "slug": "lgpd-marketing-vendas",
        "resumo": "Consentimento, cookies conforme o Guia da ANPD, legítimo interesse, perfis e crianças.",
        "conteudo": """# LGPD em Marketing e Vendas

## Consentimento de verdade
Consentimento é manifestação **livre, informada e inequívoca** para finalidade determinada
(Art. 5º, XII). Autorização genérica é **nula** (Art. 8º, § 4º); por escrito, vai em **cláusula
destacada** (§ 1º); o controlador tem o **ônus de provar** (§ 2º); revogação **gratuita e
facilitada** a qualquer momento (§ 5º). Mudou a finalidade? Informe antes — o titular pode
revogar (Art. 9º, § 2º).

Base comprada de e-mails carece de hipótese legal: compartilhar dados consentidos com outro
controlador exige consentimento **específico** (Art. 7º, § 5º).

## Cookies — o que o Guia da ANPD (2022) diz
- Cookies **necessários** ao funcionamento: o legítimo interesse pode ser a base; consentimento
  **não** é apropriado (não há escolha real).
- Cookies **não necessários** (rastreamento, publicidade): **consentimento**. Para publicidade e
  formação de perfis, o legítimo interesse dificilmente cabe. Analíticos com dados **agregados**
  e sem perfis podem usar legítimo interesse.
- Banner de **primeiro nível** com botão para **rejeitar todos os não necessários**, bem visível;
  **segundo nível** com consentimento por finalidade e categorias **desativadas por padrão**.
- Sem pré-marcação, sem "continuar navegando é consentir", sem aceite forçado.
- Política de cookies informa finalidades, **retenção** e compartilhamento; retenção
  indeterminada é incompatível.

## Legítimo interesse (Art. 10; Guia da ANPD, 2024)
Só para dados **não sensíveis**, em situações **concretas**, com **teste de balanceamento**
(finalidade, necessidade, balanceamento e salvaguardas) e respeito à **legítima expectativa** do
titular. Promoções dos próprios produtos a clientes, com descadastro, cabem (Art. 10, I e II).
O titular pode se opor e, se não atendido, peticionar à ANPD.

## Perfis, decisões automatizadas e crianças
Perfil comportamental de pessoa identificada é dado pessoal (Art. 12, § 2º). Decisão
**unicamente automatizada** dá direito a revisão (Art. 20). Dados de crianças: consentimento
específico de um dos pais ou responsável (Art. 14, § 1º), sem exigir dados além do necessário
(§ 4º); publicidade que ignora o melhor interesse não cabe por legítimo interesse.
""",
    },
    {
        "area": "ATENDIMENTO", "ordem": 1, "titulo": "LGPD no Atendimento e SAC", "slug": "lgpd-atendimento-sac",
        "resumo": "Como receber e responder os pedidos do titular (Art. 18 e 19) sem expor dados.",
        "conteudo": """# LGPD no Atendimento e SAC

O atendimento é a porta por onde o titular exerce seus direitos — e por onde os dados mais
vazam. Duas regras convivem: **atender com facilidade** e **entregar só a quem tem direito**.

## Quem pode pedir
Os direitos são exercidos por **requerimento expresso do titular ou de representante legalmente
constituído** (Art. 18, § 3º). Parente, colega ou "quem mora na mesma casa" não. Como a empresa
deve proteger os dados de acesso não autorizado (Art. 46), **confirma-se a identidade** antes de
responder.

## O que o titular pode pedir (Art. 18)
Confirmação de tratamento, acesso, correção, anonimização/bloqueio/eliminação, portabilidade,
eliminação dos dados consentidos, informação sobre compartilhamento, informação sobre a
possibilidade de não consentir, revogação. A qualquer momento e **sem custos** (§ 5º). Se a
empresa não trata os dados daquela pessoa, diz isso e indica quem trata, se souber (§ 4º, I).
Se não puder atender de imediato, responde com as razões (§ 4º, II).

## Prazos (Art. 19)
Confirmação e acesso em formato **simplificado: imediatamente**; declaração **completa** (origem,
critérios, finalidade): **até 15 dias**. Entrega por meio eletrônico seguro ou impresso, a critério
do titular (§ 2º). Com base em consentimento ou contrato, cópia eletrônica integral em formato
reutilizável (§ 3º). Agentes de pequeno porte têm prazos em dobro (Resolução CD/ANPD nº 2/2022).

## Registrar e prestar contas
Todo pedido é registrado com data, providência e resposta — é assim que se demonstra conformidade
(Art. 6º, X). Corrigiu ou eliminou? Avise quem recebeu os dados por uso compartilhado, para
repetirem o procedimento (Art. 18, § 6º). Quem exerce direitos não pode ser prejudicado por isso
(Art. 21).

## No dia a dia do balcão
- Gravação de ligações: informar a finalidade (Art. 9º; transparência, Art. 6º, VI).
- Consentimento por telefone vale se ficar demonstrada a vontade — registre (Art. 8º).
- "Dar uma olhada" no cadastro de um conhecido é acesso indevido (necessidade e menor privilégio).
- Doença relatada pelo cliente é dado **sensível** (Art. 11): registre só se indispensável.
- Se a reclamação não for resolvida, o titular pode peticionar à **ANPD** e aos órgãos de defesa
  do consumidor (Art. 18, §§ 1º e 8º).
- Em incidente, a comunicação ao titular é **simples, direta e individualizada**, com um contato
  para informações (Resolução CD/ANPD nº 15/2024, art. 9º).
""",
    },
    {
        "area": "JURIDICO", "ordem": 1, "titulo": "LGPD no Jurídico e em Compras", "slug": "lgpd-juridico-compras",
        "resumo": "Contratos com operadores, responsabilidade, transferência internacional, encarregado e sanções.",
        "conteudo": """# LGPD no Jurídico e em Compras

## Papéis e contratos
Quem **decide** finalidades e elementos essenciais é o **controlador**; quem trata em nome dele é
o **operador**, que só age no limite das instruções (Art. 39). O contrato controlador–operador não
é exigido literalmente pela lei, mas é a boa prática recomendada pela ANPD — com instruções,
segurança e ciência ao controlador quando o operador contrata **suboperador**. **Controladoria
conjunta** existe quando dois controladores decidem juntos finalidades e elementos essenciais, com
acordo de responsabilidades (Guia de Agentes da ANPD).

## Responsabilidade (Arts. 42 a 45)
Quem causa dano tratando dados em violação à lei repara. O operador responde **solidariamente**
quando descumpre a lei ou as instruções lícitas; controladores diretamente envolvidos respondem
solidariamente. Excludentes (Art. 43): não tratou, tratou sem violar a lei, ou culpa exclusiva do
titular ou de terceiro. Inversão do ônus da prova a favor do titular (Art. 42, § 2º); direito de
regresso (§ 4º). Relações de consumo seguem também o CDC (Art. 45).

## Transferência internacional (Art. 33; Resolução CD/ANPD nº 19/2024)
Exige **base legal E mecanismo**: decisão de adequação (União Europeia e EEE — Resolução
nº 32/2026), **cláusulas-padrão** adotadas **integralmente e sem alteração**, normas corporativas
globais (mesmo grupo, aprovação prévia) ou cláusulas específicas (excepcionais, aprovação prévia).
Prazo de 12 meses para incorporar as cláusulas-padrão aos contratos existentes.

## Encarregado (Art. 41; Resolução CD/ANPD nº 18/2024)
O controlador deve indicar por **ato formal escrito, datado e assinado**; para o operador é
facultativo; pequeno porte é dispensado, mas mantém canal com o titular. Pode ser pessoa natural ou
**jurídica**, sem certificação obrigatória, acumulando funções desde que **sem conflito de
interesse**. Divulgação pública com **nome completo** e contato — só um e-mail não basta. Substituto
formalmente designado. O responsável pela conformidade perante a ANPD é o **agente**, não o
encarregado.

## RIPD e governança
A ANPD pode determinar o relatório de impacto, inclusive em tratamentos por legítimo interesse
(Art. 38; Art. 10, § 3º), com tipos de dados, metodologia, segurança e mitigação. Programa de
governança em privacidade (Art. 50, § 2º) inclui avaliação de riscos e plano de resposta a
incidentes. Dados de acesso público respeitam a finalidade e o interesse público da divulgação
(Art. 7º, § 3º).

## Sanções e dosimetria (Art. 52; Resolução CD/ANPD nº 4/2023)
Gradativas, isoladas ou cumulativas; suspensão e proibição só após outra sanção no mesmo caso
(§ 6º). Infração **grave**: afeta direitos e, cumulativamente, ocorre sem hipótese legal, com
sensíveis/crianças, em larga escala, com vantagem econômica ou obstrução. Reincidência específica:
mesmo dispositivo em 5 anos. Advertência para leve/média sem reincidência. Vazamentos individuais
admitem conciliação direta com o titular (§ 7º). Competência sancionatória é **exclusiva da ANPD**
(Art. 55-K), cujas normas passam por consulta pública (Art. 55-J, § 2º).
""",
    },
]
