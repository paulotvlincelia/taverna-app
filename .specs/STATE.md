# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue #15. TLC Spec Driven; A1 aprovada. Oito critérios NP e 34 requisitos do produto continuam Pending até a qualificação integral.
- Branch: codex/15-native-access-reconciled, base c25dc4eb0d963afa916ac7605c5f2665e66318ba. Último commit de implementação: b48476b240a902ca46a6c4883cc6f07aa415bdef. Ancestrais substituídos não foram unidos.
- Completed: T1–T3 com Verifier PASS em 53b31fdfe8398d858395dc4b366f814c76ff3c51; T5 com build clean dos quatro produtos, cinco casos clean do autor e cinco do Verifier, sem falhas/skips. Cada sensor detectou seis mutantes. Correção da cardinalidade foi autorizada em 17/out/2026; comparação integral de bytes preservada.
- Gates: 29 codec, 10 transporte, 76 Foundation, 15 checkpoints startup e 12 CLI; checker/compileall/spec/tasks/whitespace aprovados. Revisão T5: native-payload-review.md. Evidências, tentativas e limites: native-execution.md. Prova iOS vinculada ao commit de implementação; este registro documental não afirma novo build.
- Next: publicar pacote revisado e PR em rascunho; conferir CI. T4 continua exigindo lifecycle efetivo Share/NSE, com ambiente de notificações pendente. T6 depende de T4 e T5. Não integrar a feature nem avançar para admissão/UI por inferência de PASS parcial.
- Ownership: Codex autor/harness/integrador; transporte, startup, Xcode, drivers e artefatos native-*.md. Ambientes e simulador exclusivos em .build; Verifier escreve somente seu relatório.
- Limites: app + CLI em fixture, sem provar dois aparelhos, extensões, APNs ou operação. DESIGN.md aprovado precede UI. Publicação exige classificação e digest exato; não enviar branch antiga. Nenhuma credencial/dado real pertence ao público.
- Uncommitted: relatório e registros documentais deste fechamento até o próximo commit; reconciliar git status antes de retomar.
