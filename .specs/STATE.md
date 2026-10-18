# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue #15; TLC Spec Driven, seis tarefas nativas. T1–T3/T5 aprovadas no recorte; T4 parcial, T6 e oito NP agregados continuam pendentes.
- Branch: codex/15-native-access-qualified, base c25dc4eb0d963afa916ac7605c5f2665e66318ba. Retomada encontrou HEAD 4e0051008da46e3fdf9a1c3d3918f554d41e832f limpo; código/testes/targets preservados.
- Aprovação: proprietário aprovou identidade visual InnerMesh do PR #20 (HEAD 67aed65c) em 2026-10-18 e retomou a prova NSE, sem merge. Não autoriza distribuição de assets ou implementação antecipada de UI/renomeação.
- Novas provas do autor em 4e0051008: cinco payloads Full sem falhas/skips (162,838 s), startup 15 checkpoints (24,332 s), 76 Foundation, checker/compileall/whitespace. Produtos correspondem ao build clean share-final-clean preservado; nenhum novo build do autor alegado. Primeira tentativa recusou guard default antigo; repetição usa guard-share-b explícito. Ver native-execution.md.
- Share: Verifier encontrou instabilidade na seleção direta (1/2). Correção para More e centro do ícone passou em desenvolvimento: 22 checkpoints, um XCTest sem falhas/skips, quatro produtos inalterados; oito XCTAssert idênticas. Quatro métodos first-build independentes passaram em 4e. Terceira revisão limpa/sensor pendentes; não afirmar T4 completa.
- NSE: BLOCKED_ENVIRONMENT. O artefato local não qualifica identidade nem entrega remota APNs. APNs Sandbox e provisionamento permanecem fora do escopo atual; ver nse-environment.md. Não usar simctl push ou classe instanciada no app como prova efetiva.
- Next: concluir revisão independente Share e qualificar um ambiente APNs Sandbox isolado antes da prova NSE. Manter T4/T6 abertas até processo efetivo, ordem, protocolos e sensor aprovados. Publicação requer digest/Verifier; nenhum merge autorizado.
- Ownership: Codex autor/harness/integrador, transporte/startup/drivers e documentos; Verifier independente escreve somente seu relatório. Ambientes e estado exclusivos em .build; limites definidos em native-proof.md.
- Uncommitted: nenhum após o commit documental; conferir git status antes de retomar. Fix de seleção limitado ao target de qualificação Share e seus registros; código do app preservado.
