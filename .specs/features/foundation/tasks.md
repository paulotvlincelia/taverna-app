# Tasks da fundação pública

## Execution Protocol

TLC Spec Driven carregada, plano aprovado em 2026-10-16. Codex desktop autor/integrador, branch codex/foundation, worktree exclusivo foundation fora do clone principal. Propriedade: documentação Taverna, .agents, .specs/features/foundation, tools/taverna e CI. Fonte do mensageiro preservada. Verifier independente obrigatório antes de integrar.

**Status**: Implementation complete; CI/independent verification pending

## Test Coverage Matrix

Guias: AGENTS.md e CONTRIBUTING.md. Ferramentas novas usam unittest stdlib; nenhuma compilação iOS é declarada pelo gate da fundação.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Checker e preflight | unit + CLI | válido, ausente, malformado, versão, erro/timeout e gates negados | tools/taverna/tests | python3.12 -m unittest discover -s tools/taverna/tests -v |
| Docs/config | auditoria | links, licenças, workflow sem segredos, proveniência e readback | docs/taverna | python3.12 tools/taverna/check_foundation.py |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | componente | python3.12 -m unittest discover -s tools/taverna/tests -v |
| Full | fase | Quick + python3.12 tools/taverna/check_foundation.py |
| Build | final | Full + python3.12 -m compileall -q tools/taverna + git diff --check |

## Execution Plan

### Phase 1: Fundação pública

```text
T1 -> T2 -> T3
```

## Task Breakdown

### T1: Pacote público de contribuição

**Where**: public foundation
**Depends on**: None
**Requirement**: PUB-01, PUB-02, PUB-05, PUB-06
**Done when**: checker de origem/licenças, docs e CI sem segredos aprovado, testes de falha co-localizados (mínimo 14).
**Tests**: unit + CLI e auditoria
**Gate**: Full

### T2: Preflight e isolamento

**Where**: tools/taverna
**Depends on**: T1
**Requirement**: PUB-03, PUB-04, PUB-06
**Done when**: dependências e gates explícitos, testes ausente/versão/timeout/estado isolado aprovados e execução real registrada sem alegar build.
**Tests**: unit + CLI
**Gate**: Full

### T3: Roadmap e verificação

**Where**: public portfolio
**Depends on**: T2
**Requirement**: PUB-07, PUB-06
**Done when**: issues/Project públicos autossuficientes, CI no SHA final e Verifier independente com clone limpo/sensor aprovados.
**Tests**: auditoria + regressão
**Gate**: Build

## Diagram-Definition Cross-Check

T1: None/None; T2: T1/T1; T3: T2/T2. Match.

## Test Co-location Validation

T1 e T2: unit/CLI no commit do componente; T3: auditoria e regressão dos checks. Nenhum teste adiado.
