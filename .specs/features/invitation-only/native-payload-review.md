# Revisão independente: transporte nativo T5

**Data:** 2026-10-17

**Baseline verificado:** `9d7c614021d992ccd35716c2d6d43a77892117db..b48476b240a902ca46a6c4883cc6f07aa415bdef`

**Método:** TLC Spec Driven, Verifier independente do autor

**Escopo:** somente T5 de `native-tasks.md`, transporte de mensagens, arquivos, revogação, política ausente e sentinela no processo SimpleX com um peer CLI oficial

## Verdict

**PASS no recorte T5.** A execução clean independente repetiu os cinco casos no SHA exato. Mensagens foram comparadas pelo conteúdo recebido nos dois sentidos. Arquivos distintos de 2.097.289 bytes foram comparados integralmente nos dois sentidos. Revogação e política ausente interromperam um upload em andamento, fecharam os fluxos observados e negaram novas conexões SMP/XFTP abaixo do limite de 60 segundos. A sentinela recebeu somente sua conexão de controle.

**A feature `invitation-only` permanece PARTIAL e NOT READY.** T4 e T6 continuam abertas. Todos os oito NP e os 34 requisitos do produto permanecem `Pending` no agregado. Este relatório não substitui `validation.md`, não executa `validate_state.py` e não declara app, extensões, admissão, aparelho, produção ou distribuição prontos.

## Task verdict

| Tarefa | Resultado | Evidência decisiva |
| --- | --- | --- |
| T5, mensagens SMP | PASS no recorte | `tools/taverna/native_access_tests/test_payload.py:19`–`:35` cria contato, envia texto aleatório nos dois sentidos e exige o objeto recebido com o mesmo texto. |
| T5, arquivos XFTP | PASS no recorte | `test_payload.py:38`–`:65` exige lista não vazia de links, esquema `simplex`, caminho `/file`, descrição presente, download pelo outro núcleo e igualdade de todos os bytes. |
| T5, revogação | PASS no recorte | `test_payload.py:74`–`:101` exige progresso estritamente parcial, fluxo XFTP ativo, fechamento por autorização, tempo menor ou igual a 60 s, novas tentativas SMP/XFTP falhas e ausência de conclusão do arquivo. |
| T5, política ausente | PASS no recorte | O mesmo predicado de `test_payload.py:74`–`:101` executa após remoção da política e exige falha fechada. |
| T5, sentinela | PASS no recorte | `test_payload.py:103`–`:113` prova alcance positivo, falha do teste pelo core e contagem final ainda igual a um. |
| T4, Share Extension/NSE | NOT RUN | `native-tasks.md:78`–`:87` continua aberta. Compilação dos targets não prova execução dos processos. |
| T6, relatório agregado | NOT RUN | `native-tasks.md:100`–`:109` depende de T4 e T5. Este documento é a revisão intermediária delimitada de T5. |

## Spec-anchored outcomes

| Obrigação | Resultado do recorte | Evidência de valor/estado |
| --- | --- | --- |
| NP-05, mensagem recebida igual à enviada | PASS | `test_payload.py:27`–`:35` constrói `expected` com o texto aleatório e exige sua presença no `/tail` do destinatário. O laço executa app→CLI e CLI→app. |
| NP-05, bytes XFTP recebidos iguais aos enviados | PASS | `test_payload.py:41`–`:63` cria bytes aleatórios distintos por sentido, transfere pelo link retornado e compara `received.read_bytes()` com o payload original. Os receipts clean registram 2.097.289 bytes por sentido. |
| T5, link de arquivo utilizável | PASS | `test_payload.py:50`–`:59` exige lista não vazia, todos os links com `simplex:/file` e `desc` não vazio, usa o primeiro link no outro núcleo e exige `rcvStandaloneFileCreated`. Não há cardinalidade arbitrária. |
| NP-06, arquivo em andamento | PASS | `test_payload.py:82`–`:87` exige `0 < sentSize < totalSize` e ao menos um fluxo XFTP autorizado ativo antes da alteração. A repetição independente observou 4.194.304 de 34.603.008 bytes. |
| NP-06, fechar fluxos abertos em até 60 s | PASS | `payload_session.py:191`–`:206` deriva conexões ativas dos eventos do gateway e exige `authorization_ended` mais `streams_closed` para todas. `test_payload.py:88`–`:92` mede o corte. A repetição independente observou 0,3242 s para revogação e 0,1511 s para política ausente. |
| NP-06, bloquear novas conexões | PASS | `test_payload.py:93`–`:99` executa testes reais do core para SMP e XFTP, exige `failed is True` em ambos e evento `denied_before_backend`. Os logs clean contêm negação para os dois protocolos. |
| NP-02/04, sem fallback direto à sentinela | PASS no negativo de T5 | `TavernaNativeProbe.swift:189`–`:198` pede ao core um servidor fora da rota permitida. `test_payload.py:105`–`:113` exige controle positivo e nenhuma segunda conexão. As coberturas completas de NP-02/04 permanecem dependentes dos demais recortes. |
| NP-08, origem e isolamento desta prova | PASS para o receipt T5; PARTIAL no agregado | `payload_session.py:72`–`:92` exige commit, fonte limpa, quatro produtos, sessão e guard válidos. `:232`–`:246` revalida produtos, hashes das fontes, HEAD e porcelain antes de emitir receipt. O build clean e todos os receipts apontam para `b48476b240a902ca46a6c4883cc6f07aa415bdef`, processo `SimpleX` e o mesmo digest de app. T6 permanece aberta. |

Os statuses canônicos continuam corretos em `native-proof.md:53`–`:62`. Este recorte adiciona evidência para NP-05/06 sem promovê-los isoladamente a requisito agregado concluído.

## Gate evidence

| Gate | Resultado |
| --- | --- |
| Build iOS clean | Quatro produtos arm64 iOS Simulator presentes e com hashes iguais ao receipt `.build/attempts/payload-clean-a/receipt.json`; `source_state` vazio e commit b48476b. |
| Payload clean do autor, inspecionado | 5 testes, 0 falhas, 0 skips, 148,673 s; cinco receipts `CHECK_PASS`, `qualification_mode=clean`, fonte/app/build concordantes. |
| Payload clean do Verifier | `TAVERNA_NATIVE_BUILD=.build/attempts/payload-clean-a/receipt.json python3.12 tools/taverna/native_access_tests/test_payload.py`: 5 testes, 0 falhas, 0 skips, 147,314 s, estado e credenciais novos por caso. |
| Startup padrão clean | Mesmo build b484; 1 teste, 15 checkpoints exatos, 0 falhas, 0 skips, 23,638 s. Preserva o ramo sem `mode=payload`. |
| Network.framework/macOS | 10 testes, 0 falhas, 0 skips, 28,271 s, fixture nova. |
| Fixture CLI oficial | Sequência documentada `init` → `start` → `clients` → `test_boundary.py` → `stop`: 12 testes, 0 falhas, 0 skips, 12,686 s. Uma chamada preliminar sem preparar a fixture foi classificada como bootstrap inválido e não contou como teste. |
| Swift codec | 29 asserts, 0 falhas. |
| Foundation | 76 testes, 0 falhas, 0 skips, 1,144 s. |
| Foundation checker | PASS, limitado à fundação. |
| Python compileall e whitespace | PASS. |
| TLC estrutural | `validate_spec.py`: 0 erros/0 avisos. `validate_tasks.py`: 0 erros e o aviso esperado de T6 sem testes. `check_commit.py`: PASS. |

O processo executado foi o app `SimpleX`; o segundo cliente foi o binário CLI oficial fixado. O guard do mesmo PID registrou negação IPv4/IPv6 antes de `main` e loopback disponível. Somente as portas efêmeras do gateway foram publicadas em `127.0.0.1`; os relays ficaram nas redes Docker internas. O núcleo e os relays permaneceram nos pins documentados em `entry-design.md:54` e `:138`–`:141`.

## Discrimination sensor

O recorte trata autenticação, fail-closed e integridade de payload. O sensor manual crítico usou seis mutações em cópias sob `Projects`, montadas somente nas fixtures novas. O checkout, o build e os quatro produtos do autor não foram alterados. Cada mutante executou o processo SimpleX no simulador exclusivo com o mesmo build clean.

| Mutação | Resultado | Assert discriminante |
| --- | --- | --- |
| M1: o peer acrescenta bytes ao texto antes do envio | KILLED | `test_payload.py:31`–`:35`, conteúdo exato não apareceu no destinatário. |
| M2: o peer inverte o primeiro byte do arquivo antes do upload | KILLED | `test_payload.py:63`, igualdade integral dos bytes falhou. |
| M3: o evento do peer troca o URI de arquivo por `https:/file` | KILLED | `test_payload.py:53`–`:56`, esquema esperado `simplex` falhou. |
| M4: qualquer política não vazia autoriza o certificado, mesmo após revogação | KILLED | `test_payload.py:90`, fluxos existentes não fecharam pelo predicado de autorização. |
| M5: política ausente retorna autorização positiva | KILLED | `test_payload.py:90`, fluxos existentes não fecharam pelo predicado de autorização. |
| M6: o driver injeta uma segunda conexão direta à sentinela | KILLED | `test_payload.py:113`, contagem foi 2 em vez de 1. Este mutante prova discriminação do observador; não é uma mutação compilada do app. |

Nos mutantes M4/M5, o wrapper scratch reduziu somente a espera do mesmo predicado de 60 para 5 segundos. A árvore e o teste versionado mantiveram o limite da spec. Nenhum mutante morreu por sintaxe, dependência ausente ou bootstrap.

**Sensor:** 6/6 killed, 0 survived. Resultado: PASS.

## Code quality and isolation

- O diff T5 adiciona o probe DEBUG/Simulator, driver e adaptações da fixture necessárias aos cinco casos. Não altera criptografia SimpleX, protocolo, locks, dependências ou caminhos de produção.
- O mailbox de qualificação é compilado somente em DEBUG Simulator e restringe comandos, caminhos de arquivo e duração em `TavernaNativeProbe.swift:168`–`:241`.
- Os testes afirmam valores da spec: texto exato, bytes exatos, formato do URI, progresso parcial, estado de fechamento, tempo, resultado SMP/XFTP e contagem da sentinela. Não usam eco, contagem de chamadas ou handshake como substituto de payload.
- `test_transport.py`, `test_startup.py` e `test_boundary.py` não foram enfraquecidos pelo diff T5. A mudança de cardinalidade do URI pertence ao teste novo, foi autorizada pelo proprietário em 2026-10-17 e preserva links válidos mais comparação integral dos bytes.
- O porcelain de fonte do autor estava vazio antes dos sensores e voltou ao mesmo baseline vazio após todos os gates. Depois disso, somente este relatório ficou untracked. HEAD e hashes dos seis fontes T5 permaneceram iguais. Nenhum container da fixture ficou ativo.
- A revisão não fez push, merge, deploy, publicação, alteração de provider/DNS ou uso de credencial real.

## Gaps and limits

1. **T4 permanece NOT RUN:** Share Extension e NSE não foram executadas como processos efetivos. Build dos targets não satisfaz NP-07.
2. **T6 permanece NOT RUN:** falta o relatório agregado depois de T4 e T5, CI e Verifier no último commit que integrar a feature.
3. **NP e produto permanecem Pending:** a prova usa um processo iOS Simulator e um peer CLI, não dois aparelhos. Não cobre APNs, assinatura de aparelho, distribuição, admissão, convites ou operação live.
4. **Sensor M6 é limitado ao observador:** ele prova que a contagem detecta uma conexão direta extra. Não recompila uma variante Swift com fallback direto.
5. **Artefatos são locais:** fixtures, credenciais fictícias, logs e receipts permanecem ignorados em `.build`; o relatório publica somente resultados sanitizados e caminhos relativos.

## Conclusion

**PASS delimitado para T5 no SHA `b48476b240a902ca46a6c4883cc6f07aa415bdef`.** O gate clean independente passou 5/5 e o sensor matou 6/6 mutantes. Não há gap de T5 identificado nesta revisão. A feature continua PARTIAL por T4 e T6, com todos os NP e 34 requisitos do produto ainda `Pending` no agregado.
