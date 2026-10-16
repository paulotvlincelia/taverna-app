# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6. TLC Spec Driven, sete tarefas, execução inline.
- **Phase / Task**: Execute; T1 preparando compilador exato. T2/T7 concluídas; T3–T6 pendentes.
- **Completed**: Nix/cache assinado autorizados; fonte/locks fixados; sete pins SwiftPM preservados. Ambiente/guard e caches Xcode provados com controle UIKit próprio; 40 testes Python, incluindo os 28 herdados. Isso não prova a Taverna.
- **In-progress**: retomada após update em 2026-10-16 17:07 UTC encontrou a tentativa -02 interrompida, sem processos nem receipt final. Status INTERRUPTED, retorno desconhecido em interruption.json; logs preservados. Nenhum GHC final ou núcleo realizado. Preparação isolada da dependência GHC 700zdsaz... iniciada 17:08:30 UTC, max-jobs=1/cores=10, prazo 18:38:30 UTC; sessão exec 57073, monitor 3685, Nix 3692. Metadados/logs/receipt em .build/attempts/nix-ghc-small-20261016-03. Conferir processos e receipt antes de retomar; não duplicar.
- **Next step**: conferir resultado da dependência; depois preparar o restante do grafo e qualificar bibliotecas reais para fechar T1. Só então integrar guard em todos os launches e navegação de T3.
- **Blockers**: núcleo, build e testes reais da Taverna ainda sem prova; nenhuma aprovação ou autenticação pendente.
- **Uncommitted files**: conferir git; checkpoint documental da retomada não conclui T1.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, feature ios-first-build e tools/taverna; integrador de CI/locks nesta sessão. Repos/estado em Projects, store Nix como exceção aprovada. UDID próprio 0DE957D3-B2E4-42D6-BEFC-006CC04315B2 e dispositivo anterior DE62C0FF-4FB1-4AAE-AF52-A1161ED5BB95 desligados. Reconciliar aliases/dados antes de remoção, sem limpeza forçada. Taverna nunca instalada/aberta. Preservar rede administrativa, ambiente externo e serviço externo. Verifier independente após último commit.
