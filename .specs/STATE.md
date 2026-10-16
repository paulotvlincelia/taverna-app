# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. As propostas de ios-first-build aguardam revisão; não substituem decisões aprovadas.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: Specify; plano preparado para revisão, implementação não iniciada.
- **Completed**: levantamento de dependências e prontidão; especificação e contexto escritos. Nenhum requisito de build verificado.
- **In-progress**: revisão do proprietário das propostas registradas no plano.
- **Next step**: após aprovação, ler as referências TLC de Design e Tasks, qualificar a rota do núcleo e definir tarefas com checks rastreáveis.
- **Blockers**: bibliotecas nativas ausentes, origem/ABI não qualificadas; seleção do destino Xcode, assinatura de simulador e contenção de rede ainda sem prova.
- **Uncommitted files**: none após o commit deste plano; conferir Git ao retomar.
- **Branch**: codex/6-ios-first-build-plan, base stable 8b2ffa71dc414615236f3fd41cb3a11876be740c.
- **Ownership**: Codex, planejamento; arquivos .specs/features/ios-first-build e .specs/STATE.md. Este agente integra o handoff nesta branch; nenhuma alteração de CI, locks ou projeto Xcode nesta etapa.
