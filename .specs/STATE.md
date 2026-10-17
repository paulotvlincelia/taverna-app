# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue #15. TLC Spec Driven; A1 técnica aprovada. Oito critérios NP e 34 requisitos do produto continuam Pending até a qualificação integral.
- Branch: codex/15-native-access-qualified, base c25dc4eb0d963afa916ac7605c5f2665e66318ba. T5 transposta em 7d248badce6c4882c8ac879619d65bb782059141; fontes/testes idênticos ao baseline. Nova prova clean no HEAD 8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c.
- Completed: T1–T3 e T5 no recorte. Novo build clean de quatro produtos, cinco casos do autor e cinco do Verifier, sem falhas/skips; startup padrão 15 checkpoints. Sensor anterior 6/6 preservado como histórico, validado por equivalência de fontes/produtos; não reexecutado.
- Gates: 29 codec, 10 transporte, 76 Foundation e 12 CLI nas rodadas registradas. Checker/compileall/spec/tasks/whitespace aprovados. native-publication-revalidation.md distingue origem histórica e nova prova; native-execution.md conserva tentativas e limites. Este commit documental não afirma novo build.
- Next: PR #19 publicado em rascunho no HEAD anterior, CI aprovada. Share de T4 passou 22 checkpoints em desenvolvimento, com sentinela, leitura da política antes dos comandos e suíte própria sem filtros. Quatro métodos first-build passaram sem filtros. O Verifier rejeitou a composição anterior das suítes em 73d; correção aguarda prova limpa e novo sensor independente antes de publicar. T4 exige lifecycle efetivo Share/NSE, com ambiente de notificações pendente. T6 depende de T4 e T5. Não integrar a feature nem avançar para admissão/UI por inferência de PASS parcial.
- Ownership: Codex autor/harness/integrador; transporte, startup, Xcode, drivers e artefatos native-*.md. Ambientes e simulador exclusivos em .build; Verifier escreve somente seu relatório.
- Limites: app + CLI em fixture, sem provar aparelhos, NSE, APNs ou operação. Share tem prova de desenvolvimento, ainda pendente de repetição limpa e Verifier. A fixture da extensão usa interposição de socket explicitamente identificada, sem alegar sandbox do kernel; app principal preserva o kernel guard. DESIGN.md aprovado precede UI. Publicação exige classificação e digest exato; branches anteriores locais não devem ser enviadas. Nenhuma credencial/dado real pertence ao público.
- Uncommitted: fontes/provas Share e registros da subentrega estão incluídos no commit atômico; reconciliar git status antes de retomar.
