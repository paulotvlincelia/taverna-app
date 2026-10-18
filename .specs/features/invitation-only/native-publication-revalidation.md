# Revalidação independente de proveniência para publicação

**Data:** 2026-10-17

**HEAD verificado:** `8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c`

**Último commit de implementação T5:** `7d248badce6c4882c8ac879619d65bb782059141`

**Baseline T5 anteriormente verificado:** `b48476b240a902ca46a6c4883cc6f07aa415bdef`

**Método:** TLC Spec Driven, Verifier independente do autor

**Escopo:** revalidar proveniência e execução clean de T5 depois da transposição/sanitização documental. A revisão de conteúdo público e digest pertence a outro Verifier.

## Verdict

**PASS para a proveniência e os gates clean de T5 no HEAD `8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c`.** Os fontes e testes executáveis são byte idênticos ao baseline T5 aprovado. Os quatro produtos do build novo têm as mesmas hashes do build anterior. O autor e este Verifier repetiram os cinco casos payload em fonte limpa no novo SHA. O Verifier repetiu também os 15 checkpoints do startup padrão.

**A feature `invitation-only` permanece PARTIAL e NOT READY.** T4 e T6 continuam abertas. Todos os oito NP e os 34 requisitos do produto permanecem `Pending` no agregado. Este relatório não aprova conteúdo de publicação, não substitui `validation.md` e não autoriza merge, deploy ou integração da feature.

## Equivalência de fontes

`git rev-parse` confirmou os mesmos tree IDs em `b48476b`, `7d248bad` e no HEAD:

| Árvore | Tree ID comum |
| --- | --- |
| `apps/ios` | `51363acc9741afd794abe28b5c6d91bb7c7bc52e` |
| `tools/taverna` | `31a75a0a016657cac1766940bd07e58240fa7982` |

Os seis blobs diretamente usados por T5 também são idênticos entre `b48476b` e o HEAD:

| Fonte | Blob ID comum |
| --- | --- |
| `apps/ios/Shared/TavernaNativeProbe.swift` | `ebd982976bd4ecf29ea46a699f803c6796d714f9` |
| `tools/taverna/native_access_tests/payload_session.py` | `8c1f9a5afafe7d85d34cafeaf048e29a1f4f80d5` |
| `tools/taverna/native_access_tests/test_payload.py` | `29eee2437546c21e0a6ca06cf235648dd893965e` |
| `tools/taverna/access_proof/client.py` | `5ab87d48321f5e9e439bea25570357e9a7f3c6a0` |
| `tools/taverna/access_proof/fixture.py` | `8b6363a8ca8a253db6172612aabf3e38ea636072` |
| `tools/taverna/access_proof/gateway.py` | `e66abd2a131884769368a027a1b6aa9fae5c0a94` |

O diff `7d248bad..8d3d9a7` toca somente documentação sob `.specs`. Não há diff em `apps/ios` ou `tools/taverna`.

## Equivalência do build

O receipt `.build/attempts/payload-public-clean-a/receipt.json` registra commit `8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c`, `source_state` vazio e quatro produtos arm64 iOS Simulator. As hashes do receipt novo são iguais às do build `payload-clean-a` usado na revisão T5 anterior e aos arquivos atualmente presentes:

| Produto | SHA-256 comum |
| --- | --- |
| `SimpleX.app` | `30b5f5e6715108a0d5f81eac24ef6380e2a279a582ff8fa8c8cf72021d51fe2c` |
| `SimpleXChat.framework` | `80ea034e6857b3ef1837c9b8fffce6451d89682629c55586f936d090c24a9289` |
| `SimpleX NSE.appex` | `f62109198f8fd47c0d0194de508dad195de58e88cfa75c6bda93d53a80daede8` |
| `SimpleX SE.appex` | `a3979d9aa7f0d8960e8aa7439c7b2aa104462163080e6fc95e0a070b0289b81e` |

Isso demonstra que a mudança de SHA veio da documentação. Não demonstra execução das extensões; T4 permanece `NOT RUN`.

## Gate evidence no novo SHA

| Gate | Resultado |
| --- | --- |
| Build clean do autor | Quatro produtos, exit 0, `source_state` vazio, receipt vinculado ao HEAD `8d3d9a7`. |
| Payload clean do autor | 5 testes, 0 falhas, 0 skips, 149,742 s. Cinco receipts `CHECK_PASS`, `qualification_mode=clean`, commit/build/app/fontes concordantes. |
| Payload clean do Verifier | `TAVERNA_NATIVE_BUILD=.build/attempts/payload-public-clean-a/receipt.json python3.12 tools/taverna/native_access_tests/test_payload.py`: 5 testes, 0 falhas, 0 skips, 147,802 s. |
| Startup clean do Verifier | Mesmo build: 1 teste, 15 checkpoints exatos, 0 falhas, 0 skips, 23,421 s. Processo `SimpleX`, commit e `source_state` conferidos pelo receipt. |
| TLC estrutural | `validate_spec.py`: 0 erros/0 avisos. `validate_tasks.py`: 0 erros e o aviso esperado de T6 sem testes. |
| Foundation checker | PASS, explicitamente limitado à fundação. |
| Python compileall e whitespace | PASS. |

Na repetição do Verifier, os dois arquivos XFTP tinham 2.097.289 bytes por sentido. Revogação observou 4.194.304 de 34.603.008 bytes antes do corte e fechou em 0,3059 s. Política ausente observou o mesmo progresso parcial e fechou em 0,1685 s. Novas tentativas SMP/XFTP foram negadas nos dois casos. A sentinela manteve somente a conexão de controle.

## Sensor histórico e adequação

**O sensor não foi repetido nesta revalidação.** A revisão anterior em `native-payload-review.md` executou seis mutações em scratch e obteve **6/6 killed, 0 survived**: alteração de mensagem, alteração de byte, URI inválido, revogação fail-open, política ausente fail-open e conexão extra à sentinela.

Esse resultado histórico permanece adequado para o novo HEAD porque:

1. `apps/ios` e `tools/taverna` têm os mesmos tree IDs no baseline verificado, no commit de implementação transposto e no HEAD.
2. Os seis blobs que formam o probe, o driver, os testes e a fixture T5 são idênticos.
3. Os quatro produtos do build novo têm as mesmas hashes dos produtos usados pelo sensor anterior.
4. Os cinco casos clean e o startup padrão passaram novamente no novo SHA.

O resultado **6/6** é evidência histórica transferida por equivalência byte a byte. Ele não é apresentado como nova execução de mutantes no commit `8d3d9a7`. Uma nova rodada não acrescentaria discriminação sobre o código inalterado e criaria apenas novos artefatos operacionais.

## Isolation and limits

- O checkout estava limpo antes dos gates e voltou ao mesmo baseline depois deles. HEAD, fontes e produtos permaneceram inalterados durante as execuções.
- Cada caso payload criou estado e credenciais fictícias novos. Fixtures e receipts permanecem ignorados em `.build`.
- Nenhum container da fixture permaneceu ativo depois do teardown.
- O processo efetivamente exercitado foi `SimpleX` com um peer CLI oficial. Isso não equivale a dois aparelhos nem à execução de Share Extension/NSE.
- T4 permanece `NOT RUN`; build dos targets não prova lifecycle das extensões.
- T6 permanece `NOT RUN` e depende de T4. NP-01..08 e os 34 requisitos do produto continuam `Pending` no agregado.
- Não há prova nova de aparelho, APNs, assinatura, admissão, convite, distribuição, provider, DNS ou operação live.
- A classificação do conteúdo público e o digest do pacote de publicação não fazem parte desta revalidação.

## Conclusion

**PASS delimitado de proveniência para T5 no SHA `8d3d9a7ba3ad4225801e2d0565b2d0f74404e81c`.** Fontes, testes e produtos são equivalentes ao baseline aprovado; clean5 e startup passaram novamente no novo SHA. O sensor 6/6 permanece histórico e aplicável por equivalência, sem alegação de reexecução. A feature continua PARTIAL por T4 e T6, com todos os NP e 34 requisitos do produto ainda `Pending` no agregado.
