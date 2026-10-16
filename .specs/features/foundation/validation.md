# Fundação pública: validação independente

**Verdict**: PASS
**Date**: 2026-10-16
**Spec**: `.specs/features/foundation/spec.md`
**Diff range**: `479548ee53ffb73db73841e77acbeee5a78dbbd5..96bb6dc0ead1d46299b7a6d07f05fa37db32fa98`
**Verifier**: independente, autor diferente do implementador

O PASS cobre somente a fundação F0. Não comprova build iOS, assinatura, push, binário ou distribuição.

## Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | PASS | Checker, licenças, atribuições, documentação e CI aprovados. |
| T2 | PASS | Preflight e isolamento aprovados; dependências ainda ausentes permanecem `BLOCKED`. |
| T3 | PASS | Roadmap público, clone limpo, CI e Verifier conferidos no SHA acima. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| PUB-01 | Origem oficial, SHA base e licenças preservados. | `tools/taverna/tests/test_foundation.py:42` — `self.assertIn('preserved license changed: LICENSE', ...)`; `tools/taverna/tests/test_foundation.py:56` — `self.assertIn('upstream: repository/SHA mismatch', ...)`; `tools/taverna/tests/test_foundation.py:61` — exige as duas licenças. Hashes atuais iguais aos da base. | PASS |
| PUB-02 | README factual, autoridade comum, redirect e TLC atribuída. | `tools/taverna/tests/test_foundation.py:65` — exige redirect para `AGENTS.md`; `tools/taverna/tests/test_foundation.py:86` — exige `NOTICE.md`; `README.md:7` e `README.md:19` declaram estado e entrada de desenvolvimento. | PASS |
| PUB-03 | Preflight registra ferramentas e retorna `BLOCKED`/exit 2 sem dependências. | `tools/taverna/tests/test_preflight.py:37-45` — afirma gates bloqueados e `build_proven == False`; `tools/taverna/tests/test_preflight.py:52-55` — cada ausência bloqueia seu gate; `tools/taverna/tests/test_preflight.py:138-142` — exit 2, `overall == 'BLOCKED'` e SHA ausente. | PASS |
| PUB-04 | Estado gravável e simulador confinados ao worktree; nada usa estado global automaticamente. | `tools/taverna/tests/test_preflight.py:85-87` — caminhos disjuntos, confinados e sem criação; `tools/taverna/tests/test_preflight.py:123-125` — set ausente bloqueia sem consulta/criação; `tools/taverna/tests/test_preflight.py:133-134` — comando usa somente `.build/SimulatorDevices`. | PASS |
| PUB-05 | Distribuição permanece bloqueada até provas próprias. | `tools/taverna/tests/test_foundation.py:38` — exige erro `BLOCKED`; `tools/taverna/tests/test_foundation.py:47` — rejeita trocar o gate para `PASS`; `tools/taverna/tests/test_foundation.py:90-91` — CLI retorna 2 e imprime `BLOCKED`. | PASS |
| PUB-06 | CI sem privilégios/segredos detecta falhas reais e o SHA final tem Verifier independente. | `tools/taverna/tests/test_foundation.py:78` — rejeita workflow privilegiado; `tools/taverna/tests/test_foundation.py:82` — rejeita workflow extra; `.github/workflows/foundation.yml:5-21` limita permissão e executa os gates. Sensor matou 2/2 mutações públicas. | PASS |
| PUB-07 | Roadmap público autossuficiente com issues canônicas e gates. | `docs/taverna/roadmap.md:3-15` registra Project, issues, pais, estados e conclusão; o readback live encontrou oito itens públicos, pais canônicos e a entrega F0 em `Verificação`. `tools/taverna/check_foundation.py:45-60` e o teste válido em `tools/taverna/tests/test_foundation.py:35` conferem links e fronteira documental. | PASS |

**Status**: 7/7 requisitos corresponderam ao resultado definido pela spec; zero gaps de precisão.

## Diff surface and independence

- O merge-base do HEAD é exatamente o upstream `479548ee53ffb73db73841e77acbeee5a78dbbd5`.
- A diff não altera fonte funcional do mensageiro. Workflows herdados foram movidos sem mudança; somente `foundation.yml` está ativo.
- Os objetos Git dos commits da outra linha de desenvolvimento não existem neste repositório.
- A revisão da superfície pública não encontrou paths locais reais, links que exijam acesso restrito, nomes de máquinas, material de acesso ou dados de mensagens. As únicas strings sintéticas desses formatos estão nas fixtures que testam rejeição.
- `LICENSE` e `assets/ASSETS_LICENSE.md` têm os mesmos SHA-256 da base. `docs/taverna/asset-policy.json:3-6` mantém `release_status: BLOCKED` e nenhum asset aprovado.

## Discrimination sensor

| Mutation | File:line | Expected detector | Result |
| --- | --- | --- | --- |
| Remover o bloqueio de release solicitado | `tools/taverna/check_foundation.py:39-40` | `test_release_stays_blocked` e `test_cli_failure_nonzero` | KILLED: 2 falhas em 14 testes. |
| Consultar simuladores mesmo sem set local | `tools/taverna/preflight.py:57-62` | `test_missing_session_simulator_set_never_queries_global_devices` | KILLED: 1 falha em 14 testes. |

**Sensor depth**: lightweight, 2 mutações comportamentais.
**Isolation**: worktree scratch descartado sem `stash`; porcelain da árvore real permaneceu vazio antes/depois.

## Gates

| Check | Result |
| --- | --- |
| Clean clone no SHA exato | PASS; porcelain vazio. |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` | PASS: 28 testes, 0 falhas, 0 skips. |
| `python3.12 tools/taverna/check_foundation.py` | PASS. |
| `python3.12 -m compileall -q tools/taverna` | PASS. |
| `git diff --check` | PASS. |
| TLC `validate_spec --strict` / `validate_tasks` | PASS: 0 erros, 0 avisos. |
| Preflight em clone sem device set | Exit 2 esperado; `overall=BLOCKED`, build/push falsos e nenhum diretório criado. |
| Gate de release | Exit 2 esperado; `BLOCKED`. |
| CI push run 38899290421 | SUCCESS no SHA exato. |
| CI PR run 38899296230 | SUCCESS no SHA exato. |

Testes existentes da base não foram alterados. Os 28 testes são novos para a fundação; nenhum teste foi removido, pulado ou enfraquecido.

## Edge cases and limits

- Ferramenta ausente, versão incompatível, erro, timeout, SDK inválido e set de simulador ausente permanecem `BLOCKED`.
- Set local ausente não provoca consulta global nem criação automática.
- Asset sem autorização e fonte correspondente sem prova mantêm release bloqueada.
- `build_proven` e `push_proven` permanecem falsos. O runtime e um simulador reservado não mudam esse resultado.

## Summary

**Overall**: PASS para F0 no SHA `96bb6dc0ead1d46299b7a6d07f05fa37db32fa98`.

O integrador deve versionar este relatório e repetir a CI no commit resultante antes de remover o draft ou integrar o PR. Esse passo mantém o contrato de CI no commit final; não amplia o escopo para F1.
