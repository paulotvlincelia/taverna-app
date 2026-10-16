# Contexto do primeiro build iOS

Coletado em 2026-10-16. Status: especificação e defaults aprovados pelo proprietário nesta data; qualificação em andamento.

Especificação: [spec.md](spec.md). Levantamento factual: [readiness.md](readiness.md).

## Limite da entrega

Comprovar a base iOS do fork Taverna em simulador no MacBook, preservando a fundação já integrada. Após revisar o plano, o proprietário autorizou sua execução, começando pela qualificação das bibliotecas oficiais. Publicação, distribuição e alterações administrativas continuam sujeitas aos limites registrados no plano.

## Orientações já dadas pelo proprietário

- Produto chamado Taverna, com mensageria privada para pessoas convidadas.
- Repositório público do app e repositório privado de operação, com planos claros em ambos.
- GitHub como fonte do projeto, sem depender do Hermes para desenvolvimento.
- Repos e pastas de trabalho organizados sob Projects; branch e worktree próprios por sessão/harness.
- Não alterar a VPN do outro Mac nem o agente OpenClaw existente.

## Defaults aprovados e limite encontrado

As opções da tabela Assumptions & Open Questions da especificação foram aprovadas. A pesquisa não qualificou uma biblioteca oficial pré-compilada. O [relatório](core-qualification.md) e o [Design](design.md) detalham a alternativa de compilação do núcleo. O uso de Nix requer uma instalação administrativa fora de Projects, ainda não autorizada.

| Área | Proposta | Alternativa e consequência |
| --- | --- | --- |
| Primeiro resultado visível | App herdado compilado e onboarding testado. | Fazer branding antes mistura viabilidade da base com substituição de assets e identidade. |
| Núcleo nativo | Qualificar bibliotecas oficiais pré-compiladas. | Compilar o núcleo do fonte amplia toolchains e tempo de preparação; passa a ser necessário se a rota oficial não puder ser qualificada. |
| Simulador | iPhone 17, runtime 27.0, SDK 27.1. | Runtime 27.1 instalado lista apenas iPhone Duo; a seleção do destino precisa de prova nas duas opções. |
| Prova mínima | Abertura e navegação inicial em sessão com saída de rede bloqueada. | Troca de mensagens e criação de perfil são provas posteriores e não fazem parte deste marco. |

## Discricionariedade técnica

O agente deve investigar as lacunas técnicas sem pedir ao proprietário fatos que o código ou o ambiente podem responder. A implementação e suas tarefas serão definidas após revisão da especificação e deste contexto. Não existe autorização implícita para instalar toolchains globais com administrador, aceitar contratos ou consultar credenciais Apple.

## Ideias adiadas

Identidade visual Taverna, inventário completo de assets, assinatura própria, push, aparelho físico e grupos por convite permanecem nas issues existentes. Este marco não encerra essas entregas.
