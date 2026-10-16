# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: ios-first-build, issue #6; TLC Spec Driven, oito tarefas, implementação inline.
- **Phase / Task**: Execute; T1/T2/T7/T8 concluídas; T3 validação automática ativa.
- **Completed**: núcleo real local/4.187 objetos; build-for-testing -02/-03 exit 0; quatro produtos arm64 Simulator, ad hoc e símbolos Haskell verificados; onboarding real passou nas tentativas. 51 testes Python (28 Foundation herdados preservados).
- **In-progress**: UI ios-app-ui-20261016-03, início 20:04:39 UTC/prazo 21:04:39 UTC, sessão exec 3351. UDID 4C162668-2CB6-4460-AC24-82A854980A81. Build -03/patch iOS e dois hashes Swift vinculados; não editar código iOS durante a sessão. T8 final passou em public-native-preparation-20261016-02, exit 0 e cinco hashes reproduzidos. Probe parcial separado (partial-suite-rejection-probe-20261016, sessão 44507) serve somente ao formato/recusa de suíte incompleta, não ao gate positivo.
- **Next step**: conferir UI completa, xcresult e adequação T3; depois T4, guia, duas execuções limpas no commit final e Verifier/CI.
- **Blockers**: UI -01 venceu 15 min/130 positivos e -02 venceu 20 min/177 positivos, sem falhas de asserção observadas, suítes incompletas. Nova janela 60 min registrada antes da -03, sem mudar limites de 30 s ou cortar casos. Enumeração oficial mostra quatro métodos lógicos, sem expansão. Nenhuma autorização/autenticação pendente.
- **Uncommitted files**: dois testes iOS e ChatView.swift; novo componente/testes nativos; spec/design/tasks/execution/handoff. T3 permanece aberta; conferir git.
- **Branch**: codex/6-ios-first-build-plan; HEAD 53a06d25c.
- **Ownership**: Codex, feature/tools/integração CI/locks; Projects e store Nix como exceção. Preservar dados/aliases antigos DE62C0FF, 0DE957D3 e 2775E39A, Shutdown confirmado; sem limpeza forçada. Tailscale, Mac mini, Alfred e produção intocados. Sem conta Apple, perfil, mensagem ou distribuição.
