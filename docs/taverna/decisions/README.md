# Decisões públicas

## APP-001: fundação em 2026-10-16

Fork independente do SimpleX, mantendo AGPL, atribuições e restrições de assets. Primeiro iOS; build, identidade e notificações próprias precisam de prova antes da distribuição. GitHub e TLC versionado orientam agentes; cada sessão tem branch, worktree e estado isolados. Esta decisão não altera protocolos ou criptografia.

## APP-002: Nix para preparar o núcleo iOS, em 2026-10-16

O proprietário autorizou a instalação oficial Nix 2.34.9 no MacBook para realizar a receita Haskell.nix fixada pelo upstream. A qualificação não encontrou bibliotecas oficiais iOS que atendessem ao plano nas fontes consultadas. Reutilizar a derivação preserva GHC 9.6.3 e os locks; compatibilidade e resultado do build ainda precisam de prova.

Store /nix, volume APFS, contas técnicas, configuração e serviços do gerenciador são a exceção administrativa autorizada à organização sob Projects. Repositórios, worktrees, produtos, bancos, simuladores e evidências do projeto continuam na árvore Projects. A autorização não permite desativar proteções do macOS nem equivale a um build concluído.

O histórico desta execução fica nos artefatos de ios-first-build sob .specs/features. Seguir também o [guia de ambientes](../environments.md). Uma troca de derivação, flags ou locks precisa de justificativa e revisão; não atualizar dependências silenciosamente para resolver incompatibilidades.

## APP-003: cache assinado da toolchain, em 2026-10-16

O proprietário autorizou cache.iog.io e a chave pública hydra.iohk.io publicada no Haskell.nix fixado. A configuração do Nix permite esse substituter; cada comando do projeto o seleciona explicitamente. A verificação de assinaturas permanece habilitada e trusted-users continua restrito a root. Não conceder privilégios adicionais ao usuário ou aceitar chaves fornecidas por um flake sem revisão.

O auxiliar GHC 8.10.7 foi localizado no cache com a derivação exata esperada e assinatura dos metadados validada. Importação de conteúdo, hash local e resultado da avaliação são provas posteriores. Registrar separadamente os itens obtidos do cache e os compilados localmente; o uso do cache não comprova reconstrução local do núcleo.
