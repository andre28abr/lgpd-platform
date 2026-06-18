# Sobre o autor

## André Augusto Azarias De Souza

→ [LinkedIn](https://linkedin.com/in/adreaugusto-azariasdesouza) · [GitHub](https://github.com/andre28abr) · [Profile completo](https://github.com/andre28abr)

---

## Resumo

Profissional com mais de 18 anos de experiência em **gestão administrativa, compliance, governança da informação e proteção de dados pessoais**, com atuação integrada entre áreas administrativas, tecnologia da informação e conformidade regulatória.

Formação dupla em **Direito (Anhanguera)** e **Análise e Desenvolvimento de Sistemas (Mackenzie)**, complementada por especializações em LGPD, Direito Digital, Segurança Digital e Liderança Ágil.

Exerceu por quase duas décadas a função de **Gerente Administrativo e Encarregado de Dados (DPO)** em organização do setor de saúde suplementar, com atuação na organização da governança, adequação à LGPD, controle documental e apoio às áreas administrativas e tecnológicas.

Atualmente em transição de carreira, com **disponibilidade imediata**, busca posições em DPO (Encarregado de Dados), Compliance, Governança & GRC, Privacy Engineering ou Security Analyst com viés regulatório.

---

## Por que esse projeto existe

A **Plataforma LGPD** nasceu como exercício pessoal de portfólio com três objetivos:

1. **Traduzir conceitos regulatórios em código.** A LGPD não é só política — é também como o sistema *implementa* o registro de operações (Art. 37), o relatório de impacto (Art. 38), o atendimento a direitos do titular (Art. 18), a resposta a incidentes (Art. 48) e a trilha de auditoria/accountability (Art. 6º, X). Este projeto força essa tradução em decisões técnicas concretas, do banco de questões ancorado em artigos até os módulos operacionais do Encarregado.

2. **Demonstrar fluência técnica suficiente pra dialogar com times de engenharia e segurança.** Um DPO que entende multi-tenancy, 2FA/TOTP, política de senha, CSP, rate limit e migrações de banco consegue conversar diretamente com a equipe técnica — sem intermediário que traduza requisitos.

3. **Exercitar a orquestração de um projeto técnico com auxílio de IA generativa.** A skill emergente do mercado pós-2024 não é "decorar sintaxe" — é **definir requisitos, validar arquitetura, traduzir necessidade de negócio em especificação** e usar IA para acelerar a entrega. O projeto foi conduzido nesse modelo, com suíte de testes verde e CI.

---

## Atuação neste projeto

**Papel:** Product Owner técnico, com auxílio de assistentes de IA generativa para a etapa de codificação.

**Entregas pessoais (direção e revisão do autor):**
- Definição de **requisitos, escopo e roadmap** (MVP educacional + fase 2 de gestão de privacidade).
- **Validação da arquitetura**: monólito Flask multi-tenant, banco agnóstico (SQLite ↔ PostgreSQL), segurança em camadas, empacotamento Docker.
- **Tradução de exigências LGPD em funcionalidades**: banco de questões e trilhas ancorados nos artigos; diagnóstico de maturidade; **ROPA (Art. 37)**; **RIPD (Art. 38)**; **direitos do titular (Art. 18)**; **incidentes (Art. 48)**; trilha de auditoria (Art. 6º, X).
- **Curadoria do conteúdo**: trilhas por setor (RH, Financeiro, TI, Marketing…) e banco de questões com base legal e explicação.
- **Decisões de trade-off**: SQLite *default* × Postgres-ready, 2FA opt-in × obrigatório por empresa, rate limit em memória × Redis, banco curado de questões × geração por IA.

**Etapa de codificação:** orquestrada com auxílio de IA generativa, sob direção e revisão do autor. A stack (Python/Flask, SQLAlchemy, Jinja, etc.) foi escolhida pela aderência ao caso de uso e pela exposição prévia em estudos, não por domínio prático prévio em escrita de código de produção.

---

## Formação relevante para o domínio

### Formação acadêmica

- **Bacharelado em Direito** — Anhanguera Educacional
- **Análise e Desenvolvimento de Sistemas** — Universidade Presbiteriana Mackenzie

### Pós-graduações ligadas a Privacy / Security / Tech

- **Privacidade e Proteção de Dados Pessoais (LGPD)** — Faculdade Focus
- **Direito, Inovação e Tecnologia** — Faculdade CERS
- **Direito Digital** — Legale Educacional
- **Segurança Digital, Governança e Gestão de Dados** — PUCRS

### Certificações ligadas ao tema deste projeto

- **DPO – Data Protection Officer (LGPD)** — CERS (2020)
- **Cybersecurity Essentials** — Cisco (2022)
- **Cibersegurança – Ameaças e Táticas de Prevenção** — FGV (2023)
- **Crise Cibernética e Continuidade de Negócios** — FGV (2023)
- **Fundamentos na Lei Geral de Proteção de Dados** — Certiprof Summit (2023)
- **Data Mapping: da Teoria à Prática** — IbiJus (2023)
- **AI for Leaders** — StartSe University (2024)
- **Visual Law** — Legale Educacional (2023)

---

## Outros projetos

- **[SentinelBR](https://github.com/andre28abr/SentinelBR-platform)** *(público)* — plataforma open-source de SIEM + LGPD para servidores Linux de PMEs brasileiras: detecção em tempo real, gestão de firewall, SELinux, resposta a incidentes e compliance nativa. Python/FastAPI + Go + React.

- **[VigiaOS](https://github.com/andre28abr/VigiaOS)** *(público)* — suíte de segurança, privacidade e LGPD para Fedora Workstation (GTK4 + libadwaita), com módulos de monitor, ferramentas, Red (pentest) e Blue (SOC).

- **SC Platform** *(privado, sob NDA — disponível para apresentação em entrevistas mediante solicitação)* — Plataforma SaaS multi-tenant para gestão de licitações públicas brasileiras (PNCP em tempo real, simulador FSM da Lei 14.133, robô de lances, extração de PDF com IA local, gerador de propostas, CRM, Telegram). Stack: **Python 3.14 + Flask 3 + SQLAlchemy 2 + PostgreSQL 15 + Redis + Playwright + ReportLab + Manifest V3 Chrome Extension**. ~75.000 linhas, 420 testes, 30 modelos, 245 rotas, 29 migrations.

---

## Vagas em foco

- **DPO / Encarregado de Dados** (LGPD)
- **Compliance & Governança (GRC)** — políticas, controles, mapeamento de dados
- **Privacy Engineering** — bridge entre legal e técnico
- **Security Analyst** com viés regulatório
- **Consultoria em LGPD / Privacy**

**Modalidades aceitas:** remoto, híbrido, presencial — Brasil.

---

## Contato

Para apresentação técnica de projetos privados (SC Platform), entrevistas, ou propostas de oportunidade, o canal de contato é o **[LinkedIn](https://linkedin.com/in/adreaugusto-azariasdesouza)**.

Dados de contato direto (email, telefone) são fornecidos sob demanda durante processo seletivo, via canais formais do RH.
