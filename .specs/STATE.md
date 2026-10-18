# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, BRAND-01, registro documental InnerMesh 0.5.2. TLC Spec Driven; pedido e seção inicial do HANDOFF delimitam a entrega. Nenhuma UI implementada.
- Branch: codex/identity-design-draft, início ec4f2c1545b88bd675368f40a95374550ed35079. Codex autor/harness/integrador, worktree exclusivo identity-design-draft.
- Scope: DESIGN.md substituído, GOVERNANCE.md novo (ausente antes), 49 referências em docs/innermesh/design, registro e relatório desta subentrega. docs/taverna, código, identificadores, catálogos e CI não mudam. Exceção autorizada: dois destinos novos na cópia da fixture Foundation, sem mudar asserts.
- Capacity: proprietário confirmou 20 convidados além dele, 21 pessoas. Ajuste autorizado somente em DESIGN.md/HANDOFF.md; spec intacta.
- Checks: contraste 17 pares/34 medições PASS, bytes do JSON idênticos ao pacote. Links de fase 6 esperados: docs/innermesh/assets.md e docs/innermesh/asset-policy.json. Demais links devem resolver. Regressões Foundation e Verifier exigidos antes de publicar.
- Next: revisão independente do registro; resolver bloqueio do publicador para 25 PNGs antes de publicar o pacote completo no PR para stable. Não contornar guard, implementar UI ou inferir aprovação de navegação/telas.
- Native transport: permanece pausado e fora desta branch. NSE efetiva continua pré-requisito antes de UI. Plano de remediação externo citado no pacote não localizado nos documentos locais; numeração preservada sem inventar estado.
- Ownership: somente documentação e handoff; Verifier escreve seu relatório. Estado/evidências locais em .build. Registro detalhado em .specs/features/invitation-only/innermesh-handoff.md.
