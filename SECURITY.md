# Política de segurança

## Reportando vulnerabilidades

Não abra issue pública para uma vulnerabilidade. Abra um [GitHub Security Advisory privado](https://github.com/andre28abr/lgpd-platform/security/advisories/new) ou escreva para o mantenedor pelo e-mail do [perfil](https://github.com/andre28abr).

A resposta sai em até 7 dias. É um projeto de portfólio sem SLA comercial: a gravidade pauta a prioridade.

## Escopo

**São vulnerabilidades reportáveis:** quebra de isolamento entre empresas (multi-tenant), bypass de autenticação ou do 2FA, escalada de privilégio entre papéis (colaborador, gestor, DPO, administrador), SQL injection, XSS, CSRF, SSRF, path traversal, adulteração da trilha de auditoria ou de provas e certificados, exposição de dados pessoais de titulares fora do tenant, dependências vulneráveis que afetem o projeto (rode `pip-audit` antes; o CI já roda).

**Não são vulnerabilidades:** credenciais de seed usadas apenas em ambiente de desenvolvimento (a instalação de produção exige senha própria), SQLite como banco padrão (é uma plataforma de demonstração; o caminho PostgreSQL existe), rate limit em memória no modo local.

## Defesas existentes

- Isolamento por empresa em todas as consultas; verificação por papel em cada rota.
- 2FA por TOTP, política de senha, hashing com salt, sessão com cookie httpOnly.
- CSP, cabeçalhos de segurança e rate limit em autenticação.
- Trilha de auditoria à prova de adulteração e integridade das provas.
- Chave secreta obrigatória em produção; segredos fora do repositório (`.env`).
- CI com lint, `pip-audit` e testes em SQLite e PostgreSQL.

## Histórico de divulgações

Nenhuma vulnerabilidade reportada até o momento. Auditoria interna de segurança concluída em setembro de 2026, com correções e testes de regressão registrados no histórico do projeto.
