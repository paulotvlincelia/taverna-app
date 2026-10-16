# Taverna por convite: especificação da próxima fase

Data: 2026-10-16. **Status: especificação aprovada pelo proprietário em 2026-10-16; prova técnica autorizada, produto ainda não implementado.**
Issue canônica: [#7](https://github.com/paulotvlincelia/taverna-app/issues/7).
Método: TLC Spec Driven 3.3.0, escopo complexo por envolver app, autorização, relays, estado e distribuição. A especificação define obrigações; o design técnico e as tarefas serão produzidos após sua aprovação.

## Problem Statement

O primeiro build comprova a base iOS derivada do SimpleX. A interface e o modelo de uso continuam herdados: ainda não comprovamos entrada exclusiva na Taverna, configuração fechada dos servidores nem grupos administrados somente pelo proprietário. Precisamos definir essas diferenças antes de ampliar o fork.

## Goals

- Especificar entrada individual, conversas e grupos com critérios verificáveis.
- Comprovar a viabilidade do controle de acesso nos serviços antes da personalização extensa.
- Orientar as entregas de identidade, servidores próprios e piloto sem confundir intenção com capacidade entregue.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Android, desktop e chamadas | Entregas posteriores; áudio aqui significa gravação enviada como mensagem. |
| Integração com bots e serviços externos | Exige especificação e autorização próprias. |
| Criptografia ou protocolo próprios | Reutilizar o núcleo aberto e revisar qualquer adaptação necessária de autorização em entrega específica. |
| Apagar remotamente cópias recebidas | O administrador não controla cópias, exportações ou capturas nos aparelhos. |
| Transferir automaticamente o convite pela instalação | O usuário instala e reabre o link original. |
| Deploy, DNS, credenciais Apple e gastos nesta especificação | Exigem entregas e autorizações operacionais correspondentes. |
| Produzir a identidade visual completa agora | Esta fase fixa o contrato do futuro DESIGN.md; cores, marca e telas terão revisão própria. |
| Impedir comunicação externa ou software independente nos aparelhos | A autoridade da Taverna se limita aos seus serviços e grupos; não controla o dispositivo do convidado. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Emissor de entrada | Somente o proprietário | Canal de pessoas escolhidas pelo proprietário | y, direção do produto |
| Aceite do convite | Uso único, sem aprovação posterior | Escolha explícita do proprietário nesta discussão | y |
| Administração de grupos | Somente o proprietário cria grupos e escolhe membros | Escolha explícita nesta discussão | y |
| Conversas individuais | Entre convidados ativos com aceite mútuo | Escolha explícita nesta discussão | y |
| Documento de identidade | DESIGN.md canônico na raiz na fase de identidade | Pedido explícito do proprietário | y |
| Convite repassado | O primeiro dispositivo que confirmar pode entrar; não há prova automática da identidade civil | Consequência do convite suficiente, sem nova aprovação; compartilhar por canal escolhido e verificar a pessoa por fora quando necessário | y, plano aprovado em 2026-10-16 |
| Validade do convite | 72 horas; igualdade com a data de expiração já é inválida | Limitar exposição sem obrigar uso imediato | y, plano aprovado em 2026-10-16 |
| Dispositivos | Um iPhone ativo por convidado no piloto; substituição exige nova autorização do proprietário | Delimitar credenciais, perda e revogação no primeiro piloto | y, plano aprovado em 2026-10-16 |
| Capacidade | 20 convidados ativos, além do proprietário | Preservar piloto de até 20 convidados | y, plano aprovado em 2026-10-16 |
| Retirada de membro | Bloquear novas operações em até 60 segundos, inclusive em sessões abertas; preservar histórico local | Retirada precisa ter efeito nos serviços; solução ainda depende de prova técnica | y, plano aprovado em 2026-10-16 |
| Indisponibilidade da autorização | Negar operações que não possam verificar associação ativa | Evitar que falha de um serviço abra acesso | y, plano aprovado em 2026-10-16 |
| Privacidade administrativa | Proprietário vê associações e estados, sem acesso administrativo ao texto das conversas | Administração de entrada exige metadados; conteúdo mantém criptografia ponta a ponta | y, plano aprovado em 2026-10-16 |
| Notificações | Prévia genérica por padrão, sem texto da mensagem | Proposta de privacidade a detalhar na entrega de identidade/push | y, plano aprovado em 2026-10-16 |
| Limites de entrada | URL de convite até 8192 bytes; cinco falhas de resgate por minuto por origem, sexta tentativa aguarda 60 segundos | Limitar entrada e abuso; validar efeitos de NAT e sinal de origem no design | y, plano aprovado em 2026-10-16 |
| Emissão segura | Token aleatório com pelo menos 256 bits; nenhum segredo global embutido no app ou no fonte | Fonte público e binário distribuído não são custódia de segredo compartilhado | y, plano aprovado em 2026-10-16 |
| Visual | Português do Brasil, temas claro/escuro e suporte aos ajustes de acessibilidade do iOS | Público inicial e padrões do dispositivo; direção artística ainda aberta | y, plano aprovado em 2026-10-16 |

**Open questions:** none — o proprietário aprovou o plano e seus pressupostos em 2026-10-16 e autorizou a prova isolada. Viabilidade e arquitetura permanecem não comprovadas; eventual revisão dos critérios exige decisão explícita.

## User Stories

Todos os blocos abaixo são P1 para o piloto completo. Podem ser entregues e provados separadamente em ambientes fictícios; aprovar a especificação não significa que todo o piloto será implementado em um único PR.

### P1: Entrada individual

**User Story**: Como proprietário, quero convidar pessoas escolhidas para que somente elas obtenham acesso à instância.

**Acceptance Criteria**:
1. WHEN o proprietário autenticado emitir um convite THEN a Taverna SHALL produzir um convite individual com uma utilização e validade de 72 horas. (`INV-01`)
2. WHEN um convite válido for confirmado pelo convidado THEN a Taverna SHALL ativar uma única associação de dispositivo sem exigir aprovação posterior do proprietário. (`INV-02`)
3. IF dois dispositivos resgatarem simultaneamente o mesmo convite THEN a Taverna SHALL ativar exatamente um deles. (`INV-03`)
4. WHEN o mesmo dispositivo repetir o resgate após perder a resposta THEN a Taverna SHALL retornar a mesma associação sem consumir outra vaga. (`INV-04`)
5. IF o convite estiver expirado, cancelado, adulterado ou já usado por outro dispositivo THEN a Taverna SHALL recusar a ativação com estado visível de convite inválido. (`INV-05`)
6. WHEN um navegador ou serviço de prévia abrir o endereço por GET THEN a Taverna SHALL preservar o convite sem consumi-lo. (`INV-06`)
7. WHEN o convidado instalar o app e reabrir o link original THEN a Taverna SHALL permitir confirmar o convite no app instalado. (`INV-07`)
8. IF o limite de 20 convidados ativos tiver sido atingido THEN a Taverna SHALL recusar a ativação do convidado seguinte sem consumir o convite. (`INV-08`)
9. The Taverna SHALL dispensar telefone e e-mail como identificadores obrigatórios de entrada. (`INV-09`)

**Independent Test**: Em ambiente fictício, emitir, pré-visualizar, resgatar, repetir e disputar o mesmo convite em dois dispositivos; conferir associações e vagas.

### P1: Associação e retirada

**User Story**: Como proprietário, quero retirar o acesso de um membro sem confundir essa ação com apagar seu histórico.

**Acceptance Criteria**:
1. WHILE o dispositivo não tiver uma associação ativa a Taverna SHALL recusar novas operações autenticadas de mensagens, arquivos e administração da instância. (`MEM-01`)
2. WHEN o proprietário revogar uma associação THEN a Taverna SHALL impedir em até 60 segundos novas operações de envio e recebimento desse membro nos serviços da instância, incluindo sessões já abertas. (`MEM-02`)
3. WHILE o serviço de autorização estiver indisponível a Taverna SHALL recusar operações que não consigam verificar uma associação ativa. (`MEM-03`)
4. WHEN a revogação for exibida ao proprietário THEN a Taverna SHALL informar que cópias já recebidas continuam nos dispositivos dos participantes. (`MEM-04`)
5. IF um cliente modificado tentar usar uma credencial revogada THEN os serviços da Taverna SHALL rejeitar a operação mesmo sem a interface oficial. (`MEM-05`)
6. WHEN o proprietário consultar os membros THEN a Taverna SHALL mostrar o estado ativo ou revogado e a data da alteração sem expor conteúdo das conversas. (`MEM-06`)

**Independent Test**: Usar associações fictícias para abrir sessões, revogar uma delas e tentar operações novas e em sessões existentes com um cliente de prova que ignore a interface.

### P1: Grupos e conversas

**User Story**: Como convidado, quero conversar com os outros participantes; como proprietário, quero controlar os grupos e seus membros.

**Acceptance Criteria**:
1. WHEN o proprietário solicitar a criação de um grupo THEN a Taverna SHALL permitir criar o grupo da instância. (`CHAT-01`)
2. IF um convidado tentar criar um grupo por interface ou chamada direta THEN a Taverna SHALL rejeitar a criação do grupo da instância. (`CHAT-02`)
3. IF um convidado tentar alterar a associação ou papel de outro membro ou emitir convite de grupo THEN a Taverna SHALL rejeitar a alteração de membros do grupo da instância. (`CHAT-03`)
4. WHEN um convidado ativo aceitar uma solicitação individual de outro convidado ativo THEN a Taverna SHALL habilitar a conversa individual entre eles. (`CHAT-04`)
5. WHILE uma solicitação individual não tiver aceite a Taverna SHALL impedir a entrega de mensagens de conversa dessa solicitação. (`CHAT-05`)
6. WHEN um participante sair de um grupo THEN a Taverna SHALL registrar sua saída sem conceder a ele permissão de readmissão. (`CHAT-06`)

**Independent Test**: Com proprietário e dois convidados fictícios, criar um grupo, tentar criação e inclusão sem permissão e aceitar ou rejeitar uma conversa individual.

### P1: Servidores próprios

**User Story**: Como convidado, quero entrar e conversar sem configurar servidores manualmente e sem usar relays públicos como alternativa oculta.

**Acceptance Criteria**:
1. WHEN uma associação for ativada THEN a Taverna SHALL configurar automaticamente os destinos SMP e XFTP qualificados da instância. (`NET-01`)
2. IF um contato, grupo, link curto, importação ou configuração indicar um destino SMP ou XFTP fora da lista autorizada THEN a Taverna SHALL recusar a operação antes de abrir conexão com esse destino. (`NET-02`)
3. IF os servidores autorizados estiverem indisponíveis THEN a Taverna SHALL manter a operação pendente ou recusada sem recorrer a servidores públicos. (`NET-03`)
4. The Taverna SHALL validar a autenticidade da configuração da instância antes de utilizá-la. (`NET-04`)
5. The Taverna SHALL preservar a criptografia ponta a ponta do SimpleX para o conteúdo das conversas. (`NET-05`)
6. The Taverna SHALL documentar Apple APNs e o canal de distribuição como dependências externas distintas dos relays de mensagens e arquivos. (`NET-06`)

**Independent Test**: Usar servidores fictícios autorizados e um destino sentinela proibido; comprovar mensagens/arquivos entre dois clientes, falha dos autorizados e zero conexão à sentinela.

### P1: Identidade visual documentada

**User Story**: Como proprietário, quero uma identidade Taverna coerente e reproduzível por qualquer agente.

**Acceptance Criteria**:
1. WHEN a fase de identidade for submetida à aprovação THEN o repositório SHALL conter um DESIGN.md na raiz cobrindo todos os itens do contrato de identidade abaixo. (`BRAND-01`)
2. WHEN uma tela Taverna for implementada THEN sua revisão SHALL identificar os tokens, componentes e estados correspondentes no DESIGN.md aprovado. (`BRAND-02`)
3. IF um asset não tiver origem e licença compatíveis registradas THEN a entrega de identidade SHALL bloquear seu uso em distribuição customizada. (`BRAND-03`)

**Independent Test**: Revisar o DESIGN.md contra o contrato abaixo e rastrear três telas representativas até tokens, estados e assets licenciados.

### P1: Provas antes do piloto

**User Story**: Como proprietário, quero distinguir demonstração local de uma versão adequada ao uso privado.

**Acceptance Criteria**:
1. WHEN a implementação desta fase for declarada concluída THEN o Verifier independente SHALL apresentar evidência de cada critério no último commit de implementação e detectar falhas de autorização e de fallback injetadas em ambiente isolado. (`PROOF-01`)
2. WHEN a versão for considerada apta ao piloto THEN a validação SHALL comprovar mensagens, áudio gravado, foto e arquivo entre dois iPhones com identidades e servidores próprios qualificados. (`PROOF-02`)
3. WHEN notificações próprias forem declaradas prontas THEN a validação SHALL comprovar push em aparelho com o app em segundo plano usando identidade e capabilities próprias. (`PROOF-03`)
4. The Taverna SHALL manter o piloto bloqueado enquanto distribuição, assets, recuperação, capacidade e custo não tiverem evidências aprovadas nas respectivas entregas. (`PROOF-04`)

**Independent Test**: Revisar evidências por commit, executar testes negativos e provas em aparelhos; manter cada gate sem prova em BLOCKED ou NOT RUN.

## Contrato do DESIGN.md

O arquivo será produzido na fase de identidade, antes das telas personalizadas. O documento técnico da feature, `design.md`, descreve arquitetura; o `DESIGN.md` da raiz será a autoridade visual. A identidade ainda não foi criada ou aprovada.

| Área | Conteúdo obrigatório e prova de completude |
| --- | --- |
| Marca | Conceito Taverna, público, personalidade, tom de voz, usos do nome e limites das afirmações de privacidade. Referência a local reservado e encontro por convite, sem prometer anonimato absoluto. |
| Símbolo e assinatura | Logo, ícone iOS, variantes, área de proteção, tamanhos mínimos, fundos permitidos, usos incorretos, arquivos mestres e licença. |
| Cores | Paleta e tokens semânticos para temas claro/escuro, texto, superfícies, ações, erro, aviso, sucesso, foco e estados desabilitados; valores exatos e contraste medido, com mínimos propostos de 4,5:1 para texto normal e 3:1 para texto grande e controles. |
| Tipografia e medidas | Famílias e licenças, hierarquia, tamanhos, pesos, entrelinhas, Dynamic Type, espaçamento, grid, raios, bordas, sombras, áreas seguras e alvos de toque de pelo menos 44 × 44 pontos. |
| Ícones, ilustrações e movimento | Origem, estilo, regras de consistência e alternativas para Reduce Motion. |
| Componentes | Botões, campos, navegação, listas, avatares, cartões de convite, mensagens, anexos, áudio, diálogos e alertas; estados normal, pressionado, foco, carregando, desabilitado, vazio e erro, quando aplicáveis. |
| Fluxos e telas | Entrada com/sem app instalado; convite válido, expirado, usado e cancelado; entrada ativa; conversa pendente/aceita; lista, conversa, grupos, mídia, configurações, falta de rede e acesso revogado; diferenças entre proprietário e convidado. |
| Privacidade e acessibilidade | Prévias de notificações, ocultação de dados sensíveis, VoiceOver, ordem de foco, contraste, ampliação e informação que não dependa só de cor. |
| Aplicação iOS | App, Share Extension, Notification Service Extension, ícones, tela inicial e materiais de distribuição; nomes e assets herdados a substituir. |
| Implementação e verificação | Mapeamento de tokens para SwiftUI/asset catalogs, versões, formatos exportáveis, inventário com origem/licença e exemplos visuais de referência. Revisão de três telas nos dois temas e em texto ampliado. |

## Edge Cases

Convite repassado pode ser usado por quem o receber primeiro. Prévia do link não pode consumi-lo. Resgate e revogação concorrentes precisam de ordem consistente e estado durável. Depois de revogado, o membro pode continuar lendo dados já recebidos. Conversas fora da Taverna e cópias locais ficam fora do perímetro.

Remover uma opção de menu não comprova autorização. Uma senha SMP/XFTP compartilhada também não comprova revogação individual. O gate técnico deve testar credenciais antigas, sessões abertas, chamada direta, importação e clientes que ignorem a interface. Se o protocolo/servidor adotado não sustentar um critério, registrar BLOCKED e propor revisão explícita; nunca trocar o requisito silenciosamente por uma restrição visual.

## Dimensions Sweep

| Dimensão | Cobertura |
| --- | --- |
| Entrada e limites | INV-01, INV-05, INV-08 e pressupostos de tamanho/tentativas/entropia |
| Falhas e estado parcial | INV-04, MEM-03, NET-03; persistência da ativação precisa anteceder resposta de sucesso |
| Idempotência e repetição | INV-03, INV-04, INV-06 |
| Autorização e limites | MEM-01 a MEM-05, CHAT-02/03, pressuposto de tentativas |
| Concorrência e ordem | INV-03, MEM-02; revogação vence operações iniciadas após sua efetivação |
| Ciclo e expiração | INV-01/05, MEM-02/04; política de retenção dos relays é gate operacional separado |
| Observabilidade | MEM-06; diagnóstico sem tokens, convites completos, conteúdo ou identidade civil obrigatória |
| Dependências externas | MEM-03, NET-03/06, PROOF-03/04 |
| Integridade de transições | emitido → resgatado, expirado ou cancelado; ativo → revogado; sem reativação por reutilização do convite |

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| INV-01 | Entrada individual | Specify | Pending |
| INV-02 | Entrada individual | Specify | Pending |
| INV-03 | Entrada individual | Specify | Pending |
| INV-04 | Entrada individual | Specify | Pending |
| INV-05 | Entrada individual | Specify | Pending |
| INV-06 | Entrada individual | Specify | Pending |
| INV-07 | Entrada individual | Specify | Pending |
| INV-08 | Entrada individual | Specify | Pending |
| INV-09 | Entrada individual | Specify | Pending |
| MEM-01 | Associação e retirada | Specify | Pending |
| MEM-02 | Associação e retirada | Specify | Pending |
| MEM-03 | Associação e retirada | Specify | Pending |
| MEM-04 | Associação e retirada | Specify | Pending |
| MEM-05 | Associação e retirada | Specify | Pending |
| MEM-06 | Associação e retirada | Specify | Pending |
| CHAT-01 | Grupos e conversas | Specify | Pending |
| CHAT-02 | Grupos e conversas | Specify | Pending |
| CHAT-03 | Grupos e conversas | Specify | Pending |
| CHAT-04 | Grupos e conversas | Specify | Pending |
| CHAT-05 | Grupos e conversas | Specify | Pending |
| CHAT-06 | Grupos e conversas | Specify | Pending |
| NET-01 | Servidores próprios | Specify | Pending |
| NET-02 | Servidores próprios | Specify | Pending |
| NET-03 | Servidores próprios | Specify | Pending |
| NET-04 | Servidores próprios | Specify | Pending |
| NET-05 | Servidores próprios | Specify | Pending |
| NET-06 | Servidores próprios | Specify | Pending |
| BRAND-01 | Identidade visual documentada | Specify | Pending |
| BRAND-02 | Identidade visual documentada | Specify | Pending |
| BRAND-03 | Identidade visual documentada | Specify | Pending |
| PROOF-01 | Provas antes do piloto | Specify | Pending |
| PROOF-02 | Provas antes do piloto | Specify | Pending |
| PROOF-03 | Provas antes do piloto | Specify | Pending |
| PROOF-04 | Provas antes do piloto | Specify | Pending |

**Coverage:** 34 critérios, zero implementados nesta fase de planejamento. Cada critério receberá tarefas e evidências após aprovação e design.

## Sequência proposta de entregas

| Etapa | Resultado | Gate para avançar |
| --- | --- | --- |
| 1. Fechar produto | Aprovar esta spec, contexto e pressupostos | Revisão humana dos comportamentos e limites |
| 2. Qualificar autorização e compatibilidade | Experimento isolado: associação individual, uso único, retirada, sessões existentes, permissões de grupos e destinos autorizados | Provas positivas e negativas; comparar 2–3 alternativas técnicas e custo de manutenção; nenhum requisito reduzido sem aprovação |
| 3. Definir identidade | Inventário de assets/dependências e DESIGN.md com referência visual aprovada | Todos os itens do contrato de identidade e licenças revisados; viabilidade do perímetro já conhecida |
| 4. Construir uma fatia completa | Convidar → instalar/reabrir → entrar → conversar nos servidores de teste → revogar; interface Taverna guiada pelo DESIGN.md | Testes derivados da spec, duas sessões isoladas quando aplicável, CI e Verifier independente no commit final |
| 5. Qualificar operação e distribuição | Servidores próprios, identidade Apple, push, retenção, recuperação e custo | Entregas operacionais privadas e provas em aparelhos, sem publicar custódia/topologia administrativa |
| 6. Piloto | Proprietário e dois convidados primeiro; ampliar até o limite somente após prova | Aceite do proprietário e evidências de uso real; TestFlight e seu vencimento documentados |

Não há cronograma fechado antes do experimento técnico. As issues #5 (assets) e #8 (identidade/push) permanecem canônicas; este plano não cria cópias do backlog. Deploy não faz parte da aprovação documental.

## Success Criteria

O convidado entra com um convite, sem configurar servidores, e conversa somente nas condições aprovadas. O proprietário controla entrada e grupos e consegue retirar novas operações de um membro dentro do prazo especificado. As provas distinguem controles de interface, autorização dos serviços, histórico local e dependências externas. A identidade visual tem um DESIGN.md utilizável por Codex e Claude.

## Sources

- [Contexto e decisões do proprietário](context.md).
- [Diferenças, evidências e lacunas técnicas](research.md).
- [Primeiro build comprovado](../ios-first-build/validation.md).
- [Roadmap e issues canônicas](../../../docs/taverna/roadmap.md).
