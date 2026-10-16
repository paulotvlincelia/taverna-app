# Execução do primeiro build iOS

Registro factual de 2026-10-16. O núcleo e o app ainda não foram compilados nesta etapa. Este arquivo não substitui o relatório independente de validação.

## Ambiente Nix validado

O proprietário concluiu a execução do instalador pelo Terminal gráfico. O helper registrou exit 0. A validação posterior encontrou Nix 2.34.9 e conexão funcional com o daemon.

| Prova | Resultado observado | Registro local ignorado |
| --- | --- | --- |
| Instalação gráfica | Exit 0 | .build/attempts/nix-bootstrap-20261016/gui-install.exit |
| Versão | nix (Nix) 2.34.9 | .build/attempts/nix-validation-20261016/environment.json |
| Conexão com daemon | Exit 0; version 2.34.9; trusted false | .build/attempts/nix-validation-20261016/daemon-ping.json |
| Store | /nix montado em APFS, global permissions habilitadas | environment.json e consulta diskutil da validação |

O cliente permanece sem privilégios de trusted user do Nix. A preparação dos inputs usa cache/configuração temporária sob .build/nix no worktree. Store e serviços do gerenciador seguem a exceção APP-002 já autorizada.

O erro inicial de vifs não foi tratado como instalação concluída. A tentativa com falha foi preservada, seguida da tentativa gráfica com exit 0. Não foi necessário desativar proteções do macOS.

## Fonte fixado e correspondência

A consulta flake metadata terminou com exit 0 usando o commit 479548ee53ffb73db73841e77acbeee5a78dbbd5 de simplex-chat/simplex-chat, com no-write-lock-file e no-update-lock-file.

Nar hash registrado pelo Nix: sha256-UnuHHuOg1GHTAHYLuht16IuLQvoQRK71MN2DYeGr3po=.

Os hashes SHA-256 de sete arquivos do fonte recuperado foram comparados com o fork:

- flake.nix e flake.lock;
- cabal.project e simplex-chat.cabal;
- LICENSE;
- apps/ios/SimpleXChat/SimpleX.h;
- Package.resolved do projeto iOS.

Todos os sete são idênticos. Os hashes individuais e o vínculo com o commit estão em .build/attempts/nix-core-evaluation-20261016/source-correspondence.json. Nenhuma biblioteca nativa foi qualificada por essa comparação: ela comprova as entradas examinadas, não um produto compilado.

## Avaliação da receita

O alvo selecionado é packages.aarch64-darwin com o atributo aarch64-darwin-ios:lib:simplex-chat. O primeiro probe desabilitou import-from-derivation e terminou com exit 1: a receita precisa realizar derivações auxiliares durante a avaliação.

A avaliação seguinte permite esse mecanismo da receita original, preservando o commit e os locks. Ela pode construir auxiliares usados para resolver o plano Haskell. Isso não equivale a compilar o app Swift ou a executar o mensageiro.

Registros locais: .build/attempts/nix-core-evaluation-20261016/drv-path-ifd.stdout, drv-path-ifd.stderr.log e drv-path-ifd-receipt.json, este último gravado ao término da tentativa. Nenhuma mudança do fonte é feita para silenciar erros da receita.

## Próximas provas

Ainda faltam resolver a derivação, obter as bibliotecas reais, conferir plataforma/arquitetura e fechar o executor de build e testes conforme a [especificação](spec.md). O destino isolado, a contenção de rede, o teste observável, a repetição limpa e o Verifier permanecem pendentes.
