# Execução: transporte nativo

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
