# Revalidação independente: transporte nativo T1–T3

**Data:** 2026-10-16

**Baseline:** `c25dc4eb0d963afa916ac7605c5f2665e66318ba..53b31fdfe8398d858395dc4b366f814c76ff3c51`

**Método:** TLC Spec Driven, ciclo 2 do Verifier independente

**Escopo:** correção do gate de T3 e regressão de T1/T2; implementação e testes lidos sem alteração

## Verdict

**PASS para o recorte T1–T3 no commit `53b31fdfe8398d858395dc4b366f814c76ff3c51`.** O campo crítico `socksMode` agora é comparado ao literal Codable `always`, o mutante M6 foi morto e o processo SimpleX executou testes reais SMP e XFTP nos dois endereços exatos da fixture.

**A feature invitation-only permanece NOT READY.** T4, T5 e T6 estão abertos. Nenhum dos oito requisitos NP nem os 34 requisitos do produto muda de `Pending` com esta revalidação.

## Task verdict

| Tarefa | Resultado | Evidência decisiva |
| --- | --- | --- |
| T1, codec SOCKS | PASS no recorte | Os blobs de codec/teste são idênticos aos do baseline técnico anterior. Compilação fresca executou 29 asserts sobre autenticação, frames, allowlist e limites. |
| T2, listener e TLS | PASS no recorte de componente | Os blobs do adaptador/driver/testes são idênticos aos já verificados. Rodada fresca executou dez testes Network.framework, sem falhas ou skips, contra fixture nova. |
| T3, startup do app | PASS no recorte do processo SimpleX | A reprodução limpa exigiu 15 checks. `apps/ios/Shared/TavernaNativeProbe.swift:92`–`:93` afirma o modo contra literal independente; `:101`–`:104` exige `serverTestResult` sem falha e endereço exato para SMP e XFTP. |
| T4, extensões | NOT RUN | `native-tasks.md:78`–`:87` permanece aberto. Build dos targets não comprova lifecycle de Share Extension ou NSE. |
| T5, payload e revogação | NOT RUN | `native-tasks.md:89`–`:98` permanece aberto. Os testes de protocolo de T3 não comparam mensagem SMP ou bytes XFTP e não revogam arquivo em andamento. |
| T6, relatório final | NOT RUN | `native-tasks.md:100`–`:109` depende de T4 e T5. Este documento valida somente o recorte concluído. |

## Spec-anchored outcomes

| Obrigação | Resultado do recorte | Evidência de valor/estado |
| --- | --- | --- |
| NP-01, credencial por execução | PASS no codec/adaptador | `apps/ios/SimpleXChat/Taverna/SocksCodec.swift:61`–`:77` só autoriza após usuário e senha; `tools/taverna/native_access_tests/test_transport.py:134`–`:147` exige credenciais distintas e recusa ausência, senha errada e credencial de outro processo. |
| NP-02, duas rotas exatas | PASS no componente | `SocksCodec.swift:78`–`:107` emite `connect` só para destino permitido; `test_transport.py:149`–`:159` exige negação precisa e nenhuma conexão à sentinela após controle positivo. |
| NP-03, confiança externa e TLS interno | PASS no componente e no app para os dois protocolos | `RelayTransport.swift:84`–`:96` fixa TLS 1.3, identidade, hostname e âncora exclusiva; `test_transport.py:116`–`:132` compara certificado interno. No app, `TavernaNativeProbe.swift:101`–`:104` aceita somente resposta exata e `testFailure == nil` para SMP e XFTP da fixture. Isso prova handshake de protocolo, não payload entre clientes. |
| NP-04, falhar fechado | PARTIAL | `apps/ios/Shared/Model/SimpleXAPI.swift:331`–`:333` e `:369`–`:371` aplicam configuração antes de start/activate. `TavernaNativeProbe.swift:65`–`:69` e `:110`–`:114` exigem `notReady` e core parado sem transporte. T2 cobre credencial, TLS, stop e indisponibilidade do componente. Extensões e payload real continuam ausentes. |
| NP-07, startup/retomada | PASS somente para o processo SimpleX | A ordem está no código citado acima; o receipt limpo contém os 15 checks exatos, incluindo modo obrigatório, ambos os protocolos, start, resume, stop e negativas. Share Extension e NSE pertencem a T4. |
| NP-08, proveniência e limites | PARTIAL | O build limpo e o driver ligam commit, fonte limpa, quatro produtos, hashes de fontes, hash do app, receipt de build e PID do processo ao guard. O relatório final da feature continua em T6. |

NP-05 não foi executado. NP-06 mantém somente a evidência parcial do componente em `test_transport.py:177`–`:190`; não há arquivo em andamento nem dois clientes do core. Os statuses `Pending` de `native-proof.md:53`–`:62` continuam corretos.

## Evidence

| Gate | Resultado desta revalidação |
| --- | --- |
| Swift codec | 29 asserts, 0 falhas. |
| Network.framework/macOS | 10 testes, 0 falhas, 0 skips, fixture nova. |
| Foundation | 76 testes, 0 falhas, 0 skips. O total aumentou em relação às 70 regressões do baseline anterior. |
| Foundation checker | PASS, limitado à fundação. |
| Python compileall | PASS. |
| Diff whitespace | PASS para base até HEAD. |
| Build iOS limpo | `exit_code == 0`, commit exato, fonte limpa e quatro produtos arm64 válidos: app, framework, NSE e Share Extension. Compilação das extensões não conta como execução. |
| Driver clean do app | Status PASS, processo SimpleX, 15 checks em ordem exata, fonte limpa e mesmo commit. Hashes do app, do build receipt e dos quatro fontes conferem. |
| Contenção | O evento `before_main` do mesmo PID registrou loopback permitido e IPv4/IPv6 remoto negados. |
| Capability | Não apareceu em stdout, stderr, startup result ou driver receipt sob o padrão qualificado. O probe também verificou defaults padrão e App Group. |

O Verifier inspecionou `.build/attempts/startup-hardened-clean-a/receipt.json` e `.build/access-qualification/run-startup-a21c48c4/ios/driver-receipt.json`; não repetiu o build nem relançou o app. Os asserts do driver impedem criar o receipt final antes de verificar status, lista de checks, processo, guard e hashes em `tools/taverna/native_access_tests/test_startup.py:29`–`:98`.

Os controles SMP/XFTP exercitam APIs reais do core, SOCKS, mTLS externo e confiança interna para os endereços fictícios exatos. Eles não enviam mensagem, não transferem arquivo e não comprovam revogação de payload.

## Discrimination sensor

O caminho é crítico por controlar autenticação e fail-closed. Seis mutações manuais foram executadas em worktree descartável, com dependências imutáveis copiadas e estado novo. O checkout real ficou limpo antes e depois.

| Mutação | Resultado | Teste discriminante |
| --- | --- | --- |
| M1: aceitar qualquer segredo com o tamanho esperado | KILLED | `NativeTransport.test_01_local_authentication_and_process_separation` recusou a credencial de outro processo. |
| M2: aceitar método sem autenticação no greeting | KILLED | `SocksTests.swift:32`–`:34`. |
| M3: aceitar qualquer destino quando a allowlist não está vazia | KILLED | `SocksTests.swift:42`–`:45`. |
| M4: aprovar confiança TLS externa incondicionalmente | KILLED | `NativeTransport.test_04_wrong_gateway_hostname_and_ca_are_denied`. |
| M5: trocar IPv4 loopback por IPv6 any | KILLED | `NativeTransport.test_08_bindings_are_loopback_only`. |
| M6: trocar `socksMode = .always` por `.onion` | KILLED | Compilação isolada executou `CoreTransport.swift` alterado com o predicado comprometido corrigido. Resultado: controle amplo `true`, literal obrigatório `false`, predicado final `false`, outcome da spec `false`; exit 1. |

**Sensor:** 6/6 killed, 0 survived. Resultado: PASS.

M6 foi um sensor isolado do produtor e do predicado Codable, não um novo build ou lançamento iOS mutante. A execução limpa do app validou o código sem mutação; o sensor demonstrou que a correção distingue especificamente o valor inseguro.

## Code quality and isolation

- A correção de T3 adiciona um assert literal e dois controles positivos do core. Não altera protocolo, criptografia, dependências ou código de extensões.
- `test_startup.py:22`–`:24` exige os 15 nomes exatos; remover o check do modo ou qualquer controle de protocolo invalida o receipt.
- As respostas dos testes de protocolo exigem endereço exato e falha ausente. Um simples retorno de chamada não passa.
- O histórico FAIL permanece em `native-startup-review.md`. A lição L-003 foi registrada pelo script como candidate e referencia o mutante sobrevivente original.
- T5 depende de T3; T6 depende de T4 e T5. O grafo e os campos `Depends on` concordam em `native-tasks.md`.
- O sensor não alterou a árvore real. O scratch foi removido antes da criação deste relatório.
- Nenhuma operação live, conta, provider, push, merge ou publicação foi executada.

## Gaps

1. T4 ainda precisa executar startup e retomada dentro dos processos reais Share Extension e NSE.
2. T5 ainda precisa comparar mensagem SMP e bytes XFTP entre clientes e provar corte de arquivo aberto por revogação ou falha da autoridade.
3. A ausência de capability foi observada em defaults e saídas coletadas; não houve varredura dinâmica ampla de Keychain, bancos, unified logging e todos os arquivos.
4. CI e o gate validado de publicação não foram executados para esta entrega local.

## Risks

- `apiTestProtoServer` prova handshake e confiança nos dois protocolos, sem provar semântica de mensagens ou integridade de arquivo.
- Simulador e assinatura ad hoc não provam aparelho, APNs, distribuição ou operação.
- O PASS vale somente para T1–T3 e para o commit/diff identificados acima. Qualquer mudança posterior exige novos hashes e nova verificação.
