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
