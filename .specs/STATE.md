# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue #15. TLC Spec Driven; A1 aprovada. Oito critérios NP e 34 requisitos do produto continuam Pending até a qualificação integral.
- Branch: codex/15-native-access-reconciled, base c25dc4eb0d963afa916ac7605c5f2665e66318ba. T5 e este handoff pertencem ao mesmo commit atômico; conferir git log para seu SHA. Ancestrais substituídos não foram unidos, e provas anteriores permanecem preservadas.
- Completed: T1–T3 com Verifier PASS em 53b31fdfe8398d858395dc4b366f814c76ff3c51, seis mutantes detectados. T5: cinco casos Full de desenvolvimento passaram juntos em 150,949 s: mensagens e arquivos exatos bilaterais, revogação e ausência de política durante upload, sentinela. Correção da cardinalidade foi autorizada em 17/out/2026; comparação integral preservada.
- Gates: 29 codec, 10 transporte, 76 Foundation, 15 checkpoints startup e 12 CLI; checker/compileall/spec/tasks/whitespace aprovados. Detalhes e tentativas em native-execution.md. Build development payload-dev-d; ainda não há prova limpa/Verifier final/CI/publicação de T5.
- Next: compilar commit limpo e executar os cinco casos em fixtures novas; Verifier independente no último commit de implementação. T4 continua exigindo lifecycle efetivo Share/NSE, com ambiente de notificações pendente. T6 depende de T4 e T5. Não avançar para admissão/UI por inferência de PASS parcial.
- Ownership: Codex autor/harness/integrador; transporte, startup, Xcode, drivers e artefatos native-*.md. Ambientes e simulador exclusivos em .build. Verifier só escreve relatório. Nenhuma outra sessão deve usar este simulador durante a prova.
- Limites: execução app + CLI em fixture, sem provar dois aparelhos, extensões, APNs ou operação. DESIGN.md aprovado precede UI. Publicação somente com classificação e digest exato; não enviar branch antiga. Nenhuma credencial/dado real pertence ao público.
- Uncommitted: nenhum esperado após o commit atômico de T5; reconciliar git status antes de retomar.
