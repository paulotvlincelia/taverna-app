# Contribuição

Leia [AGENTS.md](AGENTS.md). Abra uma issue canônica com problema, resultado, critérios e dependências. Ao executar, registre responsável, harness/sessão, branch, worktree, arquivos sob sua responsabilidade e integrador. Uma issue pública continua pública mesmo quando adicionada a um Project privado; contexto sensível não pertence aos comentários.

Crie o checkout da sessão com Git nativo, fora do clone principal:

```bash
git fetch origin
git worktree add -b codex/issue-tema ../taverna-app-worktrees/issue-sessao origin/stable
```

Leia as instruções de [ambientes isolados](docs/taverna/environments.md). Não compartilhe DerivedData, caches graváveis, banco, logs ou simulador entre sessões. Não remova um worktree com arquivos locais, conflitos ou trabalho não integrado; reconcilie antes de usar git worktree remove, sem --force.

TLC Lean/Driven estão em [.agents/skills](.agents/skills). Preserve licenças e origem. Checks da fundação (Python 3.12, sem bibliotecas externas):

```bash
python3.12 -m unittest discover -s tools/taverna/tests -v
python3.12 tools/taverna/check_foundation.py
python3.12 -m compileall -q tools/taverna
git diff --check
```

O preflight registra dependências e retorna exit 2 quando há gates bloqueados; não precisa acessar contas ou segredos. Build iOS usa o [guia isolado](docs/taverna/ios-build.md), com commit, toolchains, dependências, comandos e resultados próprios. Distinguir núcleo do fonte de bibliotecas pré-compiladas. Simulador não prova assinatura ou push em aparelho.

PRs trazem issue canônica, escopo, testes e limites. Integrar apenas após CI e Verifier independente no último commit. Nunca executar código de PR externo com credenciais de publicação. Distribuição exige revisão de assets, licença AGPL, fonte correspondente e capabilities próprias. Os workflows herdados estão arquivados em docs/taverna/upstream-workflows; somente Foundation fica ativo nesta etapa.
