# Revisão independente: transporte nativo T1/T2

**Veredicto geral:** PARTIAL. T1 PASS como codec isolado no commit `e0bb288974e22773152e81f49c52c9d9b17ed2c9`. T2 FAIL no gate Full; a atribuição causal permanece INCONCLUSIVE. A feature, o app e NP-01..08 não estão concluídos.

**Data:** 2026-10-16
**Base informada:** `b0fe90f0261d7af3dfe3a382f12b6a1128d1ecce`
**HEAD verificado:** `e0bb288974e22773152e81f49c52c9d9b17ed2c9`
**Diff T1:** `e0bb28897^..e0bb28897`
**Verifier:** agente independente do autor; ownership limitado a este relatório

## T1: PASS para o codec isolado

T1 satisfaz os dois itens de `native-tasks.md:47-51`. O resultado não comprova listener, TLS externo, TLS interno, processo iOS, SMP, XFTP ou NP-01/02 completos.

| Obrigação de T1 | Evidência rederivada | Resultado |
| --- | --- | --- |
| Exigir autenticação usuário/senha e falhar em versão, método ou credencial inválidos | `apps/ios/SimpleXChat/Taverna/SocksCodec.swift:44-72`; `tools/taverna/native_access_tests/SocksTests.swift:21-22`, `:32-41` comparam replies e fechamento exatos | PASS |
| Autorizar somente as duas rotas DNS configuradas | `SocksCodec.swift:73-105`; `SocksTests.swift:23`, `:43-59` comparam `.connect` ou reply SOCKS + close para host, porta, comando e tipo de endereço | PASS |
| Preservar fragmentação, pipeline e bytes opacos | `SocksCodec.swift:38-42`, `:106-109`; `SocksTests.swift:24-31` comparam a sequência inteira de eventos e os bytes | PASS |
| Limitar entrada e tornar falha terminal | `SocksCodec.swift:39-40`; `SocksTests.swift:32-34`, `:56` exigem ausência de recuperação e close acima do limite | PASS |
| Gate Quick | suíte Swift: `29 assertions passed`; Foundation: `Ran 70 tests ... OK`; checker Foundation: PASS; `git diff --check`: exit 0 | PASS |
| Integridade da entrega | commit checker: PASS; `validate_tasks.py`: 0 erros, 1 aviso esperado para T6 sem testes; o commit toca somente codec, suíte e dois artefatos TLC | PASS |

O relatório de execução delimita corretamente a alegação em `native-execution.md:5` e `:24-26`: bytes opacos no codec não são prova de TLS interno; NP-01/02 completos continuam pendentes. `native-proof.md:55-62` mantém NP-01..08 como `Pending`.

## Sensor de discriminação T1

O sensor usou somente cópias em `Projects/taverna-native-t1-sensor-e0bb28897`. Não houve `stash`. O diretório scratch foi removido ao final.

| Mutação em cópia | Assert que matou | Resultado |
| --- | --- | --- |
| M1: senha deixou de participar da comparação de credencial | `SocksTests.swift:37`, `NP-01: wrong process credential denied` | KILLED, exit 133 |
| M2: destino DNS válido deixou de exigir presença no conjunto de rotas | `SocksTests.swift:45`, `NP-02: unauthorized or malformed destination denied before connect` | KILLED, exit 133 |
| M3: estágio stream descartou payload em vez de emiti-lo | `SocksTests.swift:24`, `NP-03: opaque bytes after authorization` | KILLED, exit 133 |

**Sensor:** 3/3 mortos, 0 sobreviventes. O texto NP-03 de M3 nomeia somente preservação de bytes no teste. Ele não foi contado como prova de NP-03.

O porcelain real antes e depois do sensor foi idêntico:

```text
 M tools/taverna/access_proof/fixture.py
?? apps/ios/SimpleXChat/Taverna/RelayTransport.swift
?? tools/taverna/native_access_tests/RelayDriver.swift
?? tools/taverna/native_access_tests/test_transport.py
```

## T2: FAIL no gate; causa INCONCLUSIVE

T2 permanece não commitado e os dois itens de `native-tasks.md:59-63` continuam desmarcados. O handoff registra 8 de 9 testes aprovados e erro estável em `test_05_revocation_and_policy_failure_cut_streams`, com primeira execução `native-f24d6411`, repetição isolada `native-fc303b7f` e repetição sem resumption/tickets `native-ff2e5ec2`. Os três diretórios e seus drivers existem sob `.build/access-qualification`. O Verifier não executou uma quarta rodada, conforme o limite da investigação.

O erro acontece na abertura de um novo TLS interno no começo da subiteração `unavailable=True`, em `test_transport.py:164`, antes de `policy.json` ser removido em `:166`. A subiteração anterior já tinha fechado dois fluxos, negado nova conexão e restaurado Alice em `:173`. O erro observado é `ssl.SSLEOFError`.

### O que a leitura prova

1. O SOCKS local e o TLS externo chegaram além da autenticação e da rota. `RelayTransport.swift:167-173` só envia a resposta SOCKS de sucesso depois que a `NWConnection` TLS externa entra em `.ready`. O EOF ocorre quando `inner_tls()` inicia o TLS do relay em `test_transport.py:99-108`.
2. Depois do TLS externo ficar pronto, o gateway ainda pode fechar por três famílias de causa: autorização falsa antes/depois do backend (`gateway.py:43-48`), falha ao abrir o backend (`:45-57`) ou encerramento do fluxo (`:50-66`). Essas causas são convertidas no mesmo EOF visto pelo cliente.
3. O gateway não registra nenhuma dessas decisões. As execuções preservadas contêm somente `READY: experimental boundary...`; os `stderr.log` dos drivers estão vazios. Portanto o artefato não prova se `permitted()` retornou falso, se o backend falhou ou se o fechamento veio do adaptador.
4. A política final preservada nas três rodadas tem schema 1, Alice e Bob ativos, e exclui unknown. Isso prova o estado final, não o estado visível ao gateway no instante do EOF.
5. Não há estado de revogação persistido no Swift. Cada cliente cria uma `Session` e uma `NWConnection` novas em `RelayTransport.swift:59-65` e `:81-100`; `Session.close()` cancela cliente/remoto e remove a sessão em `:130-135`. A leitura não encontrou um caminho explícito que mantenha Alice revogada no adaptador.
6. Desabilitar resumption e tickets em `RelayTransport.swift:85-89` não eliminou a falha na terceira rodada. Isso reduz a plausibilidade de reutilização de sessão TLS como causa, mas não prova o restante do lifecycle assíncrono de Network.framework.

### Hipótese mais forte, ainda não provada

A fixture abre a segunda subiteração sem uma barreira de transição. `fixture.py:34-38` substitui o arquivo de política e retorna sem confirmação do consumidor. `test_transport.py:173` restaura Alice e o laço volta imediatamente para `:164`. O gateway consulta a política a cada conexão e seu watcher usa polling de 0,2 s em `gateway.py:50-52`. A suíte de fronteira anterior adiciona 0,3 s depois de restaurar a política em `test_boundary.py:14-18`; a suíte nativa não tem espera ou readback equivalente em `test_transport.py:55-59` nem dentro de T2-05.

Esse contraste e a repetição no mesmo ponto tornam uma corrida de visibilidade/transição da fixture a explicação mais provável. Ela não pode ser promovida a causa raiz sem um trace sanitizado da decisão de `permitted()` e da abertura do backend. Um defeito assíncrono do adaptador também não está excluído.

O integrador informou uma reprodução fresca da fixture default com 12/12 `test_boundary.py` aprovados. Isso enfraquece uma regressão geral em `permitted()` ou no modo legado, mas não reproduz a publicação loopback, PKCS#12, Network.framework nem a transição imediata da suíte nativa.

## Evidência secundária e limites

- `RelayTransport.swift`, `RelayDriver.swift` e `test_transport.py` permanecem untracked; `fixture.py` permanece modificado. Nenhum deles recebeu aprovação ou commit desta revisão.
- Há artefatos arm64 macOS e iOS Simulator sob `.build/native-access`, e o integrador informou compilação nos dois destinos. A presença de binários/cache não substitui um receipt de build nem o gate runtime.
- Nenhum experimento Docker/E2E, simulador, Keychain, provider ou rede foi iniciado pelo Verifier.
- T3, T4, T5 e T6 não foram iniciados por esta revisão. NP-03..08 não recebem PASS. NP-01/02 continuam parciais porque T1 é somente o codec.
- `validate_state.py invitation-only` não deve passar enquanto a feature de 34 requisitos e NP-01..08 permanecer incompleta. Este relatório não cria nem falsifica `validation.md`.

## Gaps ranqueados

1. **Gate T2 falho:** 8/9 não satisfaz Full; T2 e todas as dependentes permanecem bloqueadas.
2. **Sem trace causal:** o gateway reduz autorização negada, backend indisponível e erro TLS ao mesmo EOF e só registra `READY`. Falta evidência do ramo executado no instante da falha.
3. **Transição sem barreira:** a restauração em `test_transport.py:173` não tem confirmação de visibilidade antes da próxima conexão em `:164`; o contraste com `test_boundary.py:18` sustenta uma corrida provável.
4. **Adapter não absolvido:** a revisão estática não encontrou estado de revogação aderente, mas callbacks e estados de Network.framework não foram observados no momento do EOF.
5. **Receipts incompletos:** os resultados 8/9 e as compilações foram entregues no handoff; não há transcript versionado que permita rederivar contagem, traceback e comando exato sem repetir o experimento proibido.

## Próximo gate

O limite de três tentativas foi atingido. Não cabe uma quarta execução cega. Antes de nova verificação, o implementador precisa separar o ramo causal com trace sanitizado ou uma barreira observável de política, preservar o caso de revogação e então apresentar um novo gate Full. Alterar ou relaxar a expectativa de T2-05 não é correção.

## Lição fundamentada para o integrador

O FAIL e a ausência de trace geram um sinal `gate_fail`. O Verifier não executou o comando porque `.specs/lessons.json` e `.specs/LESSONS.md` estão fora de seu ownership. O integrador pode registrar:

```bash
python3.12 .agents/skills/tlc-spec-driven/scripts/lessons.py add \
  --feature invitation-only \
  --signal gate_fail \
  --source ".specs/features/invitation-only/native-review.md#t2-fail-no-gate-causa-inconclusive" \
  --text "Record sanitized authorization decisions and backend-open failures before treating a TLS EOF as causal evidence" \
  --scope tools/taverna/native_access_tests
```

## Conclusão

**PARTIAL:** T1 está aprovado como codec isolado no SHA `e0bb28897`, com gate Quick e sensor 3/3. T2 está reprovado no gate Full e causalmente inconclusivo; a hipótese principal é uma corrida de transição da fixture, não um fato demonstrado. O app, as extensões, SMP/XFTP ponta a ponta e os requisitos NP-01..08 permanecem sem conclusão.
