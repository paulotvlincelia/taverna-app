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

## Conferência do destino da navegação

O teste planejado passou a usar Your profile, o cabeçalho real da view CreateFirstProfile, aberta por Get started. A referência anterior à view CreateProfile foi corrigida antes de escrever o novo teste, conforme o contexto da feature. O código do app não foi alterado para acomodar o teste.

## Preparação SwiftPM independente

Enquanto a receita prepara seus auxiliares, as sete dependências Swift foram resolvidas com exit 0. Package.resolved permaneceu byte a byte idêntico, SHA-256 1b894975e60be2417dd202dce69b644f7d201560d98d4e661689e8df3cbb02ae. As revisões e o número de pins foram conferidos antes/depois.

O comando usou os flags documentados clonedSourcePackagesDirPath, packageCachePath, derivedDataPath, disableAutomaticPackageResolution, onlyUsePackageVersionsFromResolvedFile e skipPackageUpdates. O ambiente da ferramenta recebeu somente variáveis necessárias; HOME não foi reatribuído. Um probe Foundation confirmou home/Library Cocoa sob .build/xcode-user com CFFIXED_USER_HOME; temporários, configuração e module caches foram direcionados ao worktree.

O artefato WebRTC resolvido declara slice ios-x86_64_arm64-simulator. Essa observação de Info.plist não substitui a inspeção Mach-O dos produtos nem comprova o núcleo SimpleX. O manifesto fixado da dependência referencia WebRTC-M110.0.0.xcframework.zip com checksum 2598307f788ab668e0f42b2a1daef4306adbb9ec9c3959441064e8e84f7310ee. A resolução não manteve uma cópia ZIP nos diretórios examinados; não foi inventado um hash de arquivo baixado ausente.

Registros ignorados: .build/attempts/swiftpm-preparation-20261016/resolve-receipt.json, resolve.log, directory-probe.json e binary-platform-metadata.json. Nenhum app foi lançado por essa preparação.

## Cache auxiliar Haskell

O cache indicado no flake.nix de Haskell.nix da revisão fixada, cache.iog.io, respondeu HTTP 403 ao identificador padrão do Python. Uma conferência posterior com User-Agent Nix/2.34.9 respondeu HTTP 200. A indisponibilidade inicialmente atribuída ao cache era uma conclusão incorreta; a restrição observada é específica ao cliente da consulta.

O cache contém o output rkapi2fhggp8axjb6ykh3ql8jsdnwhgi-ghc-8.10.7, correspondente à derivação auxiliar exata em compilação. nix store verify --store https://cache.iog.io --no-contents --sigs-needed 1, com a chave pública hydra.iohk.io publicada no Haskell.nix fixado, terminou com exit 0. Isso verifica a assinatura dos metadados; o conteúdo ainda não foi importado ou conferido localmente. Probes e proposta de configuração estão sob .build/attempts/nix-cache-configuration-20261016 e nix-core-evaluation-20261016-02/cache-probes.json.

Nenhuma configuração global de confiança de caches foi modificada até esse registro. O proprietário recebeu a proposta concreta de permitir somente esse cache e sua chave pública, mantendo verificação de assinatura e o usuário sem trusted-users. A compilação auxiliar continua enquanto a decisão está pendente. Versões auxiliares de bootstrap não são apresentadas como a versão do compilador selecionada para o núcleo, ghc963.

## Limite da primeira avaliação

A tentativa com import-from-derivation e limite inicial de 1.800 s terminou com exit 124. Ela ainda compilava GHC 8.10.7 como auxiliar; nenhum caminho da derivação final foi produzido. O timeout permanece registrado em drv-path-ifd-receipt.json e não é PASS.

A segunda tentativa iniciou em 2026-10-16 às 13:59:59 UTC, com limite de 5.400 s previsto para builds. Usa o mesmo commit, atributo e locks, com keep-failed. Registros próprios em .build/attempts/nix-core-evaluation-20261016-02. O receipt.json dessa tentativa só será emitido ao término; .build/active-native-core.json identifica o processo e a sessão em andamento. Os outputs já completos da store foram preservados. A compilação incompleta do compilador auxiliar reiniciou.
