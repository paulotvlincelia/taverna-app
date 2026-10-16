# Design do primeiro build iOS

**Spec:** [spec.md](spec.md), aprovada em 2026-10-16.
**Status:** rota Nix e exceção administrativa autorizadas pelo proprietário em 2026-10-16. Instalação em andamento; compilação ainda não realizada.

## Architecture Overview

O plano aprovado selecionou bibliotecas oficiais pré-compiladas, condicionadas à origem comprovada. O [levantamento](core-qualification.md) não localizou uma entrada qualificada. O proprietário escolheu Nix e autorizou a exceção administrativa descrita abaixo. As alternativas permanecem registradas como contexto da escolha.

| Abordagem | Benefício | Custo e condição |
| --- | --- | --- |
| **Nix/Haskell.nix fixado, recomendada** | Reutiliza a receita do upstream, seus locks e GHC 9.6.3. | Nix ainda não instalado; instalação macOS cria store /nix e serviços/arquivos de sistema. Exige exceção explícita. Compatibilidade com o macOS/Xcode instalado ainda precisa de prova. |
| GHC/Cabal instalados localmente sob Projects | Mantém toolchain e estado do projeto na árvore aprovada, sem daemon Nix. | Exige traduzir a derivação, preparar dependências C, flags e empacotamento, e comprovar equivalência. Essa adaptação não foi implementada nem qualificada como atalho. |

Ambas miram o mesmo resultado do plano: app com núcleo real em simulador arm64, teste observável e repetição independente. As bibliotecas do núcleo passariam a ser construídas do fonte; esse estado precisa aparecer nas evidências, sem alegar reprodução bit a bit.

## Rota Nix proposta

1. Instalar o pacote oficial Nix fixado e revisado, com confirmação administrativa pessoal quando exigida pelo macOS. Preservar os checkouts e manter os arquivos de preparação sob Projects. Não aceitar contratos de terceiros ou consultar contas Apple.
2. Avaliar a derivação do fonte fixado sem atualizar flake.lock. Selecionar packages.aarch64-darwin com o atributo aarch64-darwin-ios:lib:simplex-chat. A sintaxe do comando final será validada pela ferramenta instalada; nenhum comando de compilação é apresentado aqui como já executado.
3. Registrar o plano de dependências e construir a biblioteca, incluindo flags swift/client_library, CommonCrypto e demais opções da receita original. Não substituir o conjunto por GHC/Cabal mais recentes.
4. Copiar os produtos da store imutável para o estado próprio do worktree. Preservar entrada original e registrar cada transformação mac2ios -s aplicada às cópias para simulador.
5. Inspecionar objetos e plataforma final, fixar hashes, licenças e entradas em manifesto. Só então avançar para SwiftPM/Xcode, seleção do simulador e contenção de rede.

O desenho restante do executor Xcode será fechado com as entradas conhecidas. Uma alteração de flake, flags ou locks para resolver erro é uma mudança revisável, não uma atualização automática.

## Exceção administrativa autorizada

A [documentação oficial do Nix](https://nix.dev/manual/nix/2.34/installation/installing-binary.html) e os scripts do pacote revisado descrevem instalação multiusuário no macOS. O instalador 2.34.9 rejeita --no-daemon no Darwin.

| Superfície | Efeito esperado do instalador oficial |
| --- | --- |
| /nix | Store e estado do gerenciador; volume APFS de suporte no macOS. |
| /etc/synthetic.conf e /etc/fstab | Montagem do volume, preservando entradas existentes. |
| /Library/LaunchDaemons | Serviço de montagem e daemon do Nix. |
| Usuários/grupo de build | Contas técnicas e grupo nixbld para a compilação. |
| /etc/nix/nix.conf | Configuração do gerenciador. |
| Perfis de shell de sistema | Inicialização do ambiente Nix e backups gerados pelo instalador. |
| Keychain do sistema | Se o volume for criptografado, credencial gerada para sua montagem; não é consulta a senhas existentes do projeto. |

Repos, worktrees, produtos do app, evidências, bancos e simuladores continuam sob Projects. O gerenciador e sua store de dependências seriam a exceção explícita, comparável a uma ferramenta instalada no sistema, e não um novo checkout do projeto. Não mover repositórios para /nix.

A preparação para revisão já baixou o pacote fixado dentro do worktree e conferiu o hash publicado pelo instalador. Nenhum script foi executado. Não prometer que --no-modify-profile evita alterações no modo daemon: a flag é tratada de forma diferente nos scripts examinados. Não instalar automaticamente canais móveis; a receita do app vem de flake.lock.

## Code Reuse Analysis

| Componente | Local | Uso previsto |
| --- | --- | --- |
| Receita do núcleo | flake.nix e flake.lock | GHC e dependências fixados; empacotamento de arquivos .a. |
| Dependências Haskell | cabal.project | Commits das fontes e index-state preservados. |
| Conversão de plataforma | mobile-core-tools, commit 4dcb77d5ea896d749381806dfab5358851b08951 | Ferramenta mac2ios da receita, com prova dos hashes antes/depois. |
| Projeto e scheme | apps/ios/SimpleX.xcodeproj | App, framework, extensões e suíte iOS existentes. |
| Ferramentas da fundação | tools/taverna | Checks preservados; não equivalem a prova iOS. |

## Components

- **Manifesto do núcleo:** identifica fonte, receita, ferramentas, hashes, licença e plataforma das bibliotecas reais. A qualificação atual tem estado BLOCKED e não fornece um manifesto de biblioteca aprovada.
- **Preparo da sessão:** mantém estado do projeto no worktree; registra responsável, caminhos e UDID exclusivo. Nix requer a exceção de sistema acima.
- **Executor de build/testes:** só será implementado após resolver a entrada do núcleo e demonstrar destino e rede isolados. Registra produtos reais, códigos de saída e testes obrigatórios.
- **Relatório final:** distingue build Swift, núcleo construído do fonte, assinatura em aparelho e distribuição; depende de duas execuções e do Verifier.

## Data Models

Nenhuma mudança de dados da aplicação. O registro local da qualificação contém schema, horário, commit fonte, status, exit_code, consultas e seus resultados, qualified_artifacts, downloaded_core_binaries, hashes dos arquivos de entrada e estados build/ios_tests/verifier. A ausência de uma biblioteca qualificada impede PASS.

## Error Handling Strategy

| Erro | Tratamento |
| --- | --- |
| Ausência de biblioteca qualificada | BLOCKED, exit 2; nenhum download ou build do núcleo presumido. |
| API indisponível ou sem JSON | INCONCLUSIVE para essa consulta; preservar a resposta e não convertê-la em ausência de artefatos. |
| Hash de ferramenta divergente | Não abrir o arquivo nem executar o instalador. |
| Conflito de instalação no Mac | Interromper; preservar os recursos existentes e pedir reconciliação, sem limpeza forçada. |
| Falha ao avaliar/buildar a receita fixada | Preservar logs e registrar o erro exato; não atualizar o lock para silenciá-lo. |

## Risks & Concerns

| Risco | Local | Impacto | Mitigação |
| --- | --- | --- | --- |
| Endpoint móvel e diretórios compartilhados | scripts/ios/download-libs.sh:36 e scripts/ios/prepare.sh:6 | Origem sem vínculo e interferência entre sessões. | Não executar esses scripts; entradas fixadas e cópias próprias. |
| Receita antiga com toolchain Apple atual | flake.nix:33, flake.lock | A instalação do Nix não garante que o núcleo compilará. | Avaliar/buildar o lock preservado e relatar incompatibilidades. |
| Conversão de plataforma altera arquivos | scripts/ios/prepare.sh:13 e mac2ios.c da revisão fixada | Arm64 sozinho não prova ABI de simulador. | Preservar original, inspecionar objetos e registrar hashes antes/depois. |
| Testes de lançamento sem asserção da tela | apps/ios/Tests iOS/Tests_iOS.swift:25 | Sucesso da suíte não prova navegação. | Acrescentar teste observável, preservando os existentes. |
| Biblioteca desktop confundida com iOS | Releases simplex-chat-libs | Link inválido ou falsa prova de compatibilidade. | Não substituir bibliotecas iOS por arquivos macOS sem a receita e a prova exigidas. |
| Efeitos administrativos fora de Projects | Instalador Nix 2.34.9 | Extrapolar a organização autorizada do Mac. | Exceção explícita antes de executar; pacote já preparado para revisão. |

## Tech Decisions

O proprietário autorizou Nix 2.34.9 no MacBook, com store e serviços fora de Projects, mantendo os projetos e suas evidências na árvore aprovada. A rota pré-compilada permanece bloqueada; a alternativa GHC/Cabal local não foi adotada. A instalação é um pré-requisito administrativo; o restante do executor será detalhado em tarefas antes de alterar código.

## Andamento da instalação

A primeira tentativa autenticou no macOS, criou o ponto /nix e um volume APFS vazio, mas terminou com exit 1 em vifs: error creating /etc/fstab. Não houve instalação do binário ou daemon até essa etapa. Evidência local: .build/attempts/nix-bootstrap-20261016/install.log.

O [relato no repositório Nix](https://github.com/NixOS/nix/issues/13723#issuecomment-3251454726) apresenta o mesmo erro e informa sucesso ao executar pela sessão gráfica. Isso indica um caminho de investigação; a causa neste MacBook ainda não foi comprovada. Não desativar SIP ou alterar permissões globais como atalho.

O controle automatizado do Terminal foi recusado pela ferramenta de UI por segurança. Foi preparado um helper local interativo, com verificação de hash e logs próprios, para execução manual pelo proprietário. Nenhum instalador foi reiniciado automaticamente após a falha, e o volume vazio foi preservado. Depois da execução manual, validar versão, conexão com o daemon e montagem antes de iniciar a avaliação da receita.
