# Tarefas do porte SMP

## Execution Protocol (MANDATORY -- do not skip)

Executar com `tlc-spec-driven` e verificar cada commit.

**Design**: `.specs/features/device-test-stable-port/design.md`
**Status**: Implementation complete, independent verification pending

## Test Coverage Matrix

> AGENTS.md, CONTRIBUTING.md, test_device_policy.py, test_transport.py, device_test_core.py e device_test_delivery.py definem o nível da prova.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Listener e fixture | integration | Handshake, credencial, destino, revogação | tools/taverna/native_access_tests | Gate Full |
| Núcleo iOS | integration | Rota efetiva antes de iniciar, host comum, bloqueio e reabertura | tools/taverna/native_access_tests | Gate Full |
| Host e pacote | integration | Ordem de configuração, isolamento e origem do build | tools/taverna/tests | Gate Build |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Diff | `git diff --check` e Foundation |
| Full | Transporte ou núcleo | Testes da camada alterada, Foundation e prova nativa em artefato compilado quando aplicável |
| Build | Candidato | Suíte portátil, compileall, Foundation, prova do simulador e `device_build.py --technical` |

## Execution Plan

### Phase 1: Porte do ensaio

```
T1 → T2 → T3
```

## Task Breakdown

### T1: Incluir listener e fixture

**What**: Portar a camada de transporte e a fixture de prova.
**Where**: transporte da fixture
**Depends on**: None
**Reuses**: codec, listener e fixture existentes
**Requirement**: PORT-01, PORT-03
**Tools**: Swift e Docker local. MCP nenhum.
**Done when**:

- [x] A suíte nativa do listener passa com 14 testes.

**Tests**: integration
**Gate**: full

### T2: Portar a inicialização SMP

**What**: Aplicar o delta do controlador e qualificar seu protocolo.
**Where**: núcleo técnico iOS
**Depends on**: T1
**Reuses**: inicializador técnico e sonda do núcleo
**Requirement**: PORT-02, PORT-03, PORT-04
**Tools**: Nix, simctl e fixture de loopback.
**Done when**:

- [x] A sonda do núcleo passa e os históricos dos dois processos preservam 20 itens depois de reabrir.

**Tests**: integration
**Gate**: full

### T3: Projetar e verificar o pacote

**What**: Portar o host técnico e fechar seu build.
**Where**: projeção do pacote técnico
**Depends on**: T2
**Reuses**: host técnico e receita unsigned
**Requirement**: PORT-01, PORT-05, PORT-06
**Tools**: Swift e xcodebuild.
**Done when**:

- [x] A suíte portátil preserva os 76 testes da base e o pacote técnico arm64 passa.

**Tests**: integration
**Gate**: build

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | Listener e fixture | OK |
| T2 | Inicialização do núcleo | OK |
| T3 | Host e pacote | OK |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | OK |
| T2 | T1 | T1 | OK |
| T3 | T2 | T2 | OK |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Listener e fixture | integration | integration | OK |
| T2 | Núcleo iOS | integration | integration | OK |
| T3 | Host e pacote | integration | integration | OK |
