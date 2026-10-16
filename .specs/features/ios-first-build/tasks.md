# Tarefas do primeiro build iOS

## Execution Protocol

Usar tlc-spec-driven conforme a skill versionada. A especificação, sua execução e a rota Nix foram autorizadas pelo proprietário. Esta decomposição preserva os critérios aprovados. Verificar e fechar cada tarefa separadamente, sem marcar uma etapa concluída só porque sua preparação terminou. O preparo de T2 independe das bibliotecas e pode ocorrer enquanto a operação Nix de T1 aguarda; T3 exige ambas aprovadas. O Verifier independente é obrigatório após o último commit de implementação.

**Design:** [design.md](design.md).
**Status:** In Progress — preparação administrativa concluída; T1 em andamento, sem biblioteca qualificada ainda.

Ferramentas: Git nativo, Python 3.12 stdlib, Nix 2.34.9 e ferramentas do Xcode instalado. A integração de handoff, CI e locks nesta branch pertence ao Codex. Não há delegação de implementação; sete tarefas cabem em uma sequência local. A verificação final será independente.

## Test Coverage Matrix

Gerada de AGENTS.md, CONTRIBUTING.md, docs/taverna/environments.md, CI Foundation e amostras de tools/taverna/tests, além dos dois arquivos de testes iOS existentes. Os 28 testes Foundation são o piso; não representam um build iOS. Não há linter Swift configurado para esta entrega; usar compilação e git diff --check, sem inventar gate de ferramenta ausente.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Receita e preparação do núcleo | integration | Fonte/lock fixados, hashes, licença, plataforma, falhas de origem/extração e limites aplicáveis | Registros próprios de cada tentativa sob .build/attempts | Nix com no-write-lock-file e no-update-lock-file; conferências de produtos reais descritas no registro |
| Ambiente de execução | integration | UDID exclusivo e armazenamento físico local, destino efetivo do Xcode, rede negada com controle externo, retomada sem apagar outra sessão | Registros próprios sob .build/attempts e .build/SimulatorDevices | simctl e probes reais do executor; comando exato e resultado registrados antes de considerar T2 concluída |
| Interface inicial iOS | e2e | Get started visível/habilitado, Your profile após toque, sem envio de formulário; suíte herdada preservada | apps/ios/Tests iOS | xcodebuild test do scheme SimpleX (iOS), com destino qualificado e caminhos locais explícitos |
| Validação da prova | unit + integration | Rejeitar hash/plataforma errados, produto ausente, etapa falha/timeout e zero testes obrigatórios; conferir artefatos reais | tools/taverna/tests | python3.12 -m unittest discover -s tools/taverna/tests; validação da tentativa real |
| Documentação e handoff | none | Links, comandos comprovados, estado factual e nenhum material privado versionado | docs/taverna e .specs/features/ios-first-build | check_foundation.py, validate_spec.py e conferência de links da feature |

## Gate Check Commands

Os comandos existentes vêm de CONTRIBUTING.md. Comandos específicos do build são fixados no registro da tarefa após os probes de compatibilidade; não declarar um comando candidato como executado. Toda tentativa registra exit code e preserva falhas. Ausência de prova impede avançar.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Código Python da prova | python3.12 -m unittest discover -s tools/taverna/tests |
| Full Native | T1 | Quick + avaliação/realização Nix fixada + inspeção e hashes das bibliotecas reais |
| Full Session | T2 | Quick + prova real de destino exclusivo e contenção de rede |
| Full iOS | T3 | Full Session + xcodebuild do app/framework/extensões + suíte iOS, com exit 0 e testes obrigatórios executados |
| Build | T4–T6 e fechamento | Quick + python3.12 tools/taverna/check_foundation.py + python3.12 -m compileall -q tools/taverna + git diff --check; repetir Full iOS quando exigido pela tarefa |

## Execution Plan

Ordem completa, incluindo dependências entre fases:

```text
T1 → T3 → T4 → T5 → T6
T2 → T7 → T3
```

### Phase 1: Núcleo e sessão

```text
T1  T2 → T7
```

### Phase 2: Compilação e prova

```text
T3 → T4
```

### Phase 3: Reprodução e documentação

```text
T5 → T6
```

## Task Breakdown

### T1: Realizar e qualificar o núcleo fixado

**What**: Produzir o conjunto nativo com origem e plataforma comprovadas, registrando preparação, comandos e resultados.
**Where**: `.specs/features/ios-first-build/execution.md`
**Depends on**: None
**Reuses**: flake.nix, flake.lock, cabal.project e mac2ios da revisão fixada.
**Requirement**: IOS-01, IOS-02, IOS-07, IOS-09, IOS-16, IOS-19.
**Tools**: Nix e ferramentas nativas de inspeção; TLC Spec Driven.
**Tests**: integration; registros de avaliação, realização, hashes e inspeção dos objetos reais. O download de um compilador auxiliar não prova a biblioteca final.
**Gate**: Full Native.
**Done when**:

- [ ] Bibliotecas e manifesto real identificam URL imutável do fonte, commit, receita, licença e hashes dos artefatos originais/transformados.
- [ ] Arquitetura e plataforma de simulador são comprovadas; uma entrada incompatível ou sem origem permanece bloqueada.
- [ ] O registro distingue produto construído localmente de eventual produto obtido por substituição de cache, sem afirmar reconstrução local indevida.

### T2: Provar a sessão isolada

**What**: Demonstrar um executor que seleciona o simulador próprio e contém IP remoto no processo do app antes do main, conforme APP-004.
**Where**: `tools/taverna/ios_session.py`, `tools/taverna/ios/`, `tools/taverna/tests/test_ios_session.py`, `.specs/features/ios-first-build/execution.md`
**Depends on**: None
**Reuses**: simctl padrão, controles UIKit qualificados e política de estado local da fundação.
**Requirement**: IOS-04, IOS-05, IOS-10, IOS-15.
**Tools**: CLI Xcode e probes locais; TLC Spec Driven.
**Tests**: integration; controle externo bloqueado e correspondência entre UDID, armazenamento físico, aliases e destino do executor; rejeição de destino alheio e helper ausente/divergente. Um probe sintético é prova do ambiente, não prova do app.
**Gate**: Full Session.
**Done when**:

- [x] Produtos, caches, bancos, dados e logs físicos do simulador pertencem ao worktree; índices por UDID do SDK são aliases próprios, respeitada a exceção Nix autorizada.
- [x] O executor Xcode seleciona o UDID exclusivo registrado no índice padrão do SDK, com correspondência física comprovada.
- [x] A contenção de IP remoto no processo do app antes do main e a comunicação local são demonstradas sem alterar VPN/firewall global; se não houver método comprovado, não lançar o app e registrar BLOCKED.
- [x] Nova tentativa preserva registros anteriores e não limpa outras sessões.

### T7: Confinar os caches efetivos do Xcode

**What**: Corrigir a lacuna encontrada após T2: CFFIXED_USER_HOME e os caches de módulos não relocam CACHE_ROOT do Xcode.
**Where**: `tools/taverna/ios_session.py`, `tools/taverna/tests/test_ios_session.py`, `.specs/features/ios-first-build/execution.md`
**Depends on**: T2
**Reuses**: preflight e controle UIKit de T2; mesma aprovação APP-004, sem mudança de critério.
**Requirement**: IOS-04, IOS-05, IOS-10, IOS-15.
**Tools**: Python 3.12 e Xcode; TLC Spec Driven, execução inline.
**Tests**: unit + integration; rejeitar cache global, campo ausente e alias escapando do worktree; repetir destino/controle com os ajustes efetivos corrigidos.
**Gate**: Full Session + Build.
**Done when**:

- [x] CACHE_ROOT, precompilados, estatísticas de SDK e CAS efetivos pertencem ao worktree; campos ausentes ou externos impedem avançar.
- [x] Controle UIKit e sensor sem guard continuam discriminantes; testes herdados preservados.
- [x] Falha anterior permanece registrada e a nova tentativa não a sobrescreve.

### T3: Acrescentar e executar o teste observável

**What**: Acrescentar um teste da navegação inicial e compilar/executar a suíte do app com entradas qualificadas.
**Where**: `apps/ios/Tests iOS/Tests_iOS.swift`, `apps/ios/Tests iOS/Tests_iOSLaunchTests.swift`
**Depends on**: T1, T7
**Reuses**: XCTest e testes existentes, sem remover asserções ou usar skips para obter sucesso.
**Requirement**: IOS-03, IOS-06, IOS-08, IOS-11, IOS-12, IOS-13.
**Tools**: Xcode/xcodebuild; TLC Spec Driven.
**Tests**: e2e, no mesmo arquivo; preservar os três métodos de teste herdados nos dois arquivos da suíte e acrescentar um método com asserções do onboarding. Configurar todas as instâncias de XCUIApplication com o guard qualificado, sem eliminar launch/performance/screenshot herdados. Contagens efetivas, inclusive configurações de UI repetidas pelo XCTest, devem constar do resultado.
**Gate**: Full iOS.
**Done when**:

- [ ] Sete revisões SwiftPM preservadas e configuração efetiva de assinatura registrada sem provisionamento de conta.
- [ ] App, framework, NSE e Share Extension compilados e identificados.
- [ ] Get started visível e habilitado em 30 s; após o toque, Your profile visível em 30 s; nenhum envio do formulário.
- [ ] Suíte real aprovada, com contagens de execução/falha/skip e artefatos, sem usar somente screenshot ou medição de launch como prova da interface.

### T4: Validar os artefatos e estados da prova

**What**: Implementar a checagem da prova real, rejeitando sucesso vazio ou artefatos inconsistentes.
**Where**: `tools/taverna/ios_proof.py`
**Depends on**: T3
**Reuses**: Python stdlib, estilo unittest da fundação e estrutura real do resultado Xcode observado em T3.
**Requirement**: IOS-02, IOS-09, IOS-14, IOS-16, IOS-19, IOS-20.
**Tools**: Python 3.12 e ferramentas Xcode para inspeção; TLC Spec Driven.
**Tests**: unit + integration, co-localizados em tools/taverna/tests; uma asserção por resultado definido, incluindo produto ausente, hash errado, plataforma errada, etapa não zero, timeout e teste obrigatório não executado. Fixtures são fictícias; o gate também exige a tentativa real de T3.
**Gate**: Build + validação dos artefatos reais.
**Done when**:

- [ ] Tests derivam dos critérios, preservando pelo menos os 28 testes Foundation anteriores.
- [ ] Falha ou ausência de etapa/produto/teste impede PASS e produz exit não zero com indicação da etapa.
- [ ] Registros contêm fonte, manifesto, versões, destino, comandos sanitizados, saídas e hashes; build do app, origem do núcleo e assinatura/push têm estados separados.
- [ ] Binários, screenshots e xcresult permanecem no estado ignorado.

### T5: Documentar o procedimento reproduzível

**What**: Publicar no guia local os comandos efetivamente comprovados, limites, dependências e retomada.
**Where**: `docs/taverna/ios-build.md`
**Depends on**: T4
**Reuses**: Registros reais de T1–T4 e guia de ambientes.
**Requirement**: IOS-04, IOS-07, IOS-15, IOS-16, IOS-19, IOS-20.
**Tools**: Arquivos locais e Git; TLC Spec Driven.
**Tests**: none — documentação, conforme matriz; comandos de build precisam corresponder às execuções registradas.
**Gate**: Build e links relativos válidos.
**Done when**:

- [ ] Guia pode ser seguido em outro worktree, sem memória de chat, credenciais ou Downloads compartilhado.
- [ ] Explica origem das bibliotecas, método de isolamento comprovado, tentativas e limites da prova.

### T6: Apresentar o estado factual e repetir a prova

**What**: Atualizar a entrada do projeto com o resultado comprovado e obter duas execuções do commit final de implementação em ambientes distintos.
**Where**: `README.md`
**Depends on**: T5
**Reuses**: Guia, receipts e validação de artefatos.
**Requirement**: IOS-17, IOS-18, IOS-19, IOS-20.
**Tools**: Git, Xcode e Verifier independente; TLC Spec Driven.
**Tests**: integration; repetir Full iOS no commit final e em worktree/caches/UDID distintos. Nenhum runtime/estado gravável da primeira sessão substitui a segunda prova.
**Gate**: Build + duas provas reais no mesmo commit de implementação, CI nesse commit e Verifier com sensor discriminante.
**Done when**:

- [ ] README informa resultado e data reais, com link para o guia e limites de identidade, assinatura, push e distribuição.
- [ ] Autor e Verifier registram execuções do mesmo commit final de implementação; commits posteriores somente de relatório identificam esse SHA explicitamente.
- [ ] Verifier cobre todos os critérios e confirma que as checagens matam falhas injetadas em cópia isolada.
- [ ] Publicação/CI remota respeitam a autorização correspondente. Gate remoto pendente não é apresentado como aprovado.

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | Um conjunto nativo e seu registro operacional | Granular |
| T2 | Um ambiente de execução e seu registro | Granular |
| T7 | Correção dos caches desse ambiente | Granular |
| T3 | Um teste UI no arquivo existente, com gate real | Granular |
| T4 | Um validador da prova e testes do próprio componente | Granular |
| T5 | Um guia | Granular |
| T6 | Uma entrada de estado do produto e gate de reprodução | Granular |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Entrada da fase 1 | Match |
| T2 | None | Entrada independente da fase 1 | Match |
| T7 | T2 | T2 → T7 na fase 1 | Match |
| T3 | T1, T7 | Entrada da fase 2 após núcleo e sessão corrigida | Match |
| T4 | T3 | T3 → T4 | Match |
| T5 | T4 | Entrada da fase 3 após fase 2 | Match |
| T6 | T5 | T5 → T6 | Match |

## Test Co-location Validation

| Task | Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Núcleo operacional | integration | integration com artefatos reais | Match |
| T2 | Ambiente operacional | integration | integration com probes reais | Match |
| T7 | Caches do ambiente | unit + integration | Python + controle real | Match |
| T3 | UI | e2e | e2e no arquivo alterado | Match |
| T4 | Validador | unit + integration | Testes e prova real no mesmo componente | Match |
| T5 | Documentação | none | none, gate documental | Match |
| T6 | Reprodução | integration | integration real repetida | Match |

## Estado

T1 em andamento; T2 concluída como ambiente com controle UIKit sintético e preflight real. T7 concluída: CACHE_ROOT e caches efetivos confinados e gate repetido; T3–T6 pendentes. Nenhuma conclusão de feature declarada; todos os requisitos permanecem sem verificação final.
