# Diferenças e lacunas antes da implementação

Data: 2026-10-16. Base inspecionada: fork stable 9bfd78275a6f354ce3d18aaa7f2d47b48ba71756, derivado do upstream 479548ee53ffb73db73841e77acbeee5a78dbbd5. Pesquisa somente leitura. Não houve teste de autorização em serviços reais nesta fase.

## O que justifica a Taverna

| Aspecto | Base SimpleX | Resultado Taverna proposto | Situação |
| --- | --- | --- | --- |
| Convites | Já existem conexões individuais por link/QR e grupos | Convite autoriza associação à instância, emitido somente pelo proprietário | Entrada na instância não implementada |
| Servidores | Configuração de servidores próprios já disponível | Configuração automática, destinos qualificados e ausência de fallback público | Perímetro não comprovado |
| Grupos | APIs e papéis para administração de membros | Proprietário controla criação e associação aos grupos da instância | Enforcement além da interface não comprovado |
| Conversas individuais | Conexões e aceite já fazem parte da base | Conversas entre convidados ativos, com aceite mútuo | Política de associação não implementada |
| Retirada | Excluir um endereço de contato não encerra conexões já existentes | Revogação da associação com efeito nos serviços | Requer qualificação técnica própria |
| Identidade | Marca e interface upstream, com licenças específicas | Marca Taverna documentada em DESIGN.md e assets próprios/licenciados | Documento visual e substituições pendentes |
| Núcleo | Mensagens, mídia e criptografia existentes | Preservar a base e limitar divergências mantidas no fork | Build de base comprovado; produto próprio pendente |

Essas diferenças são propostas de produto. Servidores próprios e um fork não comprovam maior segurança por si. A operação de admissão introduz metadados de associação visíveis ao administrador; não anunciar ausência de cadastro administrativo ou anonimato equivalente ao modelo upstream sem qualificação.

## Evidências da base

O [guia oficial de conexões](https://simplex.chat/docs/guide/making-connections.html) explica o uso único de convites e distingue conexão estabelecida de endereço apagado. Também descreve o risco de outra pessoa usar o link antes do destinatário. Por isso o convite da instância e a retirada de membro precisam de ciclo próprio.

O [guia SMP no fonte fixado](https://github.com/simplex-chat/simplex-chat/blob/479548ee53ffb73db73841e77acbeee5a78dbbd5/docs/SERVER.md) descreve create_password como controle de criação de filas. O [guia XFTP fixado](https://github.com/simplex-chat/simplex-chat/blob/479548ee53ffb73db73841e77acbeee5a78dbbd5/docs/XFTP-SERVER.md) descreve autenticação de upload. A conclusão de engenharia é que esses dois mecanismos, sozinhos, não demonstram revogação individual de todas as operações em filas, arquivos e sessões já existentes.

Pontos de inspeção no fork, sem mudanças nesta fase:

- docs/SERVER.md:718–727; docs/XFTP-SERVER.md:340–354: escopo da autenticação documentada.
- src/Simplex/Chat/Operators/Presets.hs:49–106: conjuntos de servidores e dependência de resolução de links curtos.
- apps/ios/SimpleXChat/APITypes.swift:267: configuração de fallback SMP herdada.
- apps/ios/Shared/Model/SimpleXAPI.swift:1035, 1983, 2017 e 2078: conexão e APIs de membros/links de grupo.
- cabal.project:21–24: SimpleXMQ externo fixado em efaad8e73436d60f5052f07dda6b71151ad5039b; qualificar esse código e sua compatibilidade com os daemons adotados antes de escolher autorização.

## Gate técnico seguinte

Após aprovação da spec, comparar 2–3 abordagens de autorização, considerando recursos upstream, camada adicional por associação/dispositivo e extensão mínima dos serviços se necessária. Ainda não existe arquitetura escolhida. Não embutir senha global em um app público e tratá-la como segredo.

O experimento usa fixtures e serviços isolados. Deve distinguir criação de filas, envio, recebimento, upload, download e sessões abertas. Deve avaliar consumo único atômico, repetição do mesmo dispositivo, revogação, estado após reinício e bloqueio de membros sem depender dos botões da interface.

Para grupos, definir como a autorização do proprietário é comprovada além da UI e dos clientes cooperativos. Um cliente pode formar conversas fora da Taverna; isso não autoriza um grupo dentro da instância. Se a base não sustentar o requisito de grupos fechados sem alterar substancialmente o protocolo, o resultado é BLOCKED e uma decisão explícita de escopo/manutenção, não um PASS por esconder a criação de grupos.

O teste de destinos precisa incluir bootstrap, filas de recepção de pares, links curtos, presets, proxy SMP, importações, extensões e configuração editável. Configurar apenas os servidores locais de um cliente não demonstra por onde passam as operações com outros pares.

Apple APNs e distribuição permanecem dependências externas. A infraestrutura administrada pelo proprietário inclui os relays de mensagens/arquivos e a futura qualificação de notificações; não prometer que todo processo de rede do iOS pertence à Taverna.

## Limites da pesquisa

A leitura demonstra superfícies existentes e lacunas de prova; não demonstra que a arquitetura desejada seja impossível ou já suportada. Não foram feitos deploy, auditoria criptográfica, testes de carga ou coleta operacional nova. Topologia administrativa, custódia, custo e estado real de produção pertencem ao repositório privado. Context7 não está disponível nesta sessão; fontes primárias e código fixado foram usados.
