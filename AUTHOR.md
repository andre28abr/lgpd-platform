# Sobre o autor

## André Augusto Azarias de Souza

→ [LinkedIn](https://linkedin.com/in/andreaugusto-azariasdesouza) · [GitHub](https://github.com/andre28abr) · contato@azariasdesouza.com

---

## Quem é

Gestor com **18 anos de atuação como Gerente Administrativo e Encarregado de Dados (DPO)** em organização do setor de saúde suplementar, ambiente regulado pela ANS e pela LGPD. Participou de decisões de diretoria, conduziu a relação com hospitais e operadoras, liderou a modernização dos sistemas administrativos e de segurança da informação e coordenou o programa de adequação à LGPD da organização, com dados sensíveis de saúde sob o Art. 11.

Formado em **Direito** e em **Análise e Desenvolvimento de Sistemas**, com pós-graduações em segurança digital, governança de dados, privacidade, direito digital e liderança ágil.

Atua na interseção entre **Compliance, GRC, privacidade e segurança da informação**: mapeamento de dados e ROPA (Art. 37), RIPD/DPIA (Art. 38), direitos do titular (Art. 18), gestão de operadores e terceiros (Art. 39), resposta a incidentes (Art. 48), interface com a ANPD, e os frameworks NIST CSF, CIS Controls e ISO/IEC 27001/27701. Trabalha com o princípio de que proteção de dados é também arquitetura: Security by Design, Zero Trust, defesa em camadas e menor privilégio.

Desde 2025 conduz, como **product owner técnico**, projetos open-source de segurança e privacidade em Python, Go, Rust e Swift, com a codificação orquestrada por assistentes de IA generativa sob sua direção e revisão. Desenvolve **automações de processos com n8n** e é autor de cinco livros publicados, entre eles *Da Norma à Liderança*, sobre atualização profissional em GRC.

---

## Automação de processos com n8n

Projeta e opera **automações de processos de negócio e jurídicos em n8n**, self-hosted em Docker Compose, com foco em privacidade: processamento local, gravação em disco restrita a pastas definidas, sem envio de dados a serviços de terceiros. Entre o que já construiu:

- **Triagem automática de publicações judiciais**: busca de hora em hora no DJEN (Comunica CNJ) por OAB, classificação por urgência, cálculo de prazo provisório em dias úteis, contexto do processo via DataJud e painel web de tratamento por advogado.
- **Onboarding de clientes**: formulário web que gera em segundos procuração, declaração de hipossuficiência e contrato de honorários em PDF (Gotenberg), com registro do cliente para os fluxos seguintes.
- **Portal e páginas servidas pelo próprio n8n** via webhooks, instaladores para Mac e Windows, variante para servidor com HTTPS automático e autenticação (Caddy) e rotina de backup.
- **Integrações com APIs públicas** (DJEN, DataJud, BrasilAPI) e desenho de fluxos com Code nodes, banco JSON local e controle de estado entre execuções.

---

## Por que esse projeto existe

A **Plataforma LGPD** nasceu como exercício pessoal de portfólio com três objetivos:

1. **Traduzir conceitos regulatórios em código.** A LGPD não é só política, é também como o sistema *implementa* o registro de operações (Art. 37), o relatório de impacto (Art. 38), o atendimento a direitos do titular (Art. 18), a resposta a incidentes (Art. 48) e a trilha de auditoria/accountability (Art. 6º, X). Este projeto força essa tradução em decisões técnicas concretas, do banco de questões ancorado em artigos até os módulos operacionais do Encarregado.

2. **Demonstrar fluência técnica suficiente pra dialogar com times de engenharia e segurança.** Um DPO que entende multi-tenancy, 2FA/TOTP, política de senha, CSP, rate limit e migrações de banco consegue conversar diretamente com a equipe técnica, sem intermediário que traduza requisitos.

3. **Exercitar a orquestração de um projeto técnico com auxílio de IA generativa.** A skill emergente do mercado pós-2024 não é "decorar sintaxe", é **definir requisitos, validar arquitetura, traduzir necessidade de negócio em especificação** e usar IA para acelerar a entrega. O projeto foi conduzido nesse modelo, com suíte de testes verde e CI.

---

## Atuação neste projeto

**Papel:** Product Owner técnico, com auxílio de assistentes de IA generativa para a etapa de codificação.

**Entregas pessoais (direção e revisão do autor):**
- Definição de **requisitos, escopo e roadmap** (MVP educacional + fase 2 de gestão de privacidade).
- **Validação da arquitetura**: monólito Flask multi-tenant, banco agnóstico (SQLite ↔ PostgreSQL), segurança em camadas, empacotamento Docker.
- **Tradução de exigências LGPD em funcionalidades**: banco de questões e trilhas ancorados nos artigos; diagnóstico de maturidade; **ROPA (Art. 37)**; **RIPD (Art. 38)**; **direitos do titular (Art. 18)**; **incidentes (Art. 48)**; trilha de auditoria (Art. 6º, X).
- **Curadoria do conteúdo**: trilhas por setor (RH, Financeiro, TI, Marketing…) e banco de questões com base legal e explicação.
- **Decisões de trade-off**: SQLite *default* × Postgres-ready, 2FA opt-in × obrigatório por empresa, rate limit em memória × Redis, banco curado de questões × geração por IA.
- **Ciclo de auditoria e hardening (set/2026)**: condução de uma auditoria completa de segurança e correção do projeto, isolamento multi-tenant, chave secreta, integridade da prova, migrações em PostgreSQL, trilha de auditoria à prova de adulteração, com decisão explícita de manter o SQLite como padrão por ser uma plataforma de demonstração, e de tornar o caminho PostgreSQL verdadeiro em vez de removê-lo. O processo (achado → correção → teste de regressão → CI) é o material de base para o e-book sobre GRC do autor.

**Etapa de codificação:** orquestrada com auxílio de IA generativa, sob direção e revisão do autor. A stack (Python/Flask, SQLAlchemy, Jinja, etc.) foi escolhida pela aderência ao caso de uso e pela exposição prévia em estudos, não por domínio prático prévio em escrita de código de produção.

---

## Outros projetos

**[SentinelBR](https://github.com/andre28abr/SentinelBR-platform)** ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) ![Go](https://img.shields.io/badge/-Go-00ADD8?logo=go&logoColor=white) ![React](https://img.shields.io/badge/-React-20232A?logo=react&logoColor=61DAFB)<br>
Plataforma open-source de **SIEM + LGPD** para PMEs brasileiras. Agente Go com gRPC e mTLS, detecção em tempo real, resposta automatizada e compliance LGPD nativa, multi-tenant. 225 testes entre servidor, agente e frontend; CI em 16 jobs.

**[VigiaOS](https://github.com/andre28abr/VigiaOS)** ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) ![Rust](https://img.shields.io/badge/-Rust-000000?logo=rust&logoColor=white) ![GTK4](https://img.shields.io/badge/-GTK4-4A86CF?logo=gtk&logoColor=white)<br>
Suíte de **segurança, privacidade e LGPD** para a estação de trabalho (Fedora Workstation, GTK4 + libadwaita), com 13 ferramentas defensivas, módulos de detecção e resposta e laboratório educacional com termo de uso. 1460 testes em Python e 28 em Rust.

**[Peapod](https://github.com/andre28abr/Peapod)** ![Go](https://img.shields.io/badge/-Go-00ADD8?logo=go&logoColor=white) ![Swift](https://img.shields.io/badge/-Swift-F05138?logo=swift&logoColor=white) ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)<br>
Sandboxes **isolados e descartáveis para agentes de IA**, dirigidos por MCP, CLI, dashboard web e app nativo de macOS: rede desligada por padrão, allowlist de domínios, trilha de auditoria. Go e Swift, distribuído por Homebrew.

**[Uptend](https://github.com/andre28abr/Uptend)** ![Swift 6](https://img.shields.io/badge/-Swift%206-F05138?logo=swift&logoColor=white) ![macOS](https://img.shields.io/badge/-macOS-000000?logo=apple&logoColor=white)<br>
App nativo de macOS para **configurar e manter o Mac** e **auditar servidores Linux**: coletor portátil, relatórios, correlação com CVEs, MITRE ATT&CK, lente LGPD e playbook de hardening com rollback. Swift 6, 428 testes.

**[banana](https://github.com/andre28abr/banana)** ![Rust](https://img.shields.io/badge/-Rust-000000?logo=rust&logoColor=white) ![Tauri 2](https://img.shields.io/badge/-Tauri%202-24C8D8?logo=tauri&logoColor=white) ![Svelte 5](https://img.shields.io/badge/-Svelte%205-FF3E00?logo=svelte&logoColor=white)<br>
Editor **local-first** de notas Markdown, código e PDF, com vault cifrado (Argon2id + AES-256-GCM). Tauri 2, Rust e Svelte 5, 393 testes.

**SC Platform** *(privado, disponível para apresentação mediante solicitação)* ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?logo=postgresql&logoColor=white)<br>
SaaS multi-tenant para gestão de licitações públicas, com PNCP em tempo real, simulador da Lei 14.133/2021, robô de lances em três modos, extração de PDF com IA local, CRM e Telegram. Cerca de 75 mil linhas e 547 testes.

**AUGRAZ** *(privado, produto da empresa do autor)* ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white)<br>
Plataforma de compliance **LGPD + ISO 27001** para assessoria de proteção de dados: 11 módulos por empresa-cliente (ROPA, canal do titular, incidentes, comunicações com a ANPD, fornecedores, treinamentos), biblioteca dos 93 controles do Anexo A da ISO/IEC 27001:2022 com Gap Analysis, relatórios imprimíveis e geradores de política de privacidade, aviso de cookies e termos de uso. Flask, testes em SQLite e PostgreSQL, CI com lint e auditoria de dependências.

**Site AUGRAZ** *(privado, protótipo ainda não publicado)* ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5&logoColor=white) ![PHP](https://img.shields.io/badge/-PHP-777BB4?logo=php&logoColor=white)<br>
Site institucional em HTML e PHP com formulário de contato em PDO e prepared statements, credenciais fora do repositório e `.htaccess` com HTTPS forçado, bloqueio de arquivos sensíveis e cabeçalhos de segurança (HSTS, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy).

---

→ **[LinkedIn](https://linkedin.com/in/andreaugusto-azariasdesouza)** · [GitHub](https://github.com/andre28abr)
