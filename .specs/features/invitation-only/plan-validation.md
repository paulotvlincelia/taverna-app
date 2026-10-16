# Verificação independente do plano Taverna por convite

Data: 2026-10-16. Verifier independente do autor. Escopo fixado no conteúdo de `b68a6f87b9c3e0cf927017b1398826ba4e7f561a`, comparado com a base `9bfd78275a6f354ce3d18aaa7f2d47b48ba71756`.

## Veredito

**PASS para publicação e integração do plano documental, após a CI do commit deste relatório.** O conteúdo verificado teve as duas execuções Foundation do PR #11 aprovadas. O plano é consistente, publicável e separa requisitos aprovados de funcionalidades entregues. Este veredito não comprova controle de acesso, servidores próprios, convites, revogação, grupos, identidade visual, push, distribuição ou qualquer um dos 34 critérios do produto.

## Escopo observado

O diff contém `spec.md`, `context.md`, `research.md`, atualização de README, roadmap e handoff, além da inclusão da pasta da feature na fixture isolada Foundation. Não há mudança no app, protocolos, workflows, lockfiles, assets, simuladores ou ambientes operacionais.

O plano registra as escolhas do proprietário em `.specs/features/invitation-only/spec.md:34`: somente o proprietário emite entrada; `:35` dispensa aprovação posterior; `:36` reserva a ele criação e associação de grupos; `:37` permite conversas individuais com aceite mútuo; `:38` estabelece o futuro `DESIGN.md`. O contexto repete as decisões em `.specs/features/invitation-only/context.md:14` e preserva direção artística para revisão futura em `:16` e `:20`.

A distinção entre plano e produto está explícita em `.specs/features/invitation-only/spec.md:3`, `:9`, `:51` e `:215`; em `README.md:5` e `:36`; e em `docs/taverna/roadmap.md:19` e `:23`. Todos os 34 IDs aparecem uma única vez nos critérios e uma única vez na rastreabilidade, com status `Pending` em `.specs/features/invitation-only/spec.md:180` a `:213`.

## Evidências reproduzidas

| Prova | Resultado |
| --- | --- |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` | 70 testes passaram; zero falhas e zero skips. |
| `python3.12 tools/taverna/check_foundation.py` | Exit 0: `PASS: foundation only; no iOS build or release proof`. |
| `python3.12 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/invitation-only/spec.md --strict` | Exit 0; zero erros e zero avisos. |
| `git diff --check 9bfd78275a6f354ce3d18aaa7f2d47b48ba71756..b68a6f87b9c3e0cf927017b1398826ba4e7f561a` | Exit 0. |
| `check_commit.py` sobre os três commits do diff | Três mensagens Conventional Commits aprovadas. |
| CI Foundation do PR #11 no conteúdo `b68a6f87b9c3e0cf927017b1398826ba4e7f561a` | Duas execuções concluídas com `SUCCESS`. |
| Scanner independente sobre README, roadmap, STATE e todos os Markdown de `invitation-only` | 42 links Markdown inspecionados, 26 relativos; todos resolvem dentro do repositório. |
| Scanner independente de acesso privado | Nenhum caminho de usuário, IP Tailscale, chave privada, senha, token ou segredo atribuído encontrado no conteúdo novo. |
| URLs primárias citadas em `research.md` | Guia oficial SimpleX e dois arquivos fixados no commit upstream retornaram HTTP 200. |
| Conferência dos IDs | 34 critérios únicos, 34 linhas únicas de rastreabilidade, conjuntos idênticos e todos `Pending`. |

A fixture mudou somente sua preparação em `tools/taverna/tests/test_foundation.py:23`, acrescentando a pasta documental à cópia isolada. Nenhuma asserção, teste, skip ou código do checker foi enfraquecido.

As fontes técnicas citadas existem no commit: `docs/SERVER.md:718` limita `create_password` à criação de filas; `docs/XFTP-SERVER.md:349` limita a autenticação ao upload; `src/Simplex/Chat/Operators/Presets.hs:46` documenta a relação com links curtos; `apps/ios/SimpleXChat/APITypes.swift:267` mantém fallback SMP herdado; e `cabal.project:21` fixa SimpleXMQ. `research.md:35` mantém arquitetura sem escolha e `:47` declara os limites da pesquisa.

## Sensor de discriminação

As mutações foram feitas em worktree descartável sob `Projects`, no commit fixado. O worktree real permaneceu limpo antes e depois.

| Mutação isolada | Resultado |
| --- | --- |
| Trocar o link `context.md` da spec por `missing-context.md` | Scanner independente falhou com o caminho quebrado; mutante morto. |
| Inserir um caminho local de usuário sintético na spec | Scanner independente falhou por material de acesso privado; mutante morto. |
| Retirar `invitation-only` da cópia preparada em `test_foundation.py:23` | A suíte Foundation falhou e listou quatro links quebrados no README/roadmap; mutante morto. |

O sensor prova a revisão documental e a necessidade da alteração da fixture. Ele não é sensor de autorização real, fallback de rede, revogação ou segurança dos serviços.

## Defeito encontrado e corrigido

No HEAD anterior `44efc731e68287e1416b6dc520a5ff1e0466a689`, `README.md:5` ainda dizia que entrada e configuração seriam especificadas, em conflito com o plano publicado. O commit `b68a6f87b9c3e0cf927017b1398826ba4e7f561a` corrige a frase: entrada/configuração têm especificação aprovada, seguem sem implementação/prova, e notificações continuam pendentes de especificação detalhada e prova.

## Lacunas e riscos preservados

- O checker Foundation não percorre recursivamente o conteúdo de `.specs/features/invitation-only`; nesta revisão, links internos e vazamentos foram cobertos pelo scanner independente. Ampliar o checker em entrega própria reduzirá essa dependência manual.
- A issue #7 permanece aberta e sua descrição ainda apresenta a spec como pendente; isso corresponde ao PR ainda não integrado e deve ser reconciliado ao concluir a issue.
- Nenhum dos 34 critérios recebeu teste de comportamento ou evidência de implementação. A própria spec os mantém `Pending` em `.specs/features/invitation-only/spec.md:180` a `:213`.
- Não houve acesso a produção, credenciais, servidores, DNS, Mac mini, Tailscale, Alfred, simuladores ou contas Apple nesta verificação.

## Gate de integração

O conteúdo `b68a6f87b9c3e0cf927017b1398826ba4e7f561a` recebeu duas execuções Foundation verdes. Integrar somente se a CI também ficar verde depois do commit que acrescentar este relatório e se esse commit não modificar fontes além deste arquivo. O próximo trabalho continua sendo a prova técnica isolada; não é consequência comprovada deste PASS documental.
