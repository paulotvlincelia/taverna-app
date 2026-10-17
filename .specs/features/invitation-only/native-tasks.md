# Transporte nativo: execução

## Execution Protocol

Usar tlc-spec-driven efetivamente carregada. Desenho A1 e implementação autorizados pelo proprietário em 2026-10-16. Esta decomposição executa o desenho aprovado, sem novo escopo. Ferramentas: Git, Python 3.12, Swift/Xcode/SDK instalados e Docker já qualificado. Não requer novo provider ou gerenciador de agentes. Autor Codex; Verifier independente ao fim. Seis tarefas; implementação pelo autor. T4 e T5 partem de T3, e T6 exige ambas. A prova de payload do app pode continuar enquanto se qualifica o ambiente de execução das extensões.

**Design**: entry-design.md. **Spec**: native-proof.md. **Status**: In Progress.

## Test Coverage Matrix

Diretrizes: AGENTS.md, CONTRIBUTING.md, docs/taverna/environments.md e ios-build.md; amostras: cinco suítes tools/taverna/tests, test_boundary.py e Tests_iOS.swift. Testes co-localizados com a tarefa; não reduzir asserções existentes.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Codec SOCKS | unit | NP-01/02, frames completos/fragmentados/inválidos e rejeições precisas | tools/taverna/native_access_tests | swiftc + executável local de teste, com caches no worktree |
| Adaptador TLS | integration | NP-01..04; controle real de TLS interno, rota, segredo por processo, limite/cancelamento/timeout | tools/taverna/native_access_tests | driver Python/Swift da tarefa T2, com fixture exclusiva |
| Startup nativo | integration | NP-07 e negativos antes de iniciar/retomar núcleo | apps/ios e driver de qualificação | xcodebuild nos targets existentes, driver da tarefa T3/T4 |
| Prova real | integration | NP-05/06 e NP-07 em processos efetivos; zero substituição por mocks | tools/taverna/native_access_tests | driver da tarefa T5 contra núcleo/relays fixados |
| Fundação/documentação | none | Build gate sem enfraquecer as 70 verificações | tools/taverna/tests | python3.12 -m unittest discover -s tools/taverna/tests -q |

Os comandos novos do driver serão definidos e entregues com cada tarefa; não são ferramentas existentes declaradas prontas. Gate falho impede concluir a tarefa e iniciar a dependente.

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | T1 | Compilar/executar a suíte Swift co-localizada; python3.12 -m unittest discover -s tools/taverna/tests -q |
| Full | T2 a T5 | Comando reproduzível do driver entregue na tarefa, Quick e regressões Foundation |
| Build | T6 | Todos os gates aplicáveis, python3.12 tools/taverna/check_foundation.py, python3.12 -m compileall -q tools/taverna, git diff --check; CI e Verifier no commit final |

## Execution Plan

### Phase 1: Native qualification

```text
T1 → T2 → T3
T3 → T4 → T6
T3 → T5 → T6
```

## Task Breakdown

### T1: Codec de negociação SOCKS

**What**: Validar frames e credenciais/rotas antes do transporte, com suíte Swift co-localizada.
**Where**: `apps/ios/SimpleXChat/Taverna/SocksCodec.swift`
**Depends on**: None
**Reuses**: SOCKS5 do núcleo fixado, contratos NP-01/02.
**Done when**:
- [x] Aceite exato e rejeições de versão/método/credencial/rota têm asserts; frames fragmentados são preservados até completos, com limite.
- [x] Gate Quick passa; 29 asserções Swift, 70 testes Foundation; nenhuma asserção existente alterada. Evidências em native-execution.md.
**Tests**: unit
**Gate**: Quick

### T2: Adaptador nativo TLS

**What**: Implementar listener loopback autenticado e transporte mTLS para backends fixos; testar integração com fixture exclusiva.
**Where**: `apps/ios/SimpleXChat/Taverna/RelayTransport.swift`
**Depends on**: T1
**Reuses**: Codec, Network.framework, ponte/inputs oficiais do experimento anterior.
**Done when**:
- [x] Componente isolado em macOS: ativo preserva TLS interno, credencial/rota/TLS inválidos negam; segredo de processo, timeout, cancelamento e limite são comprovados em dez testes. Ainda não é execução do app.
- [x] Keychain pessoal e política/containers de outras rodadas permanecem intactos; Full passa, com artefatos arm64 iOS Simulator compilados e regressões preservadas. Evidências em native-execution.md.
**Tests**: integration
**Gate**: Full

### T3: Política de início do núcleo

**What**: Aplicar configuração/credencial antes de iniciar ou reativar o núcleo no app.
**Where**: `apps/ios/Shared/Model/SimpleXAPI.swift`
**Depends on**: T2
**Reuses**: NetCfg, framework e controlador existente.
**Done when**:
- [x] Gate local corrigido passou 15 checkpoints: valor always independente, core parado sem transporte, precedência, não persistência e apiTestProtoServer real SMP/XFTP. Build dos quatro targets e regressões passaram na base reconciliada; reprodução limpa e re-verificação independente PASS no commit 53b31fdfe8398d858395dc4b366f814c76ff3c51, seis mutantes detectados. Evidências em native-execution.md.
**Tests**: integration
**Gate**: Full

### T4: Startup das extensões

**What**: Aplicar a mesma política antes de iniciar ou retomar o núcleo em cada extensão.
**Where**: `apps/ios`
**Depends on**: T3
**Reuses**: Política compartilhada e lifecycle NSE/Share existentes.
**Done when**:
- [ ] Build dos dois targets e provas de ordem no processo efetivo passam; teste unitário de framework não substitui execução da extensão.
**Tests**: integration
**Gate**: Full

### T5: Prova SMP/XFTP e falhas nativas

**What**: Entregar driver reproduzível de mensagens/arquivos, revogação, falha de autorização e sentinela com núcleo real.
**Where**: `tools/taverna/native_access_tests`
**Depends on**: T3
**Reuses**: Ferramentas de isolamento e fixture real fixada, sem reaproveitar dados/receipts.
**Done when**:
- [x] NP-05/06 no recorte app + cliente oficial passaram em cinco casos novos, com bytes exatos bilaterais, arquivo interrompido, novas conexões negadas e sentinela. Implementação transposta em 7d248badce6c4882c8ac879619d65bb782059141; novo build e Full clean 5/5 no HEAD 8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c. Verifier repetiu 5/5 e os 15 checkpoints de startup; sensor anterior 6/6 preservado como histórico por equivalência de fontes/produtos, sem gaps de T5. Evidências em native-execution.md e native-publication-revalidation.md; T4/T6 continuam abertas.
**Tests**: integration
**Gate**: Full

### T6: Relatório delimitado

**What**: Registrar provas por critério/processo e estado correto, sem liberar admissão ou piloto com gate ausente.
**Where**: `.specs/features/invitation-only/native-execution.md`
**Depends on**: T4, T5
**Reuses**: Comandos/receipts da rodada e obrigações NP-01..08.
**Done when**:
- [ ] NP-08 tem comandos/SHA/limites; relatório independente e sensor verificam o último commit antes de integração.
**Tests**: none
**Gate**: Build

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Início | Match |
| T2 | T1 | T1 → T2 | Match |
| T3 | T2 | T2 → T3 | Match |
| T4 | T3 | T3 → T4 | Match |
| T5 | T3 | T3 → T5 | Match |
| T6 | T4, T5 | T4 → T6; T5 → T6 | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Codec | unit | unit | Match |
| T2 | Adaptador | integration | integration | Match |
| T3 | Startup app | integration | integration | Match |
| T4 | Startup extensões | integration | integration | Match |
| T5 | Protocolo real | integration | integration | Match |
| T6 | Documentação | none | none | Match |

Granularidade: T1/T2 são componentes; T3 é um ponto compartilhado de startup; T4 é a integração da mesma política nas extensões; T5 é o driver; T6 é o relatório. Testes e estado são incluídos no commit da própria tarefa. Gates sem prova mantêm a tarefa aberta; eventual bloqueio é documentado no handoff sem marcar dependentes como concluídas.

## Sequência reconciliada

A execução efetiva da NSE é um gate próprio de T4. A documentação Apple distingue sua ativação por push remoto de notificações simuladas com simctl. O ambiente/caminho ainda precisa ser qualificado; compilação permanece evidência limitada. T5 depende do transporte e startup do app (T3), por isso pode comprovar payloads e revogação enquanto T4 está pendente. T6 exige T4 e T5 aprovados. Todas as obrigações NP e os critérios de integração permanecem exigidos.
