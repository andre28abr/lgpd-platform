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

python app.py           # http://127.0.0.1:8080 (abre o navegador sozinho)
pytest                  # 35 testes

docker compose up --build   # alternativa: web + PostgreSQL + Redis
```

## Estrutura

- `app.py` — app factory (CSRF, cabeçalhos, logging com request-id, filtros Jinja, CLI).
- `config.py` · `extensions.py` · `security.py` · `utils.py` — base e configuração.
- `models.py` — 18 modelos multi-tenant (tudo escopado por `empresa_id`).
- `routes/` — 16 blueprints · `services/` — lógica (métricas, PDFs, diagnóstico, e-mail, 2FA, auditoria, relatórios).
- `templates/` (Jinja) · `static/` (CSS flat próprio, JS mínimo, sem framework).
- `seed.py` — conteúdo curado + demo · `tests/` — pytest · `migrations/` — Alembic.

## Convenções

- **Português** em tudo (UI, mensagens, commits).
- **Sem emojis** em nenhum lugar visível — UI, botões, títulos, modais, toasts, logs.
  Se precisar de ícone, **perguntar antes** (padrão: SVG flat do sistema).
- Banco **agnóstico** via SQLAlchemy: SQLite default, Postgres quando `DATABASE_URL`
  estiver setado. Não acoplar a um dialeto.
- Toda consulta de tenant é **escopada por `empresa_id`**; acesso cruzado → 404.
- Datas: usar **`utils.agora_utc()`**, nunca `datetime.utcnow()` (deprecado no 3.12+).
- **Não fazer push** sem o usuário pedir. Trabalhar na branch `main`.
- Ao usar o preview, **parar o servidor (porta 8080)** antes de devolver o controle.

## Armadilhas (já resolvidas — não regredir)

- **`.env` próprio:** `app.py` faz `load_dotenv(override=True)` do `.env` deste projeto,
  pra uma `DATABASE_URL` de outro projeto na máquina não "vazar". Não remover.
- **Testes:** `conftest.py` usa SQLite temporário; define `LGPD_SKIP_DOTENV=1` e
  `limiter.enabled = False` (o Flask-Limiter lê `RATELIMIT_ENABLED` só no `init_app`).
- **Migrações SQLite:** coluna `NOT NULL` nova exige `server_default`; FK nova em modo
  batch exige **nome explícito** (`create_foreign_key('fk_...', ...)`, nunca `None`).
- **Segurança:** CSRF por sessão em toda mutação, 2FA TOTP, CSP/cabeçalhos. Não afrouxar.

## Estado

Pilar 1 (educacional) + Pilar 2 (gestão de privacidade) completos. 35 testes, 6 migrações,
CI no GitHub Actions. Licença AGPL-3.0. Repo: https://github.com/andre28abr/lgpd-platform
