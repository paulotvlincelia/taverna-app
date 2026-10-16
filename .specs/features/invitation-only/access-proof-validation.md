# Validação independente da prova de fronteira de acesso

**Veredito:** PASS para AP-01..AP-07 no experimento local delimitado. Este
veredito não aprova nenhum dos 34 requisitos do app, que continuam `Pending`.

**Data:** 2026-10-16

**Base integrada:** `984a21659e6b846a874ae1a672fef5a890865070`

**HEAD verificado:** `7d03ba2908c0b9111a25d62b07fc7e8376421729`

**Correção de runtime:** `e99ee5d2496ae7c7c12c82073fadea5de4f43e9a`

**Verifier:** subagente independente; autor diferente do Verifier
**Escopo:** `.specs/features/invitation-only/access-proof-plan.md`, AP-01..AP-07

## Resultado por obrigação

| Obrigação | Resultado definido | Evidência rederivada | Veredito |
| --- | --- | --- | --- |
| AP-01 | Credencial ativa opera SMP e XFTP reais, preservando o protocolo interno | `tools/taverna/access_proof/test_boundary.py:67` compara a mensagem exata nos dois sentidos; `tools/taverna/access_proof/test_boundary.py:86` compara os bytes XFTP; `tools/taverna/access_proof/client.py:22` e `tools/taverna/access_proof/client.py:25` mantêm adaptadores locais fixos para os clientes oficiais | PASS |
| AP-02 | Sem certificado ou sem associação ativa, nenhum byte do backend chega ao cliente | `tools/taverna/access_proof/test_boundary.py:24` exige `{'allowed_bytes': False}` nos casos de `tools/taverna/access_proof/test_boundary.py:88` e `tools/taverna/access_proof/test_boundary.py:92`; `tools/taverna/access_proof/gateway.py:43` exige certificado e associação | PASS |
| AP-03 | Revogação encerra sessões existentes e impede novas em menos de 60 s | `tools/taverna/access_proof/test_boundary.py:41` exige fechamento, `tools/taverna/access_proof/test_boundary.py:42` exige menos de 60 s, `tools/taverna/access_proof/test_boundary.py:96` cobre os dois backends e `tools/taverna/access_proof/test_boundary.py:125` impede o download revogado | PASS |
| AP-04 | Política ausente ou inválida fecha acesso novo e existente em menos de 60 s | `tools/taverna/access_proof/gateway.py:21` valida schema/lista, `tools/taverna/access_proof/gateway.py:26` falha fechado, e `tools/taverna/access_proof/test_boundary.py:102`/`tools/taverna/access_proof/test_boundary.py:108` cobrem ausência e oito formas inválidas | PASS |
| AP-05 | A ponte usa somente os dois backends administrativos fixos | `tools/taverna/access_proof/gateway.py:13` fixa SMP e XFTP; `tools/taverna/access_proof/gateway.py:76` não lê destino do cliente; `tools/taverna/access_proof/test_boundary.py:159` prova que a sentinela é alcançável no controle e `tools/taverna/access_proof/test_boundary.py:165` exige contador inalterado após payload `CONNECT` | PASS |
| AP-06 | Redes internas, nenhuma porta publicada, dados fictícios e estado gravável no worktree | `tools/taverna/access_proof/fixture.py:15` ancora estado em `.build` no checkout; `tools/taverna/access_proof/fixture.py:70` cria containers sem `-p`, com rootfs somente leitura, capabilities removidas e `no-new-privileges`; `tools/taverna/access_proof/fixture.py:99` cria redes internas; `tools/taverna/access_proof/test_boundary.py:132` inspeciona redes, portas, privilégio, rootfs e bypass; `tools/taverna/access_proof/test_boundary.py:167` confere logs no run selecionado | PASS |
| AP-07 | Relatório identifica entradas, versões, comandos e limites; requisitos do app permanecem pendentes | Hashes e commits estão em `tools/taverna/access_proof/inputs.json:4`; comandos estão em `docs/taverna/access-proof.md:19`; limites estão em `docs/taverna/access-proof.md:52`; os 34 itens seguem `Pending` em `.specs/features/invitation-only/spec.md:180` e a contagem está em `.specs/features/invitation-only/spec.md:215` | PASS |

## Cobertura reversa dos testes

| Teste | Obrigação reclamada |
| --- | --- |
| `test_00_active_device_reaches_both_real_backends` | AP-01, controle positivo dos dois listeners |
| `test_01_real_smp_two_way` | AP-01, mensagem SMP exata nos dois sentidos |
| `test_02_real_xftp_exact_bytes` | AP-01, XFTP real e comparação byte a byte |
| `test_03_missing_certificate` | AP-02, credencial ausente |
| `test_04_unknown_device_same_ca` | AP-02, certificado válido sem associação |
| `test_05_revocation_cuts_open_sessions_and_new_access` | AP-03, sessão aberta e acesso novo após revogação |
| `test_06_missing_policy_fails_closed` | AP-04, política ausente |
| `test_07_invalid_policy_fails_closed` | AP-04, oito políticas inválidas |
| `test_08_revoked_device_cannot_fetch_existing_file` | AP-03, arquivo existente após revogação |
| `test_09_only_internal_networks_no_public_ports` | AP-06, redes, portas, privilégios, rootfs e bypass direto |
| `test_10_fixed_backends_do_not_follow_client_destination` | AP-05, destino sentinela fornecido pelo cliente |
| `test_11_logs_belong_to_selected_run` | AP-06/AP-07, isolamento e reprodução por slug |

Todos os 12 testes reivindicam uma obrigação do plano. Nenhum teste foi
contado para convite, grupo, iOS, distribuição ou operação.

## Reprodução independente e gates

O Verifier criou o branch exclusivo `codex/access-proof-verifier-vbase` e os
worktrees `access-proof-verifier-vbase` e `access-proof-sensor`. Somente os
quatro binários qualificados foram copiados como inputs somente leitura. Bancos,
certificados, chaves e logs foram gerados nesses checkouts e permaneceram sob
`.build/access-qualification`, ignorado por `.gitignore:92`.

Entradas qualificadas novamente:

- SMP server v7.0.0.6 / `efaad8e`, SHA-256
  `def80bc70800d0dbc0d8f81433b0cfce706691303788d12206853f8714853544`.
- XFTP server v7.0.0.6 / `efaad8e`, SHA-256
  `4a69d025d6a886b50841d622395f88fa0d97a05663d1f483f1c5d183585dc148`.
- SimpleX Chat v7.0.0.11, SHA-256
  `70a439699053c1d9b7f83fef9dcdd5e391a5b6648a28a797b4e1b730a08b1c1b`.
- XFTP client v1.0.1, SHA-256
  `9c3e73b6bb2dfecbacd97edc6aa60315a52e28256784f68e3a8b5b297af599d2`.
- Imagem local `taverna-access-proof:20261016`:
  `sha256:e5a49b89589c7f8db1f9d7347d3e8b0737060fe117b61b7a01d30831374cdafe`.

Comandos e resultados no HEAD final:

```text
TAVERNA_PROOF_RUN=vfix python3.12 tools/taverna/access_proof/fixture.py init
TAVERNA_PROOF_RUN=vfix python3.12 tools/taverna/access_proof/fixture.py start
TAVERNA_PROOF_RUN=vfix python3.12 tools/taverna/access_proof/fixture.py clients
TAVERNA_PROOF_RUN=vfix python3.12 tools/taverna/access_proof/test_boundary.py
=> 12 passed, 0 failed, 0 skipped, 12.936 s

python3.12 -m unittest discover -s tools/taverna/tests -q
=> 70 passed, 0 failed, 0 skipped, 0.452 s

python3.12 tools/taverna/check_foundation.py
=> PASS: foundation only; no iOS build or release proof

python3.12 -m compileall -q tools/taverna
=> exit 0

git diff --check
=> exit 0

python3.12 .agents/skills/tlc-spec-driven/scripts/validate_spec.py \
  .specs/features/invitation-only/spec.md
=> 0 errors, 0 warnings
```

Após restaurar todos os mutantes, a suíte completa também passou no estado
`vsensor`: 12/12, zero skips, 12.461 s. `fixture.py stop` removeu somente os
containers e redes `vfix`/`vsensor`; os arquivos das rodadas foram preservados.
O porcelain dos dois worktrees de verificação voltou ao baseline vazio.

No PR #14, `gh pr checks 14 -R paulotvlincelia/taverna-app` retornou duas
execuções `foundation` verdes no HEAD exato
`7d03ba2908c0b9111a25d62b07fc7e8376421729`.

## Ciclos de verificação

### Ciclo 1: FAIL no SHA `a706721559a6e561eec77a93b28fb49e83fc378c`

Uma reprodução fresca com `TAVERNA_PROOF_RUN=vbase` encontrou
`tools/taverna/access_proof/fixture.py:107` redirecionando os dois logs para
`/work/run-a`. Sem esse diretório residual, o relay encerrou com:

```text
sh: 1: cannot create /work/run-a/smp.log: Directory nonexistent
sh: 1: cannot create /work/run-a/xftp.log: Directory nonexistent
```

Os 11 testes foram executados, com 12 falhas de asserção/subteste e 2 erros.
Casos negativos e de isolamento passaram, mas não serviram como substituto para
os controles positivos SMP/XFTP. O Verifier rejeitou a primeira reprodução.

### Ciclo 2: PASS no SHA final

`e99ee5d2496ae7c7c12c82073fadea5de4f43e9a` passou a derivar ambos os caminhos
de log de `RUN.name` e acrescentou `test_11_logs_belong_to_selected_run`. A
reprodução independente `vfix` passou sem diretório residual `run-a`. O runtime
desse commit é idêntico ao HEAD documental final `7d03ba290`.

## Sensor de discriminação

O sensor rodou somente no scratch `access-proof-sensor`, em redes e estado
`vsensor` próprios. Cada mutante alterou comportamento de autorização ou rota;
somente o gateway próprio foi reiniciado. Não houve `stash`, alteração do
worktree do autor, erro de sintaxe ou recurso compartilhado.

| Mutante | Falha comportamental injetada | Teste que matou | Resultado |
| --- | --- | --- | --- |
| M1 | `permitted()` aceita todo certificado da CA, ignorando a lista ativa | `test_04_unknown_device_same_ca` observou `allowed_bytes=True` nos dois backends | KILLED |
| M2 | TLS aceita ausência de certificado e os três gates deixam o cliente sem DER seguir | `test_03_missing_certificate` observou `allowed_bytes=True` nos dois backends | KILLED |
| M3 | Erro ao ler/parsear política retorna permitido | `test_06_missing_policy_fails_closed` manteve sessão aberta além do limite observado de 4 s | KILLED |
| M4 | Watcher ignora revogação e mantém sessão | `test_05_revocation_cuts_open_sessions_and_new_access` manteve sessão aberta além de 4 s | KILLED |
| M5 | Listener SMP aponta para a sentinela `unknown:19000` | `test_10_fixed_backends_do_not_follow_client_destination` viu contador `2`, esperado `1` | KILLED |
| M6 | Listener XFTP aponta para o backend SMP | `test_02_real_xftp_exact_bytes` excedeu 45 s sem completar o envio XFTP | KILLED |

**Profundidade:** autorização crítica, seis mutações comportamentais.

**Resultado:** 6/6 mortos, 0 sobreviventes válidos.

Uma tentativa preliminar de M2 removeu só parte das defesas e não mudou o
comportamento porque o recheck e o watcher ainda negavam DER ausente. Ela foi
classificada como mutação equivalente/incompleta, corrigida antes da contagem,
e não indica fraqueza do teste.

## Revisão de código, segurança e clareza

- A mudança implementa somente a fixture autorizada. Não há emissão de
  convite, administração, UI, grupo ou deploy escondido no delta.
- `gateway.py` mantém duas rotas administrativas explícitas, TLS 1.3,
  certificado obrigatório, associação por fingerprint, recheck após abrir o
  backend e polling fail-closed. O sensor comprovou que os checks distinguem
  as falhas de maior risco.
- `fixture.py` valida slug, hashes dos inputs e nomes exclusivos. Containers
  usam usuário sem privilégio, rootfs somente leitura, capabilities removidas,
  `no-new-privileges`, memória/CPU limitadas e redes internas sem portas
  publicadas.
- Estado e credenciais são fictícios, locais e ignorados. Nenhuma chave,
  certificado, banco, conversa ou convite foi versionado. A string
  `fixture-only-passphrase` é um valor constante de fixture, não uma credencial
  externa.
- A divisão entre `fixture.py`, `gateway.py`, `client.py` e
  `test_boundary.py` é direta e proporcional ao experimento. Não foi encontrada
  abstração, configuração ou alteração adjacente sem vínculo com AP-01..AP-07.

## Limites e riscos residuais

Este PASS não integra nem comprova:

- app iOS, Share Extension ou NSE;
- emissão, resgate, repetição, expiração ou recuperação de convites;
- grupos oficiais ou autoridade administrativa de grupos;
- download grande interrompido durante revogação;
- todos os caminhos de egress/fallback/proxy interno do cliente;
- aparelhos, troca de dispositivo, APNs, assinatura ou distribuição;
- VPS, DNS, operação, monitoramento ou recovery de produção.

A ferramenta XFTP CLI de prova é experimental/deprecated e não foi adotada
como componente do app. A imagem fixa o Ubuntu por digest, mas os pacotes APT
da receita não constituem build bit a bit. A posse da credencial fictícia prova
somente a associação técnica nesta fixture, não a identidade de uma pessoa.

O `validate_state.py invitation-only` não deve transformar este relatório em
`validation.md`: esse gate representa a feature completa e marcaria
indevidamente os 34 requisitos. O arquivo separado mantém o PASS restrito ao
experimento AP-01..AP-07.

## Lição fundamentada para o integrador

A falha do ciclo 1 é sinal reutilizável. O Verifier não executou o comando
abaixo porque sua responsabilidade de escrita se limita a este relatório; o
integrador pode persistir a lição com:

```bash
python3.12 .agents/skills/tlc-spec-driven/scripts/lessons.py add \
  --feature invitation-only \
  --signal gate_fail \
  --source ".specs/features/invitation-only/access-proof-validation.md#ciclo-1" \
  --text "Derive every fixture output path from the selected run identifier and prove it in a fresh worktree" \
  --scope tools/taverna/access_proof
```

## Conclusão

**PASS:** AP-01..AP-07 foram demonstrados no HEAD
`7d03ba2908c0b9111a25d62b07fc7e8376421729`, com 12/12 testes de integração,
70/70 regressões, CI verde e 6/6 mutantes comportamentais mortos. A primeira
reprodução falha foi preservada, corrigida e requalificada. Os 34 requisitos do
produto continuam `Pending`, e nenhum uso sensível, piloto ou deploy está
liberado por este resultado.
