# Design

**Status: Draft · versão 0.5.2 · 2026-10-18 · paleta e símbolo aprovados; telas pendentes.**

Este documento define a identidade e a interface do InnerMesh para iOS. Governança, licenças, gates de assets, distribuição e provas de implementação estão em [GOVERNANCE.md](GOVERNANCE.md). Arquitetura e autorização continuam na [spec do produto](.specs/features/invitation-only/spec.md) e no [desenho técnico](.specs/features/invitation-only/entry-design.md).

Referências: [protótipo navegável](docs/innermesh/design/prototype/InnerMesh%20App.dc.html), [explorações de símbolo e paleta](docs/innermesh/design/prototype/InnerMesh%20Exploracoes.dc.html), [handoff](docs/innermesh/design/HANDOFF.md), [tokens sRGB](docs/innermesh/design/tokens.json), [contraste](docs/innermesh/design/contrast.json). Este arquivo é a autoridade.

**0.5.2:** revisão de handoff, sem mudança visual. A primeira versão implementada tem um único círculo (3.1); vários círculos e limite configurável ficam como alvo de design e dependem de spec própria. A renomeação de código e caminhos sai desta entrega e segue a fase 6 do plano de remediação (11). Links do protótipo apontam para `docs/innermesh/design/`; `contrast.json` e `measure_contrast.py` passam a acompanhar o pacote.

**0.5.1:** paleta champanhe aprovada (o bordô de 5.1.2 sai de cogitação) e símbolo **1a, Malha** aprovado: 6 nós, anel e duas cordas (1→3 e 4→0); no tamanho médio fica só uma corda e no pequeno nenhuma. O nó que fica de fora no convite é o 1.

**Mudanças desde 0.4** (decisões do anfitrião de 17/10/2026):

- **Vários círculos no mesmo app.** Entra o seletor de círculo no topo de Conversas, o avatar de círculo (anel) e a divisão de Ajustes em “Este círculo” e “App” (3, 5.4, 6).
- **Perfil por círculo.** Cada círculo tem seu nome de exibição e foto; nada é compartilhado entre círculos (3.1).
- **Acesso retirado** deixa de ser estado raiz quando a pessoa ainda tem outros círculos (3.1, 8.3).
- **Limite de membros configurável** pelo anfitrião, contando o próprio anfitrião (6, 8.3).
- **Aparência** com três opções: Sistema (padrão), Claro e Escuro (6).
- Confirmados: nome do remetente neutro (5.1.1) e o termo “anfitrião” (9).

**Mudanças da 0.4 em relação à 0.3** (revisão da direção InnerMesh, sem trocar paleta nem nome):

- **Símbolo:** a construção da 0.3 (6 nós, vizinhos + opostos) forma uma roda com três diâmetros cruzando o ponto central, e a variante com cordas alternadas formaria um hexagrama. A 0.4 proíbe figuras com leitura religiosa ou mística, separa o ponto central das linhas e define três tamanhos ópticos (1.1).
- **Entrada no círculo:** coreografia especificada passo a passo, com tempos, curva, háptico e versão Reduce Motion (1.2).
- **Acento:** a regra “um acento por tela” da 0.3 contradizia a lista de usos (vários nomes de remetente em `accent` na mesma conversa). O nome do remetente sai do acento; a regra passa a ser “uma categoria de acento por tela” (4, 5.1.1).
- **Tema escuro:** `primary` e `accent` ficam a 1,66:1 entre si. Nova regra: nunca diferenciar os dois só por cor (5.1).
- **Bordô medido:** 8,93 no claro e 8,37 no escuro sobre `surface` (5.1.2).
- **Texto neutro em gênero:** “Você foi convidado” e “o círculo dele” supunham o gênero de quem convida e de quem é convidado. Textos reescritos (8.3).
- **Pessoa sem convite:** “Peça um a quem administra o seu círculo” não fazia sentido para quem ainda não tem círculo. Corrigido.
- **Círculo × grupo:** definição e exemplos para não confundir os dois termos (9).
- **Capacidade:** o limite de 20 convidados além do anfitrião aparece na Gestão (“12 de 21 membros”) (6).
- **Ícone iOS:** variantes claro, escuro e tingido (1.1).
- **Briefing:** o pedido da rodada (antiga 0.5) saiu do corpo e foi para o Apêndice A, para o documento não envelhecer a cada rodada.
- **Contraste:** todos os pares da 0.3 foram remedidos e conferem. Três pares que faltavam foram adicionados (5.1).

---

## 0. Briefing

### 0.1 O que é

O InnerMesh é um mensageiro privado para iPhone, de entrada exclusivamente por convite. Cada instância é um **círculo**: um grupo pequeno de pessoas escolhidas por um anfitrião, com limite definido por ele, que conversam sobre negócios, carreira, startups e assuntos sensíveis. Os servidores são próprios e as conversas têm criptografia de ponta a ponta (núcleo derivado do SimpleX).

Funcionalmente é um mensageiro comum: conversas individuais, grupos pequenos, áudio gravado, fotos e arquivos. O que muda é quem está dentro e como se entra. Como alvo de design, uma pessoa pode participar de vários círculos no mesmo app, sem mistura entre eles. A primeira versão implementada tem um único círculo (3.1).

### 0.2 O conceito do nome

*Inner circle* é o círculo de confiança de alguém: as pessoas com quem se fala o que não se fala em público. *Mesh* é a malha de pessoas ligadas entre si. InnerMesh é a rede de confiança que se forma dentro desse círculo.

Três consequências para o design:

1. **Pertencimento.** A sensação principal ao abrir o app é “estou entre as pessoas certas”. O momento de marca mais importante é a entrada no círculo.
2. **Conexão.** O símbolo mostra pontos ligados dentro de um círculo. No futuro, membros de confiança poderão convidar outras pessoas, e a árvore de convites vira literalmente essa malha.
3. **Discrição.** Nada no app chama atenção para si. De longe, a tela parece um mensageiro sóbrio.

### 0.3 Para quem

Executivos, fundadores, investidores e profissionais seniores no Brasil, de 35 a 60 anos, que usam iPhone, leem em português e circulam bem em inglês. Estão acostumados a produtos premium e discretos: banco privado, cartão de alta renda, clube de membros, concierge. Têm pouco tempo e pouca paciência para onboarding.

Implicação prática: texto ampliado é comum nessa faixa. Testar Dynamic Type grande é obrigatório, não um extra.

### 0.4 Tom visual

Referências de sensação, não para copiar: o salão de um clube privado à noite, um cartão de visita em papel grosso, o app de um banco privado, a capa de um relatório anual bem editado.

| Queremos | Evitamos |
| --- | --- |
| Sóbrio, editorial, noturno, seguro | Startup colorida, gradiente, ilustração cartunesca |
| Contraste alto entre tinta e marfim | Verde-natureza, papel kraft, tons de feira orgânica |
| Um único acento metálico fosco, usado com parcimônia | Dourado brilhante, ostentação, “VIP” escrito |
| Exclusividade sugerida pelo ritual de entrada | Exclusividade anunciada em texto (“seleto”, “elite”) |
| Tema escuro como assinatura, claro igualmente cuidado | Estética hacker, terminal, cadeados por toda parte |

---

## 1. Marca

- **Personalidade:** discreta, adulta, confiável, cuidadosa.
- **Nome:** sempre **InnerMesh**, uma palavra, I e M maiúsculos. No texto corrido, “o InnerMesh” (o app). A instância é sempre “o círculo”.
- **Assinatura:** “O seu círculo, por convite.” Versão descritiva, quando o contexto não deixa claro que é um mensageiro: “Conversas privadas no seu círculo.”
- **Confiança vem de estados concretos:** quem convidou, o que será confirmado, se a mensagem está pendente, quem administra o grupo, o que uma revogação faz.

| Fazer | Evitar |
| --- | --- |
| Explicar criptografia e limite de cópias locais onde isso afeta uma decisão | Prometer anonimato absoluto, bloqueio de captura de tela ou histórico apagado remotamente |
| Sugerir exclusividade pelo ritual: convite, confirmação, entrada | “Exclusivo”, “seleto”, “elite”, “VIP” na interface |
| Um cadeado pequeno na nota de criptografia da conversa | Cadeados decorativos em cada tela, estética hacker |
| Acento champanhe em sinais pequenos | Dourado brilhante, textura metálica, gradientes promocionais, urgência artificial |

### 1.1 Símbolo

Pontos ligados por linhas finas sobre uma circunferência, com um ponto central separado em acento. Lê-se como “pessoas ligadas entre si, em volta de algo comum”. Reconhecível em uma cor e em 20 pt. Não reutilizar símbolo, marca, papagaio, imagens ou wallpapers do SimpleX.

**Construção de partida (grade 64):**

- 6 nós de raio 3,5 sobre uma circunferência de raio 22 centrada em (32, 32).
- Anel: cada nó ligado aos dois vizinhos.
- Malha: 2 cordas curtas e assimétricas entre nós não vizinhos. **Nenhuma corda passa pelo centro.**
- Ponto central de raio 3, sem tocar nenhuma linha. Ele é “o que é comum”, não um nó da malha.
- Linhas de 2,5, pontas arredondadas.

**Regras de exploração:**

| Regra | Valor |
| --- | --- |
| Figuras proibidas | Hexagrama, pentagrama, roda ou asterisco (diâmetros pelo centro), cruz, molécula, ícones genéricos de “rede” ou “compartilhar”. Testar o símbolo invertido e rotacionado: nenhuma leitura religiosa, mística ou de química |
| Nós | 5 a 7. Ímpar ou levemente irregular ajuda a fugir das figuras proibidas |
| Tamanhos ópticos | **Grande** (≥ 64 pt): construção completa. **Médio** (24–48 pt): linhas 3/64 e uma corda só. **Pequeno** (20 pt): só anel e ponto central, nós maiores (4,5/64), linha com pelo menos 1,5 pt real |
| Cor | Nós e linhas em `primary`; ponto central em `accent`. Monocromático: tudo `primary` ou tudo `onPrimary` |
| Área de proteção | ≥ 1/4 da largura do símbolo em todos os lados |
| Mínimos | Símbolo 20 pt no app; assinatura completa 120 pt de largura. Abaixo disso, só o símbolo, com rótulo acessível |
| Estado “convite” | Um nó fora da circunferência, a 1,6 × o raio, em anel vazado `accent` (traço, sem preenchimento), sem linha que o ligue. Os demais nós completos |
| Variante “fora do círculo” | Igual ao estado convite, mas todo em `textSecondary` e sem ponto central. Só para convite indisponível e acesso retirado |
| Ícone iOS | Mestre 1024 × 1024, sem texto, margem de 18%, sem cantos arredondados embutidos. **Escuro (principal):** fundo `canvas` escuro, símbolo `primary` escuro, ponto `accent`. **Claro:** fundo `canvas` claro, símbolo `primary` claro. **Tingido:** monocromático, sem ponto em cor própria |
| Usos incorretos | Esticar, rotacionar, adicionar brilho, sombra, glow ou selo de segurança. O símbolo não substitui estado de acesso |

### 1.2 Momento de marca

O símbolo aparece grande em três telas e em nenhuma outra.

| Tela | Tratamento |
| --- | --- |
| Entrada sem convite | Símbolo 96 pt centrado; wordmark “InnerMesh” em New York 40 pt semibold; assinatura abaixo |
| Confirmar convite | **Entrada no círculo:** símbolo 200 pt em estado “convite”, sobre um disco `innerLight` de 264 pt. Coreografia abaixo |
| Acesso retirado / convite indisponível | Variante “fora do círculo”, 72 pt, alinhada à esquerda com o título |

**Coreografia da entrada no círculo** (dispara uma vez, quando o servidor confirma a entrada; nunca ao tocar o botão):

| Tempo | O que acontece |
| --- | --- |
| 0–360 ms | O nó externo percorre um arco até sua posição na circunferência. Curva ease-out (0,2; 0; 0; 1). O anel vazado vira nó preenchido no fim do trajeto |
| 240–520 ms | As duas linhas do anel que tocam o nó são desenhadas a partir dele (traço progressivo) |
| 520–600 ms | O ponto central sobe de 85% para 100% de opacidade. Háptico `.success` uma vez, se o sistema permitir |
| 600 ms | Título muda para “Você está no círculo.” VoiceOver anuncia “Você entrou no círculo” |

Com Reduce Motion: troca direta do estado “convite” para o completo, com fade de 150 ms, sem deslocamento. Se a confirmação falhar, o nó não se move.

A entrada se repete a cada novo círculo: entrar no segundo ou terceiro círculo tem o mesmo ritual do primeiro.

Fora dessas três telas, o símbolo só aparece pequeno (20 a 24 pt) ao lado do wordmark, como ícone da linha Gestão em Ajustes e na cobertura ao trocar de app. Nunca em telas de conversa.

---

## 2. Objetivos do produto

O convidado entende o convite, confirma a entrada e conversa sem configurar servidores. O anfitrião controla convites, grupos e membros. Conversa individual entre membros depende de aceite mútuo.

**Primeira versão:** leitura, composição, áudio gravado, fotos, arquivos, grupos pequenos. **Fora desta fase:** Android, desktop, chamadas, feeds públicos, descoberta aberta, integrações externas, convites feitos por membros.

**Sinais de sucesso** (exigem teste com a interface implementada): a pessoa acha a ação principal sem ajuda; distingue pendente de entregue; localiza as informações do grupo; entende erro de convite e revogação; conclui os mesmos fluxos com VoiceOver e texto ampliado.

| Pessoa | Necessidade | Contexto |
| --- | --- | --- |
| Anfitrião | Convidar, criar grupos, escolher membros, retirar acesso | Gestão ocasional; confirmação antes de ações irreversíveis |
| Membro convidado | Confirmar convite, responder, compartilhar mídia, aceitar conversas | iPhone, sessões curtas, uma mão, rede instável, entre reuniões |
| Participante com recursos assistivos | Ler, ouvir e operar os mesmos fluxos | VoiceOver, Dynamic Type, alto contraste, Reduce Motion |

---

## 3. Arquitetura de informação

Duas abas: **Conversas** e **Ajustes**. Navegação e barras nativas. Sem seção social, sem painel de métricas.

```
Entrada sem convite ─► Confirmar convite ─► Perfil local ─► Conversas
                          └► Convite indisponível
Conversas ─┬─ Seletor de círculo (sheet) ─┬─ Trocar de círculo
           │                             └─ Abrir outro convite
           ├─ Busca (só no círculo atual)
           ├─ Solicitações (seção, só quando houver)
           └─ Recentes ─► Conversa ─► Informações (grupo ou pessoa)
Ajustes ───┬─ Este círculo ─┬─ Meu perfil neste círculo
           │                ├─ Gestão do círculo (só anfitrião) ─┬─ Convites (Criar convite)
           │                │                                    ├─ Membros (Retirar acesso, Limite)
           │                │                                    └─ Grupos (Criar grupo, Escolher membros)
           │                └─ Sair do círculo (só membro)
           └─ App ─ Aparência, Privacidade, Notificações, Armazenamento, Sobre
Acesso retirado: substitui Conversas do círculo afetado; vira estado raiz só se não restar nenhum círculo
```

| Superfície | Conteúdo e ação principal | Papel |
| --- | --- | --- |
| Entrada sem convite | Wordmark, assinatura, “Abrir convite”, orientação para pedir convite | Sem associação |
| Convite no navegador | Instruções de instalação e de reabrir o link original. GET/HEAD não consomem convite; o token não aparece | Destinatário |
| Confirmar convite | Nome do círculo, quem convidou (só se comprovado), uso, validade, “Entrar no círculo” | Destinatário |
| Perfil local | Nome de exibição (obrigatório), foto opcional. Nunca telefone ou e-mail | Membro novo |
| Conversas | Seletor de círculo, Busca, Solicitações, Recentes do círculo atual | Membro |
| Conversa | Cabeçalho compacto, nota de criptografia, histórico, compositor, anexos, áudio | Participante |
| Informações | Nome, descrição, membros, administrador. “Sair do grupo”. Anfitrião vê “Escolher membros” | Participante |
| Seletor de círculo | Sheet com os círculos da pessoa, atividade em cada um, “Abrir outro convite” | Membro |
| Ajustes | “Este círculo” (perfil, gestão ou sair) e “App” (aparência, privacidade, notificações, armazenamento, versão) | Membro |
| Gestão do círculo | Linha em Ajustes → Este círculo. Segmentos Convites, Membros, Grupos | Anfitrião do círculo atual |
| Acesso retirado | Estado explícito, limites, apagar dados locais do círculo | Associação revogada |

**Criar grupo** fica só em Gestão → Grupos. Não há botão de criar na lista de Conversas, para nenhum papel. Ocultar o que não é permitido; a autorização continua aplicada no serviço e no núcleo.

**Reserva para convites por membros (fase futura):** quando existir, a ação entra em Ajustes → Este círculo como “Convidar alguém”, nunca na lista de Conversas. Não desenhar agora.

### 3.1 Vários círculos

**Escopo da primeira versão implementada: um círculo.** Esta seção descreve o alvo de design. Na primeira versão não há seletor nem sheet de círculos, há um perfil local, o acesso retirado é estado raiz e o limite é de 20 convidados ativos além do anfitrião (21 pessoas no total), exibido como “N de 21 membros”, sem stepper. Implementar vários círculos ou limite configurável exige antes uma spec própria, que trate várias identidades e pontes no aparelho, a NSE atendendo várias instâncias e o modelo de operação com outros anfitriões.

- **Isolamento.** Cada círculo é uma instância separada, com servidores, membros e conversas próprios. A interface nunca mistura conversas de círculos diferentes numa mesma lista, busca ou notificação.
- **Círculo atual.** O app sempre está em um círculo. Conversas, busca, solicitações e Ajustes → Este círculo valem para ele. O app guarda o último círculo aberto.
- **Seletor.** No topo de Conversas, acima do título: avatar de círculo 24 + nome do círculo + chevron, em `section`. Toque abre um sheet com:
  - um item por círculo: avatar 40, nome, papel (“Você é anfitrião” ou “Anfitrião: Rafael Prado”) e “N conversas com novidade” quando houver;
  - o círculo atual marcado com check e peso semibold;
  - no fim, “Abrir outro convite”.
- **Atividade em outros círculos.** Ponto de 8 pt em `primary` ao lado do chevron do seletor, com rótulo acessível “Há novidades em outros círculos”. Sem contagem e sem nome do outro círculo na tela atual.
- **Ordem no sheet:** última atividade primeiro. Sem reordenação manual nesta fase.
- **Perfil por círculo.** Nome de exibição e foto são definidos a cada entrada. O perfil local pré-preenche o nome usado no último círculo, editável. Nada indica a outros membros em que outros círculos a pessoa está.
- **Novo convite com círculos existentes.** Abrir um link de convite mostra Confirmar convite como sheet de tela cheia sobre o app. Depois da entrada e do perfil, o app troca para o novo círculo.
- **Mesmo círculo duas vezes.** Se o convite for de um círculo em que a pessoa já está: “Você já está neste círculo.” + “Abrir círculo”. O convite não é consumido.
- **Sair do círculo** (membro): Ajustes → Este círculo → “Sair do círculo”, com alerta. Anfitrião não sai; transferir o círculo fica fora desta fase.
- **Acesso retirado em um círculo:** o círculo fica no seletor com a etiqueta “Acesso retirado”. Ao selecioná-lo, a tela de acesso retirado aparece no lugar de Conversas, com as abas visíveis. “Apagar dados deste aparelho” remove o círculo do seletor. Se era o único círculo, vira estado raiz.
- **Share Extension:** escolher primeiro o círculo (pula a etapa se houver só um), depois a conversa.

---

## 4. Princípios

1. **A leitura é o centro.** Cor marca ação e estado; não compete com o conteúdo.
2. **Nativo onde ajuda.** Voltar, sheets, menus, alertas, seletor de foto, gravação, compartilhamento. A marca não muda a ordem nem o significado dessas ações.
3. **Confirmar o que é irreversível.** Resgate de convite, revogação, sair do grupo, apagar dados.
4. **Progresso real.** Mostrar o estado verdadeiro, permitir sair de uma tela carregando, guardar o que foi digitado.
5. **Vazio é aceitável.** Sem publicidade, sem sugestão de contatos.
6. **Silêncio visual.** Cada tela usa no máximo **uma categoria** de acento da lista 5.1.1. Exemplo: a lista de Conversas pode ter vários prefixos “Rascunho:”, mas nenhum outro uso de `accent`.

---

## 5. Linguagem visual

### 5.1 Cor

Tinta e marfim, acento champanhe fosco. O tema escuro é a assinatura da marca e o que aparece em materiais de apresentação; o app segue a configuração do sistema, e o tema claro recebe o mesmo cuidado. Prefixo de implementação `InnerMesh/`. Nenhum componente usa um hexadecimal próprio.

| Token | Claro | Escuro | Uso |
| --- | --- | --- | --- |
| `canvas` | `#F5F3EE` | `#0D1015` | Fundo raiz |
| `surface` | `#FCFBF8` | `#161A21` | Cards, células, bolha recebida, alertas |
| `surfaceMuted` | `#EAE7E0` | `#20262F` | Agrupamento, campo de busca, segmentado, avatar de pessoa, fundo desabilitado |
| `separator` | `#DFDBD3` | `#252B35` | Só linhas decorativas entre células e sob barras |
| `text` | `#14181F` | `#F1EDE4` | Texto principal |
| `textSecondary` | `#565D68` | `#A7AEB9` | Apoio, horários, prévias, nome do remetente |
| `border` | `#767D88` | `#5F6876` | Limites essenciais de controles |
| `primary` | `#1B2638` | `#E6DCC6` | Ação principal, links, aba ativa, avatar de grupo, símbolo |
| `primaryPressed` | `#111A28` | `#D6C9AE` | Estado pressionado |
| `onPrimary` | `#FCFBF8` | `#10141A` | Conteúdo sobre `primary` |
| `accent` | `#7E6128` | `#C9A86A` | Sinais de identidade (lista fechada em 5.1.1) |
| `innerLight` | `#EFE6D2` | `#262117` | Só o disco atrás do símbolo na entrada no círculo |
| `outgoing` | `#E4E8EF` | `#243041` | Bolha enviada, avatar do próprio perfil |
| `danger` | `#A3262A` | `#FF9D95` | Ações destrutivas, gravação |
| `success` | `#256445` | `#8DD3A7` | Confirmações, interruptor ligado |
| `warning` | `#835600` | `#E6C072` | Offline, pendente, falha recuperável |
| `focus` | `#7E6128` | `#D8B878` | Anel de foco |
| `disabledText` | `#8A9099` | `#6E7683` | Texto de controle desabilitado |
| `scrim` | `#0A0D12` a 45% | `#000000` a 60% | Fundo atrás de alertas e sheets |

O token `label` da 0.3 saiu da tabela de cor: era só um apelido de `textSecondary`. Continua como token de tipo (5.2).

**Regra do tema escuro:** `primary` (marfim) e `accent` (champanhe) ficam a 1,66:1 entre si. Nunca usar a diferença entre os dois como único sinal. Um link `primary` ao lado de um rótulo `accent` precisa de outra diferença: peso, sublinhado ou posição.

**Contraste** (WCAG 2.x, cores opacas, remedido em 17/10/2026). Todos os pares de texto atendem 4,5:1; bordas e foco, 3:1.

| Par | Claro | Escuro | Mínimo |
| --- | --- | --- | --- |
| `text` / `canvas` | 16,05 | 16,31 | 4,5 |
| `text` / `outgoing` | 14,48 | 11,42 | 4,5 |
| `textSecondary` / `surface` | 6,42 | 7,81 | 4,5 |
| `textSecondary` / `outgoing` | 5,41 | 5,97 | 4,5 |
| `textSecondary` / `surfaceMuted` | 5,38 | 6,81 | 4,5 |
| `onPrimary` / `primary` | 14,70 | 13,56 | 4,5 |
| `primary` / `canvas` (links) | 13,71 | 13,99 | 4,5 |
| `accent` / `surface` | 5,59 | 7,72 | 4,5 |
| `accent` / `outgoing` | 4,71 | 5,90 | 4,5 |
| `accent` / `innerLight` | 4,66 | 7,08 | 3 (gráfico) |
| `warning` / `surface` | 6,16 | 10,09 | 4,5 |
| `danger` / `surface` | 7,08 | 8,73 | 4,5 |
| `success` / `surface` | 6,79 | 9,98 | 4,5 |
| `onPrimary` / `success` (interruptor) | 6,79 | 10,56 | 3 |
| `border` / `surface` | 4,01 | 3,10 | 3 |
| `border` / `canvas` | 3,74 | 3,38 | 3 |
| `focus` / `canvas` | 5,22 | 10,02 | 3 |

Os três pares novos são `text/outgoing`, `textSecondary/surfaceMuted` e `border/canvas`. `separator` (1,24 e 1,34 sobre `canvas`) é decorativo e não pode ser o único limite de um controle.

**Nota sobre `disabledText`:** texto desabilitado é isento do mínimo de 4,5:1 (WCAG 1.4.3). Medido: 2,60 e 3,32 sobre `surfaceMuted`. O controle desabilitado precisa de mais de um sinal: fundo `surfaceMuted` + texto `disabledText` + motivo visível quando não for óbvio (“Digite um nome para continuar”).

#### 5.1.1 Onde o acento pode aparecer

Lista fechada. Fora dela, usar `primary` ou `textSecondary`. No máximo uma categoria por tela (princípio 6).

| # | Uso | Tela |
| --- | --- | --- |
| 1 | Ponto central do símbolo e o nó que entra no círculo | Entrada, Convite |
| 2 | Validade do convite (“Mais 2 dias”) | Convite |
| 3 | Rótulo “Administrador” nas listas de membros | Informações, Gestão → Membros |
| 4 | Prefixo “Rascunho:” | Conversas |
| 5 | Estado “Pendente” ou “Novo” na lista de convites | Gestão → Convites |
| 6 | Subtítulo “Fulano está escrevendo…” | Conversa |

Na tela Convite, os usos 1 e 2 contam como uma categoria só: os dois falam do convite.

**Saiu da lista:** nome do remetente em bolhas de grupo. Ele passa a `textSecondary` semibold. Numa conversa de grupo o nome aparece em quase toda bolha, e em champanhe a tela inteira ficava dourada.

Nunca: preenchimento de botão, texto pequeno sobre fundo `accent`, ícones de navegação, bordas decorativas.

#### 5.1.2 Paleta alternativa para comparação

Na rodada de exploração, aplicar a duas telas uma variante com acento **bordô** no lugar do champanhe, mantendo tinta e marfim:

| Token | Claro | Escuro |
| --- | --- | --- |
| `accent` (bordô) | `#7A2E36` | `#E3A3A9` |
| sobre `surface` | 8,93 | 8,37 |
| sobre `outgoing` | 7,52 | 6,40 |

É mais séria e menos associada a luxo. No escuro, o bordô se separa melhor do `primary` marfim do que o champanhe, o que resolve a regra do tema escuro de 5.1. Em contrapartida, fica perto de `danger` no claro: se for adotado, `danger` precisa de ajuste. A decisão fica com o anfitrião depois de ver as telas.

### 5.2 Tipografia

Fontes do sistema Apple, sem arquivos de fonte embutidos. **New York** (serifa, `design: .serif`) para o wordmark e títulos de fluxo; **SF Pro** para todo o resto. A serifa dá o tom editorial e de clube; a SF garante leitura em conversa. Em protótipos web, `ui-serif` e `system-ui`, que resolvem para as mesmas fontes em aparelhos Apple.

| Token | Fonte e estilo iOS | Referência | Entrelinha mín. | Uso |
| --- | --- | --- | --- | --- |
| `wordmark` | New York, semibold | 40 pt | 46 | Só o nome “InnerMesh” nas telas de marca |
| `hero` | New York, title1 | 28 a 30 pt semibold | 34 | Título de tela de fluxo (convite, perfil, retirado) |
| `display` | SF Pro, largeTitle | 34 pt bold | 41 | Títulos de aba (Conversas, Ajustes, Gestão) |
| `title` | SF Pro, title2 | 22 pt semibold | 28 | Nome em Informações |
| `section` | SF Pro, headline | 17 pt semibold | 22 | Nome na linha de conversa, títulos de card |
| `body` | SF Pro, body | 17 pt regular | 23 a 24 | Mensagens, explicações |
| `secondary` | SF Pro, subheadline | 15 pt regular | 21 | Prévias, detalhes |
| `caption` | SF Pro, footnote | 13 pt regular | 18 | Horários, ajudas |
| `label` | SF Pro, footnote | 13 pt semibold, caixa alta, +0,04 em, `textSecondary` | 18 | Títulos de seção (“SOLICITAÇÕES · 1”, “MEMBROS · 3”) |
| `tab` | SF Pro, caption2 | 12 pt; ativa bold, inativa medium | n/a | Rótulos da barra de abas |

New York só em títulos de fluxo e marca. Nunca em mensagens, listas, botões ou campos. Respeitar Dynamic Type em toda a escala, inclusive New York. Horários e durações usam números tabulares. Nomes e conteúdo quebram linha. Não reduzir fonte para caber.

### 5.3 Espaço, raios e bordas

- **Espaço:** `4 · 8 · 12 · 16 · 24 · 32 · 48`. Margem lateral 20 em listas, 24 em telas de fluxo.
- **Raios:** `control=10`, `button=12`, `card=16`, `bubble=18` (canto da origem 6), `avatarGroup=30%` do lado, `avatarPerson=50%`.
- **Bordas:** campo 1 pt `border`; foco 2 pt `focus` com afastamento de 2 pt.
- **Sombra:** nenhuma informação depende dela. Sem sombra em bolhas. Sheets e menus usam material nativo, com alternativa opaca em Reduce Transparency.

### 5.4 Avatares

| Tipo | Forma | Cor | Iniciais |
| --- | --- | --- | --- |
| Pessoa | Círculo | `surfaceMuted` / texto `primary` | SF Pro semibold |
| Grupo | Quadrado, raio 30% | `primary` / texto `onPrimary` | New York semibold |
| Você | Círculo | `outgoing` / texto `primary` | SF Pro semibold |
| Círculo (instância) | Anel: círculo vazado, traço 1,5 pt `primary`, fundo `canvas` | Texto `primary` | New York semibold |

**Forma indica tipo; cor não indica papel, acesso nem identidade verificada.** Iniciais: primeira letra das duas primeiras palavras significativas, ignorando “de, da, do, das, dos, e” (“Mesa de ideias” → MI). Tamanhos: 24 (seletor), 38 (cabeçalho), 40 (membros e sheet de círculos), 44 (solicitação), 52 (lista), 84 a 96 (Informações, Perfil).

### 5.5 Ícones e movimento

SF Symbols via API, peso alinhado ao texto. O rótulo acessível descreve a ação (“Anexar arquivo”, “Gravar áudio”, “Informações da conversa”). Alternativa original: traço de 1,8 a 2 pt em grade 24.

Transições de 120 a 200 ms. A única animação de marca é a entrada no círculo (1.2). Além dela, só: spinner de progresso, pulso lento no ponto de gravação e no indicador de digitação. Com Reduce Motion: sem deslocamento nem pulsação. Sem confete, sem animação contínua no onboarding, sem som automático.

---

## 6. Componentes

| Componente | Aparência | Estados e regras |
| --- | --- | --- |
| **Botão primário** | `primary`/`onPrimary`, altura ≥ 52, raio 12, 17 pt semibold | Normal, pressionado, foco, carregando (spinner + rótulo estável, ex. “Entrando…”), desabilitado (`surfaceMuted`/`disabledText`). Largura não muda no progresso |
| **Botão secundário** | Borda 1 pt `border`, texto `primary` | Mesmos estados |
| **Botão destrutivo** | Borda ou texto `danger` | Sempre seguido de alerta de confirmação |
| **Botão de texto** | `primary`, área ≥ 44 pt | “Agora não”, “Cancelar” |
| **Campo** | Label persistente acima, fundo `surface`, borda `border`, ajuda `caption` abaixo | Vazio, preenchido, foco, inválido com explicação, desabilitado. Placeholder não é label |
| **Busca** | `surfaceMuted`, raio 10, ícone lupa, sem borda | Sem resultado: “Nenhuma conversa com “termo”.” Solicitações somem durante a busca |
| **Segmentado** | Trilho `surfaceMuted`, segmento ativo `surface` + semibold | Usado em Aparência (Sistema · Claro · Escuro; padrão Sistema) e Gestão. Ativo identificável por peso, não só por cor |
| **Seletor de círculo** | Linha acima do título de Conversas: avatar de círculo 24, nome, chevron; ponto `primary` se houver novidade em outro círculo | Abre sheet (3.1). Área de toque ≥ 44 pt. Rótulo: “Círculo atual: Conselho. Trocar de círculo” |
| **Interruptor** | Ligado `success`, desligado `border` | `role=switch` com estado anunciado |
| **Barra de abas** | Fundo `canvas`, separador acima | Ativa: ícone preenchido + rótulo bold `primary`. Inativa: contorno + medium `textSecondary` |
| **Cabeçalho de conversa** | Compacto: voltar, avatar 38, nome, subtítulo, botão info | Subtítulo: “3 membros · toque para ver” ou “Conversa individual”; vira “Fulano está escrevendo…” em `accent` |
| **Linha de conversa** | Avatar 52, nome, hora, prévia de uma linha, contador | Não lida: hora e contador em `primary`, rótulo “N mensagens não lidas”. Rascunho: prefixo em `accent`, substitui a prévia. Pendente: prefixo “Pendente ·” em `warning`. Grupo: prévia com “Remetente:”; as suas com “Você:” |
| **Cartão de solicitação** | `surface`, raio 16, avatar 44, “Fulano quer conversar com você”, linha “Membro do seu círculo · nada é entregue antes do aceite” | “Aceitar” (primário) e “Recusar” (secundário) lado a lado, mesma largura. Recusar pede confirmação. Aceitar cria a conversa com mensagem de sistema |
| **Cartão de convite** | `surface`, linhas rótulo/valor: Círculo, Convite de, Uso, Validade | Validando, válido, entrando, confirmado, falhou, indisponível, limite atingido. Nunca mostrar token |
| **Bolha** | Recebida `surface`, enviada `outgoing`, padding 10 × 14, largura máx. 84% | Remetente só em grupo, `textSecondary` semibold 13 pt, e só na primeira bolha de uma sequência da mesma pessoa. Conteúdo selecionável, hora + estado |
| **Estado da mensagem** | Texto + ícone, `caption` | Ver 8.1. Pendente em `warning`; demais em `textSecondary` |
| **Mensagem de sistema** | Centralizada, `surfaceMuted`, `caption` | Aceite de conversa, entrada e saída de membro |
| **Nota de criptografia** | Topo do histórico, cadeado 14 pt, `caption` centralizada | “Criptografia de ponta a ponta. Mensagens recebidas ficam nos aparelhos de quem participa.” |
| **Anexo** | Ícone 44 em `surfaceMuted`, nome, “tamanho · tipo · Toque para abrir” | Baixando (progresso), disponível, cancelado, falhou |
| **Áudio** | Play/pause 40 `primary`, forma de onda decorativa, duração tabular | O progresso pinta a onda em `primary`. Onda oculta do leitor de tela |
| **Gravação** | Substitui o compositor: ponto `danger` pulsando, “Gravando · 0:04”, “Cancelar” (`danger`), “Enviar” (primário) | Permissão negada, interrompido, falha |
| **Compositor** | Anexar, campo com borda (raio 20), gravar ↔ enviar | Com texto: botão enviar `primary`. Sem texto: microfone. Enter envia. Rascunho guardado por conversa |
| **Indicador de digitação** | Bolha recebida com “Fulano está escrevendo…” | Ver 8.3: depende de decisão de privacidade |
| **Banner de estado** | `surface`, ícone + texto `warning` | Offline na lista (card) e na conversa (faixa acima do compositor) |
| **Alerta** | Nativo. Título, consequência, ação, “Cancelar” | Sobre `scrim`. Ação destrutiva em `danger` |
| **Toast** | Topo, `canvas` sobre `text` (invertido), 2,6 s | Ver 8.2 |
| **Gestão** | Listas simples com estado e data. Cabeçalho de Membros: “12 de 21 membros” em `secondary`, com a linha “Limite de membros” abaixo | O limite conta o anfitrião e convites pendentes. Ao atingi-lo, “Criar convite” fica desabilitado com o motivo “O círculo está completo.” Sem gráficos, marketing ou conteúdo de mensagens |
| **Limite de membros** | Linha em Gestão → Membros, valor à direita, stepper nativo | Mínimo: membros atuais + convites pendentes. Máximo: limite técnico do servidor (a definir). Reduzir abaixo do total exige retirar acessos antes; o stepper não desce além disso e explica: “Há 12 pessoas no círculo.” |
| **Cobertura ao trocar de app** | `canvas` liso, símbolo pequeno centrado | Sem nome do círculo, sem conteúdo |
| **Etiqueta de estado do círculo** | `caption` `textSecondary` no sheet de círculos | “Acesso retirado”, “Sem conexão”. Nunca só cor |

Alvos de toque ≥ 44 × 44 pt, inclusive ícones menores.

---

## 7. Acessibilidade

Referência: WCAG 2.2 AA aplicável + padrões iOS. A conformidade depende de prova em aparelho.

- **Ordem do VoiceOver:** título → estado/explicação → conteúdo → ação principal → secundária.
- **Sheets:** o foco vai ao título ao abrir e volta ao acionador ao fechar.
- **Mensagem:** um elemento com remetente, conteúdo, hora e estado; ações no menu acessível.
- **Áudio:** botão com “Ouvir mensagem de voz, 0:42” / “Pausar”; onda oculta.
- **Símbolo:** rótulo “InnerMesh”; a entrada no círculo anuncia “Você entrou no círculo”.
- **Progresso:** anunciar mudanças relevantes, não cada percentual.
- **Gestos:** nenhuma ação depende só de swipe ou toque longo. Compatível com Voice Control, Switch Control e teclado externo.
- **Sinais:** cor e som nunca são o único sinal de falha, recebimento ou seleção. Háptico nunca é o único sinal.
- **Revisar:** dois temas × aumento de contraste × Reduce Transparency × maior tamanho de texto. Para este público, começar pelo texto grande.
- **Privacidade:** não copiar conteúdo sensível para labels de diagnóstico, notificações ou relatórios.

---

## 8. Estados e texto

### 8.1 Mensagens

| Estado | Texto ao lado da hora | Ícone |
| --- | --- | --- |
| Pendente com rede | “Enviando” | Relógio, `warning` |
| Pendente sem rede | “Aguardando conexão” | Relógio, `warning` |
| Enviada ao servidor | “Enviada” | Um check |
| Entregue ao aparelho | “Entregue” | Dois checks |
| Falhou | “Não enviada” + “Tentar novamente” e “Apagar” separados | Alerta, `danger` |

Não existe estado “Lida” sem recibo real. Edição não aparece como nova entrega. Quando a conexão volta, as pendentes avançam sozinhas.

### 8.2 Toast e alerta

| Use toast | Use alerta | Use estado na tela |
| --- | --- | --- |
| Sucesso que não muda o que a pessoa vê: “Convite criado. Envie o link para uma pessoa.”, “Conversa com Ana aceita.” | Ação irreversível ou com consequência: revogar, sair, apagar, recusar | Qualquer erro, offline, pendente, convite inválido, acesso retirado |

**Erro nunca vai em toast.**

### 8.3 Fluxos

Textos neutros em gênero: não usar particípios ou pronomes que suponham o gênero de quem convida ou de quem é convidado (“convidado/a”, “dele/dela”).

| Situação | Texto e comportamento |
| --- | --- |
| Sem app | “Instale o InnerMesh e abra este convite novamente.” |
| Sem convite | “A entrada é por convite. Peça um a quem já participa de um círculo.” |
| Validando | Spinner + “Verificando convite…”. Não consumir no GET |
| Convite válido | Título “Você recebeu um convite.” + “Rafael Prado chamou você para o círculo **Conselho**.” + cartão + “Ao confirmar, você entra no círculo com este aparelho.” + “Entrar no círculo” / “Agora não”. Se o servidor não comprovar quem convidou: “Este convite é para o círculo **Conselho**.” |
| Entrando | Botão “Entrando…” com spinner, mesma largura |
| Resposta perdida | “Não foi possível confirmar a resposta. Seu convite continua válido.” + “Tentar novamente”. Reusar a chave local |
| Confirmado | Entrada no círculo (1.2); o título vira “Você está no círculo.” e o botão, “Continuar” → Perfil |
| Indisponível (expirado, cancelado, adulterado, usado) | “Este convite não está disponível.” + “Peça um novo a quem enviou o convite.” Mesmo texto para todos; não revelar quem usou |
| Capacidade atingida | “Este círculo está completo.” + “Fale com quem enviou o convite.” Nada é consumido |
| Perfil | “Como você quer aparecer?” + “Seu nome aparece para os membros do círculo. Não pedimos telefone nem e-mail.” Botão desabilitado até haver nome |
| Sem conversas | “Suas conversas vão aparecer aqui.” |
| Solicitação recebida | Cartão de solicitação; nada é entregue antes do aceite |
| Solicitação enviada | “Aguardando aceite.” |
| Grupo vazio | Anfitrião: “Escolha os membros deste grupo.” Membro: informativo, sem ação |
| Membro em Informações | “Só o anfitrião do círculo adiciona ou retira membros.” |
| Offline | “Sem conexão com o círculo. As mensagens continuam pendentes.” |
| Revogar membro | “Retirar acesso de Ana?” + “Ana deixa de enviar e receber mensagens no círculo. Mensagens já recebidas continuam nos aparelhos.” → “Retirar acesso” |
| Sair do grupo | “Sair de “Mesa de ideias”?” + “Você deixa de receber mensagens deste grupo. As mensagens já recebidas continuam neste aparelho.” |
| Acesso retirado | “Seu acesso ao círculo Conselho foi retirado.” + data + cartão “O que isso significa” (sem novas mensagens; cópias recebidas permanecem; o convite usado não serve para voltar) + “Apagar dados deste aparelho” |
| Gestão → Convites | “Cada convite vale para uma entrada. Se for repassado, quem usar primeiro entra.” |
| Círculo completo (anfitrião) | “O círculo está completo.” + “Aumente o limite ou retire o acesso de alguém para convidar outra pessoa.” |
| Já está no círculo | “Você já está neste círculo.” + “Abrir círculo”. Convite não consumido |
| Trocar de círculo | Sem confirmação. O título de Conversas muda; rascunhos ficam no círculo de origem |
| Sair do círculo | “Sair do círculo Conselho?” + “Você deixa de enviar e receber mensagens neste círculo. As mensagens já recebidas continuam neste aparelho até você apagá-las.” → “Sair do círculo” |
| Acesso retirado com outros círculos | Tela de acesso retirado no lugar de Conversas desse círculo; abas e seletor continuam disponíveis |
| Compartilhar no iOS | Escolher o círculo (se houver mais de um), depois a conversa. Só conversas autorizadas; erro visível sem acesso ou rede; cancelar não envia |

**Decisão pendente: indicador de digitação.** Ele revela atividade em tempo real. Proposta: desligado por padrão, com opção em Ajustes → Privacidade (“Mostrar quando estou escrevendo”), valendo nos dois sentidos.

---

## 9. Voz

PT-BR editorial, pronto para localização. Tratar por “você”, verbos concretos, nomear a consequência. Tom de quem recebe bem em casa: cordial e breve, sem intimidade forçada e sem formalidade de banco.

**Verbos de ação:** Entrar no círculo · Trocar de círculo · Abrir outro convite · Sair do círculo · Criar convite · Criar grupo · Escolher membros · Aceitar · Recusar · Retirar acesso · Sair do grupo · Tentar novamente · Apagar dados deste aparelho.

**Termos (não misturar):**

| Termo | Significa | Exemplo certo | Exemplo errado |
| --- | --- | --- | --- |
| InnerMesh | O app | “Instale o InnerMesh” | “Entre no InnerMesh do Rafael” |
| Círculo | A instância: todas as pessoas convidadas por um anfitrião | “Você está no círculo” | “Criar círculo” para um grupo de conversa |
| Grupo | Uma conversa com várias pessoas dentro do círculo | “Sair do grupo Mesa de ideias” | “Sair do círculo” para deixar um grupo |
| Convite | Abre acesso ao círculo | “Criar convite” | “Convidar para o grupo” (é “Escolher membros”) |
| Solicitação | Pede aceite para conversar entre membros | “Ana quer conversar com você” | “Convite de Ana” |
| Membro | Tem associação ativa no círculo | “12 de 21 membros” | n/a |
| Sair do círculo × Sair do grupo | Deixar a instância × deixar uma conversa | “Sair do círculo Conselho” | “Sair do grupo” para deixar o círculo |
| Anfitrião | Administra o círculo. No código e nas specs, continua `owner` | “Só o anfitrião do círculo…” | “Dono”, “admin” |
| Administrador | Papel dentro de um grupo | Rótulo na lista de membros | Usar para o anfitrião do círculo |

Nas telas de usuário, evitar SMP, XFTP, mTLS, CSR, relay, framework, gate. Termos técnicos vão para uma seção de diagnóstico sem segredos. Evitar também “exclusivo”, “seleto”, “elite” e “VIP”.

**Notificação padrão:** “Nova atividade no InnerMesh”, sem remetente, grupo, círculo ou conteúdo. Tocar abre o círculo com a atividade mais recente. Em Ajustes aparece como “Prévia das notificações: Discreta”. Prévia detalhada exige opção explícita e prova técnica.

**Troca de apps:** “Cobrir ao trocar de app”, ligado por padrão. A cobertura segue o componente da seção 6. Provar em ciclo real antes de anunciar proteção.

---

## 10. Responsividade

- iPhone em retrato e paisagem; largura mínima útil de 320 pt; safe areas variáveis.
- Sem altura fixa de tela; botões não truncam com texto ampliado.
- Com tamanho de acessibilidade, ações lado a lado (Aceitar/Recusar) passam a ficar uma em cima da outra e as células crescem.
- Na entrada no círculo com texto muito grande, o símbolo cai de 200 para 120 pt para o botão continuar visível sem rolar.
- Composição de referência: 390 × 844 pt.
- iPad não é meta; se rodar, uma coluna centralizada.
- O teclado nunca cobre o compositor nem os botões de confirmação.

---

## 11. Implementação (resumo)

Tokens com implementação única em `InnerMeshTheme` (variações Any/Dark, sRGB), consumida por app e extensões. Mapeamento direto da tabela 5.1; nenhuma view usa tom fixo. Adaptar o sistema de temas existente em vez de manter dois concorrentes. A troca de nomes, prefixos e caminhos antigos no código (`Taverna/` → `InnerMesh/`, `docs/taverna/` → `docs/innermesh/`) acontece só na fase 6 do plano de remediação, na branch `codex/innermesh-rename`, depois da prova da NSE. Arquivos novos de design entram desde já em `docs/innermesh/design/`. Detalhes de migração, assets, licenças e provas: GOVERNANCE.md.

---

## 12. Questões abertas

- [x] ~~Paleta~~: tinta, marfim e champanhe.
- [x] ~~Símbolo~~: 1a, Malha.
- [ ] **Anfitrião:** aprovar a coreografia de entrada no protótipo.
- [ ] **Anfitrião:** aprovar navegação Conversas/Ajustes com Gestão dentro de Ajustes.
- [ ] **Anfitrião:** indicador de digitação desligado por padrão com opção, ou não existir.
- [x] ~~Vários círculos no mesmo app~~: sim, como alvo de design (3.1). Implementação depende de spec própria; a primeira versão tem um círculo.
- [x] ~~Limite~~: configurável pelo anfitrião, contando o anfitrião (6), como alvo. Na primeira versão, fixo em 20 convidados ativos além do anfitrião (21 pessoas no total).
- [ ] **Produto:** mostrar ou não o número de membros no cartão de convite (o protótipo mostra; revela o tamanho do círculo a quem ainda não entrou).
- [x] ~~Termos “anfitrião” e “círculo”~~: aprovados.
- [ ] **Produto:** limite técnico máximo de membros por círculo e padrão sugerido ao criar (proposta: padrão 20).
- [ ] **Produto:** quantos círculos uma pessoa pode ter no mesmo app, e se o anfitrião de um círculo pode ser membro de outro.
- [ ] **Produto:** transferência de círculo quando o anfitrião quiser sair (fora desta fase, mas precisa de decisão para o texto).
- [ ] **Técnico:** custo de várias instâncias no mesmo aparelho (conexões, bateria, NSE) e efeito na notificação única.
- [ ] **Jurídico:** busca de marca e disponibilidade de “InnerMesh” na App Store e no INPI antes de produzir o ícone final.
- [ ] **Design:** gerar as telas do Apêndice A nos dois temas e regenerar o protótipo navegável.
- [ ] **Design:** desenhar Gestão → Grupos (criar grupo, escolher membros) e a Share Extension.
- [ ] **Design:** remedir todos os pares depois de qualquer ajuste e atualizar `tokens.json` e `contrast.json`.
- [ ] **Implementação:** finalizar símbolo e variantes do ícone no SDK adotado.

---

## Apêndice A. Rodada de design atual (0.5)

Esta seção muda a cada rodada; as regras acima não.

1. Telas nos temas escuro e claro, 390 × 844 pt, PT-BR: seletor de círculo (fechado e sheet aberto com três círculos, um com acesso retirado), entrada sem convite, confirmar convite (antes e depois da entrada no círculo), perfil local, lista de conversas com solicitação, conversa de grupo com áudio e anexo, informações do grupo, ajustes, gestão do círculo (convites, membros, grupos), acesso retirado.
2. Três explorações do símbolo dentro de 1.1, cada uma em 1024, 64, 24 e 20 pt, com teste de inversão e rotação.
3. A paleta bordô (5.1.2) aplicada a Confirmar convite e Conversa, lado a lado com a champanhe.
4. A entrada no círculo animada conforme 1.2, com a versão estática para Reduce Motion.
