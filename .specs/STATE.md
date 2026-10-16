# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6. TLC Spec Driven, sete tarefas, execução inline.
- **Phase / Task**: Execute; T1/T2/T7 concluídas. Próxima T3: build e teste observável do app.
- **Completed**: Nix/cache assinado autorizados; fonte/locks fixados; sete pins SwiftPM preservados. Ambiente/guard e caches Xcode provados com controle UIKit próprio; 40 testes Python, incluindo os 28 herdados. Isso não prova a Taverna.
- **In-progress**: nenhum build nativo ativo. -05 terminou exit 0 em 18:57:24 UTC; source/local NAR conferidos. Conversão mac2ios legada bloqueada/preservada; vtool/libtool do Xcode resolveram as cópias e conferiram payload inalterado nos 4.187 objetos/cinco arquivos. Entradas versionadas em native-inputs.json; bindings em .build/native-input-bindings.json; .build/check-native-inputs.py passou e três entradas negativas foram recusadas. Manifesto SHA ae89d70ece47ce7e5f850a403b4fd1f74cd3fcf80c537369f3c8d77712cf1ce8. App ainda não compilado/instalado/aberto.
- **Next step**: T3; copiar bibliotecas qualificadas ao caminho de simulador, integrar guard em todos os lançamentos herdados e acrescentar navegação Get started → Your profile, depois executar build e suíte completos.
- **Blockers**: nenhum bloqueio técnico aberto; faltam build, testes reais, validador, guia, reprodução e Verifier. Nenhuma aprovação/autenticação pendente.
- **Uncommitted files**: conferir git; checkpoint documental da retomada não conclui T1.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, feature ios-first-build e tools/taverna; integrador de CI/locks nesta sessão. Repos/estado em Projects, store Nix como exceção aprovada. UDID próprio 0DE957D3-B2E4-42D6-BEFC-006CC04315B2 e dispositivo anterior DE62C0FF-4FB1-4AAE-AF52-A1161ED5BB95 desligados. Reconciliar aliases/dados antes de remoção, sem limpeza forçada. Taverna nunca instalada/aberta. Preservar rede administrativa, ambiente externo e serviço externo. Verifier independente após último commit.
