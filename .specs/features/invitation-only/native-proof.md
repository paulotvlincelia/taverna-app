# Qualificação do transporte nativo

**Status:** execução local autorizada pelo proprietário em 2026-10-16 após revisão de entry-design.md; alternativa técnica A1 aprovada. Método TLC Spec Driven. Issue #15. Este recorte não implementa convites ou identidade visual.

## Problem Statement

A ponte TLS foi provada com adaptadores CLI. Precisamos provar que o transporte nativo do iOS preserva SMP/XFTP reais, autorização e TLS interno, sem publicar um onboarding que apenas esconda acesso.

## Goals

- Qualificar adaptador Swift com SOCKS autenticado por processo e duas rotas exatas.
- Provar app e extensões em ambiente fictício; distinguir compilação, execução e protocolo real.

## Out of Scope

Convites, emissão de certificados de produção, grupos, UI personalizada, VPS, DNS, APNs real, assinatura em aparelho e distribuição. Os 34 requisitos da spec canônica permanecem Pending até suas provas completas.

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Arquitetura | A1, SOCKS local sobre TLS externo | Preservar núcleo fixado | y, proprietário aprovou o desenho |
| Ambiente | Simulador exclusivo, relays fictícios Docker, somente portas de gateway em loopback | Permitir prova nativa sem produção nem exposição LAN | y, integração isolada aprovada |
| Certificados | PKCS#12 fictício de dispositivo, CA exclusiva da rodada; nenhum Keychain pessoal | Testar a primitiva TLS nativa antes do serviço de admissão | n, escolha reversível de fixture |
| Extensões | Provar o processo efetivo quando possível; ausência de execução não conta como PASS | Build/compartilhamento de biblioteca não demonstram lifecycle | n, obrigação preservada |

**Open questions:** none; hipóteses de viabilidade são gates, não capacidades prontas.

## User Stories

### P1: transporte autorizado

**User Story:** Como implementador, quero demonstrar o caminho nativo antes de construir o resgate de convites.

**Acceptance Criteria**:
1. WHEN um cliente local negociar SOCKS THEN o adaptador SHALL exigir a credencial aleatória da própria execução antes de abrir transporte externo. (`NP-01`)
2. IF o host ou porta não estiverem nas duas rotas exatas THEN o adaptador SHALL negar o CONNECT antes de DNS ou conexão externa. (`NP-02`)
3. WHEN a credencial de dispositivo ativa abrir transporte THEN o adaptador SHALL validar a confiança da ponte e preservar a validação TLS interna do relay. (`NP-03`)
4. IF faltar credencial, TLS confiável ou transporte disponível THEN o caminho nativo SHALL falhar sem conexão direta ou relay público alternativo. (`NP-04`)
5. WHEN dois clientes qualificados trocarem dados THEN a prova SHALL comparar a mensagem SMP recebida e os bytes do arquivo XFTP com os valores enviados. (`NP-05`)
6. WHEN houver revogação ou indisponibilidade de autorização THEN a prova SHALL demonstrar bloqueio de novas conexões e fechamento de fluxos abertos em até 60 segundos, incluindo arquivo em andamento. (`NP-06`)
7. WHEN o núcleo iniciar ou retomar no app, Share Extension ou NSE THEN cada processo SHALL aplicar o transporte autorizado antes de permitir operações de rede. (`NP-07`)
8. The relatório SHALL identificar SHA, comandos, processos efetivamente executados, contenção, origem das bibliotecas, resultados e limitações, mantendo qualquer prova ausente em NOT RUN ou BLOCKED. (`NP-08`)

**Independent Test:** rodada nova com chave/CA/estado e simulador próprios; controle ativo real, sentinela e testes negativos; Verifier independente e sensor de autorização no commit final.

## Edge Cases

Frames SOCKS fragmentados ou inválidos; versão/método não suportado; credencial vazia/incorreta/de outro processo; host inválido, IPv4/IPv6 não autorizados e porta divergente; timeout de negociação; cancelamento; limite de conexões; TLS não confiável; relay com fingerprint errado; suspensão/reconexão; arquivo grande revogado a meio. A negociação não pode acumular bytes sem limite. A fixture anterior sem portas publicadas mantém seus próprios critérios; esta rodada admite somente publicação explícita em 127.0.0.1 para alcançar a ponte pelo simulador.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| NP-01 | Transporte autorizado | Execute | Pending |
| NP-02 | Transporte autorizado | Execute | Pending |
| NP-03 | Transporte autorizado | Execute | Pending |
| NP-04 | Transporte autorizado | Execute | Pending |
| NP-05 | Transporte autorizado | Execute | Pending |
| NP-06 | Transporte autorizado | Execute | Pending |
| NP-07 | Transporte autorizado | Execute | Pending |
| NP-08 | Transporte autorizado | Execute | Pending |

## Success Criteria

Oito critérios com evidência por processo e protocolo, CI e Verifier aprovados; nenhuma inferência de sucesso a partir de eco, compilação ou fixture CLI. Se uma limitação do ambiente impedir NP-07, preservar os resultados e reportar o bloqueio antes de avançar para admissão.
