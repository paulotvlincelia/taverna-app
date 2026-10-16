# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. As propostas de ios-first-build aguardam revisão; não substituem decisões aprovadas.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: avaliação da receita Nix aprovada; nenhum código do app alterado.
- **Completed**: instalação gráfica exit 0; Nix 2.34.9, daemon e montagem validados; fonte upstream fixado recuperado e sete arquivos-chave comparados com hashes idênticos ao fork.
- **In-progress**: avaliação do atributo iOS arm64 com import-from-derivation requerido pelo upstream. Pode construir auxiliares de resolução Haskell; nenhum app lançado.
- **Next step**: conferir drv-path-ifd-receipt.json e logs da avaliação, obter a derivação e planejar a compilação/qualificação nativa. Fechar tarefas antes de modificar código de build/testes.
- **Blockers**: nenhum bloqueio administrativo pendente; compatibilidade da receita ainda não comprovada. Bibliotecas reais, destino/rede isolados, build e testes continuam sem prova.
- **Uncommitted files**: conferir Git; registro de execução e atualização de ambiente nesta sessão.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, .specs/features/ios-first-build e handoff. Estado local em .build/attempts/nix-validation-20261016 e nix-core-evaluation-20261016; cache/configuração sob .build/nix.
