# CLAUDE.md

Orientações para o Claude Code trabalhar neste repositório. Leia antes de agir.

## O que é

Plataforma LGPD — app web **Flask multi-tenant** para **treinar, avaliar e certificar**
os setores de uma empresa em LGPD (Pilar 1) e **operar a privacidade** sob o
Encarregado/DPO (Pilar 2: diagnóstico de maturidade, ROPA, RIPD, direitos do titular,
incidentes, legislação). **SQLite por padrão, PostgreSQL-ready.** Tudo em português.
Detalhes em [README.md](README.md) e [AUTHOR.md](AUTHOR.md).

## Como rodar / testar

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt     # dev (inclui pytest); use requirements.txt p/ só runtime
export FLASK_APP=app

flask db upgrade        # aplica migrações (ou: flask init-db p/ SQLite rápido)
flask seed              # empresa de demo — login dpo@acme.com.br / senha lgpd1234

python app.py           # http://127.0.0.1:8080 (abre o navegador sozinho; FLASK_DEBUG=1 p/ reloader)
pytest                  # 101 testes (SQLite temp) · LGPD_TEST_DATABASE_URL=postgresql://... p/ Postgres
flask demo-reset --confirmar   # recria a demo do zero (só SQLite)
ruff check . && pip-audit -r requirements.txt   # o CI exige os dois limpos + cobertura ≥ 85%

docker compose up --build   # alternativa: web + PostgreSQL + Redis
```

## Estrutura

- `app.py` — app factory (CSRF, cabeçalhos, logging com request-id, filtros Jinja, CLI).
- `config.py` · `extensions.py` · `security.py` · `utils.py` — base e configuração.
- `models.py` — 21 modelos multi-tenant (tudo escopado por `empresa_id`).
- `routes/` — 17 blueprints · `services/` — lógica (métricas, KPIs, prazos, PDFs, e-mail/caixa de saída,
  auditoria encadeada, anexos, ciclo de vida, portabilidade, ROPA export/import…).
- `conteudo/` — banco de questões e trilhas (**só fonte oficial**; ver regra abaixo) · `docs/` — dossiê de fontes e CSV.
- `templates/` (Jinja) · `static/` (CSS flat próprio, JS mínimo, sem framework).
- `seed.py` — `atualizar_biblioteca()` idempotente + empresas demo · `tests/` — pytest · `migrations/` — Alembic.

## Convenções

- **Português** em tudo (UI, mensagens, commits).
- **Sem emojis** em nenhum lugar visível — UI, botões, títulos, modais, toasts, logs.
  Se precisar de ícone, **perguntar antes** (padrão: SVG flat do sistema).
- Banco **agnóstico** via SQLAlchemy: SQLite default, Postgres quando `DATABASE_URL`
  estiver setado. Não acoplar a um dialeto.
- Toda consulta de tenant é **escopada por `empresa_id`**; acesso cruzado → 404.
- **Id de FK vindo de formulário** (`setor_id`, `ropa_id`, `responsavel_id`…) passa por
  `routes._helpers.fk_do_tenant()` — nunca `int(request.form[...])` direto.
- **Texto livre em PDF** passa por `services.pdf_utils.esc()` antes do `Paragraph`.
- Datas: usar **`utils.agora_utc()`**, nunca `datetime.utcnow()` (deprecado no 3.12+).
- **Auditoria** via `services.auditoria.registrar()` — é best-effort e encadeia hash; não
  gravar `AuditLog` direto.
- **Papéis no Pilar 2:** só o Encarregado altera; o Gestor visualiza (`gestor_somente_leitura`).
  Rotas de escrita novas nesses módulos herdam o bloqueio pelo `before_request`.
- **Conteúdo (questões/trilhas):** só o que está no texto da lei (Planalto) ou em norma/guia
  oficial da ANPD, com a fonte no campo `artigo`. Nada de "praxe de mercado". Regenerar
  `docs/banco-questoes.csv` (`flask exportar-questoes`) ao mexer no banco. O checklist é
  `tests/test_banco_questoes.py`. Questões que saem do banco são **desativadas** pelo seed, não apagadas.
- **Demo-first:** o projeto é uma demonstração para baixar e rodar local. Não exigir serviço
  externo (SMTP, Redis, VPS) para nenhuma funcionalidade; o caminho Docker/Postgres deve
  continuar funcionando, mas é opcional.
- **Não fazer push** sem o usuário pedir. Trabalhar na branch `main`.
- Ao usar o preview, **parar o servidor (porta 8080)** antes de devolver o controle.

## Armadilhas (já resolvidas — não regredir)

- **`.env` próprio:** `app.py` faz `load_dotenv(override=True)` do `.env` deste projeto,
  pra uma `DATABASE_URL` de outro projeto na máquina não "vazar". Não remover.
- **Testes:** `conftest.py` usa SQLite temporário; define `LGPD_SKIP_DOTENV=1` e
  `limiter.enabled = False` (o Flask-Limiter lê `RATELIMIT_ENABLED` só no `init_app`).
- **Migrações SQLite:** coluna `NOT NULL` nova exige `server_default`; FK nova em modo
  batch exige **nome explícito** (`create_foreign_key('fk_...', ...)`, nunca `None`).
- **Migrações Postgres:** default booleano é `sa.false()`, **nunca** `sa.text('0')` — o
  Postgres rejeita `DEFAULT 0` em coluna boolean e o `upgrade` inteiro dá rollback.
  O CI roda as migrações num Postgres real justamente para isso.
- **Autoflush:** um helper que consulta o banco no meio do preenchimento de um objeto
  novo já na sessão precisa de `db.session.no_autoflush` (ver `fk_do_tenant`).
- **SECRET_KEY:** sem env var, `app.py` gera e persiste em `instance/secret_key`. Nunca
  reintroduzir um default literal (nem no `.env.example`, nem no `docker-compose.yml`).
- **Segurança:** CSRF por sessão em toda mutação, 2FA TOTP (desativar exige senha), CSP/HSTS,
  cronômetro da prova validado no servidor. Não afrouxar.

## Estado

Pilar 1 (educacional) + Pilar 2 (gestão de privacidade) completos. Ciclo de auditoria de
segurança, hardening e melhorias de produto/conteúdo concluído em set/2026 (detalhes no
Roadmap do README). 101 testes, 12 migrações, 229 questões, CI (ruff · pip-audit ·
pytest 3.12/3.13 · PostgreSQL 16). Licença AGPL-3.0. Repo: https://github.com/andre28abr/lgpd-platform
