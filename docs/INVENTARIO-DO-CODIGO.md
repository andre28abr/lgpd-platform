# Inventário do código: lgpd-platform

> Gerado por `raiz/maquina/inventario.py` em 2026-09-20, direto do código. Não editar à mão: regenerar ao fechar um bloco de trabalho. Serve de mapa para quem vai mexer no projeto; a explicação do porquê está no README, no CLAUDE.md e nos docs do repositório. Testes são contados por função declarada; o pytest e o cargo podem reportar mais execuções por causa de parametrização.

## Resumo

| Linguagem | Números |
|---|---|
| Python | 63 módulos, 315 funções, 78 rotas, 21 modelos, 121 testes em 23 arquivos |
| Web | 0 componentes, 2 módulos JS/TS, 0 testes em 0 arquivos |

## Python

### Módulos

| Arquivo | O que é (docstring) | Classes | Funções | Linhas |
|---|---|---|---|---|
| `app.py` | App factory da Plataforma LGPD. | 0 | 28 | 410 |
| `config.py` | Configuração da aplicação. | 1 | 4 | 103 |
| `conteudo/__init__.py` | Biblioteca curada: banco de questões e trilhas, chaveados por área. | 0 | 0 | 19 |
| `conteudo/questoes_a.py` | Banco de questões — parte A: GERAL, RH e FINANCEIRO. | 0 | 0 | 555 |
| `conteudo/questoes_b.py` | Banco de questões — parte B: MARKETING, TI, ATENDIMENTO e JURIDICO. | 0 | 0 | 654 |
| `conteudo/trilhas.py` | Trilhas de treinamento (Markdown), uma por área, casadas com o banco de questões. | 0 | 0 | 307 |
| `extensions.py` | Instâncias das extensões Flask, isoladas para evitar import circular. | 0 | 0 | 21 |
| `migrations/env.py` |  | 0 | 6 | 113 |
| `migrations/versions/3fd207b0885f_2fa_bloqueio_de_conta_e_tempo_de_prova.py` | 2fa, bloqueio de conta e tempo de prova | 0 | 2 | 45 |
| `migrations/versions/40992fa1d33a_diagnostico_de_maturidade_e_auditoria.py` | diagnostico de maturidade e auditoria | 0 | 2 | 103 |
| `migrations/versions/7a06145bac02_ropa_e_pedidos_do_titular.py` | ropa e pedidos do titular | 0 | 2 | 76 |
| `migrations/versions/9d4da826ffc0_esquema_inicial.py` | esquema inicial | 0 | 2 | 226 |
| `migrations/versions/a2e6c9d1f4b7_anonimizacao_de_usuario.py` | anonimizacao de usuario | 0 | 2 | 26 |
| `migrations/versions/afce8b02a0a7_2fa_obrigatorio_recovery_codes_e_.py` | 2fa obrigatorio, recovery codes e diagnostico por setor | 0 | 2 | 58 |
| `migrations/versions/b3f7e1c9d5a2_trilha_leituras.py` | leitura de trilhas (progresso do treinamento) | 0 | 2 | 40 |
| `migrations/versions/c7a1e5b2d9f0_auditoria_encadeada_e_remetente.py` | auditoria encadeada por hash e remetente de e-mail por empresa | 0 | 2 | 33 |
| `migrations/versions/d8b2f4a6c1e3_caixa_de_saida_de_emails.py` | caixa de saida de e-mails | 0 | 2 | 43 |
| `migrations/versions/e9c3a7b5d2f1_protocolo_e_origem_do_pedido.py` | protocolo publico e origem do pedido do titular | 0 | 2 | 30 |
| `migrations/versions/eaedbce82aff_ripd_e_incidentes.py` | ripd e incidentes | 0 | 2 | 77 |
| `migrations/versions/f1d4b8c2a6e5_anexos_evidencias.py` | anexos (evidencias) de RIPD, incidente e pedido do titular | 0 | 2 | 45 |
| `models.py` | Modelo de dados multi-tenant da Plataforma LGPD. | 21 | 49 | 699 |
| `routes/__init__.py` |  | 0 | 0 | 1 |
| `routes/_helpers.py` | Utilitários compartilhados pelos blueprints. | 0 | 9 | 89 |
| `routes/admin.py` | Administração do tenant (somente Encarregado): setores, usuários, trilhas e questões. | 0 | 22 | 426 |
| `routes/anexos.py` | Anexos (evidências): o Encarregado envia e exclui; o Gestor pode baixar. | 0 | 6 | 82 |
| `routes/auth.py` | Autenticação: login (rate limit, bloqueio de conta, 2FA), logout e cadastro. | 0 | 8 | 217 |
| `routes/certificados.py` | Certificados: listagem, PDF e verificação pública por código. | 0 | 3 | 49 |
| `routes/diagnostico.py` | Diagnóstico de maturidade em privacidade (nível empresa). | 0 | 14 | 182 |
| `routes/direitos.py` | Pedidos do titular (Art. 18): registro e acompanhamento. | 0 | 5 | 94 |
| `routes/incidentes.py` | Incidentes de segurança (Art. 48): registro e acompanhamento. | 0 | 7 | 107 |
| `routes/legislacao.py` | Legislação: feed (ANPD) opcional + referências fixas. | 0 | 1 | 37 |
| `routes/painel.py` | Painel inicial, adaptado ao papel do usuário. | 0 | 1 | 44 |
| `routes/perfil.py` | Perfil do usuário: 2FA (TOTP) com códigos de recuperação. | 0 | 8 | 109 |
| `routes/privacidade.py` | Hub de Gestão de Privacidade — agrega os módulos da fase 2. | 0 | 1 | 26 |
| `routes/provas.py` | Avaliações: sorteio de questões, aplicação, correção e emissão de certificado. | 0 | 9 | 226 |
| `routes/publico.py` | Páginas públicas (sem login): política, healthcheck e o portal do titular. | 0 | 6 | 86 |
| `routes/ranking.py` | Ranking de conformidade entre os setores + exportações (Excel/PDF). | 0 | 3 | 39 |
| `routes/ripd.py` | RIPD — Relatório de Impacto à Proteção de Dados (Art. 38). | 0 | 7 | 110 |
| `routes/ropa.py` | ROPA — Registro das operações de tratamento (Art. 37). | 0 | 10 | 134 |
| `routes/trilhas.py` | Trilhas de treinamento (conteúdo curado em Markdown) e progresso de leitura. | 0 | 7 | 75 |
| `security.py` | Proteções transversais: CSRF por sessão e cabeçalhos de segurança. | 0 | 4 | 59 |
| `seed.py` | Popula a biblioteca curada (trilhas + questões) e as empresas de demonstração. | 0 | 5 | 306 |
| `services/__init__.py` |  | 0 | 0 | 1 |
| `services/anexos.py` | Anexos como evidência: validação, armazenamento em disco e escopo por tenant. | 0 | 6 | 95 |
| `services/auditoria.py` | Trilha de auditoria: registra ações sensíveis para accountability (Art. 6º, X). | 0 | 6 | 110 |
| `services/certificado_pdf.py` | Geração do certificado de conformidade em PDF (reportlab). | 0 | 1 | 90 |
| `services/ciclo_vida.py` | Ciclo de vida dos dados da PRÓPRIA plataforma — a LGPD aplicada a ela mesma. | 0 | 2 | 70 |
| `services/diagnostico.py` | Cálculo do diagnóstico de maturidade em privacidade. | 0 | 2 | 55 |
| `services/diagnostico_pdf.py` | PDF do resultado do diagnóstico de maturidade. | 0 | 2 | 83 |
| `services/email.py` | Envio de e-mail por SMTP, com fallback "dry-run" quando não há servidor. | 0 | 3 | 83 |
| `services/kpis.py` | Indicadores de privacidade do Encarregado (Pilar 2), calculados em poucas consultas. | 0 | 1 | 37 |
| `services/metricas.py` | Métricas de conformidade: progresso individual, por setor e ranking da empresa. | 1 | 10 | 155 |
| `services/notificacoes.py` | Notificações por e-mail: reavaliações, pedidos de titular e incidentes. | 0 | 5 | 72 |
| `services/pdf_utils.py` | Utilidades compartilhadas pelos PDFs gerados com ReportLab. | 0 | 2 | 22 |
| `services/portabilidade.py` | Exportar e importar uma empresa inteira em JSON (portabilidade/backup do tenant). | 0 | 6 | 212 |
| `services/prazos.py` | Prazos vivos: o que o Encarregado precisa olhar agora. | 0 | 3 | 97 |
| `services/recovery.py` | Códigos de recuperação de uso único para o 2FA. | 0 | 3 | 35 |
| `services/relatorios.py` | Relatórios exportáveis: ranking em Excel e conformidade em PDF. | 0 | 2 | 73 |
| `services/ripd_pdf.py` | PDF do RIPD — Relatório de Impacto à Proteção de Dados (Art. 38). | 0 | 1 | 54 |
| `services/ropa_export.py` | Exportação do ROPA (Art. 37) em Excel e PDF. | 0 | 3 | 80 |
| `services/ropa_import.py` | Importação do ROPA a partir de planilha (xlsx ou csv) — o inverso da exportação. | 0 | 5 | 123 |
| `services/senha.py` | Redefinição de senha por link temporário enviado por e-mail. | 0 | 4 | 47 |
| `utils.py` | Utilidades pequenas, sem dependências da aplicação. | 0 | 1 | 13 |

### Rotas HTTP

| Blueprint/Router | Métodos | Caminho | Handler | Arquivo |
|---|---|---|---|---|
| bp | GET | `/admin/` | `index` | `routes/admin.py` |
| bp | GET | `/admin/auditoria` | `auditoria` | `routes/admin.py` |
| bp | GET | `/admin/auditoria.csv` | `auditoria_csv` | `routes/admin.py` |
| bp | GET,POST | `/admin/configuracoes` | `configuracoes` | `routes/admin.py` |
| bp | GET | `/admin/emails` | `emails` | `routes/admin.py` |
| bp | GET | `/admin/exportar.json` | `exportar_json` | `routes/admin.py` |
| bp | GET | `/admin/questoes` | `questoes` | `routes/admin.py` |
| bp | POST | `/admin/questoes/<int:questao_id>/excluir` | `questao_excluir` | `routes/admin.py` |
| bp | GET,POST | `/admin/questoes/nova` | `questao_form` | `routes/admin.py` |
| bp | GET | `/admin/reavaliacoes` | `reavaliacoes` | `routes/admin.py` |
| bp | POST | `/admin/reavaliacoes/notificar` | `reavaliacoes_notificar` | `routes/admin.py` |
| bp | GET,POST | `/admin/setores` | `setores` | `routes/admin.py` |
| bp | GET | `/admin/trilhas` | `trilhas` | `routes/admin.py` |
| bp | POST | `/admin/trilhas/<int:trilha_id>/excluir` | `trilha_excluir` | `routes/admin.py` |
| bp | GET,POST | `/admin/trilhas/nova` | `trilha_form` | `routes/admin.py` |
| bp | GET,POST | `/admin/usuarios` | `usuarios` | `routes/admin.py` |
| bp | GET,POST | `/admin/usuarios/<int:usuario_id>/editar` | `usuario_editar` | `routes/admin.py` |
| bp | GET | `/anexos/<int:anexo_id>` | `baixar` | `routes/anexos.py` |
| bp | POST | `/anexos/<int:anexo_id>/excluir` | `excluir` | `routes/anexos.py` |
| bp | POST | `/anexos/<tipo>/<int:alvo_id>` | `enviar` | `routes/anexos.py` |
| bp | GET,POST | `/cadastro` | `cadastro` | `routes/auth.py` |
| bp | GET,POST | `/login` | `login` | `routes/auth.py` |
| bp | GET,POST | `/login/2fa` | `login_2fa` | `routes/auth.py` |
| bp | POST | `/logout` | `logout` | `routes/auth.py` |
| bp | GET,POST | `/senha/esqueci` | `esqueci_senha` | `routes/auth.py` |
| bp | GET,POST | `/senha/redefinir/<token>` | `redefinir_senha` | `routes/auth.py` |
| bp | GET | `/certificados/` | `listar` | `routes/certificados.py` |
| bp | GET | `/certificados/<int:cert_id>.pdf` | `pdf` | `routes/certificados.py` |
| bp | GET | `/certificados/verificar/<codigo>` | `verificar` | `routes/certificados.py` |
| bp | GET | `/diagnostico/` | `index` | `routes/diagnostico.py` |
| bp | GET | `/diagnostico/<int:diag_id>` | `responder` | `routes/diagnostico.py` |
| bp | GET | `/diagnostico/<int:diag_id>/pdf` | `pdf` | `routes/diagnostico.py` |
| bp | POST | `/diagnostico/<int:diag_id>/responder` | `salvar` | `routes/diagnostico.py` |
| bp | GET | `/diagnostico/<int:diag_id>/resultado` | `resultado` | `routes/diagnostico.py` |
| bp | GET | `/diagnostico/comparativo` | `comparativo` | `routes/diagnostico.py` |
| bp | GET | `/diagnostico/comparativo.pdf` | `comparativo_pdf` | `routes/diagnostico.py` |
| bp | POST | `/diagnostico/iniciar` | `iniciar` | `routes/diagnostico.py` |
| bp | GET | `/direitos/` | `listar` | `routes/direitos.py` |
| bp | GET,POST | `/direitos/<int:pid>` | `gerir` | `routes/direitos.py` |
| bp | GET,POST | `/direitos/novo` | `novo` | `routes/direitos.py` |
| bp | GET | `/incidentes/` | `listar` | `routes/incidentes.py` |
| bp | GET,POST | `/incidentes/<int:iid>` | `gerir` | `routes/incidentes.py` |
| bp | GET,POST | `/incidentes/novo` | `novo` | `routes/incidentes.py` |
| bp | GET | `/legislacao/` | `index` | `routes/legislacao.py` |
| bp | GET | `/` | `index` | `routes/painel.py` |
| bp | GET | `/perfil/` | `index` | `routes/perfil.py` |
| bp | GET,POST | `/perfil/2fa/ativar` | `ativar_2fa` | `routes/perfil.py` |
| bp | GET | `/perfil/2fa/codigos` | `codigos` | `routes/perfil.py` |
| bp | POST | `/perfil/2fa/codigos/regenerar` | `regenerar_codigos` | `routes/perfil.py` |
| bp | POST | `/perfil/2fa/desativar` | `desativar_2fa` | `routes/perfil.py` |
| bp | GET | `/privacidade/` | `index` | `routes/privacidade.py` |
| bp | GET | `/provas/` | `index` | `routes/provas.py` |
| bp | GET | `/provas/<int:prova_id>` | `realizar` | `routes/provas.py` |
| bp | POST | `/provas/<int:prova_id>/responder` | `responder` | `routes/provas.py` |
| bp | GET | `/provas/<int:prova_id>/resultado` | `resultado` | `routes/provas.py` |
| bp | POST | `/provas/iniciar` | `iniciar` | `routes/provas.py` |
| bp | GET | `/politica-de-privacidade` | `politica` | `routes/publico.py` |
| bp | GET | `/saude` | `saude` | `routes/publico.py` |
| bp | GET,POST | `/titular/<slug>` | `titular` | `routes/publico.py` |
| bp | POST | `/titular/<slug>/consultar` | `titular_consultar` | `routes/publico.py` |
| bp | GET | `/titular/<slug>/protocolo/<protocolo>` | `titular_protocolo` | `routes/publico.py` |
| bp | GET | `/ranking/` | `index` | `routes/ranking.py` |
| bp | GET | `/ranking/exportar.xlsx` | `exportar_xlsx` | `routes/ranking.py` |
| bp | GET | `/ranking/relatorio.pdf` | `relatorio_pdf` | `routes/ranking.py` |
| bp | GET | `/ripd/` | `listar` | `routes/ripd.py` |
| bp | POST | `/ripd/<int:rid>/excluir` | `excluir` | `routes/ripd.py` |
| bp | GET | `/ripd/<int:rid>/pdf` | `pdf` | `routes/ripd.py` |
| bp | GET,POST | `/ripd/novo` | `form` | `routes/ripd.py` |
| bp | GET | `/ropa/` | `listar` | `routes/ropa.py` |
| bp | POST | `/ropa/<int:reg_id>/excluir` | `excluir` | `routes/ropa.py` |
| bp | GET | `/ropa/exportar.xlsx` | `exportar_xlsx` | `routes/ropa.py` |
| bp | POST | `/ropa/importar` | `importar` | `routes/ropa.py` |
| bp | GET | `/ropa/modelo.xlsx` | `modelo_xlsx` | `routes/ropa.py` |
| bp | GET,POST | `/ropa/novo` | `form` | `routes/ropa.py` |
| bp | GET | `/ropa/relatorio.pdf` | `relatorio_pdf` | `routes/ropa.py` |
| bp | GET | `/trilhas/` | `listar` | `routes/trilhas.py` |
| bp | GET | `/trilhas/<slug>` | `ver` | `routes/trilhas.py` |
| bp | POST | `/trilhas/<slug>/lida` | `marcar_lida` | `routes/trilhas.py` |

### Modelos (ORM)

| Modelo | Tabela | Campos | Principais campos | Arquivo |
|---|---|---|---|---|
| `Empresa` | empresas | 9 | id, nome, slug, ativo, mfa_obrigatorio, email_remetente, criado_em, setores, usuarios | `models.py` |
| `Setor` | setores | 9 | id, empresa_id, nome, slug, area, descricao, criado_em, empresa, usuarios | `models.py` |
| `Usuario` | usuarios | 20 | id, empresa_id, setor_id, nome, email, senha_hash, papel, ativo, criado_em, ultimo_login, totp_secret, mfa_ativo, tentativas_falhas, bloqueado_ate … | `models.py` |
| `Trilha` | trilhas | 11 | id, empresa_id, area, titulo, slug, resumo, conteudo_md, ordem, publicada, criado_em, atualizado_em | `models.py` |
| `TrilhaLeitura` | trilha_leituras | 4 | id, usuario_id, trilha_id, lido_em | `models.py` |
| `Questao` | questoes | 10 | id, empresa_id, area, enunciado, artigo, explicacao, dificuldade, ativo, criado_em, alternativas | `models.py` |
| `Alternativa` | alternativas | 6 | id, questao_id, texto, correta, ordem, questao | `models.py` |
| `Prova` | provas | 16 | id, empresa_id, usuario_id, setor_id, area, nota_corte, nota, aprovado, status, tempo_limite_min, criado_em, finalizado_em, usuario, setor … | `models.py` |
| `ProvaItem` | prova_itens | 10 | id, prova_id, questao_id, ordem, ordem_alternativas, alternativa_escolhida_id, correta, prova, questao, alternativa_escolhida | `models.py` |
| `Certificado` | certificados | 13 | id, empresa_id, usuario_id, prova_id, setor_id, area, codigo, nota, emitido_em, valido_ate, usuario, prova, setor | `models.py` |
| `DiagnosticoPergunta` | diagnostico_perguntas | 6 | id, dimensao, texto, peso, ordem, ativo | `models.py` |
| `Diagnostico` | diagnosticos | 12 | id, empresa_id, usuario_id, setor_id, criado_em, finalizado_em, score, nivel, status, usuario, setor, respostas | `models.py` |
| `DiagnosticoResposta` | diagnostico_respostas | 6 | id, diagnostico_id, pergunta_id, valor, diagnostico, pergunta | `models.py` |
| `AuditLog` | audit_logs | 9 | id, empresa_id, usuario_id, acao, detalhe, ip, criado_em, hash, usuario | `models.py` |
| `RecoveryCode` | recovery_codes | 5 | id, usuario_id, code_hash, usado, criado_em | `models.py` |
| `EmailEnviado` | emails_enviados | 8 | id, empresa_id, remetente, destinatario, assunto, corpo, enviado, criado_em | `models.py` |
| `Anexo` | anexos | 11 | id, empresa_id, alvo_tipo, alvo_id, nome_original, nome_arquivo, mime, tamanho, enviado_por_id, criado_em, enviado_por | `models.py` |
| `RopaRegistro` | ropa_registros | 13 | id, empresa_id, setor_id, atividade, titulares, categorias_dados, finalidade, base_legal, retencao, compartilhamento, criado_em, atualizado_em, setor | `models.py` |
| `PedidoTitular` | pedidos_titular | 15 | id, empresa_id, nome_titular, contato, tipo, descricao, status, responsavel_id, criado_em, prazo, concluido_em, observacoes, protocolo, origem … | `models.py` |
| `Ripd` | ripd | 14 | id, empresa_id, ropa_id, titulo, descricao_tratamento, probabilidade, impacto, medidas, risco_residual, conclusao, status, criado_em, atualizado_em, ropa | `models.py` |
| `Incidente` | incidentes | 15 | id, empresa_id, titulo, ocorrido_em, descricao, dados_afetados, num_titulares, risco, comunicado_anpd, comunicado_anpd_em, comunicado_titulares, comunicado_titulares_em, medidas, status … | `models.py` |

### Testes

| Arquivo | Testes | O que cobre |
|---|---|---|
| `tests/test_admin.py` | 5 |  |
| `tests/test_anexos.py` | 5 | Anexos como evidência (Parte 9a): validação, escopo por tenant e papéis. |
| `tests/test_auth.py` | 6 |  |
| `tests/test_banco_questoes.py` | 9 | Checklist automático do banco de questões e do sorteio da prova. |
| `tests/test_ciclo_vida.py` | 5 | Ciclo de vida dos dados da própria plataforma (Parte 9b): |
| `tests/test_cobertura.py` | 11 | Caminhos de erro, integrações simuladas (SMTP, feed RSS) e comandos de CLI. |
| `tests/test_correcoes.py` | 5 | Regressões das correções da auditoria (Parte 2): PDFs, notificações, auditoria, métricas. |
| `tests/test_demo.py` | 4 | Demo demonstrável (Parte 7): caixa de saída de e-mails, seed rico e segunda empresa. |
| `tests/test_diagnostico.py` | 3 |  |
| `tests/test_fase2.py` | 9 |  |
| `tests/test_final.py` | 6 | Partes 10–12: trilha lida, QR no certificado, comparativo por setor, importação do ROPA, tour. |
| `tests/test_hardening.py` | 7 | Regressões do hardening (Parte 3): sessão, enumeração, reautenticação do 2FA, HSTS, proxy. |
| `tests/test_isolamento.py` | 9 | Isolamento multi-tenant: a empresa A nunca lê, grava ou referencia dados da empresa B. |
| `tests/test_papeis.py` | 3 | Papéis no Pilar 2: o Gestor apenas visualiza; só o Encarregado altera. |
| `tests/test_pilar2_vivo.py` | 6 | Pilar 2 vivo (Parte 8): portal do titular com protocolo, prazos e KPIs no painel. |
| `tests/test_produto.py` | 5 | Regressões das melhorias de produto (Parte 5): export do ROPA, reset de senha, |
| `tests/test_provas.py` | 1 |  |
| `tests/test_rbac.py` | 4 |  |
| `tests/test_relatorios.py` | 2 |  |
| `tests/test_revisao.py` | 8 | Regressões dos achados da revisão independente final (nenhum crítico; 2 altos, 5 médios, 9 baixos). |
| `tests/test_secret_key_sem_permissao.py` | 1 | A geração da chave secreta não pode derrubar o boot quando instance/ não é gravável |
| `tests/test_seguranca.py` | 5 |  |
| `tests/test_zz_demo_reset.py` | 2 | `flask demo-reset` — roda POR ÚLTIMO (prefixo zz): apaga e recria o banco de teste. |

## Web (JS/TS/Svelte/React)

| Pasta | Arquivos |
|---|---|
| `static/js` | app.js, prova.js |

## Scripts de shell

| Arquivo | Primeira linha de comentário |
|---|---|
| `INICIAR-MAC.command` | ───────────────────────────────────────────────────────────────────────── |
| `entrypoint.sh` | Entrypoint do container: aplica migrações e (opcionalmente) popula a demo, |
| `iniciar.sh` | ───────────────────────────────────────────────────────────────────────── |
