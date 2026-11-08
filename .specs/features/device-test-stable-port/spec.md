# Porte do ensaio SMP para a base estável

## Problem Statement

O host técnico já comprovou a troca de textos pelo relay privado em um iPhone. A revisão precisa de uma branch baseada em stable com as dependências do ensaio e os testes que sustentam o comportamento.

## Goals

- Levar o ensaio SMP e seu build técnico a uma branch local baseada em stable.
- Preservar a validação de identidade, a rota única e o histórico dos dois clientes.
- Conferir a origem dos binários e a classificação do diff local.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Share, NSE, convites de entrada e distribuição | Esses fluxos têm qualificação própria. |
| Assinatura, instalação, teste em aparelho e publicação | O porte usa build sem assinatura e execução isolada no simulador. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Base | Stable atual, com commits novos e focados | Mantém a revisão limitada ao ensaio e às dependências | y |
| Xcode | Incluir o transporte Swift na projeção técnica | O ensaio é o consumidor novo nesta branch | n |
| Build | Reusar as rotinas necessárias de fonte, pacote e verificação | Fecha a compilação sem importar laboratórios de outros fluxos | n |

**Open questions:** none - all resolved or logged above.

## User Stories

### P1: Revisar e reproduzir o ensaio técnico

**Acceptance Criteria**

1. The branch SHALL descend from the confirmed stable base and contain only the source, build and test changes required for the technical SMP test. (`PORT-01`)
2. WHEN the technical host applies a route THEN the core SHALL confirm a single authorized SMP route through authenticated loopback before chat start. (`PORT-02`)
3. IF the fixture revokes the identity or the route differs THEN the technical test SHALL leave the chat stopped. (`PORT-03`)
4. WHEN the isolated Simulator core and the fixture peer exchange ten texts each way and restart THEN both histories SHALL preserve the same twenty unique text items and directions. (`PORT-04`)
5. WHEN the technical host builds for iOS arm64 THEN the unsigned receipt SHALL bind the projected Swift sources, compiled core and resulting package. (`PORT-05`)
6. The stable portable suite SHALL pass with every existing test retained. (`PORT-06`)

**Independent Test**: verify ancestry and diff, run portable and native checks, and reproduce startup, delivery and unsigned build from the candidate source.

## Edge Cases

- A route without the expected authorization or configuration fails before chat start.
- Both clients restart with their existing test stores and keep the same twenty items.
- The ordinary controller retains its regular startup and server API.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| PORT-01 | Revisar e reproduzir | Verify | PASS |
| PORT-02 | Revisar e reproduzir | Verify | PASS |
| PORT-03 | Revisar e reproduzir | Verify | PASS |
| PORT-04 | Revisar e reproduzir | Verify | PASS |
| PORT-05 | Revisar e reproduzir | Verify | PASS |
| PORT-06 | Revisar e reproduzir | Verify | PASS |

## Success Criteria

- A revisão inspeciona um diff local com base em stable e classificação por arquivo.
- Startup, revogação, vinte textos e reabertura passam no núcleo compilado.
- O pacote técnico arm64 sem assinatura e a suíte portátil passam na branch.
