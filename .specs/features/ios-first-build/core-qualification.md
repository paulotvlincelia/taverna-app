# Qualificação das bibliotecas oficiais iOS

**Resultado em 2026-10-16: BLOCKED.** Nenhuma biblioteca estática oficial iOS foi qualificada para o commit upstream 479548ee53ffb73db73841e77acbeee5a78dbbd5. Nenhum binário do núcleo foi baixado, ligado ou executado. O build e os testes iOS permanecem NOT RUN.

## Evidências consultadas

| Fonte | Resultado observado | Limite da conclusão |
| --- | --- | --- |
| [Releases do app](https://api.github.com/repos/simplex-chat/simplex-chat/releases?per_page=30) | 30 releases consultadas, da v7.1.0-beta.6 à v6.5.0-beta.9; nenhum asset com nome iOS, swift ou pkg-ios. | Não exclui servidores privados ou releases anteriores às consultadas. |
| [Release v7.0.4 do app](https://github.com/simplex-chat/simplex-chat/releases/tag/v7.0.4) | APKs e aplicativos desktop/CLI; sem os arquivos estáticos usados pelo projeto iOS. | A existência de um app macOS arm64 não prova uma biblioteca iOS Simulator compatível. |
| [Releases das bibliotecas](https://api.github.com/repos/simplex-chat/simplex-chat-libs/releases?per_page=100) | 34 releases retornadas; nenhum asset com nome iOS, swift ou pkg-ios. | As bibliotecas distribuídas para desktop/Node não foram tratadas como substitutas. |
| Release v7.0.4 no repositório de bibliotecas | A consulta pelo tag retornou HTTP 404. | Esse resultado vale para esse repositório e tag; não significa que toda versão está ausente. |
| [Orientação do mantenedor](https://github.com/simplex-chat/simplex-chat/issues/2013#issuecomment-1533785672) | O mantenedor orienta compilar as bibliotecas do fonte com Nix, em resposta à ausência da URL do job de download. | Comentário histórico de 2023; usado como orientação, não como prova absoluta da oferta atual. |
| [download-libs.sh na base](../../../scripts/ios/download-libs.sh) | Exige URL do job, usa latest/download/1 e Downloads compartilhado. | Não contém um artefato imutável ou vínculo verificável ao commit adotado. Script não executado. |
| GitHub Actions artifacts | A API não retornou JSON utilizável nas duas consultas realizadas. | Disponibilidade INCONCLUSIVE; não registrada como lista vazia. |

Os JSONs públicos recebidos e seus códigos de saída foram preservados sob .build/attempts/core-qualification-20261016/raw no worktree. O resumo estruturado local está em qualification.json nesse diretório. A conclusão é ausência de entrada qualificada nas fontes consultadas, não uma alegação de inexistência de qualquer binário iOS.

## Decisão de avanço

Aplicar IOS-02: interromper o preparo com status BLOCKED e exit 2. IOS-01 e IOS-09 ainda não têm um artefato real para comprovação. Não adotar ZIP de terceiro, artefato latest ou biblioteca desktop por semelhança de versão/arquitetura.

A saída mantém qualified_artifacts vazio, downloaded_core_binaries vazio, build NOT RUN e ios_tests NOT RUN. Nenhum requisito de build foi marcado como Verified.

## Alternativa preparada

O [Design](design.md) propõe compilar o núcleo com a derivação Haskell.nix fixada pelo upstream. Isso permite relacionar a biblioteca ao fonte e registrar a transformação mac2ios, os hashes e a plataforma final.

Nix não está instalado neste MacBook: não foi encontrado no PATH, nem no caminho de perfil padrão, nem foi encontrado /nix. A instalação oficial para macOS cria recursos de sistema fora da árvore de projetos e exige administrador. Portanto, a autorização do plano não foi interpretada como permissão para executá-la.

## Preparo do instalador, sem execução

Foi baixado para revisão somente o pacote oficial da ferramenta Nix, dentro do estado ignorado do worktree. Ele não contém as bibliotecas SimpleX qualificadas e não equivale a instalar a ferramenta.

| Entrada | Valor |
| --- | --- |
| Nix proposto | 2.34.9, aarch64-darwin |
| URL fixada | https://releases.nixos.org/nix/nix-2.34.9/nix-2.34.9-aarch64-darwin.tar.xz |
| Tamanho recebido | 17974492 bytes |
| SHA-256 esperado pelo instalador oficial | 2720033f9854c666988f65cb2a9a2f73bb5c34f71eea6e47f4826473583ac703 |
| SHA-256 recebido | 2720033f9854c666988f65cb2a9a2f73bb5c34f71eea6e47f4826473583ac703 |
| Execução | Nenhuma; scripts apenas lidos como dados. |

A extração para revisão leu somente arquivos regulares de instalação por tarfile.extractfile, sem executar o instalador nem extrair links da árvore store para o host. Manifesto local: .build/attempts/core-qualification-20261016/nix-installer-review.json.

## Próxima dependência

Autorizar a exceção administrativa descrita no Design, ou escolher a adaptação local GHC/Cabal antes de executá-la. Até essa decisão, não instalar Nix, não modificar o sistema e não afirmar que o primeiro build foi comprovado.
