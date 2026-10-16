# Taverna

Um espaço privado, por convite, para conversar sobre negócios, carreira, startups e assuntos sensíveis com pessoas escolhidas.

A Taverna está em desenvolvimento. O primeiro destino é um app iOS com mensagens, mídia e pequenos grupos. Entrada por convite, configuração da instância e notificações próprias ainda serão especificadas e comprovadas.

## Estado em 16 de outubro de 2026

Este repositório público é um fork independente do [SimpleX Chat](https://github.com/simplex-chat/simplex-chat), iniciado em `stable`, commit `479548ee53ffb73db73841e77acbeee5a78dbbd5`. O código do mensageiro mantém a implementação upstream. **Ainda não há build, release ou TestFlight da Taverna.**

A fundação acrescenta regras de desenvolvimento, CI sem segredos, preflight do MacBook e planejamento. A CI Foundation verifica essas ferramentas e documentos; não compila o app iOS nem prova entrega de mensagens ou push.

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

O [guia do MacBook](docs/taverna/environments.md) descreve o preflight e a preparação iOS. Os comandos de build upstream em [apps/ios/README.md](apps/ios/README.md) são referências técnicas; nenhum build da Taverna foi comprovado nesta entrega. Não executar os scripts de preparação que usam Downloads compartilhado sem adaptar e verificar o isolamento.

## Próximas entregas

Primeiro comprovar toolchain e build iOS, inventariar assets/dependências e validar identidade e notificações próprias. Depois, especificar convites e testar distribuição. TestFlight é um canal beta com expiração; sua continuidade precisa de decisão própria.

Acompanhe o [roadmap](docs/taverna/roadmap.md), o [Project público](https://github.com/users/paulotvlincelia/projects/5) e as [issues](https://github.com/paulotvlincelia/taverna-app/issues). O [plano público da fundação](.specs/features/foundation/spec.md) é autossuficiente. Infraestrutura em uso, conversas e credenciais não pertencem a este repositório.
