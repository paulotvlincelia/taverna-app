# Testes Foundation do host técnico

Profile: standard

## Intent

O checkout limpo da CI não tem a pasta temporária do teste de identidade. Os testes de armazenamento dependem da gravação de metadados de backup do macOS para exercitar a ordem das operações. A suíte portátil deve testar a ordem e o bloqueio com uma resposta controlada. A execução nativa deve continuar conferindo a exclusão real. O código iOS e seu comportamento de bloqueio ficam intactos.

Método TLC Lean para dois arquivos de teste, sem mudança de interface, CI ou comportamento do app.

## Checks

### S1 - Preparação e armazenamento

**C1** - Em checkout sem `.build`, o teste de identidade cria seu diretório de trabalho e o probe retorna exatamente a classe, a conta fictícia e o grupo esperado.
Proof: `python3.12 -m unittest discover -s tools/taverna/tests -p test_device_identity.py -k test_literal_query_builder_executes_with_explicit_access_group -v` em uma extração limpa do commit.

**C2** - A suíte portátil confere a exclusão do diretório dedicado antes de ler a chave e abrir os bancos. A falha de exclusão encerra o fluxo com zero aberturas.
Proof: `python3.12 -m unittest discover -s tools/taverna/tests -p test_device_storage.py -k test_fresh_key_precedes_native_open -k test_existing_pair_reuses_key -k test_interrupted_creation_reuses_key -k test_backup_exclusion_precedes_open -v`

**C3** - O mesmo probe em modo nativo verifica `isExcludedFromBackup == true` no diretório de cada cenário bem-sucedido e mantém a prova de bloqueio com zero aberturas.
Proof: `python3.12 tools/taverna/tests/test_device_storage.py -k test_backup_exclusion_precedes_open -v`

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| Preparação de armazenamento portátil (4) | `fresh` C2 · `existing` C2 · `interrupted` C2 · `backupError` C2 | - |
| Preparação de armazenamento nativa (4) | `fresh` C3 · `existing` C3 · `interrupted` C3 · `backupError` C3 | - |

## Test policy

| Code | Required proofs | Coverage expectation |
| --- | --- | --- |
| Preparação do probe de identidade | C1 em checkout limpo | Consulta Swift retorna classe, conta e grupo exatos |
| Probe de armazenamento | C2 no modo portátil e C3 com Foundation nativo | Caminho e ordem nos três cenários de sucesso e bloqueio antes de abrir quando a exclusão falha |

## Swept

- validation: C1, C2, C3
- failure modes: C2, C3
- idempotency: C2 para reabrir o par de bancos
- authorization: existing - sandbox de rede do probe de armazenamento
- concurrency: C1 usa diretório temporário exclusivo por teste
- data lifecycle: C2 para o diretório dedicado e a reutilização da chave
- dependency failure: C2 e C3 para erro de exclusão
- state transitions: C2 e C3 para exclusão antes da abertura
- observability: n/a - o escopo é a execução local dos testes existentes

## Out of scope

- Código iOS, workflow da CI e execução em aparelho.
- Enviar a correção ao GitHub.

## Handoff

- S1 = 23.301 bytes dos dois arquivos / 4 = cerca de 5.826 tokens, abaixo de 150 mil. Um implementador.
- C1, C2 e C3 passaram em extração limpa. A execução nativa preserva as sete verificações e a suíte portátil preserva 136 testes.
