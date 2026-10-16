# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: Execute, T1 em realização; preparo independente de T2 em diagnóstico. Nenhum código do app alterado.
- **Completed**: instalação gráfica exit 0; Nix 2.34.9, daemon e montagem validados; fonte upstream fixado recuperado e sete arquivos-chave comparados com hashes idênticos ao fork; sete pins SwiftPM resolvidos, Package.resolved preservado byte a byte; decomposição validada. Consulta Xcode showBuildSettings exit 0 para app/SDK Simulator 27.1/arm64, sem time de assinatura e sem build. Fontes de mac2ios fixadas e inspecionadas localmente; sem execução.
- **In-progress**: avaliação 03 exit 0, derivação c27zzp98xz7brkfbs4cgkp6gy4cfxix6-simplex-chat-lib-simplex-chat-7.0.0.12.drv. Realização nativa ativa na sessão exec 98534 desde 14:42:34 UTC. Agendador adicional da mesma realização: sessão 49769, max-jobs=3/cores=2; parallel-scheduler.json. Ambos vencem às 16:12:34 UTC. Logs e receipts em .build/attempts/nix-core-realization-20261016; comando/pids em .build/active-native-core.json.
- **Next step**: acompanhar sessões 98534/49769 e qualificar produtos nativos reais. Design contém proposta pendente de revisão para T2: registro padrão do SDK com armazenamento físico no worktree e contenção do processo do app, não da sessão inteira. Nenhuma autenticação pendente. Não lançar o mensageiro antes dos gates aplicáveis aprovados.
- **Blockers**: T2 não aprovada. Probes de rede até -09: helper host bloqueia controle com EPERM, mas boot com sandbox falha inclusive com allow default. Exec sem sandbox inicializa. showdestinations não encontra UDID próprio; destino explícito é recusado com exit 64. Xcode tem library-validation, não alterada. Teste de alias no índice padrão falhou; só esse alias foi removido, sem reiniciar CoreSimulator ou tocar outros dispositivos. Produtos nativos, build e testes do app continuam sem prova.
- **Uncommitted files**: conferir Git; registro de execução e atualização de ambiente nesta sessão.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, .specs/features/ios-first-build e handoff; integração de CI/locks nesta sessão. Estado em .build/attempts e .build/nix. Primeiro simulador em .build/session.json, Shutdown após probes; índice de logs por symlink para o worktree. Segundo dispositivo de controle em .build/attempts/xcode-native-registration-20261016/registration.json: registro padrão do SDK, armazenamento e logs físicos no worktree, app UIKit sintético de controle instalado/aberto com EPERM e UIKIT_CONTROL_READY. Preservar/reconciliar ambos e seus índices antes de remover o worktree. Taverna nunca instalada/aberta nesta etapa. T2–T6 pendentes; Verifier só após implementação final. Testes existentes intactos.
