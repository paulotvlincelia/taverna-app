# Taverna

Um espaço privado, por convite, para conversar sobre negócios, carreira, startups e assuntos sensíveis com pessoas escolhidas.

A Taverna está em desenvolvimento. O primeiro destino é um app iOS com mensagens, mídia e pequenos grupos. Entrada por convite e configuração da instância têm especificação aprovada e ainda precisam ser implementadas e comprovadas. Notificações próprias continuam pendentes de especificação detalhada e prova.

## Estado em 16 de outubro de 2026

Este repositório público é um fork independente do [SimpleX Chat](https://github.com/simplex-chat/simplex-chat), iniciado em `stable`, commit `479548ee53ffb73db73841e77acbeee5a78dbbd5`. A base do fork já compilou e executou neste MacBook: app, framework, Notification Service Extension e Share Extension, com núcleo SimpleX real. Duas reproduções limpas do mesmo commit passaram no perfil first-build, com quatro métodos de UI em cada uma, zero falhas/skips e navegação Get started → Your profile. **A interface ainda é a herdada do SimpleX; não há release ou TestFlight da Taverna.**

O núcleo Haskell foi construído localmente do fonte fixado por Nix; cinco bibliotecas e 4.187 objetos de simulador foram qualificados. O WebRTC continua sendo um binário do fornecedor, com origem/checksum registrados. Assinatura ad hoc no simulador não comprova assinatura em aparelho, APNs ou distribuição. A matriz integral de idiomas/orientações/aparências permanece pendente; o perfil aprovado usa inglês/portrait/light.

A entrega inclui regras de desenvolvimento, CI sem segredos, preflight do MacBook e ferramentas de build/prova. A CI Foundation verifica essas ferramentas e documentos; não compila o app iOS nem prova entrega de mensagens ou push.

## Código e licenças

O código original segue [AGPLv3](LICENSE). Os [assets têm licença própria](assets/ASSETS_LICENSE.md), e a [marca SimpleX](docs/TRADEMARK.md) tem condições próprias. A licença do código não autoriza usar todos os ícones, ilustrações ou designs em um app modificado. A Taverna precisa substituí-los ou obter permissão antes da distribuição. Consulte o [inventário e o gate de distribuição](docs/taverna/assets.md).

Este fork não é um produto oficial ou endossado pelo SimpleX. As alterações da Taverna e a base adotada ficam em [proveniência](docs/taverna/provenance.md). A [documentação original](README.upstream.md) permanece disponível. Antes de distribuir, fornecer o fonte correspondente ao binário, atribuições, alterações, dependências e instruções comprovadas.

## Desenvolver

Leia [AGENTS.md](AGENTS.md) e [CONTRIBUTING.md](CONTRIBUTING.md). Cada sessão usa branch, worktree, caches, DerivedData e simulador próprios. As skills TLC estão versionadas com origem e licença.

Os checks da fundação usam Python 3.12 e a biblioteca padrão:

```bash
python3.12 -m unittest discover -s tools/taverna/tests -v
python3.12 tools/taverna/check_foundation.py
```

Siga o [guia de build iOS](docs/taverna/ios-build.md) e as regras de [ambientes isolados](docs/taverna/environments.md). Os [registros da primeira prova](.specs/features/ios-first-build/execution.md) distinguem tentativas interrompidas, prova local e gates finais. As duas reproduções, a CI e o Verifier independente aprovaram o commit `6ea482bd4`; o [relatório](.specs/features/ios-first-build/validation.md) cobre os 20 critérios e seis falhas injetadas detectadas. O estado está nas [tarefas](.specs/features/ios-first-build/tasks.md). Os comandos upstream em [apps/ios/README.md](apps/ios/README.md) são referências técnicas; use o procedimento isolado versionado, com entradas fixadas.

## Próximas entregas

O [plano aprovado da próxima fase](.specs/features/invitation-only/spec.md) define entrada por convite, grupos controlados pelo proprietário e conversas entre convidados com aceite mútuo. Primeiro, comprovar a autorização e o uso dos servidores da instância em ambiente isolado. A fase de identidade produzirá um `DESIGN.md` com marca, tokens, componentes, telas e acessibilidade, acompanhado do inventário de assets/dependências. Os requisitos foram aprovados; a prova isolada de autorização e destinos é a próxima entrega, ainda sem funcionalidades entregues. Notificações e distribuição continuam com gates próprios. TestFlight é um canal beta com expiração; sua continuidade precisa de decisão própria.

Acompanhe o [roadmap](docs/taverna/roadmap.md), o [Project público](https://github.com/users/paulotvlincelia/projects/5) e as [issues](https://github.com/paulotvlincelia/taverna-app/issues). O [plano público da fundação](.specs/features/foundation/spec.md) é autossuficiente. Infraestrutura em uso, conversas e credenciais não pertencem a este repositório.
