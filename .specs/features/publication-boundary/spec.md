# Publicação e cobertura documental

Método: TLC Spec Driven. Execução autorizada pelo proprietário para completar os controles de publicação. Componente público delimitado de uma entrega coordenada.

## Problem Statement

O checker verificava somente a feature inicial. Specs novas e o handoff também precisam receber a mesma validação genérica.

## Goals

Cobrir documentos próprios novos automaticamente, preservando testes, código e licenças.

## Out of Scope

Política privada, credenciais e regras particulares do mantenedor não pertencem a este componente público.

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Conteúdo validado | Toda .specs, docs próprios, instruções e skills | Novas features devem herdar os checks | y |

**Open questions:** none — componente delimitado pelo plano autorizado.

## User Stories

### P1: Cobertura automática

**User Story**: Como mantenedor, quero verificar novas specs sem manter uma lista por feature.

**Acceptance Criteria**:
1. WHEN uma nova spec ou handoff contiver padrão genérico de acesso privado THEN o checker SHALL retornar erro. (`BND-01`)
2. WHEN um documento novo contiver link relativo ausente ou fora do repositório THEN o checker SHALL retornar erro. (`BND-02`)
3. IF um documento próprio for symlink THEN o checker SHALL rejeitá-lo sem ler conteúdo externo. (`BND-03`)

**Independent Test**: Criar uma feature fictícia e um handoff com padrões sintéticos; conferir erros exatos e manter os testes anteriores.

## Edge Cases

Novas pastas de features são incluídas automaticamente. Documentos upstream preservados continuam fora da superfície própria.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| BND-01 | Cobertura | Execute | Verified |
| BND-02 | Links | Execute | Verified |
| BND-03 | Symlinks | Execute | Verified |

## Success Criteria

Suíte existente preservada, novos casos aprovados, CI e verificação independente no commit final. Código do app e licenças preservados.
