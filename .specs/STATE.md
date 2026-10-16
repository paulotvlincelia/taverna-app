# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: Execute; T1 em realização, T2 e T7 concluídas como ambiente/caches, T3–T6 pendentes.
- **Completed**: Nix instalado, cache assinado autorizado; fonte/locks fixados, sete pins SwiftPM preservados; APP-004 e critérios IOS-04/05/10 revisados conforme aprovação. Ferramentas de sessão/guard versionadas. Controle UIKit próprio comprovou EPERM IPv4/IPv6 + loopback antes do main e interface pronta; sem guard recebeu EINPROGRESS e recusou a interface. Preflight Xcode confirma UDID exclusivo, índices e armazenamento físico; 40 testes Python passaram, incluindo os 28 anteriores.
- **In-progress**: primeira realização nativa e agendador encerraram com exit 124 no prazo comum 16:12:35 UTC, ainda no GHC Stage1. Nova tentativa ativa desde 16:12:41 UTC, sessão exec 28679, max-jobs=2/cores=5, mesma derivação; prazo 17:42:41 UTC. Metadados em .build/active-native-core-retry.json; logs/receipt em .build/attempts/nix-core-realization-20261016-02. Sessões 98534/49769 fechadas. Auxiliares libffi/GMP e mac2ios realizados, 536 objetos de simulador inspecionados. WebRTC de pacote fixado tem hash, source metadata/patch e arm64 platform 7 conferidos; não é rebuild local. Ainda nenhuma biblioteca Haskell final qualificada.
- **Next step**: acompanhar núcleo, qualificar produtos/objetos/plataforma e fechar T1. Só então integrar guard em todos os launches herdados e acrescentar navegação observável de T3. Não confundir controle próprio com app real.
- **Blockers**: produto nativo, build e testes reais da Taverna ainda sem prova. Não há pergunta/aprovação pendente; não há autenticação administrativa pendente.
- **Uncommitted files**: conferir git. conferir git; checkpoint documental de T1, sem marcar a tarefa concluída.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, tools/taverna/ios_session.py, tools/taverna/ios, testes e artefatos de ios-first-build; integração de CI/locks nesta sessão. Estado físico sob .build, fontes e produtos Nix na exceção aprovada. Dispositivo ativo da sessão em .build/ios-session.json, UDID 0DE957D3-B2E4-42D6-BEFC-006CC04315B2, desligado após controle. Primeiro dispositivo customizado em .build/session.json também desligado. Reconciliar índices/aliases por UUID e dados preservados antes de remover worktree; sem limpeza forçada. Nenhum código do mensageiro alterado; Taverna nunca instalada/aberta. Verifier somente após último commit de implementação.
