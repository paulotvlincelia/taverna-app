# Escopo da documentação pública

Data: 2026-10-16. Método: TLC Spec Driven 3.3.0, entrega documental delimitada. Autorização direta do proprietário para corrigir a documentação publicada. Design e tarefas formais dispensados: um único resultado documental, sem mudança de arquitetura ou código.

## Problem Statement

A documentação pública precisa conter somente o contexto necessário ao desenvolvimento do app. Referências a ambientes externos à sessão não ajudam a reproduzir o build ou implementar as funcionalidades.

## Goals

- Limitar o contexto publicado ao app e às provas técnicas reproduzíveis.
- Preservar critérios de produto, código, testes, licenças e resultados observados.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Mudanças no app, infraestrutura e distribuição | Correção exclusivamente documental. |
| Reescrita do histórico Git | Exige avaliação de impacto separada. |
| Controles permanentes de publicação | Entrega posterior com plano próprio. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Escopo autorizado | Generalizar referências a ambientes externos na documentação atual | Pedido direto do proprietário | y |
| Critérios existentes | Preservar todos os requisitos funcionais e provas do app | Correção de contexto não muda produto | y |

**Open questions:** none — escopo definido pelo pedido de correção documental.

## User Stories

### P1: Documentação restrita ao desenvolvimento

**User Story**: Como mantenedor, quero documentação pública suficiente para desenvolver e verificar o app.

**Acceptance Criteria**:
1. WHEN a correção documental for publicada THEN a documentação SHALL descrever ambientes externos somente por sua função genérica. (`DOC-01`)
2. WHEN a documentação for corrigida THEN os critérios funcionais e resultados técnicos existentes SHALL permanecer preservados. (`DOC-02`)
3. WHEN a entrega for verificada THEN os checks de CONTRIBUTING.md SHALL passar sem alterações de código ou asserções existentes. (`DOC-03`)

**Independent Test**: Revisar o diff documental, conferir o escopo publicado e executar a suíte e o checker da fundação.

## Edge Cases

Referências técnicas genéricas a isolamento, rede e ferramentas de build continuam necessárias. A correção da árvore atual não apaga revisões anteriores.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| DOC-01 | Documentação | Execute | Verified |
| DOC-02 | Documentação | Execute | Verified |
| DOC-03 | Documentação | Execute | Verified |

## Execution Plan

1. Generalizar o contexto da documentação atual e registrar esta entrega. Arquivos: AGENTS.md, .specs/STATE.md, context.md e execution.md de ios-first-build; context.md, spec.md e plan-validation.md de invitation-only; esta spec e execution.md. Verificar diff documental, suíte Python, Foundation, compileall e diff check. Commit: docs: limit documentation to app development context.

## Success Criteria

Documentação atual revisada, critérios técnicos preservados, checks aprovados e Verifier independente no commit de implementação. Aprovação desta correção não comprova expurgo de histórico.
