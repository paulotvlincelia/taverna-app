# Roadmap do app

Estado em 2026-10-16: fundação F0 verificada; integração exige CI no commit com o relatório; app iOS, distribuição e push ainda sem prova própria. [Project público Taverna App — Roadmap](https://github.com/users/paulotvlincelia/projects/5).

| Épico | Entregas canônicas | Resultado esperado |
| --- | --- | --- |
| [E2: App iOS e identidade](https://github.com/paulotvlincelia/taverna-app/issues/1) | [Fundação](https://github.com/paulotvlincelia/taverna-app/issues/4), [assets e dependências](https://github.com/paulotvlincelia/taverna-app/issues/5), [primeiro build](https://github.com/paulotvlincelia/taverna-app/issues/6) | Compilar, testar e comprovar origem/identidade antes de distribuição |
| [E3: Convites e configuração](https://github.com/paulotvlincelia/taverna-app/issues/2) | [Spec de convites](https://github.com/paulotvlincelia/taverna-app/issues/7) | Fechar critérios para app, relays e grupos antes da implementação |
| [E4: Notificações e distribuição](https://github.com/paulotvlincelia/taverna-app/issues/3) | [Identidade e push próprios](https://github.com/paulotvlincelia/taverna-app/issues/8) | Push real em aparelho e caminho de distribuição viável |

Milestones: Fundação, TestFlight privado e Piloto até 20 convidados. O roadmap tem quadro por Status, backlog por Parent issue e roadmap agrupado por Marco. Início previsto e Alvo previsto permanecem vazios até estimativas fundamentadas; criação de campo não é compromisso de data.

Antes de mover para Pronto, aprovar a spec TLC e resolver gates de entrada. Na execução, registrar executor/harness, branch/worktree exclusivos, propriedade dos arquivos e integrador. Concluído exige critérios satisfeitos, PR integrado, CI e Verifier aplicáveis aprovados. Uma issue tem apenas um pai canônico; acompanhá-la em outro Project não cria outra spec nem muda sua visibilidade pública. Nenhuma informação operacional privada deve entrar em descrição/comentário.

Não executar o backlog automaticamente: cada entrega de produto tem escopo e provas próprios. Nesta fundação, nenhuma conta Apple, credencial, serviço de produção ou distribuição foi criada. O primeiro build deve distinguir bibliotecas pré-compiladas de núcleo reproduzido do fonte; simulador não prova APNs. Licenças e permissões dos assets seguem gates próprios.
