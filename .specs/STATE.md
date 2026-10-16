# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only. Plano aprovado/integrado pelo PR #11 em stable 984a21659e6b846a874ae1a672fef5a890865070; issue #7 é a especificação. A issue #12 é somente a prova mínima de fronteira de acesso.
- Método: TLC Spec Driven dimensionado para experimento delimitado em três passos. O proprietário orientou usar a alternativa mais simples, reutilizando o piloto SimpleX, sem overengineering; rota A apenas experimental.
- Estado: fornecedores oficiais fixados e ponte/driver implementados; 11 testes reais SMP/XFTP em run-b, mais 70 regressões Foundation, passaram. A prova não integra app ou produção; os 34 critérios do produto seguem Pending.
- Próximo passo: Verifier independente e sensor no commit final da prova; publicar e integrar somente após CI e revisão verdes. Download em andamento e semântica completa de egress do app permanecem pendentes.
- Ownership: Codex, responsável e integrador; branch codex/access-control-qualification; worktree irmão taverna-app-worktrees/access-control-qualification. Escopo: tools/taverna/access_proof, artefatos invitation-only, este handoff e guia documental relacionado.
- Recursos: fixture Docker de dados fictícios, redes internas e nenhuma porta publicada; logs/chaves/bancos sob .build no worktree. Preservar arquivos ao encerrar os containers atribuídos. Não remover worktrees de prova anteriores nem o preview no simulador.
- Limites: Mac mini, Tailscale, Alfred, produção, DNS, app iOS, CI, locks, licenças e contas Apple sem alteração. Não publicar binários, convites, chaves, bancos, logs brutos ou conteúdo de mensagens, mesmo da fixture.
