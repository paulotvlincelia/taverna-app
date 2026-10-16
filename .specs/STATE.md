# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: ios-first-build #6; TLC Spec Driven, Large (oito tarefas).
- **Completed**: T1/T2/T7/T8/T3/T4/T5. App e quatro produtos reais; perfil first-build com quatro métodos/zero falhas/skips (85,065 s), onboarding 13,334 s; nove eventos before-main. 70 testes Python, Foundation/compileall/diff aprovados.
- **In progress**: T6 README/proveniência atualizados factual; commit final de implementação preparado. Próximas alterações só de relatório, salvo falha de gate que exija novo SHA e duas novas provas.
- **Next**: criar dois worktrees/branches/UDIDs novos do mesmo SHA; autor e fresh Verifier repetem guia completo com caches próprios; comparar receipts, CI e relatório independente; fechar gates e integrar apenas com autorização.
- **Constraints**: Projects; Nix/store exceção aprovada. Sem Tailscale/Mac mini/Alfred/produção/conta Apple/perfil/conversa. Matriz integral disponível e PENDING. Nada de binários/screenshots/xcresult publicados.
- **Ownership**: Codex integrador, branch codex/6-ios-first-build-plan; nenhum push/PR F1 ainda. Sessão exploratória B096FCF6 encerrada Shutdown, registros anteriores preservados. Registrar ambos UDIDs finais antes de qualquer UI paralelo.
