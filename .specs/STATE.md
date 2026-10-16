# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. As propostas de ios-first-build aguardam revisão; não substituem decisões aprovadas.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: [ios-first-build](features/ios-first-build/spec.md), issue pública #6.
- **Phase / Task**: preparo administrativo autorizado, pré-requisito do Design; nenhum código do app alterado.
- **Completed**: qualificação pré-compilada BLOCKED; rota Nix e exceção autorizadas; pacote 2.34.9 com SHA oficial conferido; autenticação macOS confirmada pelo proprietário.
- **In-progress**: instalação manual pelo Terminal gráfico solicitada ao proprietário. O controle automatizado do Terminal foi recusado pela ferramenta por segurança; não contornar por outra ferramenta.
- **Next step**: conferir .build/attempts/nix-bootstrap-20261016/gui-install.exit e gui-install.log; validar versão, montagem e daemon. Depois avaliar derivação fixada sem atualizar o lock e fechar Design/tarefas antes de modificar código.
- **Blockers**: instalação inicial exit 1 em vifs: error creating /etc/fstab. /nix e volume APFS vazio criados, binário/daemon ainda ausentes. Falta execução manual do helper pelo proprietário.
- **Uncommitted files**: conferir Git ao retomar; checkpoint documental a commitar nesta sessão.
- **Branch**: codex/6-ios-first-build-plan.
- **Ownership**: Codex, .specs/features/ios-first-build, handoff e docs/taverna/decisions/README.md. Estado ignorado: .build/attempts/nix-bootstrap-20261016. Helper install-nix.command pronto, bash -n aprovado; não foi executado automaticamente.
