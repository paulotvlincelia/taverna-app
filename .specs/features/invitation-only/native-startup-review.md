# Revisão independente: transporte nativo T1–T3

**Data:** 2026-10-16

**Baseline verificado:** `b0fe90f0261d7af3dfe3a382f12b6a1128d1ecce..86e867e9e22bc2903dd4af1535283af27a085e29`

**Método:** TLC Spec Driven, verificação independente do autor

**Escopo:** T1, T2 e T3 de `native-tasks.md`; implementação e testes lidos sem alteração

## Verdict

**FAIL para concluir o recorte T1–T3.** Os gates nominais passam e a implementação observada aplica o transporte gerenciado. O sensor encontrou um mutante sobrevivente no oráculo de T3: trocar `socksMode` de `always` para `onion` viola a configuração obrigatória, mas o predicado comprometido no probe continua verdadeiro porque compara `actual` com `expected` produzido pela mesma função e não afirma `socksMode` de forma independente.

**A feature invitation-only está NOT READY.** T4, T5 e T6 continuam abertos. Nenhum dos oito NP nem os 34 requisitos do produto muda de `Pending` por causa desta revisão.

## Task verdict

| Tarefa | Resultado | Evidência decisiva |
| --- | --- | --- |
| T1, codec SOCKS | PASS no recorte | `SocksCodec.swift:38` processa frames por estágio; `SocksTests.swift:21`–`:59` afirma autenticação, fragmentação, rotas e limites; 29 asserts passaram em compilação fresca. |
| T2, listener e TLS | PASS no recorte de componente | `RelayTransport.swift:40`–`:68` limita o listener ao loopback e cria credencial por processo; `RelayTransport.swift:81`–`:96` fixa mTLS/TLS 1.3; os dez testes em `test_transport.py:127`–`:226` passaram contra fixture nova. Isso não é execução do app nem protocolo SMP/XFTP. |
| T3, startup do app | FAIL no gate independente | O processo real e o receipt limpo passaram os 12 checkpoints, mas `TavernaNativeProbe.swift:88`–`:89` usa a própria função sob teste como oráculo e omite o valor exato de `socksMode`; o mutante M6 sobreviveu. |
| T4, extensões | NOT RUN | `native-tasks.md:76`–`:85` permanece aberto. Compilar os targets não prova lifecycle de Share Extension ou NSE. |
| T5, SMP/XFTP e revogação | NOT RUN | `native-tasks.md:87`–`:96` permanece aberto. Não houve comparação de mensagem SMP, bytes XFTP ou arquivo em andamento revogado. |
| T6, relatório final | NOT RUN | `native-tasks.md:98`–`:107` permanece aberto e depende de T5. Este documento é só o gate independente intermediário. |

## Spec-anchored outcomes

| Obrigação | Resultado do recorte | Evidência de valor/estado |
| --- | --- | --- |
| NP-01, exigir credencial da execução | PASS no codec/adaptador | `SocksCodec.swift:61`–`:77` só avança após comparação de usuário e senha; `test_transport.py:134`–`:147` exige credenciais distintas e recusa ausência, senha incorreta e credencial de outro processo. |
| NP-02, duas rotas exatas antes de conexão | PASS no componente | `SocksCodec.swift:78`–`:107` só emite `connect` para destino permitido; `test_transport.py:149`–`:159` exige reply de ruleset e nenhuma conexão à sentinela após controle positivo. |
| NP-03, confiança externa e TLS interno | PASS no componente | `RelayTransport.swift:84`–`:96` fixa identidade, hostname, âncora exclusiva e TLS 1.3; `test_transport.py:116`–`:132` compara o certificado interno e `:167`–`:175` recusa CA/hostname externos errados. O teste `:219`–`:226` prova que a CA externa não substitui a confiança interna. |
| NP-04, falhar fechado | PARTIAL | `SimpleXAPI.swift:331`–`:333` e `:369`–`:371` configuram antes de start/activate; `TavernaNativeProbe.swift:63`–`:67` e `:101`–`:105` exigem `notReady` e core parado sem transporte. T2 cobre falhas de auth/TLS/stop. Ainda não há tráfego SMP/XFTP real para excluir toda saída alternativa. |
| NP-07, app antes de operações de rede | FAIL no gate de teste | A ordem existe em `SimpleXAPI.swift:331`–`:333`, `:369`–`:371` e `:894`–`:898`. A reprodução limpa do processo SimpleX prova negação sem configuração e start/resume nominal. O valor de `socksMode` não está protegido por assert independente, e Share Extension/NSE não executaram. |
| NP-08, proveniência e limites | PARTIAL | O receipt limpo liga o commit, quatro produtos, build, quatro fontes e PID do processo ao guard. `test_startup.py:29`–`:44` recusa SHA, fonte, produtos, sessão ou guard incompatíveis; `:78`–`:95` exige processo/checkpoints/PID/hashes. A prova final da feature e seu relatório continuam em T6. |

NP-05 não foi executado. NP-06 tem somente evidência parcial do componente em `test_transport.py:177`–`:190`; não há arquivo em andamento nem core real. Os statuses canônicos permanecem corretos em `native-proof.md:53`–`:62`.

## Gate evidence

| Gate | Resultado fresco desta revisão |
| --- | --- |
| Swift codec | 29 asserts, 0 falhas. |
| Network.framework/macOS | 10 testes, 0 falhas, 0 skips, fixture e estado novos. |
| Foundation | 70 testes, 0 falhas, 0 skips. |
| Foundation checker | PASS, explicitamente limitado à fundação. |
| Python compileall | PASS. |
| Diff whitespace | PASS para o baseline até HEAD. |
| Reprodução iOS limpa | Não repetida. O Verifier revalidou o receipt existente: commit e fonte limpa, quatro artefatos presentes e com hash válido, hash do receipt de build, quatro hashes de fonte, hash do app e evento `before_main` do mesmo PID conferem. O processo registrado é SimpleX e os 12 checkpoints são exatos. |

O scan de persistência cobre `UserDefaults.standard`, App Group, stdout, stderr e receipt em `TavernaNativeProbe.swift:90`–`:93` e `test_startup.py:85`–`:87`. Não prova ausência em Keychain, banco, unified logging ou outros arquivos. A implementação não contém escrita da capability nesses destinos, mas isso é inspeção, não prova dinâmica abrangente.

## Discrimination sensor

O risco é crítico porque autenticação e fail-closed controlam todo acesso nativo. Foram executadas seis mutações em worktree descartável, com dependências imutáveis copiadas e estado novo. O checkout real ficou limpo antes e depois.

| Mutação | Resultado | Teste discriminante |
| --- | --- | --- |
| M1: comparação de segredo aceita qualquer valor do mesmo tamanho | KILLED | `NativeTransport.test_01_local_authentication_and_process_separation`; a suíte unitária isolada não matou este mutante, mas a integração recusou credencial de outro processo. |
| M2: greeting aceita método sem autenticação em vez de username/password | KILLED | `SocksTests.swift:32`–`:34`. |
| M3: qualquer destino passa quando a allowlist não está vazia | KILLED | `SocksTests.swift:42`–`:45`. |
| M4: verificação da confiança externa retorna sucesso incondicional | KILLED | `NativeTransport.test_04_wrong_gateway_hostname_and_ca_are_denied`. |
| M5: listener muda de IPv4 loopback para IPv6 any | KILLED | `NativeTransport.test_08_bindings_are_loopback_only`. |
| M6: `socksMode = .always` muda para `.onion` | **SURVIVED** | Compilação isolada executou o `CoreTransport.swift` alterado com o predicado exato de `TavernaNativeProbe.swift:89`: `committed_predicate=true`, enquanto o resultado da spec foi `spec_always=false`. Não houve novo lançamento do app para este mutante. |

**Sensor:** 5/6 killed, 1 survived. Resultado: FAIL.

## Ranked gaps

1. **Crítico, T3:** o teste de configuração usa oráculo circular e não afirma `socksMode == always`. Correção mínima: afirmar o campo Codable de forma independente e provar as duas rotas da fixture por uma API real de teste de protocolo, sem usar `networkConfig` como fonte do próprio esperado.
2. **Obrigatório, T4:** executar app, Share Extension e NSE como processos efetivos, cada um com configuração antes de start/activate. Build de target ou teste de biblioteca não satisfaz NP-07.
3. **Obrigatório, T5:** comparar payload SMP e bytes XFTP no core real; provar novas conexões recusadas e arquivo aberto encerrado em até 60 segundos após revogação ou falha da autoridade.
4. **Evidência limitada:** a ausência de capability foi observada em defaults e saídas coletadas, sem varredura dinâmica de Keychain, banco, unified logging e outros arquivos.
5. **Publicação bloqueada:** este baseline e o remoto reconciliado têm somente a base upstream como ancestral comum. O delta precisa ser reaplicado em worktree novo e passar classificação/digest de publicação. Não mesclar o histórico substituído nem publicar esta branch antiga.

## Code quality and isolation

- O diff T1–T3 é cirúrgico para codec, adaptador, hook de startup, probe e drivers. Não altera criptografia SimpleX, locks de dependências ou código de extensões.
- Os commits de implementação são atômicos por T1, T2 e T3 e usam mensagens Conventional Commits.
- A capability é gerada por processo, mantida em memória e removida em `TavernaCoreTransport.stop()` (`CoreTransport.swift:65`–`:70`). O driver de qualificação a entrega por pipe; não há segredo operacional, credencial pessoal ou identidade pública no relatório.
- O sensor não alterou a árvore real. O scratch foi removido e o porcelain voltou ao baseline vazio.
- A revisão usou somente fontes e fixtures locais, sem publicação ou deploy.

## Fix task and lesson proposal

**Fix T3:** fortalecer o probe para comparar `socksMode` com `always` usando valor independente da função sob teste e executar controle positivo das duas rotas por uma API real do core. Repetir build/startup limpos, o mutante M6 e os gates Foundation antes de nova revisão.

**Lesson proposta, não persistida por este Verifier:** “Teste de configuração de segurança deve obter o esperado fora da função sob teste e afirmar cada campo fail-closed; comparar `actual` com outra chamada da mesma função não protege valores obrigatórios.” Grounding: `CoreTransport.swift:53`–`:62`, `TavernaNativeProbe.swift:88`–`:89`, mutante M6 sobrevivente.

## Risks

- A implementação atual observada contém `socksMode = .always`; o FAIL recai sobre a capacidade do gate de detectar regressão e impede declarar T3 concluída.
- Uma correção local no baseline antigo ainda não autoriza integração. A base remota reconciliada exige transposição limpa, novos hashes, CI e Verifier no commit final.
- Simulador e assinatura ad hoc não provam aparelho, APNs, distribuição ou operação.
