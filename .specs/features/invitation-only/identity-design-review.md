# Revisão independente da proposta de identidade

**Veredito: PASS para a entrega documental no commit `462d7715343d429be2c70a5d43ac45fb240a7acb`.** O `DESIGN.md` está pronto para a revisão visual do proprietário e cobre as dez áreas do contrato. Este veredito não aprova a direção artística, não comprova interface implementada e não conclui a feature `invitation-only`.

**Data:** 2026-10-17
**Base:** `c25dc4eb0d963afa916ac7605c5f2665e66318ba`
**Diff verificado:** `c25dc4eb0d963afa916ac7605c5f2665e66318ba..462d7715343d429be2c70a5d43ac45fb240a7acb`
**Autor do commit alvo:** Paulo Tavares, conforme metadado Git
**Verifier:** Codex em sessão independente de verificação, diferente do autor
**Método:** TLC Spec Driven, validação documental com evidência ou zero e sensor em cópias sob `.build`

## Resultado contra o pedido

| Obrigação | Evidência | Resultado |
| --- | --- | --- |
| Proposta explícita, separada de decisão humana | `DESIGN.md:5-13` declara Draft 0.1.0, aprovação visual pendente, ausência de telas implementadas e natureza ilustrativa da prancha. `DESIGN.md:242-246` reserva direção, símbolo e navegação ao proprietário. `.specs/features/invitation-only/context.md:16-20` confirma que nenhuma direção artística foi aprovada e que a escolha final não foi delegada. | PASS |
| Convite individual sem segunda aprovação | `DESIGN.md:185-192` descreve instalação, validação, confirmação explícita, estados inválidos, capacidade e ativação. `DESIGN.md:202` afirma que a ausência de segunda aprovação é decisão do produto e rejeita inferir identidade verificada. | PASS documental |
| Grupos administrados somente pelo proprietário | `DESIGN.md:69-74` restringe gestão, criação e escolha de membros ao proprietário e mantém autorização no núcleo/serviços. `DESIGN.md:195` diferencia o estado vazio por papel; `DESIGN.md:161` limita o componente de gestão ao proprietário. | PASS documental |
| Conversa individual com aceite mútuo | `DESIGN.md:43-47` fixa o objetivo. `DESIGN.md:194` mantém a conversa pendente, oferece aceitar/recusar ao destinatário e impede entrega de conteúdo antes do aceite. | PASS documental |
| Limites de privacidade | `DESIGN.md:19-23` proíbe promessas de anonimato absoluto, bloqueio de captura ou apagamento remoto. `DESIGN.md:198-202` explica o alcance da revogação e do convite. `DESIGN.md:204-210` separa convite, conversa, papéis e prévias genéricas. | PASS documental |
| Estados e papéis | `DESIGN.md:51-55`, `DESIGN.md:61-72`, `DESIGN.md:148-163` e `DESIGN.md:181-202` cobrem proprietário, convidado, participante assistivo, estados de componentes e estados de fluxo. | PASS |
| Cores, medidas, VoiceOver e escala | `DESIGN.md:86-119` define tokens e limiares; `DESIGN.md:121-138` define tipografia e medidas; `DESIGN.md:163-179` define alvos, VoiceOver, foco, Dynamic Type, contraste e comportamento responsivo. | PASS documental |
| Origem, licença e bloqueio de assets | `DESIGN.md:25-39`, `DESIGN.md:142-144` e `DESIGN.md:220-232` exigem origem/licença, não reutilização indevida e inventário final. `docs/taverna/asset-policy.json:3-5` mantém `BLOCKED` e zero assets aprovados. | PASS para manutenção do bloqueio |

## Cobertura das dez áreas contratuais

| Área do contrato em `.specs/features/invitation-only/spec.md:139-154` | Cobertura rederivada | Resultado |
| --- | --- | --- |
| Marca | `DESIGN.md:15-23` define conceito, público, personalidade, nome, assinatura, voz e limites de privacidade. | PASS |
| Símbolo e assinatura | `DESIGN.md:25-39` cobre direção do símbolo, variantes, proteção, mínimos, fundos, usos incorretos, formatos mestres, licença e gate do ícone. O símbolo continua provisório. | PASS documental |
| Cores | `DESIGN.md:84-119` define paleta semântica claro/escuro, estados, valores sRGB, mínimos e limites da medição. | PASS |
| Tipografia e medidas | `DESIGN.md:121-138` cobre famílias/licenças, hierarquia, pesos, entrelinhas, Dynamic Type, espaçamento, grid, raios, bordas, safe areas e transparência. `DESIGN.md:163` exige toque mínimo de 44 × 44 pt. | PASS |
| Ícones, ilustrações e movimento | `DESIGN.md:140-144` cobre origem, SF Symbols, alternativa original, avatares, ilustrações, Reduce Motion e áudio iniciado por ação. | PASS |
| Componentes | `DESIGN.md:146-163` cobre botões, campos, navegação, listas, avatares, convites, mensagens, anexos, áudio, diálogos, alertas, banners e gestão com estados aplicáveis. | PASS |
| Fluxos e telas | `DESIGN.md:57-74` mapeia superfícies e papéis; `DESIGN.md:181-202` cobre instalação, convite válido/inválido/cancelado/usado, entrada, conversa pendente, grupos, rede, compartilhamento e revogação. | PASS |
| Privacidade e acessibilidade | `DESIGN.md:165-173` cobre VoiceOver, foco, contraste, ampliação, controles alternativos e sinais além de cor. `DESIGN.md:204-210` cobre prévias, dados sensíveis e linguagem. | PASS documental |
| Aplicação iOS | `DESIGN.md:212-232` cobre app, Share Extension, NSE, catálogos, ícone, distribuição e substituição dos elementos herdados. | PASS documental |
| Implementação e verificação | `DESIGN.md:214-240` mapeia tokens para implementação, versões/formatos/inventário e exige revisão de três telas em dois temas e texto ampliado, além de provas em aparelho. A prancha atual é referência de escala padrão. | PASS documental |

## Prancha e tokens

`docs/taverna/design/reference.svg` foi renderizado localmente em PNG 1360 × 1820. A inspeção visual confirmou três composições fictícias, cada uma em tema claro e escuro: Confirmar convite, Conversas e Conversa. A própria prancha declara proposta, conteúdo fictício, aprovação pendente, interface não implementada, licença CC BY 4.0 e símbolo provisório em `reference.svg:1-8` e `reference.svg:161-162`.

O cálculo oficial e um cálculo independente produziram 46 pares. Todos atingem o mínimo declarado. O resultado oficial foi idêntico byte a byte a `docs/taverna/design/contrast.json`. O par com menor margem foi `light/disabledText/surfaceMuted`, razão `5.0081` para mínimo `4.5`. Isso comprova somente os pares sRGB opacos declarados, conforme `DESIGN.md:113-119`; não comprova contraste renderizado nem acessibilidade do app.

## Gates executados

| Comando/prova | Resultado |
| --- | --- |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` | PASS: 78 testes, 0 falhas, 0 skips. A base executada em cópia do commit base passou 76 testes; delta `+2`, correspondente aos casos de `DESIGN.md`. |
| `python3.12 tools/taverna/check_foundation.py` | PASS: `foundation only; no iOS build or release proof`. |
| `python3.12 -m compileall -q tools/taverna docs/taverna/design/measure_contrast.py` | PASS. |
| `python3.12 docs/taverna/design/measure_contrast.py` | PASS: 46/46 pares; saída idêntica a `contrast.json`. |
| cálculo independente dos tokens | PASS: 46/46 pares e valores arredondados iguais ao relatório versionado. |
| `git diff --check` e `git diff --check c25dc4eb0d963afa916ac7605c5f2665e66318ba..462d7715343d429be2c70a5d43ac45fb240a7acb` | PASS. |
| `docs/taverna/asset-policy.json` | PASS para o gate esperado: `release_status=BLOCKED`, `approved_assets=[]`. |

## Sensor de discriminação

As mutações ocorreram somente em três cópias integrais do commit sob `.build`. O porcelain do worktree real permaneceu idêntico antes e depois dos sensores.

| Mutação | Prova esperada | Resultado |
| --- | --- | --- |
| Link inexistente acrescentado a uma cópia de `DESIGN.md` | Checker deve recusar o documento | KILLED: exit 2 e `DESIGN.md: broken link missing-identity-design-sensor.md`. |
| Caminho privado acrescentado a outra cópia de `DESIGN.md` | Checker deve detectar material privado | KILLED: exit 2 e `DESIGN.md: private access material`. |
| `disabledText` claro alterado para a mesma cor de `surfaceMuted` | Medidor deve recusar contraste 1:1 | KILLED: exit 1, status `FAIL`, razão `1.0` contra mínimo `4.5`. |

**Sensor:** PASS, 3/3 mutações mortas, zero sobreviventes.

## Limites e gaps mantidos

- A aprovação visual do proprietário continua pendente. Este relatório não escolhe a direção verde/papel/latão, o símbolo ou a navegação.
- Nenhuma tela Taverna foi implementada. Não houve UI, aparelho, Share Extension, NSE, VoiceOver, foco, texto ampliado, toque, movimento ou acessibilidade em execução.
- O símbolo e o ícone finais, exports, inventário por arquivo, hashes, licenças e revisão em tamanhos reais continuam pendentes. Distribuição permanece bloqueada.
- `BRAND-02` e `BRAND-03` continuam `Pending`. A tabela de rastreabilidade preserva os 34 requisitos agregados como `Pending`; este PASS é estritamente documental e não declara a feature integral pronta.
- CI e integração continuam como gates posteriores. Este trabalho não publica, envia ou integra a branch.

## Condição de parada

A entrega documental pode seguir para aprovação visual do proprietário. Integração exige que este relatório seja persistido no último commit documental, que os checks sejam repetidos nesse estado e que a CI correspondente passe. Implementação visual só começa depois da aprovação humana prevista em `DESIGN.md:234-240`.
