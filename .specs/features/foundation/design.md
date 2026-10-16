# Design da fundação pública

**Status**: Approved em 2026-10-16.

Fonte upstream preservada; README e regras TLC públicas; checker stdlib da superfície acrescentada; preflight read-only e layout .build por sessão. Workflows herdados ficam arquivados. Nenhum segredo, produção, assinatura ou release é acessado. Alternativas consideradas: personalizar antes de comprovar build aumenta retrabalho; monorepo operacional público expõe contexto desnecessário. Escolha aprovada: fork independente e viabilidade antes de branding.

Modelos: upstream.json fixa origem/SHA/hashes das licenças; asset-policy.json mantém release BLOCKED; preflight informa ferramentas e gates com motivo. Falhas retornam exit 2. Inventário individual, fonte correspondente e capabilities próprias são obrigatórios antes da distribuição. Não inferir permissão de asset pela AGPL do código. O preflight não executa scripts de Downloads compartilhado e não altera xcode-select.
