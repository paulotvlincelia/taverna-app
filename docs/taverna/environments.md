# Ambiente do app no MacBook

A fundação usa Git, gh e Python 3.12. O app requer Xcode completo, SDK iOS, simulador e bibliotecas Haskell compatíveis. O upstream seleciona GHC 9.6.3 em flake.nix; dependências estão fixadas em cabal.project e nos locks upstream. Não instalar a última versão indiscriminadamente.

Cada sessão usa branch e worktree exclusivos. No worktree da sessão:

```bash
mkdir -p .build/DerivedData .build/SourcePackages .build/cabal .build/stack .build/tmp .build/logs
export CABAL_DIR="$PWD/.build/cabal"
export STACK_ROOT="$PWD/.build/stack"
export TMPDIR="$PWD/.build/tmp"
```

Usar -derivedDataPath "$PWD/.build/DerivedData" e -clonedSourcePackagesDirPath "$PWD/.build/SourcePackages" nos comandos Xcode. Escolher DEVELOPER_DIR por comando, sem mudar globalmente xcode-select. O executável do compilador pode ser compartilhado; store/cache/bancos graváveis ficam locais. Registrar um UDID de simulador exclusivo por sessão; nunca apagar/resetar todos os simuladores. Signing e aparelho físico têm um responsável de uso serializado.

O preflight será executável com Python stdlib. Seus gates distinguem compilação em simulador, núcleo compilado do fonte e assinatura em aparelho. Instalar/abrir Xcode, aceitar licença e autenticar conta são etapas do proprietário; nenhuma credencial é consultada pelo preflight.

Não executar scripts/ios/download-libs.sh ou prepare.sh automaticamente: eles usam Downloads compartilhado e substituem diretórios. A entrega do primeiro build deve preparar entradas locais e registrar proveniência/hashes de bibliotecas. Bibliotecas pré-compiladas não são prova de núcleo reproduzido do fonte.

Ambientes: desenvolvimento local, integração em teste isolado com dados fictícios e produção existente separada. Esta fundação não configura instâncias, DNS, assinaturas, APNs ou distribuição. Ao encerrar, confira git status, commits integrados e arquivos locais; preserve qualquer pendência antes de remover worktree sem force.
