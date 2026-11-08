# Handoff: InnerMesh iOS (DESIGN 0.5.2)

## Leia antes de qualquer ação

Este pacote é **referência de design para registro**. Ele não autoriza implementar telas, renomear nada nem trocar assets do app.

**O que fazer agora (única ação desta entrega):**

1. Registrar os arquivos na branch existente `codex/identity-design-draft`, conforme o mapa de destino abaixo.
2. Rodar `measure_contrast.py` e conferir que `contrast.json` bate com os tokens.
3. Abrir PR para revisão do anfitrião. Nada além disso.

**O que não fazer agora:**

- Não implementar telas, temas, tokens nem componentes no app.
- Não renomear código, caminhos (`docs/taverna/`, `tools/taverna/`, `apps/ios/SimpleXChat/Taverna/`), repositórios, Projects, bundle IDs, App Group, keychain group ou entitlements.
- Não substituir ícones, imagens ou nomes do app herdado: o gate de assets continua BLOCKED (GOVERNANCE.md).
- Não implementar vários círculos, seletor de círculo, perfil por círculo nem limite configurável.

**Quando a implementação da UI pode começar:** depois da fase 5 do plano de remediação (prova da NSE com o transporte), com aprovação do anfitrião sobre direção, símbolo e navegação, e uma spec TLC própria para cada fluxo, apontando para seções e tokens do DESIGN.md.

**Escopo da primeira versão implementada: um círculo.** As telas mostram o alvo com vários círculos. Na primeira versão:

| Elemento do design | Na primeira versão |
| --- | --- |
| Seletor de círculo e sheet “Seus círculos” | Não aparecem. O cabeçalho de Conversas começa no título |
| Ajustes → “Este círculo” e “App” | Mantidos como estão no design, com um único círculo |
| Perfil local | Um perfil, definido na entrada |
| Acesso retirado | Estado raiz, como no caso “único círculo” do design |
| Convite com círculo já existente | Não se aplica |
| Limite de membros | Valor fixo da spec atual: 20 convidados ativos além do anfitrião (21 pessoas no total), exibido como “N de 21 membros”, sem stepper |
| Share Extension | Sem etapa de escolha de círculo |

Vários círculos e limite configurável exigem uma spec nova antes de qualquer código: o app passa a manter várias identidades, certificados e pontes, a NSE precisa atender várias instâncias, e o modelo de operação muda quando outras pessoas são anfitriãs.

**Mapa de destino no repositório:**

| Arquivo do pacote | Destino |
| --- | --- |
| `DESIGN.md` | `DESIGN.md` (raiz, substitui o atual) |
| `GOVERNANCE.md` | `GOVERNANCE.md` (raiz) |
| `README.md` (este) | `docs/innermesh/design/HANDOFF.md` |
| `tokens.json`, `contrast.json`, `measure_contrast.py` | `docs/innermesh/design/` |
| `assets/` | `docs/innermesh/design/assets/` (referência; não entra nos catálogos do app) |
| `prototype/` | `docs/innermesh/design/prototype/` |
| `screenshots/` | `docs/innermesh/design/screenshots/` |

`docs/innermesh/design/` é um diretório novo e pode ser criado já. Os arquivos herdados citados no GOVERNANCE.md (`docs/innermesh/assets.md`, `docs/innermesh/asset-policy.json`) continuam em `docs/taverna/` até a fase 6; não mover agora.

**Pendências conhecidas do pacote:**

- O protótipo mostra o número de membros (“9 membros”) no cartão de convite. Isso não está especificado e revela o tamanho do círculo a quem ainda não entrou. Não implementar até decisão do anfitrião.

---

## Visão geral
InnerMesh é um mensageiro privado para iPhone, com entrada só por convite. Cada instância é um **círculo** criado por um **anfitrião** (`owner` no código). Como alvo de design, uma pessoa pode estar em vários círculos no mesmo app, sem mistura entre eles; a primeira versão implementada tem um único círculo (ver “Leia antes de qualquer ação”). Este pacote cobre identidade (símbolo, ícone, paleta, tipografia), as telas da primeira versão e seus estados.

## Sobre os arquivos
Os arquivos em `prototype/` são **referências de design feitas em HTML**: mostram aparência e comportamento, não são código de produção. A tarefa é **recriar o design em SwiftUI** (ou no ambiente que o repositório já usa), com componentes nativos (NavigationStack, TabView, sheets, alerts, Stepper, Toggle, PhotosPicker). Não embutir o HTML.

Para abrir o protótipo: abra `prototype/InnerMesh App.dc.html` num navegador (os quatro arquivos de `prototype/` precisam ficar juntos). O painel à esquerda tem atalhos para cada tela.

## Fidelidade
**Alta (hifi).** Cores, tipografia, espaçamentos, raios, textos e animação de entrada são finais. Recriar com precisão, usando os tokens de `tokens.json`.

## Ordem de autoridade
1. `DESIGN.md`: regras completas. Em caso de conflito, ele vence.
2. `tokens.json`: valores exatos.
3. `prototype/InnerMesh App.dc.html`: comportamento e composição.
4. `GOVERNANCE.md`: licenças, gates de assets, provas de implementação.

O produto se chama **InnerMesh** em todo lugar: nome do app, prefixo `InnerMesh/` de tokens e assets, `InnerMeshTheme`, caminhos `docs/innermesh/`. A troca dos nomes anteriores no código, caminhos, repositórios e identificadores **não faz parte desta entrega**: segue a fase 6 do plano de remediação, na branch `codex/innermesh-rename`, depois da prova da NSE.

## Escopo do design (alvo, não ordem de implementação)
Entra: entrada sem convite, confirmar convite (com animação), convite indisponível, perfil local por círculo, Conversas com seletor de círculo, conversa (texto, áudio, arquivo), informações do grupo, Ajustes (Este círculo / App), Gestão do círculo (Convites, Membros com limite, Grupos), acesso retirado.

Fora (ainda sem design final): tela “Escolher membros”, Share Extension, convites feitos por membros, chamadas, Android.

---

## Design tokens
Implementação única em `InnerMeshTheme`, com variantes Any/Dark em sRGB (Asset Catalog ou `Color(light:dark:)`), prefixo `InnerMesh/`. Nenhuma view usa hexadecimal próprio. O tema segue o sistema por padrão; Ajustes → Aparência oferece Sistema · Claro · Escuro (`preferredColorScheme`).

| Token | Claro | Escuro |
| --- | --- | --- |
| canvas | #F5F3EE | #0D1015 |
| surface | #FCFBF8 | #161A21 |
| surfaceMuted | #EAE7E0 | #20262F |
| separator | #DFDBD3 | #252B35 |
| text | #14181F | #F1EDE4 |
| textSecondary | #565D68 | #A7AEB9 |
| border | #767D88 | #5F6876 |
| primary | #1B2638 | #E6DCC6 |
| primaryPressed | #111A28 | #D6C9AE |
| onPrimary | #FCFBF8 | #10141A |
| accent | #7E6128 | #C9A86A |
| innerLight | #EFE6D2 | #262117 |
| outgoing | #E4E8EF | #243041 |
| danger | #A3262A | #FF9D95 |
| success | #256445 | #8DD3A7 |
| warning | #835600 | #E6C072 |
| focus | #7E6128 | #D8B878 |
| disabledText | #8A9099 | #6E7683 |
| scrim | #0A0D12 45% | #000000 60% |

**Acento (`accent`) só nestes usos, no máximo uma categoria por tela:** ponto central do símbolo e nó que entra; validade do convite; rótulo “Administrador”; prefixo “Rascunho:”; estado Pendente/Novo em Convites; “Fulano está escrevendo…”. Nunca em preenchimento de botão nem no nome do remetente.

**Tema escuro:** `primary` e `accent` ficam a 1,66:1 entre si. Nunca diferenciar os dois só por cor.

### Tipografia
Fontes do sistema, sem arquivos embutidos. New York = `.system(design: .serif)`. Tudo com Dynamic Type.

| Token | Estilo | Ref. |
| --- | --- | --- |
| wordmark | New York semibold | 40/46 |
| hero | New York, title1 semibold | 28–30/34 |
| display | SF Pro, largeTitle bold | 34/41 |
| title | title2 semibold | 22/28 |
| section | headline semibold | 17/22 |
| body | body | 17/23 |
| secondary | subheadline | 15/21 |
| caption | footnote | 13/18 |
| label | footnote semibold, CAIXA ALTA, +0,04em, textSecondary | 13/18 |
| tab | caption2; ativa bold, inativa medium | 12 |

New York só em wordmark, títulos de fluxo e iniciais de avatar de grupo/círculo. Horários e durações com `monospacedDigit()`.

### Espaço, raios, alvos
- Espaço: 4 · 8 · 12 · 16 · 24 · 32 · 48. Margem lateral 20 em listas, 24 em telas de fluxo.
- Raios: control 10, button 12, card 16, bubble 18 (canto da origem 6), compositor 20, sheet 20, avatar de grupo 30% do lado.
- Alvos de toque ≥ 44 × 44 pt. Botão primário altura 52–54.
- Sem sombras informativas. Sem sombra em bolhas.

### Avatares
| Tipo | Forma | Cor |
| --- | --- | --- |
| Pessoa | círculo | surfaceMuted / iniciais primary, SF semibold |
| Grupo | quadrado raio 30% | primary / iniciais onPrimary, New York semibold |
| Você | círculo | outgoing / iniciais primary |
| Círculo (instância) | anel vazado 1,5 pt primary sobre canvas | iniciais primary, New York semibold |

Tamanhos: 24 (seletor), 38 (cabeçalho), 40 (membros, sheet), 44 (solicitação), 52 (lista), 84–96 (Informações, Perfil). Iniciais: primeira letra das duas primeiras palavras, ignorando “de, da, do, das, dos, e” (“Mesa de ideias” → MI).

---

## Símbolo e ícone (`assets/`)
Símbolo aprovado **1a, Malha**: grade 64, centro (32,32), 6 nós sobre circunferência r=22 começando em −90°, anel ligando vizinhos, cordas 1→3 e 4→0, ponto central em `accent` sem tocar linhas.

| Tamanho óptico | Uso | Traço | Raio do nó | Ponto central | Cordas |
| --- | --- | --- | --- | --- | --- |
| Grande ≥ 56 pt | telas de marca | 2,5 | 3,5 | 3 | 1→3, 4→0 |
| Médio 24–48 | – | 3,2 | 4 | 3,5 | 1→3 |
| Pequeno 20 | linha Gestão, cabeçalho | 4,8 | 5 | 4,5 | nenhuma |

Cordas com 0,8 × o traço do anel. Pontas arredondadas.

Estados:
- **convite**: nó 1 fora, a raio 35, anel vazado `accent` (traço 1,8), sem linhas ligadas a ele. viewBox `-10 -10 84 84`.
- **completo**: todos os nós no anel.
- **fora** (acesso retirado, convite indisponível): como convite, todo em `textSecondary`, nó externo preenchido, sem ponto central.

Arquivos:
- `assets/symbol/*.svg`: grande/médio/pequeno, convite, fora, nos dois temas, mais monocromáticos. Converter para PDF vetorial no Asset Catalog (Preserve Vector Data) ou desenhar com `Canvas`/`Path` a partir da geometria acima.
- `assets/symbol/innermesh-symbol.js`: implementação de referência da geometria e da animação (função `IMSymbol`). Usar como especificação para o `Shape` SwiftUI.
- `assets/app-icon/AppIcon-{dark,light,tinted}-1024.svg`: mestre 1024, margem 18%, sem cantos arredondados. Exportar PNG 1024 e configurar as três aparências do ícone iOS 18. Ícone final depende da busca de marca (GOVERNANCE).

Onde aparece grande: Entrada (96 pt), Confirmar convite (200 pt sobre disco `innerLight` de 224–264 pt), Acesso retirado/Indisponível (72–84 pt, variante fora). Pequeno (20–24): ao lado do wordmark, linha Gestão em Ajustes, cobertura ao trocar de app. Nunca em telas de conversa.

---

## Telas
Composição de referência 390 × 844 pt. Todas usam fundo `canvas`.

### 1. Entrada sem convite
Símbolo 96 centrado, wordmark “InnerMesh” (primary), “O seu círculo, por convite.” (body, textSecondary). Embaixo: botão primário “Abrir convite” e texto “A entrada é por convite. Peça um a quem já participa de um círculo.” Margem 24.

### 2. Confirmar convite
Topo: símbolo 22 + “InnerMesh” New York 18. Se a pessoa já tem círculos, abre como sheet de tela cheia com botão fechar (X, 44 pt). Disco `innerLight` 224 com símbolo 200 em estado convite. Título hero “Você recebeu um convite.”, corpo “Helena Duarte chamou você para o círculo Mesa Faria Lima.” Cartão `surface` raio 16 com linhas rótulo/valor (Círculo · Uso · Validade; validade em `accent` semibold). Nota caption “Ao confirmar, você entra no círculo com este aparelho.”, botão “Entrar no círculo”, botão de texto “Agora não”.

Estados: validando (spinner + “Verificando convite…”) → válido → entrando (spinner no botão, “Entrando…”, largura estável) → animação → confirmado (título “Você está no círculo.”, cartão some, botão “Continuar”) | falhou (aviso `warning`: “Não foi possível confirmar a resposta. Seu convite continua válido.”, botão “Tentar novamente”). Ver também “Já está no círculo” e “Capacidade atingida” em DESIGN 8.3.

**Animação de entrada (dispara quando o servidor confirma, nunca no toque):**
| Tempo | Efeito |
| --- | --- |
| 0–360 ms | Nó externo percorre arco (raio 35→22, ângulo +28°→0) até a posição; ease-out (0.2, 0, 0, 1). Anel vazado vira nó preenchido ao chegar |
| 240–520 ms | As duas linhas do anel ligadas ao nó são desenhadas a partir dele (trim progressivo) |
| 520–600 ms | Ponto central 85%→100% de opacidade; `UINotificationFeedbackGenerator().notificationOccurred(.success)` |
| 600 ms | Título muda; VoiceOver anuncia “Você entrou no círculo” |

Reduce Motion: troca direta convite → completo com fade de 150 ms. Falha: o nó não se move. Repete a cada novo círculo.

### 3. Convite indisponível
Símbolo “fora” 84, alinhado à esquerda. “Este convite não está disponível.” + “Ele pode ter expirado, sido cancelado ou já usado. Peça um novo a quem enviou o convite.” Botão secundário “Voltar”. Mesmo texto para todos os motivos.

### 4. Perfil local (por círculo)
Confirmação `success` “Você está em Mesa Faria Lima.”, título hero “Como você quer aparecer?”, explicação. Avatar 96 (Você), “Adicionar foto (opcional)”. Campo com label persistente “Nome de exibição neste círculo”, pré-preenchido com o nome do último círculo; ajuda “Preenchido com o nome que você usa em outro círculo. Ele não fica ligado entre círculos.” Botão “Ir para as conversas” desabilitado (surfaceMuted/disabledText) sem nome. Nunca pedir telefone ou e-mail.

### 5. Conversas
- **Seletor de círculo** acima do título: anel 24 + nome (section) + chevron; ponto 8 pt `primary` se houver novidade em outro círculo (sem contagem). Rótulo VO: “Círculo atual: Conselho. Trocar de círculo”.
- Título display “Conversas”, busca `surfaceMuted` raio 10, placeholder “Buscar neste círculo” (só no círculo atual).
- Banner offline (card `surface`, ícone e texto `warning`).
- Seção “SOLICITAÇÕES · 1”: cartão `surface` com avatar 44, “Ana quer conversar com você”, “Membro do seu círculo · nada é entregue antes do aceite”, Aceitar (primário) e Recusar (secundário) de mesma largura, altura 44. Recusar pede alerta. Some durante a busca.
- “RECENTES”: linha com avatar 52, nome, hora (primary se não lida), prévia de uma linha, contador pill `primary`. Prefixos: “Rascunho:” `accent`, “Pendente ·” `warning`, “Você:”, “Remetente:” em grupo.
- Vazio: “Suas conversas vão aparecer aqui.” Busca sem resultado: “Nenhuma conversa com “termo”.”
- Sem botão de criar conversa/grupo.
- Tab bar: Conversas · Ajustes. Ativa preenchida + bold `primary`; inativa contorno + medium `textSecondary`.

**Sheet “Seus círculos”** (`surface`, raio 20 no topo, grabber): item por círculo com anel 40, nome (semibold se atual + check), meta “Você é anfitriã” ou “Anfitrião: Rafael Prado” · “N conversas com novidade”, ou “Acesso retirado” (anel em textSecondary). Ordem: última atividade. No fim, “Abrir outro convite” (anel tracejado com +). Trocar não pede confirmação; rascunhos ficam no círculo de origem.

### 6. Conversa
Cabeçalho compacto: voltar, avatar 38, nome, subtítulo (“3 membros · toque para ver” / “Conversa individual” / “Ana está escrevendo…” em `accent`), botão info. Topo do histórico: cadeado 14 + “Criptografia de ponta a ponta. Mensagens recebidas ficam nos aparelhos de quem participa.” Separador “HOJE”.
- Bolha recebida `surface`, raio 18/18/18/6; enviada `outgoing`, 18/18/6/18. Padding 10 × 14, largura máx. 84%. Remetente (grupo) em textSecondary semibold 13, só na primeira de uma sequência.
- Estado das enviadas ao lado da hora: Enviando / Aguardando conexão (relógio, `warning`) → Enviada (check) → Entregue (dois checks). Sem “Lida”.
- Arquivo: ícone 44 `surfaceMuted`, nome, “248 KB · PDF · Toque para abrir”.
- Áudio: play 40 `primary`, onda decorativa (oculta do VO) que pinta em `primary` conforme o progresso, duração tabular. Rótulo “Ouvir mensagem de voz, 0:42” / “Pausar”.
- Mensagem de sistema centralizada em `surfaceMuted`.
- Compositor: anexar (+), campo com borda raio 20, microfone ↔ enviar (círculo `primary`) quando há texto. Rascunho guardado por conversa. Gravação substitui o compositor: ponto `danger` pulsando, “Gravando · 0:04”, Cancelar (`danger`), Enviar.
- Offline: faixa acima do compositor “Sem conexão. Novas mensagens ficam pendentes.”; ao reconectar, as pendentes avançam sozinhas.

### 7. Informações do grupo
Avatar 84, nome (title), “Grupo em Conselho”, descrição. “MEMBROS · N” em card, com “Administrador” em `accent`. Anfitrião vê “Escolher membros”; membro vê “Só o anfitrião do círculo adiciona ou retira membros.” Botão “Sair do grupo” em `danger` com alerta.

### 8. Ajustes
- “ESTE CÍRCULO · Conselho”: card com perfil deste círculo (avatar 48, nome, “Membro · anfitrião: Rafael Prado”); para anfitrião, linha “Gestão do círculo” com símbolo 20 e resumo “5 de 12 membros · 1 convite pendente”; para membro, “Sair do círculo” (`danger`, alerta).
- “APP”: segmentado Aparência (Sistema · Claro · Escuro; ativo por fundo `surface` + semibold), Prévia das notificações “Discreta”, toggle “Cobrir ao trocar de app” (ligado, `success`), Armazenamento.

### 9. Gestão do círculo (só anfitrião)
Título “Gestão” + nome do círculo. Segmentado Convites · Membros · Grupos.
- **Convites:** botão “Criar convite”; ajuda “Cada convite vale para uma entrada. Se for repassado, quem usar primeiro entra.”; lista com estado (Pendente/Novo em `accent`; Usado/Expirado em textSecondary). Com o círculo completo, o botão fica desabilitado e a ajuda vira “O círculo está completo. Aumente o limite em Membros ou retire o acesso de alguém para convidar outra pessoa.”
- **Membros:** primeira linha “Limite de membros” com stepper. O limite conta o anfitrião e os convites pendentes. Mínimo = membros ativos + pendentes (o “−” fica em disabledText e a ajuda vira “Há N lugares em uso. Para reduzir, retire acessos antes.”). Máximo: limite técnico do servidor (a definir; protótipo usa 50). Lista com “Retirar” (`danger`, alerta) e “Acesso retirado”. Rodapé “5 de 12 membros · 1 convite pendente”.
- **Grupos:** “Criar grupo” (secundário), lista de grupos com “Escolher membros”.

### 10. Acesso retirado
Substitui Conversas do círculo afetado; abas e seletor continuam. Vira estado raiz só se for o único círculo. Símbolo “fora”, “Seu acesso ao círculo Investidores foi retirado.”, “Paulo Mendes retirou seu acesso em 14 de outubro. Seus outros círculos continuam como estavam.”, card “O que isso significa” (3 linhas), botão “Apagar dados deste aparelho” (contorno `danger`, alerta) que remove o círculo do seletor.

### Sobreposições
- **Alerta:** nativo. Título, consequência, ação (em `danger` se destrutiva), Cancelar.
- **Toast:** topo, fundo `text`, texto `canvas`, 2,6 s, só para sucesso. Erro nunca vai em toast.
- **Cobertura ao trocar de app:** `canvas` liso + símbolo pequeno, sem nome de círculo.

---

## Estado e dados
- `circles: [Circle]` com `id, name, role (owner|member), host, status (active|revoked), revokedOn, myProfile {displayName, photo}, limit, members, invites, chats`.
- `currentCircleId` persistido (último aberto).
- Drafts por `circleId:chatId`.
- Mensagem: `kind (text|file|audio|system), status (pending|sent|delivered|failed)`.
- Convite: `validating → valid → joining → (animating) → confirmed | failed`; `unavailable`, `full`, `alreadyMember`.
- Isolamento: nenhuma lista, busca ou notificação mistura círculos. Notificação padrão: “Nova atividade no InnerMesh”, sem remetente nem círculo.
- Autorização aplicada no serviço/núcleo; a UI apenas oculta o que não é permitido.

## Voz e termos
Usar exatamente os textos acima e os de DESIGN.md seção 8.3. Neutro em gênero. “Anfitrião” (nunca dono/admin para o círculo); “Administrador” é papel em grupo. “Sair do círculo” ≠ “Sair do grupo”. Evitar “exclusivo”, “seleto”, “elite”, “VIP” e termos técnicos (SMP, XFTP, relay) na interface.

## Acessibilidade (obrigatório)
Dynamic Type até tamanhos de acessibilidade (Aceitar/Recusar empilham; símbolo do convite cai para 120 pt); VoiceOver com ordem título → estado → conteúdo → ação; mensagem como um elemento; Reduce Motion e Reduce Transparency; cor, som ou háptico nunca como único sinal. Contrastes medidos em DESIGN.md 5.1.

## Arquivos
- `README.md`: este documento.
- `DESIGN.md`: especificação completa 0.5.1.
- `GOVERNANCE.md`: governança, licenças, gates.
- `tokens.json`: cor, tipo, espaço, raio, movimento.
- `assets/symbol/`: SVGs do símbolo + `innermesh-symbol.js` (geometria e animação de referência).
- `assets/app-icon/`: mestres 1024 escuro, claro, tingido.
- `prototype/InnerMesh App.dc.html`: protótipo navegável (abrir com `support.js` e `innermesh-symbol.js` na mesma pasta).
- `prototype/InnerMesh Exploracoes.dc.html`: explorações de símbolo e paleta (histórico; 1a e champanhe aprovados).
- `screenshots/`: capturas de referência de cada tela, temas claro e escuro (390 × 844).

## Pendências
Aprovação final da animação de entrada; tela “Escolher membros”; Share Extension; limite técnico de membros; indicador de digitação (proposta: desligado por padrão, opção em Privacidade); busca de marca antes do ícone final.
