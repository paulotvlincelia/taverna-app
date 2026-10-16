# Contexto: Taverna por convite

Data: 2026-10-16. Status: spec e contexto aprovados pelo proprietário em 2026-10-16; prova técnica isolada autorizada.
[Spec canônica](spec.md). Issue pública #7. O proprietário autorizou publicar o plano e seguir com a prova de controle de acesso e servidores próprios, preservando CI e Verifier antes de integrar. Implementação completa do app e deploy ficam fora dessa prova.

## Feature Boundary

Definir a próxima fase do app: entrada individual controlada pelo proprietário, grupos administrados por ele, conversas individuais com aceite mútuo e configuração dos servidores da instância. Incluir o contrato do futuro DESIGN.md. Não executar deploy ou mudanças em ambientes existentes.

## Implementation Decisions

O proprietário escolheu continuar o fork Taverna após ver a base no simulador. O primeiro build serve como fundação; a interface ainda é a do SimpleX.

O proprietário escolheu uma discussão guiada, com até duas decisões independentes por vez. Somente ele cria os grupos e escolhe seus membros. O convite individual de uso único basta para entrar, sem uma segunda aprovação. Os convidados podem iniciar conversas entre si com aceite mútuo.

O proprietário pediu uma especificação DESIGN.md para a fase de identidade. Ela precisa orientar a implementação da identidade visual completa e servir a diferentes agentes e harnesses. O contrato está na spec; nenhuma direção artística foi aprovada ainda.

### Agent's Discretion

Pesquisar a base e propor arquitetura, sequência e pressupostos. Nenhuma delegação da escolha artística final foi solicitada. Não transformar propostas em escolhas confirmadas do proprietário.

### Declined / Undiscussed Gray Areas → Assumptions

A spec registra propostas para validade de 72 horas, um iPhone por convidado, limite de 20 convidados além do proprietário, efeito da revogação em 60 segundos, falha de autorização, privacidade administrativa, notificações genéricas e limites de resgate. O proprietário aprovou o plano com esses pressupostos em 2026-10-16; isso fixa os critérios para a prova, sem comprovar sua viabilidade. A posse do convite não comprova a identidade da pessoa; primeiro resgate pode ser de um destinatário não pretendido.

## Specific References

Taverna significa um local reservado para negócios, carreira, startups e temas sensíveis entre pessoas escolhidas. A inspiração mencionada pelo proprietário inclui speakeasies e locais discretos de encontro. Isso orienta o briefing; não fixa decoração, paleta ou símbolo.

Nome: Taverna. Fonte aberta SimpleX como base, mantendo licenças, criptografia e procedência. Ambientes de desenvolvimento ficam em Projects, com branch e worktree por sessão.

## Deferred Ideas

Android, desktop, chamadas e integração com serviços externos. Nenhuma alteração em serviços de produção nesta fase.

## Handoff local

Responsável e integrador: Codex, sessão de planejamento invitation-only. Harness: Codex. Branch: codex/7-invitation-only-plan. Worktree: diretório irmão taverna-app-worktrees/invitation-only-plan. Escopo: esta feature, README, roadmap público e handoff. CI, código do app, lockfiles, licenças e estado de simuladores não são alterados. Não publicar detalhes operacionais privados.

## Execução da publicação

Passo atômico de suporte: incluir a nova feature na cópia isolada usada pela suíte Foundation. Arquivo: tools/taverna/tests/test_foundation.py, somente preparação da fixture. Sucesso: as 70 verificações existentes passam, sem alteração de asserção, skip ou código do checker. A primeira execução detectou quatro links ausentes nessa cópia; o checkout real já passava.

O primeiro commit documental foi criado antes da correção da fixture por falta de interrupção do shell após a falha da suíte; não foi publicado nesse estado. A correção recebe commit próprio e toda publicação é precedida por gates com interrupção no primeiro erro.
