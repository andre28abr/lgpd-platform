# Plataforma LGPD — treinar, avaliar e operar a conformidade

> Plataforma web **multi-tenant** que leva a LGPD ao dia a dia da empresa: **treina** os times por setor (RH, Financeiro, TI, Marketing…), **avalia** com provas montadas por sorteio a partir de um banco curado ancorado nos artigos da lei, **certifica** com validade e reavaliação periódica, e entrega ao Encarregado (DPO) as ferramentas pra **operar a privacidade**: diagnóstico de maturidade, ROPA (Art. 37), RIPD (Art. 38), direitos do titular (Art. 18) e resposta a incidentes (Art. 48). Roda em **SQLite local com um comando** ou em **PostgreSQL + Redis via Docker**. Tudo em português.

[![ci](https://github.com/andre28abr/lgpd-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/andre28abr/lgpd-platform/actions/workflows/ci.yml)
![Status](https://img.shields.io/badge/status-MVP%20%2B%20fase%202%20completos-success)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Flask](https://img.shields.io/badge/flask-3-000000)
![Tests](https://img.shields.io/badge/tests-35%20passando-success)
![License](https://img.shields.io/badge/license-AGPL--3.0-orange)

---

## 👤 Autor

**André Augusto Azarias De Souza** — DPO / Encarregado de Dados · Compliance & GRC · Privacy Engineering

Profissional com mais de 18 anos de experiência em **gestão administrativa, compliance, governança da informação e proteção de dados pessoais**, com formação dupla em **Direito (Anhanguera)** e **Análise e Desenvolvimento de Sistemas (Mackenzie)**. Atuou por quase duas décadas como **Gerente Administrativo e Encarregado de Dados (DPO)** em organização do setor de saúde suplementar, com foco em adequação à LGPD, governança documental e interface com áreas técnicas.

Atualmente em **transição de carreira, com disponibilidade imediata**, esta plataforma foi conduzida como **product owner técnico, com auxílio de assistentes de IA generativa para a etapa de codificação** — exercitando a tradução de exigências regulatórias (LGPD) em uma plataforma funcional e demonstrando fluência técnica suficiente para dialogar com times de engenharia, segurança e privacidade.

→ **[Bio completa: AUTHOR.md](AUTHOR.md)** · [LinkedIn](https://linkedin.com/in/adreaugusto-azariasdesouza) · [GitHub Profile](https://github.com/andre28abr)

### 📂 Outros projetos do autor

- **[SentinelBR](https://github.com/andre28abr/SentinelBR-platform)** *(público)* — plataforma open-source de SIEM + LGPD para servidores Linux de PMEs: detecção em tempo real, firewall, SELinux, resposta a incidentes e compliance nativa.
- **[VigiaOS](https://github.com/andre28abr/VigiaOS)** *(público)* — suíte de segurança, privacidade e LGPD para Fedora Workstation (GTK4 + libadwaita).
- **SC Platform** *(privado, sob NDA — disponível para apresentação em entrevistas)* — SaaS multi-tenant de gestão de licitações públicas (PNCP, simulador da Lei 14.133, robô de lances, extração de PDF com IA local, CRM). ~75k linhas, 420 testes. Python 3.14 + Flask 3 + PostgreSQL + Redis.

---

## Sumário

1. [TL;DR](#tldr)
2. [A LGPD em 60 segundos](#a-lgpd-em-60-segundos)
3. [Por que essa plataforma existe](#por-que-essa-plataforma-existe)
4. [O que faz (módulos)](#o-que-faz-módulos)
5. [Mapa de artigos da LGPD](#mapa-de-artigos-da-lgpd)
6. [Arquitetura](#arquitetura)
7. [Stack & motivações](#stack--motivações)
8. [Segurança em camadas](#segurança-em-camadas)
9. [Estrutura do projeto](#estrutura-do-projeto)
10. [Quickstart](#quickstart)
11. [Configuração via env vars](#configuração-via-env-vars)
12. [Métricas do código](#métricas-do-código)
13. [Roadmap](#roadmap)
14. [Licença](#licença)

---

## TL;DR

**O que é:** uma plataforma que uma empresa instala (localmente ou numa VPS) para **medir e elevar a maturidade dos seus times em LGPD** e, no mesmo lugar, **operar a privacidade** sob a régua do Encarregado.

**Em uma frase:** treina os setores em trilhas por área, aplica provas sorteadas de um banco curado por artigo da lei, emite certificados com validade e ranking de conformidade — e dá ao DPO diagnóstico de maturidade, ROPA, RIPD, atendimento a direitos do titular e registro de incidentes, tudo multi-tenant e em português.

**O que diferencia:**
- **Ancorada na lei, não genérica.** Cada questão e trilha referencia o artigo (Art. 6, 7, 11, 18, 37, 38, 46, 48); a correção mostra a base legal.
- **Dois lados numa plataforma só:** o **educacional** (treina/avalia/certifica times) e o **operacional** (o DPO opera ROPA/RIPD/direitos/incidentes) — não é só um quiz.
- **Provas por sorteio** com banco curado, **cronômetro**, **certificado com validade + verificação pública por código** e **reavaliação periódica**.
- **Diagnóstico de maturidade** com score por dimensão, **plano de ação** e **gráfico de evolução**.
- **Roda leve:** SQLite com um comando para demo/local; **Postgres + Redis via Docker** para produção. Mesmo código (SQLAlchemy).
- **Segurança séria:** 2FA (TOTP) com códigos de recuperação e modo obrigatório por empresa, bloqueio de conta, CSRF, CSP, **trilha de auditoria** + CSV e **logging estruturado com request-id**.

**Stack:** Python 3.12+ · Flask 3 · SQLAlchemy 2 + Alembic · Flask-Login · Flask-Limiter (memória/Redis) · Jinja · ReportLab (PDF) · openpyxl (Excel) · pyotp + qrcode (2FA) · feedparser · Markdown + Bleach · Gunicorn · SQLite/PostgreSQL · Docker.

---

## A LGPD em 60 segundos

Glossário rápido pra entender as decisões do projeto:

| Termo | Significado |
|---|---|
| **LGPD** | Lei Geral de Proteção de Dados Pessoais (Lei 13.709/2018). Equivalente brasileiro do GDPR. |
| **Titular** | A pessoa natural a quem os dados se referem. |
| **Dado pessoal / sensível** | Informação que identifica alguém (Art. 5º, I); sensível inclui saúde, biometria, convicções etc. (Art. 5º, II). |
| **Controlador / Operador** | Quem decide sobre o tratamento × quem trata em nome do controlador (Art. 5º). |
| **DPO / Encarregado** | Responsável pela conformidade com a LGPD (Art. 41). Papel central na plataforma. |
| **Base legal** | A hipótese que autoriza o tratamento (Art. 7º e 11) — consentimento, obrigação legal, contrato, legítimo interesse… |
| **ROPA** | Registro das Operações de Tratamento (Art. 37): inventário de quais dados a empresa trata, com que finalidade e base legal. |
| **RIPD** | Relatório de Impacto à Proteção de Dados (Art. 38): avaliação de risco de um tratamento. |
| **Direitos do titular** | Acesso, correção, eliminação, portabilidade, revogação etc. (Art. 18). |
| **Incidente** | Evento de segurança que pode acarretar risco; pode exigir comunicação à ANPD e aos titulares (Art. 48). |
| **ANPD** | Autoridade Nacional de Proteção de Dados — fiscaliza e aplica sanções (multa de até 2%, limitada a R$ 50 mi por infração — Art. 52). |
| **Accountability** | Responsabilização e prestação de contas (Art. 6º, X) — sustenta a trilha de auditoria da plataforma. |

---

## Por que essa plataforma existe

A LGPD virou obrigação (multa de até 2% do faturamento, máx. R$ 50 milhões), mas a conformidade real esbarra em duas lacunas no chão da empresa:

1. **As pessoas não sabem.** RH trata dado sensível (saúde, biometria), Financeiro lida com retenção fiscal e bureaus, Marketing com consentimento e cookies — e cada setor erra de um jeito diferente. Treinamento genérico não cola.
2. **O DPO não tem ferramenta operacional.** Existe política no papel, mas falta onde **registrar o ROPA, avaliar risco (RIPD), atender pedidos de titular e responder a incidentes** com prazo e trilha de auditoria.

Esta plataforma endereça as duas: **treina e certifica os times por setor** (com reavaliação periódica e ranking) e, no mesmo lugar, **dá ao Encarregado os módulos operacionais** — tudo ancorado nos artigos, multi-tenant, e leve o bastante para rodar localmente ou numa VPS modesta.

---

## O que faz (módulos)

### Pilar 1 — Educacional
- **Trilhas de treinamento** por área, em Markdown, ancoradas na lei.
- **Banco de questões curado** (por área, artigo e dificuldade) — administrável pela própria empresa.
- **Provas por sorteio**: questões e alternativas embaralhadas a cada tentativa, com **cronômetro** e correção comentada (artigo + explicação).
- **Certificação** com nota de corte, **validade**, **PDF** (ReportLab) e **verificação pública por código**.
- **Ranking de conformidade** entre setores + **relatórios** em Excel e PDF.

### Pilar 2 — Gestão de privacidade (hub "Privacidade")
- **Diagnóstico de maturidade**: questionário em 5 dimensões, score ponderado, nível, **plano de ação**, **PDF** e **gráfico de evolução**.
- **ROPA** (Art. 37): inventário de tratamentos por setor (dados, finalidade, **base legal**, retenção, compartilhamento).
- **RIPD** (Art. 38): matriz de risco (probabilidade × impacto), risco residual, medidas e **PDF**.
- **Direitos do titular** (Art. 18): registro de pedidos com **prazo**, status e responsável.
- **Incidentes** (Art. 48): registro e resposta, com **comunicação à ANPD e aos titulares**.
- **Legislação**: feed RSS opcional (ANPD) + referências fixas.

### Administração & gestão
- Multi-tenant: **Empresa → Setores → Usuários**, com papéis (Encarregado/DPO, Gestor, Colaborador).
- CRUD de trilhas, questões e usuários; **reavaliações** (vencidos/vencendo) com notificação por e-mail/cron.
- **Configurações** de segurança (ex.: 2FA obrigatório por empresa) e **auditoria** consultável + CSV.

### Segurança
2FA (TOTP) com **códigos de recuperação**, reset pelo Encarregado e **modo obrigatório**; bloqueio de conta por tentativas; CSRF por sessão; cabeçalhos/CSP; senha com hash; HTML sanitizado; **logging estruturado com request-id**; escopo multi-tenant em todas as consultas.

---

## Mapa de artigos da LGPD

Onde cada artigo aparece no produto — a régua jurídica vira função:

| Artigo | Tema | Onde aparece |
|---|---|---|
| Art. 6º | Princípios / accountability | Trilhas, questões, trilha de auditoria |
| Art. 7º / 11 | Bases legais | ROPA, banco de questões, correção das provas |
| Art. 18 | Direitos do titular | Módulo "Direitos do titular" |
| Art. 37 | Registro de operações | Módulo ROPA |
| Art. 38 | Relatório de impacto | Módulo RIPD |
| Art. 41 | Encarregado (DPO) | Papel central, painel do Encarregado |
| Art. 46 | Segurança | Trilha de TI, política de segurança |
| Art. 48 | Incidentes | Módulo de Incidentes (comunicação ANPD/titular) |
| Art. 52 | Sanções | Conteúdo das trilhas e questões |

---

## Arquitetura

Monólito Flask com *app factory* e organização clássica em camadas:

- **`routes/`** — 16 blueprints (auth, painel, trilhas, provas, certificados, ranking, admin, diagnóstico, ROPA, RIPD, direitos, incidentes, legislação, privacidade, perfil, público).
- **`services/`** — lógica de negócio isolada (métricas, geração de PDF, diagnóstico, e-mail, recuperação 2FA, auditoria, relatórios).
- **`models.py`** — 18 modelos SQLAlchemy, multi-tenant (tudo escopado por `empresa_id`).
- **`templates/` + `static/`** — Jinja server-rendered, CSS flat próprio, JS mínimo (sem framework).
- **`migrations/`** — Alembic (6 migrações), *Postgres-ready*.

O banco é **agnóstico**: SQLite por padrão (zero config), PostgreSQL quando `DATABASE_URL` aponta para ele. O rate limit usa memória por padrão ou **Redis** via `RATELIMIT_STORAGE_URI`.

---

## Stack & motivações

| Camada | Tecnologia | Por quê |
|---|---|---|
| Web | **Flask 3 + Jinja** | Monólito server-rendered, simples de hospedar e auditar |
| ORM / migrações | **SQLAlchemy 2 + Alembic** | Banco agnóstico (SQLite ↔ Postgres) sem reescrever código |
| Auth / 2FA | **Flask-Login + pyotp + qrcode** | Sessão + TOTP com QR e códigos de recuperação |
| Rate limit | **Flask-Limiter** | Anti força-bruta; memória local ou Redis em produção |
| PDF / Excel | **ReportLab + openpyxl** | Certificados, RIPD e relatórios de conformidade |
| Conteúdo | **Markdown + Bleach** | Trilhas em Markdown, sanitizadas contra XSS |
| Feed | **feedparser** | Legislação/notícias da ANPD (opcional) |
| Deploy | **Gunicorn + Docker** | App + PostgreSQL + Redis em um comando |

---

## Segurança em camadas

- **CSRF** por sessão em todas as mutações (token validado em `before_request`).
- **2FA (TOTP)** opcional ou **obrigatório por empresa**, com QR Code e **códigos de recuperação** de uso único; reset pelo Encarregado.
- **Bloqueio temporário** de conta após tentativas malsucedidas + rate limit no login.
- **Cabeçalhos** de segurança: CSP, X-Frame-Options, nosniff, Referrer-Policy.
- **Senhas** com hash (Werkzeug); **HTML** das trilhas sanitizado (Bleach).
- **Trilha de auditoria** das ações sensíveis (Art. 6º, X) com exportação CSV.
- **Logging estruturado** (logfmt) com `request-id` e rotação de arquivo.
- **Multi-tenant**: toda consulta escopada por `empresa_id`; 404 em acesso cruzado.

---

## Estrutura do projeto

```
app.py            app factory, CSRF, headers, logging, filtros, CLI
config.py         configuração + resolução SQLite/Postgres
extensions.py     db, migrate, login, limiter (memória/Redis)
security.py       CSRF, cabeçalhos e política de senha
models.py         18 modelos multi-tenant
utils.py          helpers (datetime UTC timezone-safe)
routes/           16 blueprints
services/         métricas, PDFs, diagnóstico, e-mail, 2FA, auditoria, relatórios
templates/        Jinja (46 templates)
static/           CSS e JS
seed.py           biblioteca curada + empresa de demonstração
tests/            suíte pytest (35 testes)
migrations/       Alembic (6 migrações)
Dockerfile · docker-compose.yml · entrypoint.sh    empacotamento (web + Postgres + Redis)
.github/workflows/ci.yml                            CI (pytest)
```

---

## Quickstart

### Local (SQLite, um comando — macOS)

```bash
./INICIAR-MAC.command
```

Cria o ambiente, prepara o banco, popula a demonstração e abre o navegador em `http://127.0.0.1:8080`.

### Manual

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
flask db upgrade        # ou: flask init-db
flask seed
python app.py           # http://127.0.0.1:8080
```

### Docker (PostgreSQL + Redis)

```bash
docker compose up --build      # http://localhost:8080
```

### Testes

```bash
pip install -r requirements-dev.txt
pytest
```

### Contas de demonstração (senha `lgpd1234`)

| Papel | E-mail |
|------|--------|
| Encarregado (DPO) | dpo@acme.com.br |
| Gestor (RH) | gestor.rh@acme.com.br |
| Colaborador (RH) | ana@acme.com.br |
| Colaborador (Financeiro) | paula@acme.com.br |

---

## Configuração via env vars

| Variável | Padrão | Função |
|---|---|---|
| `SECRET_KEY` | dev | Assina sessões e tokens CSRF |
| `DATABASE_URL` | SQLite local | Vazio = SQLite; `postgresql://…` = Postgres |
| `RATELIMIT_STORAGE_URI` | `memory://` | `redis://…` para multi-worker |
| `SESSION_COOKIE_SECURE` | `false` | `true` atrás de HTTPS |
| `TEMPO_PROVA_MIN` | `15` | Tempo da prova (0 = sem limite) |
| `NOTA_CORTE` / `QUESTOES_POR_PROVA` | `70` / `8` | Regras de avaliação |
| `CERT_VALIDADE_DIAS` | `365` | Validade do certificado |
| `LOGIN_MAX_TENTATIVAS` / `LOGIN_BLOQUEIO_MIN` | `5` / `15` | Bloqueio de conta |
| `MAIL_SERVER` … | — | SMTP (sem ele, e-mail roda em *dry-run*) |
| `FEED_URL` | — | RSS de legislação/ANPD (opcional) |

---

## Métricas do código

- **~6.300 linhas** (4.317 Python + 1.685 templates + 329 CSS/JS), sem contar venv/migrações.
- **65 rotas**, **18 modelos**, **16 blueprints**, **10 serviços**, **46 templates**.
- **35 testes** (auth, CSRF, RBAC, provas, certificados, 2FA, lockout, diagnóstico, ROPA, RIPD, direitos, incidentes, exports), **6 migrações** Alembic, **CI** no GitHub Actions.

---

## Roadmap

- **Concluído:** Pilar 1 (educacional) e Pilar 2 (gestão de privacidade) completos; qualidade (testes, 2FA, auditoria, logging); empacotamento Docker.
- **Próximos passos:** PDF do diagnóstico por setor com comparativo; integração de e-mail transacional além do *dry-run*; webhooks/portal público para o titular abrir pedidos; painel de indicadores (KPIs de privacidade).

---

## Licença

[AGPL-3.0](LICENSE).
