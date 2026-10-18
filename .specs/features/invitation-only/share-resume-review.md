# Revisão independente: retomada do recorte Share de T4

**Data:** 2026-10-18
**Método:** TLC Spec Driven, Verifier independente do autor
**Base da subentrega:** `8e9e65112d321af8c93dfbfb9bf62d534c4ac12e`
**SHA executado na terceira revisão:** `7ae8e03027516a4e54ff1ba5f8e2237e04296c31`
**SHA documental mapeado:** `8e7eb8c63eca4937dda98f153794f85160a642ff`
**Escopo:** somente o recorte Share de T4; sem concluir T4 inteira, T6, NP-01..08 ou a feature.

## Veredicto

**FAIL para fechar o recorte Share.** O build limpo e uma execução limpa em `7ae8e0302` passaram os 22 checkpoints no processo efetivo `SimpleX SE`. O gate não é reproduzível o bastante para aprovação: durante o sensor, a próxima execução parou antes de invocar a extensão porque o seletor de More não encontrou a célula dentro do prazo. A hierarquia de falha expõe `Mais` no descendente `cellTitleLabel`, enquanto o teste procura esse label no `Cell`. Não houve `share-result.json` nem evento before-main nessa tentativa. Ela não conta como mutante morto.

O sensor obrigatório terminou **1/5 killed, 1 inválido, 3 NOT RUN**. O limite de três ciclos de correção/revisão foi alcançado; não houve quarta correção automática. A evidência positiva permanece válida como diagnóstico, mas não supera o gate de invocação nem o sensor incompleto.

**Estado agregado:** feature `PARTIAL`; T4 `PARTIAL/FAIL no recorte Share`; NSE `NOT RUN / BLOCKED_ENVIRONMENT`; T6 `NOT RUN`; NP-01..08 continuam `Pending`. Nenhum merge, publicação, APNs, conta, serviço live ou recurso externo foi usado.

## Critérios e evidência direta

| Obrigação | Evidência observada | Resultado |
| --- | --- | --- |
| Invocar a extensão real pelo sistema | `TavernaShareTests.swift:38` — `XCTAssertTrue(FileManager.default.fileExists(...))`; `:40` — `XCTAssertEqual(status, "PASS")`; `:41` — `XCTAssertEqual(process, "SimpleX SE")` | **PASS em uma rodada; gate final FAIL por recorrência pré-invocação** |
| Aplicar transporte antes de criar/iniciar/reativar | `test_share.py:143` — `self.assertEqual(value['status'], 'PASS')`; `:144` — `self.assertEqual(value['checks'], CHECKS)`; produtores observados em `ShareModel.swift:174-191`, `ShareAPI.swift:24-35,88-93` e `ShareProbe.swift:65-148` | 22/22 no clean; M1 matou a remoção do preflight com `no_controller_without_transport` |
| Provar SMP/XFTP e negar fallback direto | `test_share.py:146` — `self.assertEqual(sentinel.count, 1)`; `:159` — `self.assertEqual({protocol ...}, {'smp','xftp'})` | Clean registrou SMP/XFTP e sentinela `1/0` |
| Vincular processo, PID, before-main, produtos e fonte | `test_share.py:148` — `self.assertEqual(value['process'], 'SimpleX SE')`; `:149` — `self.assertGreater(value['pid'], 0)`; `:151-154` — `self.assertTrue(...)` para PID/executável/fase/negações/loopback/mecanismo; `:164-165` — igualdade de porcelain e HEAD | Clean `run-share-cd6a4768` com `source_state` vazio e quatro produtos; M1 também chegou ao processo/before-main real |
| Manter target Share separado e sem filtros | `test_share.py:114` — `self.assertEqual(set(plan), {...})`; `:116-117` — `self.assertFalse(OnlyTestIdentifiers/SkipTestIdentifiers)` | PASS |
| Preservar first-build | `ios_proof.py:34-43` exige perfil e ausência de filtros; `:65-90` exige todos os casos PASS, zero falhas/skips e os quatro métodos; receipt e `tests.stdout.log` registram o resultado real | 4 métodos, 0 falhas, 0 skips, 91,662 s, inglês/portrait/light, no SHA `4e0051008`; carregado por equivalência de fontes, sem nova execução em `8e7` |
| Sensor de autorização mínimo cinco | `run-share-d1c73748` e `run-share-b7bb127f` no scratch independente | **FAIL: 1 morto, 1 inválido, 3 NOT RUN** |
| Executar NSE efetiva | `native-proof.md:42-45`; `nse-environment.md` | **NOT RUN / BLOCKED_ENVIRONMENT** |

## Build e execução limpa

- `.build/attempts/verifier-resume-20261018-build-c/receipt.json`: exit 0, commit `7ae8e0302`, `source_state` vazio, quatro produtos arm64 iOS Simulator, assinatura ad hoc e `account_provisioning: NOT USED`.
- `.build/access-qualification/run-share-cd6a4768/ios/share-driver-receipt.json`: um XCTest aprovado, zero falhas/skips; lista exata de 22 checks; processo `SimpleX SE`, PID 21177; SMP/XFTP autorizados; sentinela com uma conexão positiva e zero não autorizadas; contenção `test_socket_interposition`.
- `.build/access-qualification/run-share-cd6a4768/ios/ui.stdout.log`: seleção passou por Share qualification, centro de `activityImageView`, `activityTitleLabel` SimpleX e execução da extensão.
- A tentativa interrompida anterior `.build/attempts/verifier-final-build` permaneceu com seu resultado original e não recebeu PASS.

## Discrimination sensor

O sensor usou o scratch destacado `native-share-sensor-7ae8e030`, simulador próprio `98867D0A-7606-4832-BE36-05E1689D719A`, guard próprio e build-base válido. A primeira cópia de DerivedData produziu erro de PCM por caminho antigo; foi preservada e substituída por DerivedData vazio. Esse bootstrap não contou como mutante.

| Cenário | Mutação exata | Resultado |
| --- | --- | --- |
| M1 — preflight ausente | Em `ShareModel.swift:176-177`, remover `_ = try TavernaCoreTransport.networkConfig(getNetCfg())` antes de abrir banco/controlador | **KILLED.** Build allow-dirty passou. `run-share-d1c73748` invocou `SimpleX SE` PID 24466, registrou before-main por interposição e falhou com `no_controller_without_transport`. A UI chegou à linha da atividade e o XCTest recusou `status: FAIL`. |
| M2 — configuração depois de start | Em `ShareAPI.swift:24-26`, mover `apiSetNetworkConfig` para depois de `startChat` | **INVALID, não killed.** Build allow-dirty passou. `run-share-b7bb127f` falhou em `TavernaShareTests.swift:18`, `more.waitForExistence(timeout: 5)`, antes de qualquer tap na atividade. A hierarquia posterior mostra célula sem label próprio e filho `cellTitleLabel` com label `Mais`. Não há `share-result.json` ou before-main. |
| M3 — configuração depois de activate | Em `ShareAPI.swift:88-92`, mover `apiSetNetworkConfig` para depois de `apiActivateChat` | **NOT RUN.** O build allow-dirty concluído antes da ordem de parada foi preservado; nenhuma execução foi iniciada e nenhum resultado foi contado. |
| M4 — bypass da política gerenciada | Em `ShareAPI.swift:34-35`, enviar `cfg` sem `TavernaCoreTransport.networkConfig` | **NOT RUN.** |
| M5 — modo SOCKS não obrigatório | Em `CoreTransport.swift:53-62`, trocar `.always` por `.onion` | **NOT RUN.** |

Todas as mutações de produto foram revertidas e o diff de produto do scratch voltou vazio no HEAD `7ae8e0302`; nenhuma mutação atingiu o checkout do autor. O scratch mantém apenas a lição candidata L-004 em `.specs/lessons.json`/`.specs/LESSONS.md`; o integrador já portou esses dois registros e este relatório ao checkout do autor. O coletor auxiliar `simctl diagnose` de M2 foi encerrado somente depois de o XCTest terminar com falha; o teste, logs e xcresult foram preservados.

## Instabilidade observada

Esta é a terceira revisão do recorte:

1. `73d5a989a` foi rejeitado porque a qualificação Share estava composta no target first-build e o driver usava filtro incompatível com o gate.
2. Em `4e0051008`, `run-share-5389a72a` falhou antes da extensão e `run-share-8d74e366` passou no mesmo build; 1/2 não fechou o gate. A tentativa More pela célula inteira também falhou antes da tabela.
3. `7ae8e0302` passou uma execução limpa com centro do ícone, mas M2 voltou a falhar antes da extensão. O log atual mostra que a consulta ainda depende do label agregado do `Cell`, embora a árvore de falha exponha `Mais` apenas no filho `cellTitleLabel`.

A causa de todas as ocorrências históricas não foi isolada. A falha atual é suficiente para reprovar o gate porque impede observar o comportamento mutado e deixa quatro dos cinco cenários requeridos sem prova.

## Regressões preservadas

- As oito chamadas `XCTAssert*` de `TavernaShareTests.swift` permanecem com as mesmas expressões e ordem em `4e0051008`, `7ae8e0302` e `8e7eb8c63`; o `XCTUnwrap` também permanece.
- A prova independente first-build em `4e0051008` executou os quatro métodos originais sem filtros: 4/4, zero falhas/skips, 91,662 s. O coletor auxiliar foi encerrado só depois dos quatro métodos concluírem.
- As provas do autor em `4e0051008` permanecem evidência de regressão: payload 5/5 em 162,838 s e startup do app com 15 checkpoints. Não são nova execução em `7ae` ou `8e7`.
- No SHA documental `8e7eb8c63`, Foundation passou 76/76; `check_foundation.py`, `compileall` e `git diff --check` passaram. `validate_spec.py` retornou 0 erros/0 avisos; `validate_tasks.py native-tasks.md`, 0 erros e um aviso esperado para `T6 Tests: none`.
- O Verifier não repetiu seu próprio startup no SHA mapeado depois da escalada. Esse item permanece sem nova prova nesta revisão.

## Mapeamento documental

`git diff 7ae8e0302..8e7eb8c63` alterou somente `.specs/STATE.md`, `native-execution.md` e `nse-environment.md`. `git diff --exit-code ... -- apps/ios tools` e `git diff --check` passaram. Os blobs de `TavernaShareTests.swift`, ShareAPI, ShareModel, ShareProbe, ShareProbeGuard, CoreTransport e `test_share.py` são idênticos nos dois SHAs. Assim, os artefatos de `7ae` preservam sua proveniência; este relatório **não alega nova execução iOS em `8e7`**.

## Contenção e limites

A contenção da extensão é interposição dyld somente em DEBUG Simulator para `connect`, `connectx`, `sendto` e `sendmsg`, identificada como `test_socket_interposition`. Ela permite Unix/loopback e nega destinos IPv4/IPv6 externos antes do main. Não é sandbox do kernel, não cobre syscalls diretas, descritores herdados ou serviços do sistema e não prova isolamento da sessão iOS. O app principal mantém seu guard de kernel. A sentinela loopback continua relevante porque o filtro permite loopback e, portanto, não esconderia fallback direto até esse destino.

## Gaps classificados e próximo gate

1. **P0 — gate Share não reproduzível:** substituir a descoberta de More baseada no label agregado do `Cell` por uma relação derivada da hierarquia estável observada (`cellTitleLabel` descendente e respectivo ícone/célula), sem coordenada fixa nem redução das oito asserções. O plano é proposto; não foi implementado nesta revisão.
2. **P0 — sensor incompleto:** após nova autorização de ciclo, uma baseline limpa estável precisa preceder pelo menos cinco mutações comportamentais. Só contam falhas após invocação real, processo `SimpleX SE`, before-main e bootstrap válidos.
3. **P1 — regressões finais:** repetir os gates aplicáveis no novo SHA, incluindo startup independente; first-build/payload anteriores podem ser citados somente com origem e equivalência explícitas.
4. **P1 — NSE:** qualificar ambiente APNs Sandbox isolado e depois executar a NSE do produto pelo sistema. Controle mínimo, `simctl push`, build do target ou classe instanciada no app não substituem essa prova.

Nenhum item acima autoriza recurso live, publicação ou merge. Até nova revisão independente, o recorte Share permanece FAIL e T4/T6/NP agregados permanecem abertos.
