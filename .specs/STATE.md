# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: ios-first-build #6, TLC Spec Driven (Large, oito tarefas), retomada após aprovação explícita do perfil first-build.
- **Completed**: T1/T2/T7/T8, HEAD 23f14dba8. Núcleo real local, 4.187 objetos; builds -02/-03 e onboarding comprovados; tentativas integrais -01/-02/-03 preservadas sem PASS.
- **In progress**: T3 perfil inglês/portrait/light aprovado, todos quatro métodos/asserts e zero skips. T4 gravação/validação/comparação preparada; T5 rascunhada; T6 pendente.
- **Next**: rebuild das fontes novas, sessão própria nova, execução real do perfil; fechar T3/T4 com provas; guia e dois builds limpos do mesmo SHA, CI e Verifier independente.
- **Constraints**: Projects e exceção Nix aprovada; não tocar ambiente externo/rede administrativa/serviço externo/produção/credenciais Apple. Sem perfil/conversa/binários publicados. Matriz integral disponível e pendente, 541 execuções positivas da tentativa -03 não são suíte aprovada.
- **Ownership**: Codex, branch codex/6-ios-first-build-plan, integrador feature/tools/docs/CI/locks. Três Swift T3, dois arquivos Python T4 e spec/handoff não commitados; nenhum push/PR F1 ainda.
- **Sessions**: todas anteriores Shutdown; record atual 22C3C673 onboarding probe preservado. Dois UDIDs finais devem ser criados antes de qualquer UI paralelo, evitando falso new_device_ids.
