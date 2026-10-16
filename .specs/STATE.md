# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: Execute, T1 de seis tarefas em andamento; nenhum código do app alterado.
- **Completed**: instalação gráfica exit 0; Nix 2.34.9, daemon e montagem validados; fonte upstream fixado recuperado e sete arquivos-chave comparados com hashes idênticos ao fork; sete pins SwiftPM resolvidos, Package.resolved preservado byte a byte; decomposição validada. Consulta Xcode showBuildSettings exit 0 para app/SDK Simulator 27.1/arm64, sem time de assinatura e sem build. Fontes de mac2ios fixadas e inspecionadas localmente; sem execução.
- **In-progress**: segunda avaliação do atributo iOS arm64, iniciada às 13:59:59 UTC de 2026-10-16. Sessão exec 80645, limite 5.400 s; receipt e logs em .build/attempts/nix-core-evaluation-20261016-02. A primeira tentativa terminou TIMEOUT/124 após 1.800 s, sem derivação final.
- **Next step**: acompanhar a sessão 80645 e .build/active-native-core.json, obter a derivação e qualificar produtos nativos reais. Pedido assíncrono sobre cache assinado pendente: não aplicar a proposta antes da resposta.
- **Blockers**: compatibilidade da receita ainda não comprovada. Bibliotecas reais, destino/rede isolados, build e testes continuam sem prova. Cache iog funciona com User-Agent Nix; a conclusão anterior baseada no 403 do Python foi corrigida, assinatura dos metadados do auxiliar validada.
- **Uncommitted files**: conferir Git; registro de execução e atualização de ambiente nesta sessão.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, .specs/features/ios-first-build e handoff; integração de CI/locks nesta sessão. Estado local em .build/attempts; cache/configuração sob .build/nix. T2–T6 pendentes; Verifier só após implementação final. Cabeçalho UI factual corrigido para Your profile, sem alterar testes existentes.
