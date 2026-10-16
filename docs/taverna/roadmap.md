# Roadmap do app

Estado em 2026-10-16: fundação e primeiro build iOS integrados; duas reproduções em simulador, CI e Verifier aprovados no PR #10. A interface continua herdada. Identidade Taverna, entrada exclusiva, aparelho, push e distribuição ainda sem prova própria. [Project público Taverna App — Roadmap](https://github.com/users/paulotvlincelia/projects/5).

| Épico | Entregas canônicas | Resultado esperado |
| --- | --- | --- |
| [E2: App iOS e identidade](https://github.com/paulotvlincelia/taverna-app/issues/1) | [Fundação](https://github.com/paulotvlincelia/taverna-app/issues/4), [assets e dependências](https://github.com/paulotvlincelia/taverna-app/issues/5), [primeiro build](https://github.com/paulotvlincelia/taverna-app/issues/6) | Compilar, testar e comprovar origem/identidade antes de distribuição |
| [E3: Convites e configuração](https://github.com/paulotvlincelia/taverna-app/issues/2) | [Spec de convites](https://github.com/paulotvlincelia/taverna-app/issues/7) | Fechar critérios para app, relays e grupos antes da implementação |
| [E4: Notificações e distribuição](https://github.com/paulotvlincelia/taverna-app/issues/3) | [Identidade e push próprios](https://github.com/paulotvlincelia/taverna-app/issues/8) | Push real em aparelho e caminho de distribuição viável |

Milestones: Fundação, TestFlight privado e Piloto até 20 convidados. O roadmap tem quadro por Status, backlog por Parent issue e roadmap agrupado por Marco. Início previsto e Alvo previsto permanecem vazios até estimativas fundamentadas; criação de campo não é compromisso de data.

Antes de mover para Pronto, aprovar a spec TLC e resolver gates de entrada. Na execução, registrar executor/harness, branch/worktree exclusivos, propriedade dos arquivos e integrador. Concluído exige critérios satisfeitos, PR integrado, CI e Verifier aplicáveis aprovados. Uma issue tem apenas um pai canônico; acompanhá-la em outro Project não cria outra spec nem muda sua visibilidade pública. Nenhuma informação operacional privada deve entrar em descrição/comentário.

Não executar o backlog automaticamente: cada entrega de produto tem escopo e provas próprios. Nesta fundação, nenhuma conta Apple, credencial, serviço de produção ou distribuição foi criada. O primeiro build deve distinguir bibliotecas pré-compiladas de núcleo reproduzido do fonte; simulador não prova APNs. Licenças e permissões dos assets seguem gates próprios.

## Próxima fase aprovada

A [spec de entrada e configuração](../../.specs/features/invitation-only/spec.md) e o [contexto](../../.specs/features/invitation-only/context.md) registram as decisões do proprietário e os pressupostos aprovados em 2026-10-16. Somente o proprietário emite convites e cria grupos/escolhe membros. O convite individual basta para entrar, sem aprovação posterior. Os convidados podem conversar entre si com aceite mútuo. Esses comportamentos ainda não estão implementados.

Sequência: requisitos aprovados; comprovar autorização individual e compatibilidade com os serviços em ambiente isolado; preparar identidade e seu DESIGN.md; construir uma fatia completa; qualificar operação, aparelhos e distribuição; iniciar piloto pequeno. As [evidências e lacunas](../../.specs/features/invitation-only/research.md) explicam por que convites de contato e uma senha compartilhada de relay não comprovam o perímetro desejado.

O DESIGN.md será produzido na raiz durante a fase de identidade. Seu contrato na spec cobre marca, tokens, componentes, estados, fluxos, acessibilidade, assets/licenças e tradução para iOS. Não existe identidade visual aprovada nesta etapa.
