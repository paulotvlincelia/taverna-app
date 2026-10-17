# Design

## Source of truth

**Status: Draft. Versão 0.1.0. Data: 2026-10-17. Aprovação visual do proprietário: pendente.**

Este documento propõe a identidade da Taverna. A aprovação autoriza a direção visual; implementação, acessibilidade em execução, licenças de cada asset e distribuição têm gates próprios. O app ainda usa a interface herdada. Nenhuma tela desta proposta está implementada.

Escopo: app iOS, entrada por convite, conversas, grupos, gestão pelo proprietário, compartilhamento, notificações e materiais de distribuição. A arquitetura e a autorização continuam definidas na [spec do produto](.specs/features/invitation-only/spec.md) e no [desenho técnico](.specs/features/invitation-only/entry-design.md).

Evidências revisadas: [decisões do proprietário](.specs/features/invitation-only/context.md), [README](README.md), [inventário/gate de assets](docs/taverna/assets.md), [política de distribuição](docs/taverna/asset-policy.json), `apps/ios/Shared/Theme/Theme.swift`, `apps/ios/SimpleXChat/Theme/ThemeTypes.swift`, catálogos de assets e pontos de entrada do app/Share Extension/NSE. Há temas e componentes upstream reutilizáveis como código; sua presença não aprova imagens ou aparência licenciadas separadamente. Não há logo, ícone final ou telas Taverna aprovados.

Referências propostas: [prancha de três telas](docs/taverna/design/reference.svg), [tokens sRGB](docs/taverna/design/tokens.json) e [medição de contraste](docs/taverna/design/contrast.json). A prancha usa conteúdo fictício e representa composição, hierarquia e cor. Não é captura do app nem prova de comportamento. Este arquivo é a autoridade; referências acompanham sua versão.

## Brand

Taverna é um lugar reservado para conversas entre pessoas convidadas. O público discute negócios, carreira, startups e temas sensíveis. A inspiração em encontros discretos aparece na sensação de acolhimento, na porta e nos materiais quentes.

Personalidade: discreta, próxima, adulta e cuidadosa. O nome aparece como **Taverna**, com inicial maiúscula. A assinatura explicativa é “Conversas privadas, por convite.” Usar essa frase quando o contexto não deixar claro que se trata de mensagens.

Sinais de confiança vêm de estados concretos: quem convidou, qual ação será confirmada, se a mensagem está pendente, quem administra o grupo e o que uma revogação faz. Explicar a criptografia de ponta a ponta e os limites de cópias locais onde isso afeta uma decisão. Não afirmar anonimato absoluto, impossibilidade de captura de tela, histórico apagado remotamente ou independência completa de fornecedores. Push e distribuição têm dependências próprias.

Evitar decoração de pub, barris, cerveja, pergaminhos, bandeiras históricas, cadeados decorativos em cada tela, estética hacker, dourado brilhante, gradientes promocionais e urgência artificial. A referência histórica orienta a atmosfera; não transforma o mensageiro em cenário temático.

### Símbolo, assinatura e ícone

Direção proposta: um vão de porta em arco, desenhado com poucos traços, com um pequeno ponto de luz no interior. A forma precisa continuar reconhecível em uma cor. Não reutilizar o símbolo SimpleX, sua marca, papagaio, imagens, wallpapers ou assets comerciais.

A [prancha](docs/taverna/design/reference.svg) contém um estudo original do símbolo. Ele é provisório. O pacote final deverá conter SVG mestre com caminhos, PDF vetorial para os catálogos, PNGs de referência e exportação adequada ao Xcode/Icon Composer adotado. Registrar autor, licença, versão e SHA-256 por arquivo no inventário. Não embutir arquivos de fontes Apple nos exports públicos.

| Regra | Proposta para finalizar após aprovação |
| --- | --- |
| Assinaturas | Nome + símbolo horizontal; símbolo isolado para ícone; versões monocromáticas positiva e negativa |
| Área de proteção | Pelo menos 1/4 da largura do símbolo em todos os lados |
| Mínimos | Símbolo 24 pt no app; assinatura completa 112 pt de largura. Abaixo disso, usar só o símbolo e rótulo acessível |
| Fundos | `surface`/`canvas` com símbolo `primary`; bloco `primary` com símbolo `onPrimary`. Sem fundo fotográfico |
| Ícone iOS | Mestre quadrado 1024 × 1024; sem texto pequeno; elemento central com margem de 18%; sem cantos arredondados incorporados. Qualificar variantes claro/escuro/tintado e camadas no SDK de distribuição |
| Usos incorretos | Esticar, rotacionar, redesenhar traço, aplicar sombra/glow ou colocar selo de segurança; símbolo não substitui estado de acesso |
| Gate | Ícone final e variantes precisam de revisão em tamanhos reais e origem/licença antes de entrar no catálogo do app |

## Product goals

O convidado entende o convite, confirma a entrada e conversa sem configurar servidores. O proprietário controla convites, grupos e membros. Uma conversa individual entre convidados depende de aceite mútuo.

A primeira versão prioriza leitura, composição de mensagem, áudio gravado, fotos, arquivos e grupos pequenos. Android, desktop, chamadas, feeds públicos, descoberta aberta e integrações externas permanecem fora desta fase.

Sinais de sucesso para a revisão futura: a pessoa encontra e entende a ação principal sem orientação; distingue mensagem pendente de entregue; localiza informações do grupo; entende erro de convite e revogação; conclui os mesmos fluxos com VoiceOver e texto ampliado. Esses resultados exigem testes com a interface implementada.

## Personas and jobs

| Pessoa | Necessidade | Contexto de uso |
| --- | --- | --- |
| Proprietário | Convidar uma pessoa, criar grupos, escolher membros e retirar acesso | Gestão ocasional; confirmação antes de ações irreversíveis |
| Convidado | Confirmar convite, responder, compartilhar mídia e aceitar conversas | iPhone, sessões curtas, uma mão, rede instável |
| Participante com recursos assistivos | Ler, ouvir e operar os mesmos fluxos | VoiceOver, Dynamic Type, alto contraste e Reduce Motion |

## Information architecture

A primeira camada tem **Conversas** e **Ajustes**. Usar navegação e barras nativas; não acrescentar uma seção social ou um painel de métricas. A busca fica em Conversas. Solicitações de conversa são uma seção identificada dessa lista.

| Superfície | Conteúdo e ação principal | Papel |
| --- | --- | --- |
| Entrada sem convite | Nome, explicação curta e “Abrir convite”; orientação para pedir um convite ao proprietário | Qualquer pessoa sem associação |
| Convite no navegador | Instrução de instalação e de reabrir o link original. GET/HEAD não consomem convite; token não aparece na tela ou em analytics | Destinatário |
| Confirmar convite no app | Instância autenticada, nome de quem convida somente se comprovado pela resposta, validade e “Confirmar entrada” | Destinatário |
| Perfil local | Nome de exibição; avatar opcional; nenhuma exigência de telefone/e-mail | Membro ativo |
| Conversas | Solicitações, grupos e conversas aceitas; última atividade; busca | Membro ativo |
| Conversa | Nome, membros/estado, histórico, compositor, anexos e áudio | Participante |
| Informações do grupo | Nome, descrição, membros, administrador; ação “Sair do grupo” | Participante; gestão só do proprietário |
| Gestão da Taverna | Convites pendentes, membros e datas/estados. Criar grupo e escolher membros | Somente proprietário |
| Ajustes | Perfil local, aparência, notificações, privacidade, armazenamento e informações do app | Membro ativo |
| Acesso retirado | Estado explícito, limite da retirada, dados locais e orientação para pedir novo convite | Associação revogada |

Ocultar ações sem permissão reduz ruído. A autorização precisa continuar sendo aplicada nos serviços e no núcleo, inclusive com cliente alterado. Não incluir botões que aparentem implementar uma permissão ainda ausente.

## Design principles

A leitura ocupa o centro da tela. Cor acentua ação e estado, sem competir com o conteúdo. Espaço vazio é aceitável quando ainda não há conversas; não preencher com publicidade ou sugestões de contatos.

Manter padrões nativos onde ajudam reconhecimento: voltar, sheets, menus, alertas, seletor de foto, gravação e compartilhamento. A cor da marca não deve modificar a ordem ou o significado dessas ações.

Confirmar o resgate do convite e a revogação. Nunca consumir convite apenas ao abrir link. Mostrar progresso real, permitir sair de uma tela carregando e conservar o que a pessoa digitou em falhas recuperáveis.

## Visual language

### Cor e tokens

Direção: verde profundo, papel quente e um acento de latão fosco. O tema escuro usa fundo verde quase preto e texto quente. Acento é reservado para pequenos sinais de identidade; a ação principal usa `primary`.

Valores em [tokens.json](docs/taverna/design/tokens.json), sRGB opaco. O prefixo de implementação será `Taverna/`; nomes abaixo são semânticos, idênticos nos dois temas. Nenhum componente escolhe um hexadecimal próprio.

| Token | Claro | Escuro |
| --- | --- | --- |
| `canvas` | `#F7F3EB` | `#151C18` |
| `surface` | `#FFFCF6` | `#1F2923` |
| `surfaceMuted` | `#ECE6DA` | `#2A362E` |
| `text` | `#252924` | `#F4EFE5` |
| `textSecondary` | `#5E625B` | `#B7C0B8` |
| `border` | `#7B8077` | `#77897C` |
| `primary` | `#294D3E` | `#BDD4B7` |
| `primaryPressed` | `#203E31` | `#ABC89F` |
| `onPrimary` | `#FFFCF6` | `#15251C` |
| `accent` | `#785127` | `#D2AD73` |
| `danger` | `#A53232` | `#FFAAA2` |
| `success` | `#2E6348` | `#9ED0A9` |
| `warning` | `#77550D` | `#E7C77A` |
| `focus` | `#8C5C21` | `#E9C28A` |
| `outgoing` | `#E0EBDD` | `#304B3A` |
| `disabledText` | `#5E625B` | `#B7C0B8` |

`surfaceMuted` serve para agrupamento e desabilitados; mensagens enviadas usam `outgoing`, recebidas usam `surface`. Links usam `primary`, com sublinhado quando estiverem no corpo do texto. Texto de alerta usa o token de estado sobre `surface` ou `canvas`, sempre acompanhado de rótulo e ícone. Não aplicar texto pequeno em `onPrimary` sobre `accent`.

O script [measure_contrast.py](docs/taverna/design/measure_contrast.py) recalcula os pares declarados:

```bash
python3.12 docs/taverna/design/measure_contrast.py
```

Os 46 pares declarados devem atender a 4,5:1 para texto normal ou 3:1 para bordas/foco. O [relatório](docs/taverna/design/contrast.json) registra valores medidos sem arredondar a comparação ao limiar. Esses números cobrem cores opacas especificadas; transparência, imagens, materiais do sistema, antialiasing e a interface renderizada precisam de revisão própria. Não chamar isso de certificação de acessibilidade do app.

### Tipografia, grid e medidas

Usar fontes do sistema por SwiftUI `.font(.body)` e estilos relativos. A assinatura pode usar o desenho arredondado do sistema; os textos usam o desenho padrão. Sem download de fonte nem redistribuição dos arquivos San Francisco. As famílias são acessadas pelas APIs Apple, sob os termos da plataforma; a documentação web usa `system-ui` e os exports vetoriais finais precisam de autorização ou desenho de letras original.

| Token de tipo | Estilo base iOS | Tamanho/peso de referência | Entrelinha mínima de referência |
| --- | --- | --- | --- |
| `display` | largeTitle | 34 pt, bold | 41 pt |
| `title` | title2 | 22 pt, semibold | 28 pt |
| `section` | headline | 17 pt, semibold | 24 pt |
| `body` | body | 17 pt, regular | 24 pt |
| `secondary` | subheadline | 15 pt, regular | 21 pt |
| `caption` | footnote | 13 pt, regular | 18 pt |

Os valores são bases, não alturas fixas. Respeitar Dynamic Type em toda a escala de acessibilidade. Datas e durações podem usar números monoespaçados; mensagens não usam fonte monoespaçada por padrão. Nome de participante e conteúdo podem quebrar linha. Não reduzir fonte automaticamente para fazer texto caber.

Espaçamento em pontos: `space.1=4`, `.2=8`, `.3=12`, `.4=16`, `.5=24`, `.6=32`, `.7=48`. Margem lateral padrão 20; alinhamento do texto de lista e do título coincidente. Respeitar safe areas e teclado. Bolhas têm padding 12 × 16 e largura máxima de 84% na escala padrão; em texto ampliado podem ocupar toda a largura disponível.

Raios: `radius.control=12`, `radius.card=20`, `radius.bubble=18`, `radius.avatar=metade do lado`. Bordas de campo 1 pt; foco 2 pt com afastamento de 2 pt. Separador decorativo pode usar `surfaceMuted`; limites essenciais de controles usam `border`. Nenhuma informação depende de sombra. Sem sombras em bolhas; sheets e menus usam elevação/material nativos, com alternativa opaca quando Reduce Transparency estiver ativo.

### Ícones, imagens e movimento

Usar SF Symbols por API, com peso alinhado ao texto, verificando disponibilidade e termos de cada símbolo no SDK suportado. Rótulo acessível descreve a ação: “Anexar arquivo”, “Gravar áudio”, “Informações do grupo”. Nunca exportar o catálogo inteiro de símbolos para o repositório. Alternativa original deve ter traço de 1,5–2 pt em grade 24 pt e licença registrada.

Avatares são foto opcional ou iniciais em círculo; cor não representa papel, acesso ou identidade verificada. Sem wallpapers na primeira identidade. Ilustrações futuras precisam de origem/licença por arquivo. Transições curtas de 120–200 ms; reduzir/retirar deslocamento e pulsação com Reduce Motion. Sem confete, animação contínua no onboarding ou som automático. Áudio só inicia por ação da pessoa.

## Components

| Componente | Aparência e variantes | Estados e regras |
| --- | --- | --- |
| Botão | Primário preenchido `primary/onPrimary`; secundário com borda; ação destrutiva `danger` | Normal, pressionado (`primaryPressed`), foco, carregando com rótulo estável, desabilitado (`surfaceMuted/disabledText`). Não alterar largura durante progresso |
| Campo | Label persistente, entrada `text`, ajuda `textSecondary`, borda `border` | Vazio, preenchido, foco, inválido com explicação, desabilitado. Placeholder não é label |
| Barra e navegação | Padrões nativos, título e ações rotuladas | Seleção identificável além de cor; voltar preserva rascunho |
| Linha de conversa | Avatar 44 pt, nome, resumo, hora e contador | Não lida inclui “N mensagens não lidas”; pendente/offline têm texto; a prévia pode ser ocultada |
| Avatar | Foto ou iniciais, 40/44/56 pt conforme contexto | Sem foto é um estado normal; não usar imagem upstream como fallback |
| Cartão de convite | `surface`, nome da instância, validade, consequência e CTA | Validando, válido, resgatando, inválido, limite atingido, indisponível; nunca mostrar token |
| Mensagem | Texto selecionável, origem pelo alinhamento/label, hora e estado | Pendente, enviada, entregue, erro com retry. Não marcar “lida” sem recibo real. Não confundir edição com nova entrega |
| Anexo | Nome, tipo/tamanho, progresso determinado quando disponível | Baixando, disponível, cancelado, falhou; toque abre prévia; ação de cancelar rotulada |
| Áudio gravado | Play/pause, duração e progresso acessíveis | Gravando com tempo e “Cancelar”/“Enviar”; permissão negada; interrompido; falha. Forma de onda é decorativa |
| Diálogo e alerta | Nativo, título descritivo, consequência, ação/cancelar | Revogação e saída de grupo exigem confirmação; não esconder erro em toast transitório |
| Banner de estado | `surface`, ícone e texto de estado | Offline, reconectando, envio pendente. Retirado é tela/estado persistente, sem ciclo de reconexão enganoso |
| Gestão | Listas simples de convites e membros, estado/data | Só proprietário; sem gráficos, marketing ou conteúdo de mensagens |

Alvos de toque de pelo menos 44 × 44 pt, inclusive ícones com desenho menor. Botões principais com altura mínima 52 pt, crescendo com texto. Acessibilidade e foco precisam funcionar também em estados vazios, de erro e desabilitados.

## Accessibility

Meta: atender aos critérios WCAG 2.2 AA aplicáveis como referência de contraste, percepção e interação, somados aos padrões iOS. A conformidade depende da implementação e da prova em aparelho; esta proposta não a atesta.

VoiceOver segue título → explicação/estado → conteúdo → ação principal → ação secundária. Ao abrir sheet, foco vai ao título; ao fechar, retorna ao acionador. Uma mensagem é um elemento com remetente, conteúdo, hora e estado; ações ficam no menu acessível. Não ler waveform como uma sequência de valores. Progressos anunciam mudanças relevantes, sem um anúncio por percentual.

Usar rótulos, traits, ações e valores reais. Ícones decorativos ficam ocultos do leitor. Grupos de ações preservam ordem de leitura. Compatibilidade com Voice Control, Switch Control e teclado externo, sem exigir gesto de swipe ou pressão prolongada para a única forma de executar uma ação.

Revisar os dois temas com aumento de contraste, Reduce Transparency e texto no maior tamanho de acessibilidade. Cor e som não podem ser os únicos sinais de falha, recebimento ou seleção. Rascunhos e textos importantes permanecem legíveis e operáveis com VoiceOver. Não copiar conteúdo sensível para labels de diagnósticos, notificações genéricas ou relatórios de teste.

## Responsive behavior

iPhone em portrait e landscape, menor largura suportada de 320 pt úteis e safe areas variáveis. Não fixar altura das telas nem truncar botões em texto ampliado. Em largura compacta, uma coluna; a lista vira conversa por navegação. Com Dynamic Type de acessibilidade, ações secundárias migram para linhas próprias e células crescem.

A prancha usa 390 pt como referência de composição; não determina todos os tamanhos. iPad não é meta deste piloto; se o target atual permitir execução, manter uma coluna legível centralizada até a qualificação específica. Nenhum suporte a iPad é declarado a partir desta proposta. Hover é opcional; nunca o único meio de revelar ação. O teclado não cobre o compositor nem os botões de confirmação.

## Interaction states

| Situação | Texto e comportamento propostos |
| --- | --- |
| Sem app instalado | “Instale a Taverna e abra este convite novamente.” Não prometer transferência automática pela instalação |
| Sem convite | “A entrada é por convite. Peça um ao proprietário da Taverna.” |
| Validando | “Verificando convite…”; não consumir no GET; falha deixa a pessoa tentar novamente |
| Convite válido | “Você recebeu um convite para entrar.” + validade + “Confirmar entrada”. A confirmação é explícita |
| Expirado, cancelado, adulterado ou usado por outra chave | “Este convite não está disponível. Peça um novo convite.” Mesma mensagem para os estados inválidos; não revelar quem o usou |
| Capacidade atingida | “A Taverna atingiu o limite de participantes. Tente mais tarde ou fale com o proprietário.” Convite e vaga não são consumidos |
| Resposta perdida | “Não foi possível confirmar a resposta. Tentar novamente.” Reutilizar a chave local e recuperar a associação; não emitir um novo convite automaticamente |
| Ativação confirmada | “Sua entrada foi confirmada.” Abrir perfil local/conversas somente com associação/configuração verificadas |
| Sem conversas | “Suas conversas vão aparecer aqui.” Ações permitidas e solicitações recebidas ficam visíveis |
| Conversa individual pendente | “Aguardando aceite.” Destinatário vê “Aceitar”/“Recusar”; conteúdo de conversa não é entregue antes do aceite |
| Grupo vazio | Proprietário: “Escolha os membros deste grupo.” Convidado: estado informativo, sem ação de convidar/criar grupo |
| Offline/servidor indisponível | “Sem conexão com a Taverna. As mensagens continuam pendentes.” Nenhum fallback público |
| Envio falhou | Estado junto à mensagem, “Tentar novamente” e “Apagar rascunho” separados. Sem confirmar entrega antecipadamente |
| Revogação pelo proprietário | “Retirar acesso deste membro?” + “Isso impede novas operações. Mensagens já recebidas continuam nos dispositivos.” Ação “Retirar acesso” |
| Acesso retirado | “Seu acesso foi retirado.” Explicar limite das cópias locais. Sem prometer apagar histórico alheio ou oferecer reativação pelo convite usado |
| Compartilhar no iOS | Selecionar conversa autorizada; mostrar erro se não houver acesso ou rede. Cancelar não envia. Não iniciar rede antes da associação/política verificadas |

A interface de gestão informa que o convite pode ser repassado e usado primeiro por outra pessoa. A ausência de uma segunda aprovação é uma decisão do produto. Não mostrar selo “Identidade verificada” apenas porque alguém possuiu o link.

## Content voice

PT-BR como idioma editorial da identidade; manter estrutura de localização para outros idiomas. Falar com “você”, usar verbos concretos e nomear a consequência. Exemplos: “Confirmar entrada”, “Criar grupo”, “Escolher membros”, “Aceitar conversa”, “Retirar acesso”, “Tentar novamente”.

“Convite” abre acesso à instância; “solicitação de conversa” pede aceite para conversar entre membros; “membro” tem associação ativa; “proprietário” administra. Não misturar essas permissões. Nas telas de usuário, evitar termos como SMP, XFTP, mTLS, CSR, relay, framework ou gate. Informações técnicas pertencem a uma seção própria de diagnóstico sem segredos.

Prévia de notificação proposta: “Nova atividade na Taverna”, sem remetente, grupo ou conteúdo por padrão. Prévia detalhada exige opção explícita e prova técnica própria. Não alegar push pronto nem registrar payload em telemetria como consequência do design. Ao alternar apps, propor cobertura opaca do conteúdo; provar seu comportamento em ciclo real antes de declarar proteção.

## Implementation constraints

Reutilizar SwiftUI e componentes UIKit necessários ao sistema. A extensão de compartilhamento segue a mesma linguagem, sem duplicar recursos pesados; NSE não recebe uma interface própria. O ícone e nome de distribuição dependem da identidade Apple e de seus gates. Não alterar bundle IDs, grupos de Keychain, entitlements ou criptografia como efeito da aprovação visual.

Tokens de cor terão implementação única em `TavernaTheme`/catálogo semântico, consumida por app e extensões; o caminho final será definido nas tarefas de implementação. Mapeamento: `canvas` → fundo raiz; `surface` → células/cards; `text`/`textSecondary` → tipos; `primary`/`onPrimary` → ação principal; `danger`/`warning`/`success` → feedback; `outgoing` → mensagem enviada. Usar variações Any/Dark, espaço sRGB e estilos de texto relativos; nenhum tom hardcoded nas views. O JSON deste diretório é referência de design, não um carregador de tema instalado.

A base tem um sistema de temas upstream. A implementação deverá adaptar o ponto de aplicação existente, sem manter dois temas concorrentes ou habilitar temas/importações que eliminem legibilidade/estados. Definir migração de preferências e revisar o efeito nos três targets antes de substituir o tema.

### Assets e distribuição

O [gate de assets](docs/taverna/asset-policy.json) continua **BLOCKED**, com lista de assets de distribuição aprovados vazia. Referências originais desta proposta são documentação, sob CC BY 4.0 com atribuição a Taverna; não são assets finais aprovados para o app. Código mantém sua licença. As fontes Apple são usadas por APIs do sistema; assets upstream têm revisão individual e licença própria.

| Superfície herdada | Ação necessária na implementação |
| --- | --- |
| AppIcon/ícones/nomes do app, Share e notificações | Substituir por exportações Taverna aprovadas, preservando licenças e provedores; testar tamanhos e localização |
| `apps/ios/Shared/Assets.xcassets` e `SimpleXAssets.xcassets` | Inventariar cada imagem/ilustração/wallpaper/símbolo usado; substituir ou comprovar permissão |
| Onboarding, links, telas de ajuda e exemplos | Ajustar nome/copy e remover materiais de promoção upstream conforme o escopo; preservar atribuição em informações legais |
| Ícones de dependências e mídia em docs/distribuição | Registrar origem, licença, uso e substituição; não inferir licença da AGPL do código |
| Fotos/avatares dos participantes | Dados locais do usuário, nunca fixtures ou assets da marca; exemplos usam somente iniciais fictícias |

Não habilitar downloads automáticos de imagens, analytics, fontes ou CDN na identidade. Referências visuais são locais e não acessam rede. Pacote final precisa de mestres editáveis, exports, inventário com hashes/licenças e fontes correspondentes à versão distribuída.

### Verificação e passagem para implementação

Antes de implementar: proprietário aprova direção, símbolo e navegação; o recorte de transporte exigido passa; tarefas apontam para seções/tokens deste documento. Aprovar a proposta não aprova distribuição ou produção.

Revisão visual obrigatória após implementação: **Confirmar convite, Conversas e Conversa**, nos temas claro/escuro, escala padrão e maior escala de acessibilidade, pelo menos 12 combinações. Incluir offline, convite inválido e acesso retirado; verificar também os papéis proprietário/convidado e a Share Extension. A prancha representa somente escala padrão.

Provas: capturas de dados fictícios com versão/SHA/target registrados; contraste dos pares renderizados; VoiceOver, foco, toque e texto ampliado em iPhone; zero tokens/convites/conteúdo real em logs; nenhuma aprovação de critério baseada apenas em screenshot. Testes de autorização continuam verificando efeitos reais. CI e Verifier independente no último commit precedem integração. BRAND-02 e distribuição permanecem pendentes até sua implementação/prova.

## Open questions

- [ ] Proprietário: aprovar ou ajustar a direção verde/papel/latão e o estudo de porta; afeta os assets finais, sem alterar o nome Taverna.
- [ ] Proprietário: aprovar a navegação Conversas/Ajustes e a gestão restrita ao proprietário; não altera as permissões já aprovadas.
- [ ] Implementação: finalizar símbolo e variantes do ícone no SDK adotado, com origem/licença e testes em tamanhos reais. O estudo atual não é ícone final.

## Fontes e rastreabilidade

O contrato completo está em [BRAND-01..03 e Contrato do DESIGN.md](.specs/features/invitation-only/spec.md#contrato-do-designmd). Marca/símbolo correspondem a Brand; cores/tipografia/medidas a Visual language; componentes a Components; fluxos a Information architecture/Interaction states; privacidade a Content voice/Accessibility; iOS, assets e provas a Implementation constraints. A presença dessas seções não marca BRAND-02/03 como implementados.

Referências de plataforma consultadas: [Apple Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Apple App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) e [W3C, contraste mínimo](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Valores de produto que forem mais exigentes prevalecem. As regras deste documento são propostas da Taverna, sem alegar endosso Apple ou SimpleX.
