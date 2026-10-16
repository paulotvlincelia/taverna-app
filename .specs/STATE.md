# STATE

## Decisions

As decisões canônicas deste repositório ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. A especificação ios-first-build e a rota Nix foram aprovadas; os critérios ainda precisam de prova.

Registro posterior de 2026-10-16: especificação e rota Nix aprovadas; exceção administrativa canônica em APP-002. Nenhuma aprovação significa prova de build.

## Handoff

- **Feature**: ios-first-build #6 concluída; TLC Spec Driven, oito tarefas; relatório independente em features/ios-first-build/validation.md.
- **Implementation SHA**: 6ea482bd4a1912d8eef52904d930c7f6c57bf746; alterações posteriores somente de relatório.
- **Evidence**: autor/Verifier em worktrees/caches/UDIDs distintos, mesmo manifesto/perfil, quatro métodos por execução, zero falhas/skips, nove eventos before-main cada. 70 testes Python; CI exata; sensor 6/6; 20/20 critérios PASS.
- **Integration**: PR #10 publicado e condicionado aos gates; CI da fonte aprovada. Repetir checks textuais/CI do commit de relatório e integrar conforme autorização já dada. Não remover as worktrees de prova: contêm evidências locais a preservar.
- **Next product work**: inventário de assets/dependências e identidade/capabilities, nas issues existentes. Não iniciar backlog automaticamente. Matriz integral PENDING; aparelho/push NOT RUN; distribuição BLOCKED.
- **Constraints**: Projects e exceção Nix aprovada. ambiente externo/rede administrativa/serviço externo/produção/contas Apple intocados. Nenhum perfil/conversa nem binário/PNG/xcresult publicado.
- **Ownership**: Codex integrador, branch codex/6-ios-first-build-plan. Fontes A/B permanecem limpas no SHA acima; documentação de encerramento é o único diff posterior.
