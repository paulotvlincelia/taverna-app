# Contexto do primeiro build iOS

Coletado em 2026-10-16. Status: especificação e defaults aprovados pelo proprietário nesta data; qualificação em andamento.

Especificação: [spec.md](spec.md). Levantamento factual: [readiness.md](readiness.md).

## Limite da entrega

Comprovar a base iOS do fork Taverna em simulador no MacBook, preservando a fundação já integrada. Após revisar o plano, o proprietário autorizou sua execução, começando pela qualificação das bibliotecas oficiais. Publicação, distribuição e alterações administrativas continuam sujeitas aos limites registrados no plano.

## Orientações já dadas pelo proprietário

- Produto chamado Taverna, com mensageria privada para pessoas convidadas.
- Repositório público do app e repositório privado de operação, com planos claros em ambos.
- GitHub como fonte do projeto, sem depender do ferramenta externa para desenvolvimento.
- Repos e pastas de trabalho organizados sob Projects; branch e worktree próprios por sessão/harness.
- Não alterar a rede administrativa externa nem o agente serviço externo existente.

## Defaults aprovados e limite encontrado

As opções da tabela Assumptions & Open Questions da especificação foram aprovadas. A pesquisa não qualificou uma biblioteca oficial pré-compilada. O [relatório](core-qualification.md) e o [Design](design.md) detalham a alternativa de compilação do núcleo. O proprietário autorizou a instalação administrativa do Nix fora de Projects em 2026-10-16. Ela foi concluída pelo proprietário no Terminal gráfico e validada posteriormente com versão, daemon e montagem.

| Área | Proposta | Alternativa e consequência |
| --- | --- | --- |
| Primeiro resultado visível | App herdado compilado e onboarding testado. | Fazer branding antes mistura viabilidade da base com substituição de assets e identidade. |
| Núcleo nativo | Qualificar bibliotecas oficiais pré-compiladas. | Compilar o núcleo do fonte amplia toolchains e tempo de preparação; passa a ser necessário se a rota oficial não puder ser qualificada. |
| Simulador | iPhone 17, runtime 27.0, SDK 27.1. | Runtime 27.1 instalado lista apenas iPhone Duo; a seleção do destino precisa de prova nas duas opções. |
| Prova mínima | Abertura e navegação inicial em sessão com saída de rede bloqueada. | Troca de mensagens e criação de perfil são provas posteriores e não fazem parte deste marco. |

## Discricionariedade técnica

O agente deve investigar as lacunas técnicas sem pedir ao proprietário fatos que o código ou o ambiente podem responder. A implementação e suas tarefas serão definidas após revisão da especificação e deste contexto. A instalação Nix recebeu autorização administrativa explícita. Não existe autorização para aceitar contratos ou consultar credenciais Apple. A execução do restante do plano preserva esses limites.

## Ideias adiadas

Identidade visual Taverna, inventário completo de assets, assinatura própria, push, aparelho físico e grupos por convite permanecem nas issues existentes. Este marco não encerra essas entregas.

## Correção factual do alvo UI, em 2026-10-16

O texto inicialmente proposto, Create your profile, foi obtido da view CreateProfile de edição genérica. A navegação Get started abre CreateFirstProfile, definida no mesmo arquivo e com cabeçalho Your profile (CreateProfile.swift:195 e :233; SimpleXInfo.swift:128). Corrigido o texto do teste planejado antes de implementá-lo, preservando a intenção aprovada de provar a interface herdada e sem alterar a tela do app. Nenhum teste ou asserção existente foi modificado.

## Revisão do isolamento aprovada em 2026-10-16

O proprietário aprovou UDID exclusivo registrado no índice padrão do Xcode, com dados/caches/logs físicos no worktree, e contenção de IP remoto no processo do app antes do main. Serviços do sistema iOS ficam fora dela. IOS-04, IOS-05 e IOS-10 foram atualizados; os demais critérios permanecem. Não criar perfil nem mensagens, não alterar firewall/VPN. APP-004 registra a decisão; controles UIKit sintéticos não comprovam a execução da Taverna.

## Revisão aprovada do gate de UI em 2026-10-16

O proprietário aprovou explicitamente o perfil first-build: inglês, portrait e light, com os quatro métodos existentes/novo executados e todas as asserções preservadas, zero skips. A matriz integral continua disponível e pendente; nenhum resultado interrompido é aprovado. Permanecem os limites de 30 segundos por tela, dois ambientes limpos no mesmo commit/manifesto, CI e Verifier independente. A pergunta/aprovação ocorreu após a tentativa integral de 60 minutos, com 541 execuções positivas e suíte incompleta.
