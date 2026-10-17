# Execução: transporte nativo

Estado atual: T1/T2 passaram como componentes. O gate nominal de T3 teve um mutante sobrevivente; a correção passou 15 checkpoints, incluindo os dois protocolos pelo core iOS real, na base reconciliada. Reprodução limpa e nova revisão independente precedem publicação. As seções abaixo preservam as tentativas anteriores. T4–T6 e todos os critérios completos permanecem pendentes.

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
