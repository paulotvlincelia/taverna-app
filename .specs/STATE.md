# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, BRAND-01, proposta documental de identidade solicitada pelo proprietário. TLC Spec Driven preserva contrato e critérios aprovados; skill design auxilia o briefing, anti-ai-slop auxilia a escrita.
- Branch: codex/identity-design-draft; base c25dc4eb0. Codex autor/harness/integrador. Worktree exclusivo identity-design-draft; responsabilidade: DESIGN.md, docs/taverna/design, README, checker/fixture Foundation necessários à nova raiz documental e este handoff.
- Scope: Draft 0.1.0, proposta de marca/cores/tipos/componentes/estados e três telas em claro/escuro. Referências originais documentais; nenhum asset de distribuição aprovado. Não altera interface, assinatura, protocolos ou operação.
- Checks: executar os 78 testes Foundation, checker, compileall, contraste e whitespace; revisão independente documental antes de publicar. Os dois testes novos verificam links e material privado no DESIGN.md; as 76 asserções/suítes anteriores permanecem.
- Next: submeter a direção/símbolo/navegação ao proprietário. BRAND-02/03 e demais requisitos continuam Pending até suas provas. Nenhuma aprovação artística foi inferida do pedido de preparar o documento.
- Native transport: continua no worktree próprio; esta branch não altera ou integra o transporte. Publicação exige pacote classificado/digest exato e integração exige CI e Verifier.
