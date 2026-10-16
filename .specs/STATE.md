# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. As propostas de ios-first-build aguardam revisão; não substituem decisões aprovadas.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: Design; especificação/defaults aprovados em 2026-10-16. Qualificação oficial avaliada e BLOCKED.
- **Completed**: consulta de 30 releases do app e 34 releases de bibliotecas; registro da orientação do mantenedor e do bloqueio; pacote Nix 2.34.9 baixado e hash oficial conferido apenas para revisão, sem instalação.
- **In-progress**: escolha da rota alternativa e da exceção administrativa descrita no Design. Nenhuma tarefa de implementação ou requisito de build concluído.
- **Next step**: obter decisão sobre Nix em /nix ou adaptação GHC/Cabal local; depois fechar Design e tarefas TLC antes de executar a alternativa.
- **Blockers**: nenhuma biblioteca oficial iOS qualificada; Nix/GHC/Cabal ausentes; instalação administrativa fora de Projects não autorizada.
- **Uncommitted files**: conferir Git ao retomar; os documentos deste checkpoint serão incluídos no commit de qualificação.
- **Branch**: codex/6-ios-first-build-plan, base stable 8b2ffa71dc414615236f3fd41cb3a11876be740c.
- **Ownership**: Codex, qualificação e Design; arquivos .specs/features/ios-first-build e handoff. Estado local em .build/attempts/core-qualification-20261016; nenhum app/núcleo compilado, nenhuma CI/lock alterada.
