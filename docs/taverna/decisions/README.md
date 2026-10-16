# Decisões públicas

## APP-001: fundação em 2026-10-16

Fork independente do SimpleX, mantendo AGPL, atribuições e restrições de assets. Primeiro iOS; build, identidade e notificações próprias precisam de prova antes da distribuição. GitHub e TLC versionado orientam agentes; cada sessão tem branch, worktree e estado isolados. Esta decisão não altera protocolos ou criptografia.

## APP-002: Nix para preparar o núcleo iOS, em 2026-10-16

O proprietário autorizou a instalação oficial Nix 2.34.9 no MacBook para realizar a receita Haskell.nix fixada pelo upstream. A qualificação não encontrou bibliotecas oficiais iOS que atendessem ao plano nas fontes consultadas. Reutilizar a derivação preserva GHC 9.6.3 e os locks; compatibilidade e resultado do build ainda precisam de prova.

Store /nix, volume APFS, contas técnicas, configuração e serviços do gerenciador são a exceção administrativa autorizada à organização sob Projects. Repositórios, worktrees, produtos, bancos, simuladores e evidências do projeto continuam na árvore Projects. A autorização não permite desativar proteções do macOS nem equivale a um build concluído.

O histórico desta execução fica nos artefatos de ios-first-build sob .specs/features. Seguir também o [guia de ambientes](../environments.md). Uma troca de derivação, flags ou locks precisa de justificativa e revisão; não atualizar dependências silenciosamente para resolver incompatibilidades.
