# Fundação pública da Taverna

Plano aprovado em 2026-10-16. Método: TLC Spec Driven; entrega delimitada de contribuição, preflight e documentação. O código funcional upstream permanece preservado.

## Problem Statement

Preparar desenvolvimento independente do app iOS com proveniência/licenças, agentes intercambiáveis e ambientes isolados, sem apresentar o app como construído.

## Goals

Repositório público autossuficiente, CI sem segredos e preflight factual. Build iOS, identidade, convites e distribuição são entregas posteriores.

## Assumptions & Open Questions

| Assumption | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Fonte | Fork oficial stable fixado | Proveniência auditável | y |
| Execução | Git/gh/Python, worktree isolado | Harness intercambiável | y |
| Apple | Xcode/conta/assinatura são gates explícitos | Não aceitar contratos nem consultar segredos automaticamente | y |

**Open questions:** none para F0; capacidades/build pertencem a F1.

## User Stories

### P1: Preparar colaboração e ambiente sem prometer app disponível

**User Story**: Como contribuidor, quero instruções e checks públicos reproduzíveis para implementar as próximas entregas.

**Acceptance Criteria**

- PUB-01: WHEN o fork for publicado THEN SHALL preservar parent simplex-chat/simplex-chat, SHA base e licenças/atribuições.
- PUB-02: WHEN contribuidor iniciar THEN SHALL encontrar README factual, AGENTS comum, CLAUDE encaminhando e TLC com origem/licença.
- PUB-03: WHEN preflight executar THEN SHALL registrar ferramentas, SDK/simuladores/GHC exigido e gates BLOCKED/exit 2 para dependências ausentes, sem consultar segredos.
- PUB-04: WHILE sessões executarem THEN SHALL usar branch, worktree e estado gravável isolados; nenhum script usa Downloads compartilhado automaticamente.
- PUB-05: WHEN distribuição for solicitada THEN SHALL permanecer BLOCKED até inventário/permissões de assets e fonte correspondente ao binário comprovados.
- PUB-06: WHEN CI executar THEN SHALL testar a fundação sem segredos/publicação; falhas reais devem ser detectadas por testes e Verifier independente no último commit.
- PUB-07: WHEN o roadmap público for organizado THEN SHALL conter somente conteúdo genérico autossuficiente, com issues canônicas e gates de conclusão.

## Edge Cases

Ferramenta ausente, versão errada, erro/timeout de comando e dependência Apple não comprovada permanecem bloqueados. Worktree sujo não é removido. Issue pública em Project privado continua pública. Nenhuma release ou build é declarado pela fundação.

## Out of Scope

Alterar criptografia, produzir binário, habilitar APNs, distribuir ou alterar operação existente.

## Requirement Traceability

| Requirement ID | Task | Status |
| --- | --- | --- |
| PUB-01 | P1 | Verified |
| PUB-02 | P1 | Verified |
| PUB-03 | P2 | Verified |
| PUB-04 | P2 | Verified |
| PUB-05 | P1 | Verified |
| PUB-06 | P1, P2 | Verified |
| PUB-07 | P3 | Verified |
