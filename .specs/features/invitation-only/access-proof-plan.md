# Prova mínima da fronteira de acesso

Data: 2026-10-16. Escopo autorizado: experimentar a rota A mais simples e reaproveitar SimpleX, sem repetir o piloto histórico. Método TLC Spec Driven dimensionado para experimento delimitado; três passos atômicos, executados em sequência. Não é a implementação dos 34 requisitos do produto.

## Obrigações da prova

- WHEN uma credencial ativa usar a ponte THEN a prova SHALL demonstrar operação real com SMP e XFTP, preservando o protocolo interno (AP-01; recorte de NET-05).
- IF faltar credencial ou a associação não estiver ativa THEN a ponte SHALL impedir novo acesso ao backend fixado (AP-02; recorte de MEM-01/MEM-05).
- WHEN a associação for revogada THEN a ponte SHALL encerrar sessões existentes e impedir novas em até 60 segundos (AP-03; recorte de MEM-02).
- IF a política local de associações ficar indisponível ou inválida THEN a ponte SHALL fechar o acesso novo e existente em até 60 segundos (AP-04; recorte de MEM-03).
- The ponte SHALL encaminhar somente aos dois backends fixados, sem aceitar destino fornecido pelo cliente (AP-05; parte de NET-02/03).
- The experimento SHALL executar sem publicar portas e com redes internas, dados fictícios e estado gravável no worktree (AP-06; limites de ambiente).
- The relatório SHALL identificar hashes, versões, comandos e limites de cada prova e manter pendentes os critérios do app ainda não implementados (AP-07; PROOF-01).

## Execution Plan

1. Qualificar ambiente e fornecedores → arquivos: manifesto/receita do experimento → verificar hashes oficiais, versão/ajuda dos binários e isolamento Docker → commit de preparação.
2. Implementar uma ponte de teste com driver de integração → arquivos: tools/taverna/access_proof → verificar AP-01 a AP-06, mantendo os 70 testes existentes → commit do componente e seus testes.
3. Publicar os resultados delimitados → arquivos: relatório da prova e handoff → revisão independente no último commit e sensor em cópia isolada; CI antes de integração → commit documental e relatório independente.

## Test Coverage Matrix

Diretrizes: AGENTS.md e CONTRIBUTING.md; estilo unittest e checks Foundation existentes. A ponte é experimental e não deve ser anunciada como serviço pronto.

| Camada | Teste | Cobertura | Comando |
| --- | --- | --- | --- |
| Ponte TLS/lista de acesso | Integração local | Ativo, ausente, desconhecido, revogado, sessão aberta, política ausente/inválida, destinos fixados | Driver dentro das redes internas Docker |
| Protocolo real | Integração local | Controle positivo SMP/XFTP e negativa de fronteira sem modificar os daemons | CLI oficial contra os relays da fixture |
| Fundação/documentação | Regressão | Preservar asserções e licenças | python3.12 -m unittest discover -s tools/taverna/tests -q; checker Foundation |

## Gates e limites

Gate de preparação: hashes e executáveis oficiais identificados. Gate do componente: testes da prova, 70 regressões, compileall e git diff --check. Gate final: Verifier independente, falhas injetadas de autorização que os checks detectem e CI no commit final. Falha interrompe avanço; não modificar critérios para obter PASS.

Ficam pendentes: emissão/resgate de convites, configuração no app/Share Extension/NSE, proteção de grupos oficiais, observação de todos os destinos do iOS, aparelhos/APNs, deploy e operação. Nenhum controle echo ou mock satisfaz AP-01.
