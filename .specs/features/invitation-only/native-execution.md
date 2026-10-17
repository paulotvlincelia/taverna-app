# Execução: transporte nativo

Estado atual: T1–T3/T5 passaram no recorte anterior e permanecem registrados abaixo. Em 2026-10-17, o recorte Share de T4 passou em desenvolvimento; repetição limpa e revisão independente ainda precedem sua publicação. T4 inteira exige NSE efetiva, T6 depende dela, e os oito critérios agregados permanecem Pending. As tentativas abaixo são históricas, com os respectivos limites.

## T1: codec SOCKS

2026-10-16. Componente implementado em apps/ios/SimpleXChat/Taverna/SocksCodec.swift; ainda não ligado ao app. Suíte co-localizada em tools/taverna/native_access_tests/SocksTests.swift. Gate: 29 asserções passaram, 70 regressões Foundation e checker passaram, diff sem whitespace inválido. Não é prova de TLS, processo iOS ou mensagens.

```sh
mkdir -p .build/native-access
xcrun swiftc -module-cache-path .build/native-access/module-cache apps/ios/SimpleXChat/Taverna/SocksCodec.swift tools/taverna/native_access_tests/SocksTests.swift -o .build/native-access/socks-tests
.build/native-access/socks-tests
python3.12 -m unittest discover -s tools/taverna/tests -q
python3.12 tools/taverna/check_foundation.py
git diff --check
```

### Adequação e cobertura reversa

| Critério/edge | Asserção em SocksTests.swift | Resultado exigido |
| --- | --- | --- |
| NP-01, autenticação | :21/22/33/37/39/41, igualdade de replies e close | Só método com credencial correta autoriza; versões/métodos/segredos inválidos falham |
| NP-01, fragmentação/pipeline | :27/31, igualdade de toda a sequência de eventos | Mesmo CONNECT autorizado, sem perder bytes TLS ou autorizar cedo |
| NP-01, terminal/limite | :34/56, isEmpty após falha e close para chunk excessivo | Falha não se recupera; entrada limitada |
| NP-02, destinos | :23/45/48/51/54/57/59, igualdade de connect ou reply+close | Apenas as duas rotas; demais formas/portas/comandos negados |
| T1, preservar bytes opacos | :24/27/31, payload exato | Codec não altera bytes após negociação; não é prova de TLS interno |

Cada assert mapeia a NP-01/02 ou à preservação de bytes deste componente. Nenhum teste alega comprovar NP-03 completo. Diretrizes: AGENTS.md, CONTRIBUTING.md; sem teste raso, mock de mensagem ou asserção anterior removida. NP-01/02 completos continuam pendentes até integração e sensor. T2 adicionará o listener e TLS externo com credencial fictícia e armazenamento exclusivo.

## T2: listener e TLS do componente

2026-10-16. Componente Swift compilado sem warnings para macOS arm64 e arm64 iOS Simulator. Dez testes de integração executaram Network.framework no macOS contra a ponte e os relays oficiais da fixture. A execução iOS e os processos do app/extensões ainda não aconteceram. A preparação do simulador só executou o controle UIKit de contenção, sem contar como prova da Taverna.

Gate corrigido: rodada `native-f3fb46e4`, 10 testes em 28,415 segundos, zero falhas/skips; 29 asserções de codec e 70 regressões preservadas. A rodada `native-9474be0c` anterior passou os nove testes, antes de acrescentar o negativo de confiança TLS interna. Receita padrão do experimento anterior continua com suas 12 verificações e nenhuma porta publicada.

```sh
xcrun swiftc -swift-version 5 -warnings-as-errors -module-cache-path .build/native-access/module-cache apps/ios/SimpleXChat/Taverna/SocksCodec.swift apps/ios/SimpleXChat/Taverna/RelayTransport.swift tools/taverna/native_access_tests/RelayDriver.swift -o .build/native-access/relay-driver
python3.12 tools/taverna/native_access_tests/test_transport.py
```

O driver gera slug novo automaticamente e exige os quatro inputs oficiais já qualificados em .build/access-qualification/bin. Não baixa executáveis ou usa credenciais pessoais. Importa PKCS#12 fictício apenas na memória: comportamento padrão no iOS; `kSecImportToMemoryOnly` explícito no macOS 15+. A capability SOCKS aleatória vai por pipe anônimo ao teste, sem arquivo de credenciais, UserDefaults ou log.

O modo nativo usa CA/dispositivos P-256 exclusivos e duas portas aleatórias da ponte publicadas em 127.0.0.1. Redes inner/outer continuam internas; somente o gateway participa da bridge nativa de acesso pelo host. Essa bridge tem a conectividade normal do Docker e não equivale a contenção offline de toda a sessão. Relays não publicam portas. A receita default mantém redes exclusivamente internas e zero publicação; seus critérios anteriores não foram alterados.

### Falhas preservadas e correção da preparação

A primeira tentativa `native-3fc464e9` terminou no preparo: o Docker não atribuiu as portas publicadas de um container ligado somente a redes internas. A bridge nativa exclusiva resolveu a conectividade pelo host, sem alterar redes de outros projetos.

`native-f24d6411` passou 8 de 9 testes, mas falhou ao restaurar a associação para o controle positivo seguinte. O mesmo ponto falhou na repetição isolada `native-fc303b7f` e em `native-ff2e5ec2` com retomada TLS desabilitada. O [review histórico independente](native-review.md) aprovou T1 e manteve T2 FAIL/INCONCLUSIVE, com 3/3 mutantes do codec detectados. Essas tentativas não foram promovidas a PASS.

O próximo gate acrescentou eventos sanitizados do gateway e confirmação do estado visível no mount do consumidor antes do controle positivo. Não houve mudança de resultado esperado ou de asserção de acesso/revogação. `native-2cbc4368` passou os corpos dos testes, mas encontrou erros transitórios no readback de preparação. A barreira agora espera confirmação por até cinco segundos, preservando os erros locais; não adia os asserts de revogação. As duas rodadas seguintes passaram. Não afirmamos uma causa raiz inequívoca para o EOF original; os resultados demonstram a qualificação com essa precondição explícita.

A hipótese de TLS resumption não resolveu a falha e as flags experimentais de desativação foram retiradas. O protocolo e a criptografia SimpleX não mudaram. O snapshot dos fontes WIP anteriores à observação, seus hashes, gateway.log, policy-readbacks e native-test-receipt.json ficam em .build. O receipt final vincula os fontes e o executável efetivamente usado. Nenhum raw log ou certificado é publicado.

### Adequação e cobertura reversa T2

| Teste/asserção em test_transport.py | Obrigação | Resultado exigido |
| --- | --- | --- |
| :113/124 e test_00 | NP-03, componente | SOCKS success e certificado TLS interno byte a byte igual ao relay real |
| :134–147 e :100/105/106 | NP-01 | Segredos de processos distintos; no-auth, senha incorreta e credencial de outro processo recusadas |
| :158/159 | NP-02 | Reply ruleset-denied para destino/porta não autorizado e nenhuma conexão à sentinela após controle positivo |
| :165/175 | NP-03/04 | Sem associação ou sem CA/hostname confiáveis, TLS interno não abre |
| :177–190 | NP-06 parcial | Fluxos abertos fecham e novos são recusados em menos de 60 s; não conta arquivo em andamento |
| :198/199/201 | NP-01/04 | Limite e timeout fecham sockets; capacidade é liberada para novo controle positivo |
| :207–210 | NP-04 | Stop fecha fluxo e listener; não representa lifecycle iOS |
| :213–217 | NP-08, ambiente | Bindings somente IPv4 loopback e ausência de listener IPv6 |
| :225 | NP-03, componente | Uma CA externa confiável não substitui a validação da CA interna; erro SSLCertVerificationError exato |

Cada teste reivindica uma obrigação do recorte; comparação de payload de mensagens/arquivos pertence a T5. A barreira de preparação registra somente status/tempo/erros locais e não autoriza nada no gateway. Todos os critérios completos NP e os 34 critérios do produto continuam sem conclusão. O próximo gate é a integração real com o núcleo do app, seguida dos processos das extensões.

## T3: início e retomada do núcleo no app

2026-10-16. Gate local passou. O app, framework e duas extensões compilaram para arm64 iOS Simulator com as bibliotecas qualificadas, sem conta Apple. Somente o processo SimpleX executou esta prova de startup; as extensões foram compiladas e sua execução continua pendente em T4.

Arquivos desta tarefa: SimpleXChat/Taverna/CoreTransport.swift, Shared/Model/SimpleXAPI.swift, Shared/SimpleXApp.swift, Shared/TavernaNativeProbe.swift, projeto Xcode, tools/taverna/native_access_tests/test_startup.py e artefatos de execução/handoff. A capability SOCKS fica em memória. Start e activate aplicam a configuração gerenciada antes do comando ao núcleo; ausente o listener, retornam notReady. As chamadas de configuração não entram em TerminalItems. Não há emissor de convites ou provisionamento de produção.

O gate usa o processo real SimpleX no UDID exclusivo, controlador temporário e banco novo com chave fictícia explícita. A instrumentação só existe em Debug/Simulator e exige configuração dentro da fixture do checkout compilado. Não modifica telas. Durante a prova, o lifecycle visual não abre o banco normal. As APIs reais de startup do app recebem o controlador temporário; isso prova seus hooks, sem reivindicar onboarding ou entrega de mensagens.

### Comandos e resultados

```sh
python3.12 tools/taverna/ios_proof.py build --attempt native-startup-build-c --guard-manifest .build/attempts/guard/guard-manifest.json --bindings .build/native-input-bindings.json --allow-dirty
TAVERNA_NATIVE_ALLOW_DIRTY=1 TAVERNA_NATIVE_BUILD=.build/attempts/native-startup-build-c/receipt.json python3.12 tools/taverna/native_access_tests/test_startup.py
```

Rodada de desenvolvimento `startup-33f2582d`: um teste de integração, 12 checkpoints exigidos, zero falhas/skips, 30,674 segundos. O receipt vincula produto, build, fontes e processo. O guard do mesmo PID registrou contenção IPv4/IPv6 antes de main e loopback funcional. O segredo não apareceu nos logs coletados nem em UserDefaults padrão/App Group. Os 70 testes Foundation e 29 asserts de codec continuam passando.

O build inicial `native-startup-build-a` falhou por referências de fontes no grupo errado do projeto Xcode; correção de paths em `native-startup-build-b`, que passou. `startup-9e8c89fd` passou os 11 checkpoints iniciais. Foi acrescentado o assert de não persistência, mantendo os anteriores; o build C e a rodada acima passaram os 12. Tentativas e raw logs permanecem ignorados. Gate de desenvolvimento não é reprodução final limpa.

Após o commit, a reprodução usa novo attempt/slug e omite --allow-dirty/TAVERNA_NATIVE_ALLOW_DIRTY. O driver exige o mesmo SHA do build, fonte limpa, hashes dos quatro produtos, sessão própria e contenção do mesmo PID. Não reutilizar esses receipts como prova de rede, APNs ou extensões.

### Adequação e cobertura reversa T3

| Critério | Asserção localizada | Resultado exigido |
| --- | --- | --- |
| NP-04/07, sem configuração | TavernaNativeProbe.swift:63–67, catches notReady e require(stopped()) | Start e activate não iniciam núcleo; estado real chatStopped |
| NP-07, precedência e configuração | TavernaNativeProbe.swift:85–89, actual == expected e flags never/prohibit/off | Núcleo recebeu SOCKS obrigatório antes do start |
| T3, capability só em memória | TavernaNativeProbe.swift:90–93, persisted.allSatisfy sem proxy; test_startup.py:86–87, assertNotRegex | Ausente nos defaults e logs coletados |
| NP-07, controle positivo | TavernaNativeProbe.swift:94–100, apiStartChat verdadeiro, chatRunning, activate cmdOk e chatStopped | APIs reais iniciam/reativam e param o controlador |
| NP-04/07, transporte encerrado | TavernaNativeProbe.swift:101–105, catches notReady | Nova tentativa de start/activate recusa configuração removida |
| NP-08, processo/isolamento | test_startup.py:78–84, status/checks/process exatos e PID correspondente ao guard | Doze checkpoints no SimpleX real, contenção antes de main |
| NP-08, origem | test_startup.py:31–43, SHA/limpeza/produtos/SDK e guard validados | Não aceitar app antigo ou fonte suja em modo final |

Cada teste mapeia ao startup de T3 ou à proveniência NP-08. Não há assert que substitua mensagens, arquivos, revogação em andamento ou lifecycle das extensões. Diretrizes: AGENTS.md, CONTRIBUTING.md e ios-build.md. Nenhuma asserção anterior foi removida, reduzida ou marcada skip. A exigência de leitura do núcleo, estados reais e valores de configuração evita aprovação por contagem de chamadas. Critérios NP completos continuam Pending até as demais tarefas e Verifier.

### Correção do gate e transposição para a base reconciliada

O [Verifier intermediário](native-startup-review.md) encontrou M6 sobrevivente: `actual == expected` comparava o resultado com outra chamada do produtor e os asserts independentes omitiam socksMode. A implementação observada usava always; o gate não detectava sua troca por onion. O veredicto anterior permanece FAIL e a lição L-003 foi registrada pelo script como candidate.

A correção afirma o campo Codable `socksMode` contra o literal `always`, independente de networkConfig. Acrescenta ainda apiTestProtoServer com os dois URIs exclusivos da fixture. Cada resposta precisa ser serverTestResult para o endereço exato e com testFailure nil. Isso executa o core real e os protocolos SMP/XFTP por SOCKS/mTLS, com fingerprint interno; não equivale à comparação de mensagens ou arquivos entre clientes de T5.

A transposição usa a base reconciliada c25dc4eb0d963afa916ac7605c5f2665e66318ba, com delta local e sem merge de ancestrais substituídos. Bibliotecas imutáveis foram copiadas e revalidadas; pins preservados. Caches, produtos, credenciais fictícias, fixture e simulador são novos e exclusivos do checkout. O guard UIKit de controle passou com IPv4/IPv6 negados e loopback permitido antes do build do app.

Gate de desenvolvimento corrigido: build `startup-hardened-build-a`, quatro produtos arm64 iOS Simulator, e rodada `startup-bf8a4fda`, 15 checkpoints em 56,227 segundos, zero falhas/skips. T1 passou novamente 29 asserts; T2, dez testes em fixture nova; Foundation atualizada, 76 testes. O novo receipt vincula fontes/produtos/build/PID. A revisão independente precisa repetir o sensor do modo SOCKS no commit corrigido.

| Obrigação | Asserção adicional | Resultado requerido |
| --- | --- | --- |
| NP-04/07, modo obrigatório | TavernaNativeProbe.swift:93, `encoded?["socksMode"] as? String == "always"` | Valor literal obrigatório, sem oráculo circular |
| NP-03 e T3, core e duas rotas reais | TavernaNativeProbe.swift:101–105, `serverTestResult(_, address, nil)` e `address == server` | Core iOS executou os testes SMP e XFTP nos dois endereços fictícios exatos |
| NP-08, cobertura exigida | test_startup.py:22–24 e assertEqual(value.get('checks'), CHECKS) | Os 15 checkpoints são obrigatórios; ausência/falha impede PASS |

Todos os asserts anteriores permanecem. A comparação de configuração completa segue como controle complementar, enquanto o valor crítico tem assert independente. O relatório histórico continua identificando o baseline que falhou, sem alegação de que o mutante antigo foi aprovado.

## T5: implementação em andamento

Premissas: um processo iOS com núcleo fixado e um cliente CLI oficial independente podem comprovar payloads do recorte; não equivalem a dois aparelhos nem às extensões. Estado e credenciais fictícios novos por rodada. O controle de fluxo da fixture permite observar um arquivo incompleto antes de mudar a autorização.

Arquivos: tools/taverna/native_access_tests/test_payload.py e payload_session.py; tools/taverna/access_proof/{client,fixture,gateway}.py; apps/ios/Shared/TavernaNativeProbe.swift; testes Foundation necessários à integridade do driver; artefatos native-* e handoff. Nenhuma biblioteca ou protocolo de produto será alterado.

Sucesso: mensagens exatas nos dois sentidos, arquivos com bytes exatos nos dois sentidos, controle positivo da sentinela seguido de zero acessos indevidos, bloqueio de novas conexões e encerramento dos fluxos em até 60 segundos após revogação ou ausência de política, incluindo arquivo comprovadamente em andamento. Build e regressões preservados; execução incompleta mantém T5 aberta.

### T5: resultado parcial em desenvolvimento

**T5 aberta.** O gate integral ainda não passou. As rodadas abaixo usam fonte modificada, build payload-dev-d e commit-base 9d7c61402; não substituem reprodução limpa, sensor, CI ou Verifier no commit final.

| Prova | Resultado / evidência local ignorada |
| --- | --- |
| Mensagens SMP nos dois sentidos | PASS local; run-payload-42858ecc/ios/payload-receipt.json, texto aleatório recebido exatamente igual. |
| Revogação com upload incompleto | PASS local; run-payload-67ac592a, progresso 4194304 de 34603008 bytes de transferência, fluxos fechados em 0,2982 s; novas tentativas reais SMP/XFTP negadas. |
| Política ausente com upload incompleto | PASS local; run-payload-345910fa, mesmo tamanho de progresso observado, corte em 0,1516 s; novas tentativas reais SMP/XFTP negadas. |
| Sentinela alcançável | PASS local; run-payload-b428c52b, controle positivo e nenhuma conexão adicional do app após destino proibido. |
| Integridade XFTP nos dois sentidos | PENDING. O primeiro upload real terminou, mas test_payload.py:51 exige indevidamente um único URI; o núcleo retornou quatro. O plano não fixa essa quantidade. A correção do teste aguarda confirmação conforme a regra TLC; nenhuma asserção foi alterada ou removida. O download e a comparação dos bytes ainda não contam como executados. |

As quatro provas selecionadas passaram em uma execução de 116,504 s. O quinto caso continua conhecido como não aprovado; não houve uso de skip/disable para obter um gate integral verde. Os receipts dizem CHECK_PASS e development, com hashes de fontes/build/produto, processo/PID e guard antes do main. O driver confere que fontes, HEAD, estado Git e produtos permanecem iguais durante a prova. Fixtures e produtos pertencem ao checkout; arquivos e logs permanecem preservados em .build.

**Regressões:** 29 asserts do codec, dez testes Network.framework (28,445 s), 76 Foundation, checker, compileall, startup com 15 checkpoints (23,810 s) e doze testes CLI anteriores passaram. As primeiras duas rodadas CLI falharam em envio imediatamente após sentConfirmation; os diagnósticos não reproduziram o erro. A fixture passou a aguardar connStatus ready dos dois contatos, com limite de 15 s e falha se não houver confirmação. A rodada completa seguinte passou em 12,755 s. As asserções existentes de test_boundary.py permanecem intactas; o erro original sem payload capturado não recebe causa conclusiva.

A ordem de configuração foi corrigida após a resposta real chatNotStarted: o transporte continua obrigatório antes do start; servidores exclusivos são configurados e lidos de volta depois do start, antes de convite/contato ou arquivo. O caminho de mailbox e eventos é exclusivo de DEBUG Simulator. Nenhuma nova interface de produto foi criada.

### Adequação parcial T5

| Critério | Asserção localizada | Outcome da spec | Estado |
| --- | --- | --- | --- |
| NP-05, mensagem SMP | test_payload.py:36, assertIn(expected, s.contents(receiver(...))) em dois sentidos | Texto recebido igual ao enviado | Coberto localmente |
| NP-05, arquivo | test_payload.py:58, assertEqual(received.read_bytes(), payload) | Bytes recebidos iguais aos enviados | Ainda não alcançada |
| NP-06, arquivo em andamento | test_payload.py:79/80, assertGreater(sentSize, 0) e assertLess(sentSize, totalSize) | Transferência incompleta antes da alteração | Coberto localmente |
| NP-06, corte e novas tentativas | test_payload.py:85/87/91/92, closed_by_authorization, elapsed <= 60, failed is True e ausência de conclusão | Fechar fluxos e negar novas conexões, sem concluir o arquivo | Coberto localmente; open XFTP no app, open SMP preserva sua prova de componente T2 |
| NP-02/04, sentinela | test_payload.py:104/106/108, count == 1, failed is True, count == 1 | Alcançável no controle e sem saída direta na negativa | Coberto localmente |

Mapeamento inverso: handshake/contato e tipo de resposta em test_payload.py:22/24/30 sustentam o controle positivo NP-05; arquivo:48/51/54/57/58 sustenta NP-05, mas a cardinalidade em :51 não tem requisito e aguarda correção autorizada; :75/79/80/82/85/87/91/92/94 sustenta NP-06; :104/106/108 sustenta NP-02/04. A revisão de adequação permanece incompleta por NP-05/arquivo. T4 e T6 continuam abertos, e todos os requisitos NP/produto continuam Pending.

### T5: retomada autorizada em 17/out/2026

O proprietário autorizou corrigir a asserção de cardinalidade do teste. test_payload.py passa a exigir uma lista não vazia de links simplex:/file com descrição presente. A recepção real pelo outro núcleo e a comparação integral dos bytes permanecem obrigatórias nos dois sentidos. Nenhum caso foi removido ou desabilitado. Demais arquivos e critérios de T5 permanecem conforme o escopo já registrado; o gate Full e a revisão independente continuam exigidos.

### T5: gate Full local aprovado

**PASS no recorte de desenvolvimento T5.** Os cinco casos passaram juntos em 150,949 s, sem falhas ou skips, após a correção da asserção autorizada. Comando: `TAVERNA_NATIVE_BUILD=.build/attempts/payload-dev-d/receipt.json TAVERNA_NATIVE_ALLOW_DIRTY=1 python3.12 tools/taverna/native_access_tests/test_payload.py`. O conjunto exige estado novo em cada caso. A reprodução limpa e o Verifier no commit atômico continuam pendentes antes de publicar ou integrar; T4 e T6 permanecem abertos.

| Caso | Receipt local em .build/access-qualification | Resultado |
| --- | --- | --- |
| Mensagens bilaterais | run-payload-c0979f87/ios/payload-receipt.json | Texto aleatório recebido exatamente igual nos dois sentidos. |
| Arquivos bilaterais | run-payload-d66829e8/ios/payload-receipt.json | 2097289 bytes comparados integralmente por sentido, arquivos aleatórios distintos e diretórios de clientes distintos. |
| Revogação em upload | run-payload-2234d308/ios/payload-receipt.json | Progresso 4194304 de 34603008; fechamento em 0,2853 s; novas conexões SMP/XFTP negadas. |
| Autorização ausente em upload | run-payload-0c4d02bf/ios/payload-receipt.json | Progresso incompleto; fechamento em 0,1619 s; novas conexões SMP/XFTP negadas. |
| Sentinela | run-payload-4f4c2c59/ios/payload-receipt.json | Uma conexão de controle e nenhuma conexão adicional do app ao destino proibido. |

Quick e regressões mantidos: 29 asserts codec, 76 Foundation, dez testes de transporte, doze CLI, 15 checkpoints de startup; checker, compileall, spec/tasks validators e whitespace aprovados. Nenhuma asserção de regressão foi alterada. A única correção de teste foi a cardinalidade de links, aprovada pelo proprietário em 17/out/2026. As tentativas anteriores continuam registradas acima como históricas.

#### Adequação pós-gate T5

| Critério | Asserção exata | Outcome e cobertura |
| --- | --- | --- |
| NP-05, texto bilateral | test_payload.py:35 `assertIn(expected, s.contents(receiver('/tail @'+source+' 20')))` | Conteúdo recebido tem texto aleatório idêntico ao do outro cliente; os dois sentidos executados. |
| NP-05, arquivo bilateral | test_payload.py:63 `assertEqual(received.read_bytes(), payload)` | Igualdade de todos os bytes do arquivo enviado; os dois sentidos executados. |
| NP-05, link utilizável | test_payload.py:51/52/55/56 `assertIsInstance(links, list)`, `assertGreater(len(links), 0)`, `assertEqual((parsed.scheme, parsed.path), ('simplex', '/file'))`, descrição presente | Lista não vazia com formato de link válido; recepção e bytes exatos comprovam uso pelo outro núcleo. Sem cardinalidade arbitrária. |
| NP-06, arquivo em andamento | test_payload.py:84/85/87 `assertGreater(progress['sentSize'], 0)`, `assertLess(progress['sentSize'], progress['totalSize'])`, fluxo XFTP ativo | Transferência incompleta antes da alteração da autorização. |
| NP-06, corte temporal | test_payload.py:90/92 `s.wait(lambda: s.closed_by_authorization(active), 60, ...)`, `assertLessEqual(elapsed, 60)` | A fixture registra autorização encerrada e ambos os streams fechados; limite observado menor que 60 s. |
| NP-06, negar novas conexões e não concluir | test_payload.py:96/97/99 `assertIs(tested['failed'], True)`, `assertFalse(any(...sndStandaloneFileComplete...))`, denied_before_backend presente | Novos testes reais SMP/XFTP falham; arquivo interrompido não conclui. Prova de SMP aberto permanece na integração do componente T2; upload aberto pertence ao app. |
| NP-02/04, saída proibida | test_payload.py:109/111/113 `assertEqual(sentinel.count, 1)`, `assertIs(tested['failed'], True)`, `assertEqual(sentinel.count, 1, ...)` | Controle positivo alcança sentinela; tentativa proibida pelo core não a alcança. |
| NP-08, origem/isolamento | payload_session.py:76/78/79/130/235 e validação de produtos | Commit, fonte limpa exigida no modo final, PID no guard antes do main, produtos e fontes sem alteração durante o caso. Rodadas atuais explicitamente development. |

Mapeamento inverso: `test_01` e asserts de conexão/recepção sustentam NP-05/SMP; `test_02` e tipo de resposta, links, arquivo existente e igualdade de bytes sustentam NP-05/XFTP; `test_03/test_04` e todas as asserções de progresso, fluxo, tempo, negação e conclusão sustentam NP-06; `test_05` sustenta NP-02/04; os asserts comuns de bootstrap/proveniência sustentam NP-07 no app e NP-08. Não há testes fora do recorte. Diretrizes seguidas: AGENTS.md, CONTRIBUTING.md e native-tasks.md; fixtures seguem o padrão existente test_boundary.py e test_transport.py. Adequação local A–D aprovada, sem mocks, comparações tautológicas ou inferência de integridade a partir de handshake.


### T5: reprodução limpa e revisão independente

**PASS delimitado para T5 no commit `b48476b240a902ca46a6c4883cc6f07aa415bdef`.** Os resultados de desenvolvimento acima permanecem históricos. A reprodução limpa compilou os quatro produtos arm64 iOS Simulator (`payload-clean-a`, exit 0, `source_state` vazio) e executou os cinco casos em 148,673 s, sem falhas ou skips. Receipts novos em `run-payload-17b79f02`, `run-payload-85bf28c8`, `run-payload-d5e17e0e`, `run-payload-da425d78` e `run-payload-c738b60c`, sob `.build/access-qualification`, vinculam o mesmo commit, fonte, app, build, processo e guard. Mensagens e arquivos foram conferidos nos dois sentidos; cada arquivo teve 2.097.289 bytes. Revogação e política ausente fecharam o upload em 0,1741 s e 0,1685 s, respectivamente. O progresso anterior era estritamente parcial.

O [Verifier independente](native-payload-review.md) inspecionou esses receipts e repetiu o gate clean: **5 testes, 0 falhas/skips, 147,314 s**. Repetiu ainda os 15 checkpoints de startup (23,638 s), dez testes Network.framework (28,271 s), doze CLI (12,686 s), 29 asserts codec e 76 Foundation. Checker, compileall, whitespace e gates TLC estruturais passaram. O relatório registra asserções por obrigação, comandos, origem e limites.

O sensor detectou seis falhas injetadas em scratch: texto alterado, byte alterado, URI inválido, revogação ignorada, política ausente autorizada e conexão extra à sentinela. Nos dois casos de política, o scratch reduziu somente a espera do mesmo predicado a 5 s; o teste versionado preserva 60 s. O mutante da sentinela prova seu observador, sem recompilar fallback no Swift. Nenhum bootstrap inválido contou como mutante detectado. O checkout, HEAD e produtos permaneceram intactos; somente o relatório foi criado ao fim.

Este registro documental sucede o commit comprovado; não afirma novo build iOS para o commit de documentação. T4 exige lifecycle efetivo de Share Extension/NSE e continua aberta; T6 depende dela. Os oito NP e os 34 requisitos do produto permanecem Pending no agregado. O recorte pode ser publicado como PR em rascunho, sem integração da feature. Não há prova de aparelho, APNs, admissão, convite, distribuição ou operação live.


### T5: revalidação da cadeia de publicação

A branch `codex/15-native-access-qualified` preserva os fontes e testes byte a byte após reconciliação documental. A implementação T5 corresponde a `7d248badce6c4882c8ac879619d65bb782059141`; os SHAs anteriores nos relatórios permanecem a proveniência local histórica de suas rodadas. Não representam novos builds. As árvores `apps/ios` e `tools/taverna` e os quatro produtos são idênticos, conforme a [revalidação independente](native-publication-revalidation.md).

No HEAD limpo `8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c`, o build `payload-public-clean-a` passou com quatro produtos e fonte limpa. O autor repetiu os cinco casos em 149,742 s; o Verifier, em 147,802 s, e repetiu o startup padrão com 15 checkpoints em 23,421 s. Zero falhas/skips. Rodadas próprias e receipts novos preservam origem e isolamento. No autor, os cortes ocorreram em 0,1606 s e 0,1491 s; no Verifier, em 0,3059 s e 0,1685 s, dentro do limite de 60 s.

O sensor 6/6 anterior é histórico, não foi reexecutado. O Verifier confirmou sua aplicabilidade por equivalência byte a byte e pela nova execução clean. Este fechamento acrescenta somente documentação, sem alterar código ou alegar novo build para seu commit. T4/T6 continuam NOT RUN; oito NP e 34 requisitos do produto continuam Pending. Revisão do pacote exato e CI ainda precedem a publicação do PR em rascunho; integração da feature continua impedida pelos gates ausentes.


## T4: recorte Share em desenvolvimento — 2026-10-17

A ordem de startup foi corrigida na ShareAPI e no ShareModel. O modelo valida disponibilidade antes de abrir/criar controlador; start aplica a configuração gerenciada antes do comando do núcleo; activate valida antes de reabrir o store e reaplica antes de reativar. Nenhuma credencial é persistida por esse caminho. O carregamento de credencial de admissão continua fora desta entrega: sem transporte configurado, o processo falha fechado.

A prova aciona a extensão instalada pela folha UIKit do sistema, no processo SimpleX SE. O modo DEBUG Simulator cria banco/CA/identidade fictícios no worktree e não é compilado em device/release. O driver exige hashes dos quatro produtos e proveniência; não aceita a construção do controlador no processo do app como prova da extensão.

**Desenvolvimento PASS**, sem alegar commit limpo: build share-socket-d, rodada run-share-cb087563, vinte checkpoints; XCTest 1 aprovado, zero falhas/skips. SMP e XFTP reais passaram no processo da extensão. Uma sentinela loopback alcançável no controle positivo não recebeu conexão das duas tentativas proibidas. Suspensão com configuração anterior insegura, retomada pelo modelo e indisponibilidade após stop foram verificadas. Recibo local em .build/access-qualification/run-share-cb087563/ios/share-driver-receipt.json.

A [qualificação da contenção](share-containment.md) preserva tentativas falhas e limitações: o trampoline do sandbox do kernel invalidou o serviço UIKit. A alternativa da fixture é explicitamente test_socket_interposition, com quatro chamadas instrumentadas e controle anterior ao main; não é isolamento pelo kernel ou de toda a sessão, nem autorização para dados reais. O app principal mantém seu guard do kernel. A revisão independente precisa avaliar esse limite antes de aprovar o recorte.

Regressões atuais: 76 Foundation, 29 asserts codec, dez testes de transporte, quinze checkpoints de startup do app e cinco casos de mensagens/arquivos/revogação/sentinela passaram. Nenhuma asserção existente foi removida ou reduzida. Compilação C com DEBUG=0 produziu objeto sem símbolos globais; isso só verifica exclusão dessa instrumentação, não qualifica um build em aparelho. Checker, compileall e whitespace passam.

Próximo gate: commit atômico, build novo limpo, repetição Share e regressões aplicáveis e Verifier independente com sensor de autorização. T4 permanece aberta por NSE; T6, NP-01..08 e os 34 critérios de produto não são concluídos por este recorte. A proposta visual fica em PR separado e aguarda aprovação do proprietário.
