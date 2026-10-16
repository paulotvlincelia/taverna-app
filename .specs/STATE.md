# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue pública #7. TLC Spec Driven 3.3.0. Spec/contexto e pressupostos aprovados pelo proprietário em 2026-10-16; publicação do plano e prova isolada autorizadas; gates antes da integração preservados.
- Fase: pesquisa para Design, comparando autorização individual e compatibilidade dos serviços. Nenhum produto Taverna ou prova operacional declarados prontos.
- Próximo passo: publicar PR do plano; qualificar o fonte fixado e as alternativas de enforcement, registrar evidências e limites; confirmar abordagem antes de detalhar arquitetura conforme TLC.
- Entrega anterior: PR #10 integrado em stable 9bfd78275a6f354ce3d18aaa7f2d47b48ba71756. Primeiro build: duas provas, quatro métodos por prova, zero falhas/skips, 70 testes, Verifier 20/20 e sensor 6/6. Aparelho/APNs não executados; distribuição bloqueada.
- Responsável/integrador: Codex; branch codex/7-invitation-only-plan; worktree irmão taverna-app-worktrees/invitation-only-plan. Escopo: artefatos desta feature, README, roadmap e handoff. Sem reversão de mudanças de outros agentes.
- Preservação: worktrees/evidências e preview existentes mantidos. Tudo em Projects; sem mudanças em produção, app, CI, locks, licenças, ambiente externo, rede administrativa, serviço externo, DNS, credenciais ou contas Apple.
