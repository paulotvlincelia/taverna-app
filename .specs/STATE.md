# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6. TLC Spec Driven, sete tarefas, execução inline.
- **Phase / Task**: Execute; T1 realizando a biblioteca nativa, com ambos os compiladores concluídos. T2/T7 concluídas; T3–T6 pendentes.
- **Completed**: Nix/cache assinado autorizados; fonte/locks fixados; sete pins SwiftPM preservados. Ambiente/guard e caches Xcode provados com controle UIKit próprio; 40 testes Python, incluindo os 28 herdados. Isso não prova a Taverna.
- **In-progress**: ambos os GHCs 9.6.3 exatos concluídos exit 0; outputs 6mrz4w4... e pmyvxih... locais/ultimate=true, versões e conteúdo conferidos. Primeiro receipt em nix-ghc-small-20261016-03, segundo em nix-ghc-normal-20261016-04; sessões 57073/67142 encerradas. Núcleo ativo em nix-core-realization-20261016-05 desde 17:53:16 UTC, prazo 19:23:16 UTC, sessão exec 87662, monitor 41199/Nix 41207, max-jobs=1/cores=5. Conferir active.json/receipt.json antes de retomar; não duplicar. Tentativa -02 preservada como INTERRUPTED/retorno desconhecido. Nenhum núcleo final ou app realizado.
- **Next step**: conferir o núcleo ativo, depois qualificar suas bibliotecas reais e fechar T1. Só então integrar guard em todos os launches e navegação de T3.
- **Blockers**: núcleo, build e testes reais da Taverna ainda sem prova; nenhuma aprovação ou autenticação pendente.
- **Uncommitted files**: conferir git; checkpoint documental da retomada não conclui T1.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, feature ios-first-build e tools/taverna; integrador de CI/locks nesta sessão. Repos/estado em Projects, store Nix como exceção aprovada. UDID próprio 0DE957D3-B2E4-42D6-BEFC-006CC04315B2 e dispositivo anterior DE62C0FF-4FB1-4AAE-AF52-A1161ED5BB95 desligados. Reconciliar aliases/dados antes de remoção, sem limpeza forçada. Taverna nunca instalada/aberta. Preservar Tailscale, Mac mini e Alfred. Verifier independente após último commit.
