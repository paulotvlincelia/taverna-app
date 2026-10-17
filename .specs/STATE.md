# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only, issue #15. TLC Spec Driven; A1 e CLI administrativa inicial aprovados. Oito critérios NP e 34 requisitos do produto continuam Pending.
- Reconciliação: novo worktree irmão taverna-app-worktrees/native-access-reconciled e branch codex/15-native-access-reconciled, base c25dc4eb0d963afa916ac7605c5f2665e66318ba. Delta transposto sem unir ancestrais substituídos; checkout anterior e evidências preservados.
- T1/T2: fontes transpostas; codec 29 asserts, transporte 10 testes novos sem falha, Foundation 76 testes. Build limpo e startup foram reproduzidos neste checkout, no commit 53b31fdfe8398d858395dc4b366f814c76ff3c51.
- T3: gate anterior FAIL por M6. Correção passou 15 checkpoints no processo SimpleX, com valor always literal e controles reais SMP/XFTP. Reprodução limpa passou os 15 checkpoints; re-verificação independente PASS T1–T3, seis mutantes detectados. T4/T5/T6 continuam abertos.
- Ownership: Codex, autor/harness/integrador. Escopo: transporte, hooks de startup, projeto Xcode, drivers e artefatos native-*.md. Verifier só escreve relatório. Ambientes, caches, dados e simulador exclusivos em .build.
- Próximo passo: executar T5, payload/revogação entre processo iOS e cliente oficial isolado; T4 mantém a qualificação das extensões pendente. T6 exige ambas. Publicação somente pelo fluxo validado, com classificação e digest exato. Nenhum PASS nominal substitui sensor ou prova ausente.
- Limites do recorte: convites/admissão, UI, APNs e distribuição não estão implementados ou liberados. DESIGN.md aprovado precede telas. Provas ausentes permanecem NOT RUN; dados/credenciais reais não pertencem ao público.
