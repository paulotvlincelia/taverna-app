# Primeiro build iOS da Taverna

Status: aprovado pelo proprietário em 2026-10-16. Qualificação de bibliotecas iniciada; build ainda não executado.

Issue canônica: [taverna-app #6](https://github.com/paulotvlincelia/taverna-app/issues/6), vinculada ao épico E2. Método: TLC Spec Driven 3.3.0, escopo Large, pois há dependências entre bibliotecas nativas, SwiftPM, Xcode, simulador e evidências. Esta proposta preserva a fundação integrada e os critérios da issue.

## Problem Statement

O fork tem o fonte iOS e uma fundação de desenvolvimento validada, mas ainda não há prova de que o app compila e executa neste MacBook. As bibliotecas nativas estão ausentes; a compatibilidade entre seus artefatos, o commit do fonte e o SDK instalado ainda precisa ser demonstrada.

O resultado desta entrega será um build Debug para simulador arm64, ligado ao núcleo real SimpleX, com teste observável da abertura do app e repetição independente. O nome do produto continua Taverna; esta primeira prova usa a interface herdada do fork antes da entrega de identidade própria.

## Goals

- Compilar app, framework e extensões do scheme iOS a partir de um commit identificado.
- Executar um teste de interface que confirme a navegação inicial em simulador exclusivo da sessão.
- Permitir que outra sessão repita o procedimento sem reaproveitar produtos ou caches graváveis da primeira.
- Publicar futuramente uma prova textual sanitizada que distinga build do app, origem do núcleo e assinatura em aparelho.

## Out of Scope

| Item | Motivo e destino |
| --- | --- |
| Branding completo, ícone e substituição geral de assets | Inventário na [issue #5](https://github.com/paulotvlincelia/taverna-app/issues/5); identidade/capabilities na [issue #8](https://github.com/paulotvlincelia/taverna-app/issues/8). |
| Distribuir binário, App Store, TestFlight, APNs e instalar nos iPhones reais | Exigem identidade, permissões, assinatura e gates próprios; não são provados pelo simulador. |
| Implementar convites, salas ou conversas reais | Especificação de convites na [issue #7](https://github.com/paulotvlincelia/taverna-app/issues/7). |
| Comprovar criptografia ou operação ponta a ponta | A navegação inicial não testa os protocolos nem a entrega de mensagens. |
| Alterar servidores, DNS, VPN, outros Macs ou serviços de agentes | Entrega estritamente local do app, sem dependência operacional desses recursos. |
| Reconstruir obrigatoriamente o núcleo Haskell do fonte | Rota alternativa condicionada à qualificação das bibliotecas; não confundir com compilar o app Swift. |
| Atualizar o upstream, todas as dependências ou reestruturar o produto | Preservar a base atual; qualquer incompatibilidade exige correção delimitada e registrada. |

## Assumptions & Open Questions

Os defaults abaixo foram aprovados pelo proprietário em 2026-10-16. Essa aprovação não comprova fatos técnicos nem autoriza implicitamente uma instalação administrativa fora dos limites do plano.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Aparência da primeira prova | Interface herdada; chamar o resultado de build de base do fork Taverna. | Isolar viabilidade de compilação da entrega de identidade. | y |
| Origem do núcleo | Tentar bibliotecas oficiais pré-compiladas somente com vínculo verificável ao fonte e hashes fixados. | Reduzir preparação de toolchains sem afirmar reconstrução do núcleo. Nenhum artefato já foi qualificado. | y |
| Falha na qualificação das bibliotecas | Registrar BLOCKED e detalhar a rota de compilação do núcleo antes de adotá-la. | Evitar binários sem origem ou troca silenciosa do escopo. | y |
| Destino principal | SDK iOS Simulator 27.1, runtime iOS 27.0, iPhone 17 arm64. | Esse runtime está disponível e lista o modelo; o runtime 27.1 instalado lista somente iPhone Duo. Compatibilidade de execução ainda não comprovada. | y |
| Credenciais Apple | Tentar Debug para simulador sem provisionamento de conta Apple. | Evitar vincular o primeiro build a certificados ou identidades de distribuição; validar os ajustes efetivos de todos os targets. | y |
| Teste mínimo de interface | Em inglês, confirmar Get started e navegar até Your profile, sem enviar o formulário. | Resultado visível e objetivo sem criar identidade, aceitar termos ou iniciar conversa. | y |
| Execução sem serviços reais | Provar contenção de IP remoto no processo do app antes do main; serviços do iOS ficam fora dela. | O app herdado contém configuração de servidores reais; não presumir ausência de tráfego só por parar no onboarding. | y |
| Limites por tentativa | Download de cada arquivo: até 5 GiB e 30 minutos; build: 90 minutos; sessão de testes: 15 minutos. | Limites de interrupção para processos presos; não são promessa de desempenho. Mudança desses limites exige registro. | y |
| Evidências visuais | Manter screenshots e xcresult apenas no estado local ignorado; relatório público textual. | Assets e conteúdo dos bundles ainda precisam de revisão para publicação. | y |
| Local dos ambientes | Clone principal e worktrees sob a raiz Projects já definida pelo proprietário. | Preservar organização existente; nenhum novo checkout em Downloads ou Desktop. | y |

**Open questions:** none — defaults aprovados; origem/ABI das bibliotecas, seleção do simulador isolado e contenção de rede continuam sendo provas técnicas. A exceção necessária para a rota Nix foi autorizada separadamente pelo proprietário em 2026-10-16; a instalação foi concluída e validada, com o avanço registrado em execution.md.

## User Stories

### P1: Entradas e ambiente verificáveis

**User Story**: Como mantenedor, quero identificar as entradas e preparar uma sessão isolada para que o resultado do build tenha origem conhecida.

**Acceptance Criteria**:
1. WHEN uma biblioteca nativa for qualificada THEN o manifesto SHALL registrar URL imutável, commit do fonte correspondente, evidência desse vínculo, licença, SHA-256 do arquivo recebido e hashes das bibliotecas efetivamente usadas (IOS-01).
2. IF a origem, o vínculo com o fonte, o hash ou a compatibilidade das bibliotecas não puderem ser comprovados THEN o preparo SHALL terminar com status BLOCKED e código diferente de zero (IOS-02).
3. WHEN as dependências SwiftPM forem resolvidas THEN a resolução SHALL preservar as sete revisões do Package.resolved da base, com qualquer alteração submetida a revisão explícita (IOS-03).
4. WHILE uma sessão de build estiver ativa o procedimento SHALL manter seus produtos, downloads, caches graváveis controlados pelo build, bancos, dados físicos do simulador e logs dentro do próprio worktree, permitindo somente os índices por UDID do SDK como aliases e a exceção Nix autorizada (IOS-04).
5. WHEN o destino de teste for escolhido THEN o preflight SHALL comprovar que o UDID selecionado pelo executor Xcode é exclusivo daquela sessão, registrado no índice padrão do SDK, e que seus dados e logs físicos pertencem ao worktree (IOS-05).
6. WHEN os ajustes de build forem preparados THEN o relatório SHALL registrar a configuração efetiva de assinatura de cada target sem autenticar conta Apple ou habilitar atualização de provisionamento (IOS-06).
7. IF um download ultrapassar os limites definidos ou contiver caminhos que escapem do destino de extração THEN o preparo SHALL rejeitar esse artefato com código diferente de zero (IOS-07).

**Independent Test**: Em worktree novo, executar a qualificação e o preflight sem compilar o app. Entradas válidas produzem um manifesto verificável; hash adulterado, origem desconhecida e destino alheio impedem avançar.

### P1: App compilado, aberto e repetido

**User Story**: Como proprietário, quero ver o aplicativo executando e uma segunda sessão reproduzindo a prova para saber que o fork é uma base utilizável para a próxima fase.

**Acceptance Criteria**:
1. WHEN a compilação Debug do scheme SimpleX (iOS) terminar com sucesso THEN a prova SHALL identificar os produtos gerados para app, framework SimpleXChat, Notification Service Extension e Share Extension (IOS-08).
2. WHEN esses produtos forem inspecionados THEN a prova SHALL confirmar a arquitetura arm64 e a plataforma iOS Simulator dos executáveis e do código nativo ligado ao app (IOS-09).
3. WHEN o teste iniciar o aplicativo THEN o processo do app SHALL comprovar, antes do main, contenção de IP remoto por tentativa externa negada e comunicação local permitida, sem alteração da VPN ou do firewall global do Mac; os serviços do sistema iOS ficam fora dessa contenção (IOS-10).
4. WHEN o aplicativo for lançado com dados novos THEN o teste SHALL confirmar que Get started está visível e habilitado em até 30 segundos (IOS-11).
5. WHEN o teste tocar Get started THEN o teste SHALL confirmar Your profile em até 30 segundos, encerrando a navegação antes de enviar o formulário (IOS-12).
6. WHEN a suíte iOS do scheme for executada THEN o relatório SHALL registrar todos os testes descobertos, executados, falhos e ignorados, sem remover testes ou asserções nem acrescentar skips para obter sucesso (IOS-13).
7. IF qualquer etapa obrigatória falhar, exceder seu limite, não executar seus testes ou não produzir seu artefato esperado THEN a execução SHALL terminar sem PASS, com código diferente de zero e identificação da etapa (IOS-14).
8. WHEN uma tentativa for retomada após falha THEN o procedimento SHALL preservar a evidência anterior em diretório de tentativa distinto sem apagar estado de outras sessões (IOS-15).
9. WHEN uma tentativa terminar THEN seu registro SHALL identificar commit e estado do fonte, manifesto de entradas, versões de Xcode/SDK/runtime, destino, comandos sanitizados, códigos de saída, hashes dos produtos e resultados dos testes (IOS-16).
10. WHEN outra sessão repetir a prova THEN o relatório SHALL comparar duas execuções bem-sucedidas do mesmo commit e manifesto em worktrees, caches e simuladores distintos (IOS-17).
11. WHEN a entrega for declarada concluída THEN um Verifier independente SHALL aprovar cada critério no último commit de implementação, incluindo testes de falhas injetadas e CI aprovada nesse commit (IOS-18).
12. WHEN o relatório consolidado for emitido THEN ele SHALL apresentar estados separados para build do app no simulador, núcleo reconstruído do fonte e assinatura/push em aparelho, com PASS restrito ao que foi comprovado (IOS-19).
13. WHILE as permissões de assets e distribuição estiverem pendentes o procedimento SHALL manter binários, screenshots e bundles de resultados fora dos arquivos publicados no repositório (IOS-20).

**Independent Test**: Com as entradas qualificadas, compilar e testar em dois worktrees novos. Cada execução precisa gerar produtos reais e confirmar a navegação. Um runner vazio ou uma saída textual BUILD SUCCEEDED sem os produtos não satisfazem a prova.

## Proposed Delivery Path

Esta sequência foi aprovada com a especificação e seu [contexto](context.md). A qualificação foi executada e o [Design](design.md) registra o bloqueio e a alternativa concreta antes de adotá-la.

1. **Qualificar a rota do núcleo.** Localizar artefatos oficiais vinculados ao fonte da base; verificar licença, hashes, arquitetura e ABI. Se não houver prova suficiente, apresentar a rota de compilação do núcleo, sem baixar uma versão latest como substituta.
2. **Provar o isolamento.** Demonstrar seleção do UDID exclusivo pelo executor e contenção de IP remoto no processo do app antes do main. A documentação de simctl --set, sozinha, não prova que xcodebuild usa aquele conjunto.
3. **Preparar entradas locais.** Fixar manifestos, resolver SwiftPM sem atualizar pins e preparar bibliotecas dentro do worktree. Adaptar somente os pontos necessários dos scripts herdados, que hoje usam Downloads e substituem diretórios.
4. **Compilar e testar.** Construir o scheme completo, inspecionar produtos, preservar a suíte existente e acrescentar o teste de navegação com asserções observáveis.
5. **Repetir e verificar.** Refazer em sessão limpa, executar CI dos checks automatizáveis e obter a revisão independente com falhas injetadas em cópias isoladas. Registrar os limites da prova no README/guia do build.

Não há promessa de duração antes da qualificação do núcleo. A segunda execução comprova repetibilidade funcional; não exige igualdade binária entre builds do Xcode.

## Edge Cases

| Situação | Resultado requerido |
| --- | --- |
| Biblioteca arm64 de macOS ou de iPhone físico | IOS-02 e IOS-09: arquitetura sozinha não comprova a plataforma. |
| Download oficial com hash local, mas sem vínculo verificável ao fonte | IOS-01 e IOS-02: recalcular SHA não substitui evidência de origem. |
| Pacote SwiftPM muda de revisão para resolver um erro | IOS-03: revisão explícita antes de adotar o novo conjunto. |
| Índice padrão aponta para dados alheios ou destino divergente | IOS-04 e IOS-05: bloquear; não usar o simulador de outra sessão nem substituir seus arquivos. |
| App precisa de entitlements para abrir no simulador | IOS-06 e IOS-14: registrar incompatibilidade; não consultar certificados ou credenciais como atalho. |
| Contenção de rede não funciona | IOS-10: não lançar o app; registrar BLOCKED com a prova que faltou. |
| xcodebuild termina com zero, mas não executa teste obrigatório | IOS-14: não emitir PASS. |
| Suíte herdada falha com o novo Xcode | IOS-13: investigar e registrar; não enfraquecer testes para fechar a entrega. |

## Implicit Requirement Dimensions

| Dimensão | Resolução neste escopo |
| --- | --- |
| Validação e limites de entrada | IOS-01, IOS-02, IOS-03, IOS-07; manifesto, hashes, revisões e extração confinada. |
| Falha e falha parcial | IOS-14, IOS-15; limite de tempo e evidência por tentativa. |
| Repetição e idempotência | IOS-15, IOS-17; nova tentativa isolada, sem produtos anteriores. |
| Autenticação e limites de chamadas | IOS-06, IOS-10; sem contas Apple ou chamadas a serviços reais. Rate limiting de produto: N/A, nenhuma API nova. |
| Concorrência e ordem | IOS-04, IOS-05; um executor por worktree/UDID, responsável de integração identificado. |
| Ciclo de vida e expiração | IOS-15, IOS-20; dados fictícios locais, inspeção antes do encerramento. TTL de mensagens: N/A, nenhuma conversa criada. |
| Observabilidade | IOS-16, IOS-19; registro reproduzível, resultados separados e sem credenciais. |
| Dependência externa indisponível | IOS-02, IOS-07, IOS-14; erro explícito, sem atualizar locks ou trocar fonte silenciosamente. |
| Integridade de transições | IOS-14, IOS-18; preparo → build → teste → repetição → verificação; fase sem prova impede conclusão. |

## Requirement Traceability

| Requirement ID | Story / critério | Tasks | Phase | Status |
| --- | --- | --- | --- | --- |
| IOS-01 | Entradas: proveniência | T1 | Tasks | In Tasks |
| IOS-02 | Entradas: rejeição | T1, T4 | Tasks | In Tasks |
| IOS-03 | Entradas: pins SwiftPM | T3 | Tasks | In Tasks |
| IOS-04 | Entradas: estado isolado | T2, T7, T5 | Execute | In Progress |
| IOS-05 | Entradas: destino Xcode | T2 | Execute | In Progress |
| IOS-06 | Entradas: assinatura | T3 | Tasks | In Tasks |
| IOS-07 | Entradas: download/extração | T1, T5 | Tasks | In Tasks |
| IOS-08 | App: produtos do scheme | T3 | Tasks | In Tasks |
| IOS-09 | App: plataforma/arquitetura | T1, T4 | Tasks | In Tasks |
| IOS-10 | App: rede isolada | T2 | Execute | In Progress |
| IOS-11 | App: abertura observável | T3 | Tasks | In Tasks |
| IOS-12 | App: navegação observável | T3 | Tasks | In Tasks |
| IOS-13 | App: suíte preservada | T3 | Tasks | In Tasks |
| IOS-14 | App: falha detectada | T4 | Tasks | In Tasks |
| IOS-15 | App: retomada | T2, T7, T5 | Execute | In Progress |
| IOS-16 | App: registro de prova | T1, T4, T5 | Tasks | In Tasks |
| IOS-17 | App: segunda execução | T6 | Tasks | In Tasks |
| IOS-18 | App: Verifier e CI | T6 | Tasks | In Tasks |
| IOS-19 | App: alcance do PASS | T1, T4, T5, T6 | Tasks | In Tasks |
| IOS-20 | App: publicação de evidências | T4, T5, T6 | Tasks | In Tasks |

Coverage: 20 requisitos mapeados às sete tarefas de tasks.md, sem requisitos sem destino. T1 em andamento; nenhum requisito verificado e nenhum build do app declarado.

## Success Criteria

O marco estará concluído quando as duas execuções passarem nos critérios IOS-01 a IOS-20 e o Verifier aprovar a entrega no commit validado pela CI. O relatório deve permitir seguir os comandos em um worktree novo e abrir o app no simulador sem recorrer a memória de chat.

O resultado esperado para a rota recomendada é: build do app no simulador PASS; núcleo pré-compilado com origem qualificada; reconstrução do núcleo do fonte NOT RUN; assinatura/APNs em aparelho NOT RUN; distribuição BLOCKED pelas entregas próprias. Uma falha real permanece FAIL; falta de pré-requisito permanece BLOCKED.

Estado factual e fontes: [readiness.md](readiness.md). Regras de trabalho: [AGENTS.md](../../../AGENTS.md) e [ambientes](../../../docs/taverna/environments.md).

Ajuste de IOS-04, IOS-05 e IOS-10 aprovado pelo proprietário em 2026-10-16 após revisão dos controles. Decisão canônica APP-004; não equivale a prova de execução da Taverna.
