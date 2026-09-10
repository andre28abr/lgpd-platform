# Plataforma LGPD — treinar, avaliar e operar a conformidade

> Plataforma web **multi-tenant** que leva a LGPD ao dia a dia da empresa: **treina** os times por setor (RH, Financeiro, TI, Marketing…), **avalia** com provas montadas por sorteio a partir de um banco curado ancorado nos artigos da lei, **certifica** com validade e reavaliação periódica, e entrega ao Encarregado (DPO) as ferramentas pra **operar a privacidade**: diagnóstico de maturidade, ROPA (Art. 37), RIPD (Art. 38), direitos do titular (Art. 18) e resposta a incidentes (Art. 48). Roda em **SQLite local com um comando** ou em **PostgreSQL + Redis via Docker**. Tudo em português.

[![ci](https://github.com/andre28abr/lgpd-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/andre28abr/lgpd-platform/actions/workflows/ci.yml)
![Status](https://img.shields.io/badge/status-MVP%20%2B%20fase%202%20completos-success)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Flask](https://img.shields.io/badge/flask-3-000000)
![Tests](https://img.shields.io/badge/tests-121%20passando-success)
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
- **Segurança séria:** 2FA (TOTP) com códigos de recuperação e modo obrigatório por empresa, bloqueio de conta, CSRF, CSP/HSTS, **trilha de auditoria encadeada por hash** (adulteração detectável) + CSV, reset de senha por link, e **logging estruturado com request-id**.
- **Conteúdo com fonte:** 229 questões e 7 trilhas ancoradas **exclusivamente** no texto da lei (Planalto) e nas normas e guias da ANPD — o dossiê de fontes está em [`docs/fontes-lgpd.md`](docs/fontes-lgpd.md) e o banco revisável em [`docs/banco-questoes.csv`](docs/banco-questoes.csv).
- **Testada como produto:** 121 testes, incluindo **isolamento multi-tenant com duas empresas**, e CI que roda lint, auditoria de dependências e a suíte inteira **também em PostgreSQL**.
- **Demonstrável sem infraestrutura:** duas empresas de exemplo, dados do Pilar 2 em situações reais (pedido atrasado, incidente sem ANPD), caixa de saída de e-mails visível sem SMTP, portal público do titular e `flask demo-reset` para recomeçar.

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
- **Trilhas de treinamento**: uma por área (RH, Financeiro, TI, Marketing, Atendimento, Jurídico/Compras e Geral), em Markdown, com **marcação de leitura** e progresso no painel do colaborador.
- **Banco de 229 questões** (30+ por área, 42 gerais), cada uma com **fonte** (artigo da lei, resolução, guia ou enunciado da ANPD) e explicação fiel — administrável e ampliável pela própria empresa.
- **Provas por sorteio**: 7 questões da área + 3 gerais, **equilíbrio de dificuldade**, alternativas embaralhadas, **cronômetro validado no servidor**, limite de tentativas por dia e correção comentada (fonte + explicação). Se o banco da área for pequeno demais, a prova não abre.
- **Certificação** com nota de corte, **validade**, **PDF com QR Code** (ReportLab) e **verificação pública por código**.
- **Ranking de conformidade** entre setores + **relatórios** em Excel e PDF.

### Pilar 2 — Gestão de privacidade (hub "Privacidade")
- **Diagnóstico de maturidade**: questionário em 5 dimensões, score ponderado, nível, **plano de ação**, **PDF**, **gráfico de evolução** e **comparativo por setor** (HTML e PDF).
- **ROPA** (Art. 37): inventário de tratamentos por setor (dados, finalidade, **base legal**, retenção, compartilhamento), com **exportação em Excel e PDF** e **importação de planilha** (xlsx/csv, com modelo).
- **RIPD** (Art. 38): matriz de risco (probabilidade × impacto), risco residual, medidas, **PDF** e **anexos** (evidências).
- **Direitos do titular** (Art. 18): **portal público** onde o titular abre o pedido e recebe um **protocolo**; fila do DPO com prazo, status, responsável e anexos.
- **Incidentes** (Art. 48): registro e resposta, comunicação à ANPD e aos titulares, contagem de **dias úteis** (Res. CD/ANPD nº 15/2024) e anexos.
- **Painel do Encarregado**: bloco **"Atenção agora"** (pedidos vencendo/atrasados, incidentes sem ANPD, RIPDs em rascunho) e **KPIs de privacidade** (pedidos no prazo, ROPA por base legal). `flask prazos --email` para o cron.
- **Legislação**: feed RSS opcional (ANPD) + referências fixas.

### Administração & gestão
- Multi-tenant: **Empresa → Setores → Usuários**, com papéis: **Encarregado/DPO** (altera tudo), **Gestor** (acompanha o setor e o Pilar 2 **em modo leitura**), **Colaborador** (treina e se certifica).
- CRUD de trilhas, questões e usuários; **reavaliações** (vencidos/vencendo) com notificação por e-mail/cron.
- **Configurações** (2FA obrigatório, remetente de e-mail por empresa), **auditoria** consultável + CSV, **caixa de saída de e-mails** (visível mesmo sem SMTP).
- **Ciclo de vida dos dados da própria plataforma**: anonimização de usuário desligado, expurgo por política de retenção (`flask expurgar`) e **exportação/importação da empresa em JSON**.

### Segurança
2FA (TOTP) com **códigos de recuperação**, reset pelo Encarregado, **modo obrigatório** e reautenticação por senha para desativar; bloqueio de conta por tentativas (sem enumeração de contas); **reset de senha por link** de uso único; CSRF por sessão; cabeçalhos/CSP/HSTS; senha com hash; HTML sanitizado; **trilha de auditoria encadeada por hash** (`flask auditoria-verificar`); **logging estruturado com request-id**; escopo multi-tenant em todas as consultas **e nas chaves estrangeiras vindas de formulários**.

---

## Conteúdo e fontes

O banco de questões e as trilhas seguem uma regra editorial única: **só entra o que está em fonte oficial** —
o texto compilado da Lei nº 13.709/2018 no Planalto, as Resoluções do Conselho Diretor da ANPD
(2/2022, 4/2023, 15/2024, 18/2024, 19/2024, 32/2026), o Enunciado 1/2023 e os Guias Orientativos da ANPD.
Cada questão carrega a fonte no campo exibido na correção. O que sustenta isso:

- [`docs/fontes-lgpd.md`](docs/fontes-lgpd.md) — dossiê com transcrição literal de 45 artigos, resumo fiel das normas da ANPD, URLs, data de acesso e a lista do que **não** pôde ser confirmado.
- [`docs/banco-questoes.csv`](docs/banco-questoes.csv) — as 229 questões com fonte, alternativa correta, incorretas e explicação, para revisão jurídica.
- `tests/test_banco_questoes.py` — o checklist automático: cobertura por área, forma, fonte obrigatória, unicidade, três níveis de dificuldade e o comportamento do sorteio.

A validação jurídica final é do Encarregado; o repositório entrega o material e a rastreabilidade.

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

- **`routes/`** — 17 blueprints (auth, painel, trilhas, provas, certificados, ranking, admin, diagnóstico, ROPA, RIPD, direitos, incidentes, legislação, privacidade, perfil, público, anexos).
- **`services/`** — lógica de negócio isolada (métricas, KPIs, prazos, PDFs, diagnóstico, e-mail e caixa de saída, reset de senha, recuperação 2FA, auditoria encadeada, relatórios, export/import do ROPA, anexos, ciclo de vida, portabilidade).
- **`conteudo/`** — a biblioteca curada: 229 questões e 7 trilhas, com fonte em cada item.
- **`models.py`** — 21 modelos SQLAlchemy, multi-tenant (tudo escopado por `empresa_id`).
- **`templates/` + `static/`** — Jinja server-rendered, CSS flat próprio, JS mínimo (sem framework).
- **`migrations/`** — Alembic (12 migrações), validadas em SQLite e PostgreSQL.

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
- **Trilha de auditoria** das ações sensíveis (Art. 6º, X) com exportação CSV, **encadeada por SHA-256**: alterar ou apagar um registro por fora do sistema quebra a cadeia, e `flask auditoria-verificar` aponta onde. Best-effort — nunca derruba a ação auditada.
- **Logging estruturado** (logfmt) com `request-id` e rotação de arquivo.
- **Multi-tenant**: toda consulta escopada por `empresa_id`; 404 em acesso cruzado. Ids de chave estrangeira enviados em formulários (`setor_id`, `ropa_id`, `responsavel_id`) são validados contra a empresa do usuário (`fk_do_tenant`). Testado com **duas empresas reais** na suíte.
- **Chave secreta nunca pública**: sem `SECRET_KEY` no ambiente, o app gera uma aleatória e persiste em `instance/` (fora do git).
- **Cronômetro da prova validado no servidor** — o countdown do navegador é só apoio visual.
- **Reset de senha por link** assinado (1 h, uso único), com resposta idêntica para e-mail conhecido ou não.
- **Reautenticação por senha** para desativar o 2FA ou regenerar códigos de recuperação.
- **PDFs à prova de marcação**: texto livre escapado antes do ReportLab (um `<` no texto não derruba a exportação).
- **Atrás de proxy**: `PROXY_FIX_HOPS` faz rate limit e IP da auditoria enxergarem o cliente real. `SESSION_COOKIE_SECURE=true` liga também o HSTS.
- **Dependências pinadas e auditadas** (`pip-audit` no CI); `HEALTHCHECK` no container via `/saude`, que pinga o banco.

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
services/         métricas, KPIs, prazos, PDFs, diagnóstico, e-mail + caixa de saída, 2FA,
                  auditoria encadeada, relatórios, ROPA (export/import), anexos, ciclo de vida,
                  portabilidade, reset de senha
conteudo/         banco de 229 questões + 7 trilhas (fonte em cada item)
docs/             dossiê de fontes oficiais e CSV de revisão do banco
templates/        Jinja (53 templates)
static/           CSS e JS
seed.py           atualiza a biblioteca (idempotente) + empresas de demonstração
tests/            suíte pytest (121 testes, inclui isolamento multi-tenant com 2 empresas)
migrations/       Alembic (12 migrações), validadas em SQLite e PostgreSQL
ruff.toml         lint (E/F/W/I/B/BLE)
Dockerfile · docker-compose.yml · entrypoint.sh    empacotamento (web + Postgres + Redis, healthcheck)
.github/workflows/ci.yml                            CI: ruff · pip-audit · pytest 3.12/3.13 (cobertura ≥ 85%) · PostgreSQL 16
```

---

## Quickstart

### Local (SQLite, um comando)

```bash
./iniciar.sh               # Linux e macOS   (primeira vez: chmod +x iniciar.sh)
INICIAR-WINDOWS.bat        # Windows (clique duplo)
./INICIAR-MAC.command      # macOS, pelo Finder
```

Cria o ambiente, prepara o banco, popula a demonstração e abre o navegador em `http://127.0.0.1:8080`.
Para recomeçar do zero: `./iniciar.sh --reset` (ou `flask demo-reset --confirmar`). Uma instalação
antiga recebe o banco de questões novo com um simples `flask seed` — nada é recriado.

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

### Testes e qualidade

```bash
pip install -r requirements-dev.txt
pytest                          # 121 testes (SQLite temporário)
pytest --cov=. --cov-fail-under=85
ruff check .                    # lint
pip-audit -r requirements.txt   # vulnerabilidades conhecidas
flask auditoria-verificar       # integridade da trilha de auditoria
flask exportar-questoes docs/banco-questoes.csv   # banco para revisão jurídica
flask prazos --email            # alertas de prazo (cron)
flask expurgar                  # política de retenção (AUDITORIA_RETENCAO_DIAS / EMAILS_RETENCAO_DIAS)
```

Para rodar a mesma suíte contra um PostgreSQL: `LGPD_TEST_DATABASE_URL=postgresql://... pytest` (é o que o CI faz).

### Contas de demonstração (senha `lgpd1234`)

| Papel | E-mail |
|------|--------|
| Encarregado (DPO) | dpo@acme.com.br |
| Gestor (RH) | gestor.rh@acme.com.br |
| Colaborador (RH) | ana@acme.com.br |
| Colaborador (Financeiro) | paula@acme.com.br |
| Encarregado da 2ª empresa (isolamento) | dpo@novaera.com.br |

Sem login: o **portal do titular** da demo fica em `/titular/acme` (link na tela de entrada) e a
verificação pública de certificados em `/certificados/verificar/<código>`.

---

## Configuração via env vars

| Variável | Padrão | Função |
|---|---|---|
| `SECRET_KEY` | gerada em `instance/` | Assina sessões, CSRF e links de reset. Defina explicitamente em produção |
| `DATABASE_URL` | SQLite local | Vazio = SQLite; `postgresql://…` = Postgres |
| `RATELIMIT_STORAGE_URI` | `memory://` | `redis://…` para multi-worker |
| `SESSION_COOKIE_SECURE` | `false` | `true` atrás de HTTPS (liga também o HSTS) |
| `PROXY_FIX_HOPS` | `0` | Saltos confiáveis de `X-Forwarded-*` atrás de proxy reverso (normalmente `1`) |
| `FLASK_DEBUG` | `0` | `1` liga debugger/reloader no `python app.py` (só desenvolvimento) |
| `TEMPO_PROVA_MIN` | `15` | Tempo da prova (0 = sem limite), validado no servidor |
| `NOTA_CORTE` | `70` | Nota mínima para o certificado |
| `QUESTOES_POR_PROVA` / `QUESTOES_GERAIS_POR_PROVA` | `7` / `3` | Questões da área + gerais em cada prova |
| `POOL_MINIMO_FATOR` / `PROVAS_POR_DIA` | `2` / `3` | Banco mínimo (× sorteado) e tentativas diárias |
| `AUDITORIA_RETENCAO_DIAS` / `EMAILS_RETENCAO_DIAS` | `0` / `90` | Retenção dos dados da própria plataforma (`flask expurgar`) |
| `ANEXO_MAX_MB` / `ANEXOS_DIR` | `5` / `instance/uploads` | Anexos (evidências) |
| `CERT_VALIDADE_DIAS` | `365` | Validade do certificado |
| `LOGIN_MAX_TENTATIVAS` / `LOGIN_BLOQUEIO_MIN` | `5` / `15` | Bloqueio de conta |
| `MAIL_SERVER` … | — | SMTP (sem ele, e-mail roda em *dry-run*) |
| `FEED_URL` | — | RSS de legislação/ANPD (opcional) |

---

## Métricas do código

- **~10.800 linhas** (5.213 Python + 1.531 de conteúdo curado + 1.554 de testes + 2.113 templates + 362 CSS/JS), sem contar venv/migrações.
- **82 rotas**, **21 modelos**, **17 blueprints**, **19 serviços**, **53 templates**, **229 questões**, **7 trilhas**.
- **121 testes** (auth, CSRF, RBAC e papéis, **isolamento multi-tenant**, provas 7+3 e cronômetro, certificados, 2FA e reautenticação, lockout, reset de senha, diagnóstico e comparativo, ROPA export/import, RIPD, portal do titular, prazos e KPIs, anexos, anonimização e expurgo, export/import da empresa, PDFs, auditoria encadeada, métricas sem N+1, **checklist do banco de questões**), cobertura ~90%.
- **12 migrações** Alembic, validadas em SQLite **e PostgreSQL 16** no CI; **lint** (ruff) e **pip-audit** a cada push.

---

## Roadmap

- **Concluído:** Pilar 1 (educacional) e Pilar 2 (gestão de privacidade) completos; qualidade (testes, 2FA, auditoria, logging); empacotamento Docker.
- **Concluído (set/2026) — ciclo de auditoria de segurança e hardening:** chave secreta nunca pública; validação de FKs cross-tenant; cronômetro no servidor; migrações funcionando em PostgreSQL; PDFs com escape; métricas sem N+1; sessão com prazo real; ProxyFix/HSTS; reautenticação no 2FA; reset de senha; auditoria encadeada por hash; CI com lint, pip-audit e Postgres.
- **Concluído (set/2026) — produto e conteúdo:** Gestor em modo leitura no Pilar 2; caixa de saída de e-mails; seed com 2 empresas e `demo-reset`; scripts Windows/Linux; portal público do titular com protocolo; prazos vivos (dias úteis, Res. 15/2024) e KPIs; anexos como evidência; anonimização, expurgo e portabilidade da empresa; banco de 229 questões e 7 trilhas com fonte oficial; prova 7+3 balanceada; QR no certificado; trilha lida; comparativo por setor; importação do ROPA; tour por papel.
- **Próximos passos (fora do escopo de demonstração):** e-mail transacional real (SMTP/serviço); Redis para múltiplos workers; SSO; e-mail único por empresa (hoje é global); feriados no cálculo de dias úteis.

---

## Licença

[AGPL-3.0](LICENSE).
